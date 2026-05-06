import {
  Project,
  ProjectsResponse,
  TrainingInfo,
  TrainingLogResponse,
  ModelInfo,
  ComputeAnalysis,
  ProjectMetricsSummary,
  PaperEditorDocument,
} from './types';

const API_BASE = '/api';

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`);
  const data: ProjectsResponse = await res.json();
  return data.projects;
}

export async function fetchProjectData<T>(projectPath: string, dataFile: string): Promise<T> {
  // Split path and encode each segment individually to preserve slashes
  const pathSegments = projectPath.split('/');
  const encodedPath = pathSegments.map(seg => encodeURIComponent(seg)).join('/');
  const res = await fetch(`${API_BASE}/projects/${encodedPath}/data/${dataFile}`);
  if (!res.ok) throw new Error(`Failed to fetch ${dataFile}`);
  return res.json();
}

export async function fetchTrainingInfo(projectName: string): Promise<TrainingInfo> {
  return fetchProjectData<TrainingInfo>(projectName, 'training_info.json');
}

export async function fetchTrainingLog(projectName: string): Promise<TrainingLogResponse> {
  const pathSegments = projectName.split('/');
  const encodedPath = pathSegments.map(seg => encodeURIComponent(seg)).join('/');
  const res = await fetch(`${API_BASE}/projects/${encodedPath}/training-log`);
  if (!res.ok) throw new Error('Failed to fetch training log');
  return res.json();
}

export async function fetchModelInfo(projectName: string): Promise<ModelInfo> {
  return fetchProjectData<ModelInfo>(projectName, 'model_info.json');
}

export async function fetchComputeAnalysis(projectName: string): Promise<ComputeAnalysis> {
  return fetchProjectData<ComputeAnalysis>(projectName, 'compute_analysis.json');
}

export async function fetchProjectMetricsSummary(projectName: string): Promise<ProjectMetricsSummary> {
  return fetchProjectData<ProjectMetricsSummary>(projectName, 'metrics.json');
}

// Preset types
export interface LossCurvesState {
  normalize: boolean;
  xLogScale: boolean;
  yLogScale: boolean;
}

export const defaultLossCurvesState: LossCurvesState = {
  normalize: false,
  xLogScale: false,
  yLogScale: false,
};

export interface PresetState {
  selectedProjects: string[];
  globalFilter: string;
  columnFilters: Array<{ id: string; value: any }>;
  sorting: Array<{ id: string; desc: boolean }>;
  columnVisibility: Record<string, boolean>;
  expandedFolders: string[];
  showFilters: boolean;
  showColumnPanel: boolean;
  sidebarCollapsed?: boolean;
  lossCurves?: LossCurvesState;
}

export interface PresetInfo {
  name: string;
  state: PresetState;
  createdAt: string;
  description?: string;
}

export interface PresetsResponse {
  presets: PresetInfo[];
  total: number;
}

// Preset API
export async function fetchPresets(): Promise<PresetsResponse> {
  const res = await fetch(`${API_BASE}/presets`);
  if (!res.ok) throw new Error('Failed to fetch presets');
  return res.json();
}

export async function fetchPreset(name: string): Promise<PresetInfo> {
  const res = await fetch(`${API_BASE}/presets/${encodeURIComponent(name)}`);
  if (!res.ok) throw new Error(`Failed to fetch preset: ${name}`);
  return res.json();
}

export async function savePreset(name: string, state: PresetState, description?: string): Promise<void> {
  const res = await fetch(`${API_BASE}/presets/${encodeURIComponent(name)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state, createdAt: new Date().toISOString(), description }),
  });
  if (!res.ok) throw new Error(`Failed to save preset: ${name}`);
}

export async function deletePreset(name: string): Promise<void> {
  const res = await fetch(`${API_BASE}/presets/${encodeURIComponent(name)}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete preset: ${name}`);
}

export async function renamePreset(oldName: string, newName: string): Promise<void> {
  const res = await fetch(`${API_BASE}/presets/${encodeURIComponent(oldName)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ newName }),
  });
  if (!res.ok) throw new Error(`Failed to rename preset: ${oldName}`);
}

// State persistence API
export async function fetchState(): Promise<PresetState | null> {
  const res = await fetch(`${API_BASE}/state`);
  if (!res.ok) throw new Error('Failed to fetch state');
  return res.json();
}

export async function saveState(state: PresetState): Promise<void> {
  const res = await fetch(`${API_BASE}/state`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state),
  });
  if (!res.ok) throw new Error('Failed to save state');
}

export type PaperFigureKind = 'single' | 'montage';

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

export type PaperFigureRenderStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface PaperFigureRenderJob {
  id: string;
  figureIds: string[];
  status: PaperFigureRenderStatus;
  startedAt: string | null;
  finishedAt: string | null;
  command: string[];
  logs: string[];
  error: string | null;
}

export async function fetchPaperFigureCatalog(): Promise<PaperFigureCatalogResponse> {
  const res = await fetch(`${API_BASE}/paper-figures/catalog`);
  if (!res.ok) throw new Error('Failed to fetch paper figure catalog');
  return res.json();
}

export async function savePaperFigureConfig(
  figureId: string,
  config: PaperFigureConfigEntry,
): Promise<PaperFigureCatalogItem> {
  const res = await fetch(`${API_BASE}/paper-figures/config/${encodeURIComponent(figureId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) throw new Error(`Failed to save figure config: ${figureId}`);
  return res.json();
}

export async function startPaperFigureRender(figureIds: string[]): Promise<PaperFigureRenderJob> {
  const res = await fetch(`${API_BASE}/paper-figures/render`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ figureIds }),
  });
  if (!res.ok) throw new Error('Failed to start figure render');
  return res.json();
}

export async function fetchPaperFigureRenderJob(jobId: string): Promise<PaperFigureRenderJob> {
  const res = await fetch(`${API_BASE}/paper-figures/render/${encodeURIComponent(jobId)}`);
  if (!res.ok) throw new Error(`Failed to fetch render job: ${jobId}`);
  return res.json();
}

export async function fetchPaperEditorDocument(entry = 'main.tex', viewColumns?: number): Promise<PaperEditorDocument> {
  const params = new URLSearchParams({ entry });
  if (typeof viewColumns === 'number' && Number.isFinite(viewColumns) && viewColumns > 0) {
    params.set('viewColumns', String(Math.round(viewColumns)));
  }
  const res = await fetch(`${API_BASE}/paper-editor/document?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to load paper editor document');
  return res.json();
}

export async function previewPaperEditorDocument(entry: string, source: string, viewColumns?: number): Promise<PaperEditorDocument> {
  const res = await fetch(`${API_BASE}/paper-editor/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ entry, source, viewColumns }),
  });
  if (!res.ok) throw new Error('Failed to preview paper editor document');
  return res.json();
}

export async function savePaperEditorDocument(entry: string, source: string, viewColumns?: number): Promise<PaperEditorDocument> {
  const res = await fetch(`${API_BASE}/paper-editor/document`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ entry, source, viewColumns }),
  });
  if (!res.ok) throw new Error('Failed to save paper editor document');
  return res.json();
}
