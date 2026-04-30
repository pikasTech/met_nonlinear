import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { randomUUID } from 'crypto';

export type PaperFigureKind = 'single' | 'montage';
export type RenderJobStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface PaperFigureConfigEntry {
  kind?: PaperFigureKind;
  title?: string;
  description?: string;
  output_name?: string;
  renderable?: boolean;
  subfigures?: string[];
  parent_montages?: string[];
  [key: string]: unknown;
}

export interface PaperFigureCatalogItem {
  id: string;
  kind: PaperFigureKind;
  title: string;
  description: string;
  editable: boolean;
  renderable: boolean;
  outputName: string;
  previewUrl: string;
  exists: boolean;
  updatedAt: string | null;
  config: PaperFigureConfigEntry;
  projectPath: string;
  configPath: string;
}

export interface PaperFigureCatalogResponse {
  autoRenderDebounceMs: number;
  figures: PaperFigureCatalogItem[];
}

export interface PaperFigureConfigFile {
  figure_pipeline?: {
    auto_render_debounce_ms?: number;
    figures?: Record<string, PaperFigureConfigEntry>;
  };
  paper_figure?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface RenderJob {
  id: string;
  figureIds: string[];
  status: RenderJobStatus;
  startedAt: string | null;
  finishedAt: string | null;
  command: string[];
  logs: string[];
  error: string | null;
}

interface PlotProjectRecord {
  id: string;
  kind: PaperFigureKind;
  title: string;
  description: string;
  outputName: string;
  projectPath: string;
  configPath: string;
  dataPath: string;
  paper: Record<string, unknown>;
  figureConfig: PaperFigureConfigEntry;
}

interface PlotProjectIndex {
  plotRoot: string;
  byId: Map<string, PlotProjectRecord>;
  byProjectPath: Map<string, PlotProjectRecord>;
}

const TF26_CANDIDATES = [
  path.join(process.env.USERPROFILE ?? '', '.conda', 'envs', 'tf26', 'python.exe'),
  path.join(process.env.USERPROFILE ?? '', 'MiniConda3', 'envs', 'tf26', 'python.exe'),
  path.join(process.env.USERPROFILE ?? '', 'miniconda3', 'envs', 'tf26', 'python.exe'),
];

const renderJobs = new Map<string, RenderJob>();

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function readJsonConfig(configPath: string): PaperFigureConfigFile {
  return JSON.parse(fs.readFileSync(configPath, 'utf-8')) as PaperFigureConfigFile;
}

function writeJsonConfig(configPath: string, config: PaperFigureConfigFile): void {
  fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`, 'utf-8');
}

function cloneConfig(value: unknown): PaperFigureConfigEntry {
  return JSON.parse(JSON.stringify(isRecord(value) ? value : {})) as PaperFigureConfigEntry;
}

function stringValue(value: unknown): string | null {
  return typeof value === 'string' && value.length > 0 ? value : null;
}

function pathKey(value: string): string {
  return path.resolve(value).toLowerCase();
}

function relFromRoot(rootDir: string, value: string): string {
  return path.relative(rootDir, value).replace(/\\/g, '/');
}

function resolveRepoPath(rootDir: string, value: string): string {
  return path.isAbsolute(value) ? path.resolve(value) : path.resolve(rootDir, value);
}

function encodeStaticPath(value: string): string {
  return value.split(/[\\/]+/).filter(Boolean).map((part) => encodeURIComponent(part)).join('/');
}

function uniqueStrings(values: string[]): string[] {
  return Array.from(new Set(values.filter((value) => value.length > 0)));
}

function coerceKind(value: unknown, fallback: PaperFigureKind): PaperFigureKind {
  const normalized = typeof value === 'string' ? value.toLowerCase() : '';
  if (normalized === 'multi' || normalized === 'montage') {
    return 'montage';
  }
  if (normalized === 'single') {
    return 'single';
  }
  return fallback;
}

function resolvePythonExecutable(): string {
  const resolved = TF26_CANDIDATES.find((candidate) => candidate && fs.existsSync(candidate));
  return resolved ?? 'python';
}

function collectConfigPaths(dir: string, output: string[]): void {
  if (!fs.existsSync(dir)) {
    return;
  }
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      collectConfigPaths(fullPath, output);
    } else if (entry.isFile() && entry.name === 'config.json') {
      output.push(fullPath);
    }
  }
}

function scanPlotConfigPaths(plotRoot: string): string[] {
  const configPaths: string[] = [];
  collectConfigPaths(plotRoot, configPaths);
  return configPaths
    .filter((configPath) => !path.relative(plotRoot, configPath).split(path.sep).includes('data'))
    .sort((left, right) => left.localeCompare(right, undefined, { numeric: true, sensitivity: 'base' }));
}

function projectRecordFromConfig(rootDir: string, configPath: string): PlotProjectRecord | null {
  const payload = readJsonConfig(configPath);
  const paper = isRecord(payload.paper_figure) ? payload.paper_figure : {};
  const projectPath = path.dirname(configPath);
  const taskInfo = isRecord(payload.task_info) ? payload.task_info : {};
  const taskType = stringValue(taskInfo.task_type);
  const relativeParts = path.relative(path.join(rootDir, 'ex_projects', 'plot'), projectPath).split(path.sep);
  const fallbackKind: PaperFigureKind =
    taskType === 'paper-figure-multi' || relativeParts.includes('multi') ? 'montage' : 'single';
  const figureConfig = cloneConfig(paper.figure_config);
  const id = stringValue(paper.figure_id) ?? path.basename(projectPath);
  const kind = coerceKind(paper.kind ?? figureConfig.kind, fallbackKind);
  const outputName = stringValue(paper.output_name) ?? stringValue(figureConfig.output_name) ?? `${id}.png`;
  const title = stringValue(paper.title) ?? stringValue(figureConfig.title) ?? id;
  const description = stringValue(paper.description) ?? stringValue(figureConfig.description) ?? '';
  return {
    id,
    kind,
    title,
    description,
    outputName,
    projectPath,
    configPath,
    dataPath: path.join(projectPath, 'data', outputName),
    paper,
    figureConfig,
  };
}

function loadPlotProjects(rootDir: string): PlotProjectIndex {
  const plotRoot = path.join(rootDir, 'ex_projects', 'plot');
  const byId = new Map<string, PlotProjectRecord>();
  const byProjectPath = new Map<string, PlotProjectRecord>();
  for (const configPath of scanPlotConfigPaths(plotRoot)) {
    const record = projectRecordFromConfig(rootDir, configPath);
    if (!record) {
      continue;
    }
    byId.set(record.id, record);
    byProjectPath.set(pathKey(record.projectPath), record);
  }
  return { plotRoot, byId, byProjectPath };
}

function subfigureIdsFor(project: PlotProjectRecord, index: PlotProjectIndex, rootDir: string): string[] {
  const subfigures = Array.isArray(project.paper.subfigures) ? project.paper.subfigures : [];
  const ids: string[] = [];
  for (const subfigure of subfigures) {
    if (typeof subfigure === 'string') {
      ids.push(subfigure);
      continue;
    }
    if (!isRecord(subfigure)) {
      continue;
    }
    const explicitId = stringValue(subfigure.figure_id);
    if (explicitId) {
      ids.push(explicitId);
      continue;
    }
    const projectPath = stringValue(subfigure.project_path);
    if (!projectPath) {
      continue;
    }
    const child = index.byProjectPath.get(pathKey(resolveRepoPath(rootDir, projectPath)));
    ids.push(child?.id ?? path.basename(projectPath));
  }
  return uniqueStrings(ids);
}

function readAutoRenderDebounceMs(paperConfigPath: string): number {
  if (!fs.existsSync(paperConfigPath)) {
    return 900;
  }
  try {
    const config = readJsonConfig(paperConfigPath);
    const value = config.figure_pipeline?.auto_render_debounce_ms;
    return typeof value === 'number' && Number.isFinite(value) ? value : 900;
  } catch {
    return 900;
  }
}

export function listPaperFigures(rootDir: string, paperConfigPath: string): PaperFigureCatalogResponse {
  const index = loadPlotProjects(rootDir);
  const parentByChild = new Map<string, Set<string>>();
  const subfiguresByMontage = new Map<string, string[]>();

  for (const project of index.byId.values()) {
    if (project.kind !== 'montage') {
      continue;
    }
    const childIds = subfigureIdsFor(project, index, rootDir);
    subfiguresByMontage.set(project.id, childIds);
    for (const childId of childIds) {
      const parents = parentByChild.get(childId) ?? new Set<string>();
      parents.add(project.id);
      parentByChild.set(childId, parents);
    }
  }

  const figures = Array.from(index.byId.values()).map((project) => {
    const config = cloneConfig(project.figureConfig);
    config.kind = project.kind;
    config.title = stringValue(config.title) ?? project.title;
    config.description = stringValue(config.description) ?? project.description;
    config.output_name = stringValue(config.output_name) ?? project.outputName;
    if (project.kind === 'montage') {
      config.subfigures = subfiguresByMontage.get(project.id) ?? [];
    }
    const explicitParents = Array.isArray(config.parent_montages)
      ? config.parent_montages.filter((value): value is string => typeof value === 'string')
      : [];
    const discoveredParents = Array.from(parentByChild.get(project.id) ?? []);
    if (explicitParents.length > 0 || discoveredParents.length > 0) {
      config.parent_montages = uniqueStrings([...explicitParents, ...discoveredParents]);
    }

    const exists = fs.existsSync(project.dataPath);
    const updatedAt = exists ? fs.statSync(project.dataPath).mtime.toISOString() : null;
    const previewPath = path.relative(index.plotRoot, project.dataPath);
    const renderable = project.paper.renderable !== false && config.renderable !== false;
    return {
      id: project.id,
      kind: project.kind,
      title: stringValue(config.title) ?? project.title,
      description: stringValue(config.description) ?? project.description,
      editable: true,
      renderable,
      outputName: project.outputName,
      previewUrl: `/paper-plot-assets/${encodeStaticPath(previewPath)}`,
      exists,
      updatedAt,
      config,
      projectPath: relFromRoot(rootDir, project.projectPath),
      configPath: relFromRoot(rootDir, project.configPath),
    } satisfies PaperFigureCatalogItem;
  });

  figures.sort((left, right) => left.id.localeCompare(right.id, undefined, { numeric: true, sensitivity: 'base' }));
  return {
    autoRenderDebounceMs: readAutoRenderDebounceMs(paperConfigPath),
    figures,
  };
}

export function updatePaperFigureConfig(
  rootDir: string,
  paperConfigPath: string,
  figureId: string,
  nextFigureConfig: PaperFigureConfigEntry,
): PaperFigureCatalogItem {
  const index = loadPlotProjects(rootDir);
  const project = index.byId.get(figureId);
  if (!project) {
    throw new Error(`Figure config not found: ${figureId}`);
  }

  const payload = readJsonConfig(project.configPath);
  const paper = isRecord(payload.paper_figure) ? payload.paper_figure : {};
  payload.paper_figure = paper;
  paper.figure_config = nextFigureConfig;

  const title = stringValue(nextFigureConfig.title);
  const description = stringValue(nextFigureConfig.description);
  const outputName = stringValue(nextFigureConfig.output_name);
  if (title) {
    paper.title = title;
  }
  if (description !== null) {
    paper.description = description;
  }
  if (outputName) {
    paper.output_name = outputName;
  }
  if (nextFigureConfig.kind === 'single' || nextFigureConfig.kind === 'montage') {
    paper.kind = nextFigureConfig.kind;
  }

  writeJsonConfig(project.configPath, payload);

  const updated = listPaperFigures(rootDir, paperConfigPath).figures.find((entry) => entry.id === figureId);
  if (!updated) {
    throw new Error(`Updated figure config not found after save: ${figureId}`);
  }
  return updated;
}

function ensureFigureConfig(rootDir: string, figureId: string): void {
  const index = loadPlotProjects(rootDir);
  if (!index.byId.has(figureId)) {
    throw new Error(`Figure config not found: ${figureId}`);
  }
}

function appendLog(job: RenderJob, prefix: string, chunk: Buffer | string): void {
  const text = String(chunk).trim();
  if (!text) {
    return;
  }
  for (const line of text.split(/\r?\n/)) {
    job.logs.push(`${prefix}${line}`);
  }
  if (job.logs.length > 300) {
    job.logs.splice(0, job.logs.length - 300);
  }
}

export function startRenderJob(rootDir: string, _paperConfigPath: string, figureIds: string[]): RenderJob {
  if (figureIds.length === 0) {
    throw new Error('At least one figure id is required');
  }

  const index = loadPlotProjects(rootDir);
  const pythonExe = resolvePythonExecutable();
  const commands = figureIds.map((figureId) => {
    const project = index.byId.get(figureId);
    if (!project) {
      throw new Error(`Figure config not found: ${figureId}`);
    }
    return [pythonExe, 'cli.py', 'ep', relFromRoot(rootDir, project.projectPath)];
  });

  for (const figureId of figureIds) {
    ensureFigureConfig(rootDir, figureId);
  }

  const job: RenderJob = {
    id: randomUUID(),
    figureIds,
    status: 'queued',
    startedAt: null,
    finishedAt: null,
    command: commands.flatMap((command, index) => (index === 0 ? command : ['&&', ...command])),
    logs: [],
    error: null,
  };
  renderJobs.set(job.id, job);

  job.status = 'running';
  job.startedAt = new Date().toISOString();

  const runCommand = (index: number): void => {
    const command = commands[index];
    if (!command) {
      job.status = 'completed';
      job.finishedAt = new Date().toISOString();
      return;
    }
    appendLog(job, '$ ', command.join(' '));
    const child = spawn(command[0], command.slice(1), {
      cwd: rootDir,
      windowsHide: true,
      env: { ...process.env, PYTHONUTF8: '1' },
    });
    child.stdout.on('data', (chunk) => appendLog(job, '', chunk));
    child.stderr.on('data', (chunk) => appendLog(job, 'ERR ', chunk));
    child.on('error', (error) => {
      job.status = 'failed';
      job.finishedAt = new Date().toISOString();
      job.error = error.message;
      appendLog(job, 'ERR ', error.message);
    });
    child.on('close', (code) => {
      if (job.status === 'failed') {
        return;
      }
      if (code === 0) {
        runCommand(index + 1);
        return;
      }
      job.status = 'failed';
      job.finishedAt = new Date().toISOString();
      job.error = `Renderer exited with code ${code}`;
      appendLog(job, 'ERR ', job.error);
    });
  };

  runCommand(0);

  return job;
}

export function getRenderJob(jobId: string): RenderJob | null {
  return renderJobs.get(jobId) ?? null;
}
