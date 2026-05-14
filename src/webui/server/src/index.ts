import express, { Express } from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import {
  getRenderJob,
  listPaperFigures,
  startRenderJob,
  updatePaperFigureConfig,
} from './paperFigures.js';
import {
  loadPaperEditorDocument,
  loadPaperEditorDocumentState,
  PaperEditorSaveConflictError,
  previewPaperEditorDocument,
  resolvePaperEditorAsset,
  savePaperEditorDocument,
} from './paperEditor.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DEFAULT_ROOT_DIR = path.resolve(__dirname, '../../../..');

function getPaperEditorRequestMeta(req: express.Request) {
  return {
    clientId: req.get('X-Paper-Editor-Client-Id') ?? 'unknown',
    reason: req.get('X-Paper-Editor-Reason') ?? 'unspecified',
    knownRevision: req.get('X-Paper-Editor-Known-Revision') ?? null,
    remoteAddress: req.ip || req.socket.remoteAddress || 'unknown',
    userAgent: req.get('User-Agent') ?? 'unknown',
  };
}

function logPaperEditorEvent(event: string, payload: Record<string, unknown>) {
  console.log(JSON.stringify({
    ts: new Date().toISOString(),
    subsystem: 'paper-editor',
    event,
    ...payload,
  }));
}

function readJsonlFile(filePath: string): Array<Record<string, unknown>> {
  if (!fs.existsSync(filePath)) {
    return [];
  }

  return fs
    .readFileSync(filePath, 'utf-8')
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .flatMap((line) => {
      try {
        return [JSON.parse(line) as Record<string, unknown>];
      } catch {
        return [];
      }
    });
}
export function createApp(options?: { rootDir?: string }): Express {
  const rootDir = options?.rootDir ?? DEFAULT_ROOT_DIR;
  const distWebui = path.join(rootDir, 'src', 'webui', 'dist');
  const cacheWebuiDir = path.join(rootDir, 'cache', 'webui');
  const presetsDir = path.join(cacheWebuiDir, 'presets');
  const stateFile = path.join(cacheWebuiDir, 'state.json');
  const paperDir = path.join(rootDir, 'docs', 'paper');
  const paperConfigPath = path.join(paperDir, 'config.json');
  const paperFiguresDir = path.join(paperDir, 'figures');
  const paperPlotDir = path.join(rootDir, 'ex_projects', 'plot');

  if (!fs.existsSync(cacheWebuiDir)) {
    fs.mkdirSync(cacheWebuiDir, { recursive: true });
  }
  if (!fs.existsSync(presetsDir)) {
    fs.mkdirSync(presetsDir, { recursive: true });
  }

  const app: Express = express();
  app.use(cors());
  app.use(express.json({ limit: '2mb' }));
  app.use('/paper-figures-assets', express.static(paperFiguresDir));
  app.use('/paper-plot-assets', express.static(paperPlotDir));

  app.get('/api/health', (_req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  app.get('/api/paper-editor/document', (req, res) => {
    const startedAt = Date.now();
    const requestMeta = getPaperEditorRequestMeta(req);
    try {
      const entry = typeof req.query.entry === 'string' ? req.query.entry : 'main.tex';
      const rawViewColumns = typeof req.query.viewColumns === 'string' ? Number.parseInt(req.query.viewColumns, 10) : Number.NaN;
      const viewColumns = Number.isFinite(rawViewColumns) && rawViewColumns > 0 ? rawViewColumns : undefined;
      const document = loadPaperEditorDocument(rootDir, entry, viewColumns);
      logPaperEditorEvent('document', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry,
        viewColumns: viewColumns ?? null,
        revision: document.revision,
        imports: document.imports.length,
        status: 200,
        durationMs: Date.now() - startedAt,
      });
      res.json(document);
    } catch (error) {
      logPaperEditorEvent('document', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry: typeof req.query.entry === 'string' ? req.query.entry : 'main.tex',
        status: 400,
        durationMs: Date.now() - startedAt,
        error: error instanceof Error ? error.message : 'Failed to load paper document',
      });
      res.status(400).json({ error: error instanceof Error ? error.message : 'Failed to load paper document' });
    }
  });

  app.get('/api/paper-editor/state', (req, res) => {
    const startedAt = Date.now();
    const requestMeta = getPaperEditorRequestMeta(req);
    try {
      const entry = typeof req.query.entry === 'string' ? req.query.entry : 'main.tex';
      const state = loadPaperEditorDocumentState(rootDir, entry);
      logPaperEditorEvent('state', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry,
        revision: state.revision,
        imports: state.imports.length,
        status: 200,
        durationMs: Date.now() - startedAt,
      });
      res.json(state);
    } catch (error) {
      logPaperEditorEvent('state', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry: typeof req.query.entry === 'string' ? req.query.entry : 'main.tex',
        status: 400,
        durationMs: Date.now() - startedAt,
        error: error instanceof Error ? error.message : 'Failed to load paper document state',
      });
      res.status(400).json({ error: error instanceof Error ? error.message : 'Failed to load paper document state' });
    }
  });

  app.post('/api/paper-editor/preview', (req, res) => {
    const startedAt = Date.now();
    const requestMeta = getPaperEditorRequestMeta(req);
    try {
      const entry = typeof req.body?.entry === 'string' ? req.body.entry : 'main.tex';
      const source = typeof req.body?.source === 'string' ? req.body.source : '';
      const rawViewColumns = typeof req.body?.viewColumns === 'number' ? req.body.viewColumns : Number.NaN;
      const viewColumns = Number.isFinite(rawViewColumns) && rawViewColumns > 0 ? rawViewColumns : undefined;
      const document = previewPaperEditorDocument(rootDir, entry, source, viewColumns);
      logPaperEditorEvent('preview', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry,
        viewColumns: viewColumns ?? null,
        sourceBytes: Buffer.byteLength(source, 'utf-8'),
        revision: document.revision,
        status: 200,
        durationMs: Date.now() - startedAt,
      });
      res.json(document);
    } catch (error) {
      logPaperEditorEvent('preview', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry: typeof req.body?.entry === 'string' ? req.body.entry : 'main.tex',
        status: 400,
        durationMs: Date.now() - startedAt,
        error: error instanceof Error ? error.message : 'Failed to preview paper document',
      });
      res.status(400).json({ error: error instanceof Error ? error.message : 'Failed to preview paper document' });
    }
  });

  app.put('/api/paper-editor/document', (req, res) => {
    const startedAt = Date.now();
    const requestMeta = getPaperEditorRequestMeta(req);
    try {
      const entry = typeof req.body?.entry === 'string' ? req.body.entry : 'main.tex';
      const rawViewColumns = typeof req.body?.viewColumns === 'number' ? req.body.viewColumns : Number.NaN;
      const viewColumns = Number.isFinite(rawViewColumns) && rawViewColumns > 0 ? rawViewColumns : undefined;
      const source = typeof req.body?.source === 'string' ? req.body.source : '';
      const saveResult = savePaperEditorDocument(rootDir, {
        entry,
        source,
        sourceViewText: typeof req.body?.sourceViewText === 'string' ? req.body.sourceViewText : '',
        baseSource: typeof req.body?.baseSource === 'string' ? req.body.baseSource : '',
        baseSourceViewText: typeof req.body?.baseSourceViewText === 'string' ? req.body.baseSourceViewText : '',
        baseRevision: typeof req.body?.baseRevision === 'string' ? req.body.baseRevision : null,
        sourceViewColumns: viewColumns,
      });
      const document = saveResult.document;
      logPaperEditorEvent('save', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry,
        viewColumns: viewColumns ?? null,
        sourceBytes: Buffer.byteLength(source, 'utf-8'),
        revision: document.revision,
        baseRevision: saveResult.audit.baseRevision,
        currentRevisionBeforeSave: saveResult.audit.currentRevisionBeforeSave,
        patchAppliedToStaleRevision: saveResult.audit.patchAppliedToStaleRevision,
        previousSourceHash: saveResult.audit.previousSourceHash,
        nextSourceHash: saveResult.audit.nextSourceHash,
        previousBytes: saveResult.audit.previousBytes,
        nextBytes: saveResult.audit.nextBytes,
        changed: saveResult.audit.changed,
        diffSummary: saveResult.audit.diffSummary,
        requestedDiffSummary: saveResult.audit.requestedDiffSummary,
        viewDiffSummary: saveResult.audit.viewDiffSummary,
        status: 200,
        durationMs: Date.now() - startedAt,
      });
      res.json(document);
    } catch (error) {
      const statusCode = error instanceof PaperEditorSaveConflictError ? 409 : 400;
      logPaperEditorEvent('save', {
        ...requestMeta,
        method: req.method,
        path: req.path,
        entry: typeof req.body?.entry === 'string' ? req.body.entry : 'main.tex',
        status: statusCode,
        durationMs: Date.now() - startedAt,
        currentRevision: error instanceof PaperEditorSaveConflictError ? error.currentRevision : undefined,
        updatedAt: error instanceof PaperEditorSaveConflictError ? error.updatedAt : undefined,
        error: error instanceof Error ? error.message : 'Failed to save paper document',
      });
      res.status(statusCode).json({
        error: error instanceof Error ? error.message : 'Failed to save paper document',
        ...(error instanceof PaperEditorSaveConflictError
          ? {
              currentRevision: error.currentRevision,
              updatedAt: error.updatedAt,
            }
          : {}),
      });
    }
  });

  app.get('/api/paper-editor/asset', (req, res) => {
    try {
      const requestPath = typeof req.query.path === 'string' ? req.query.path : '';
      if (!requestPath) {
        res.status(400).json({ error: 'Missing asset path' });
        return;
      }
      res.sendFile(resolvePaperEditorAsset(rootDir, requestPath));
    } catch (error) {
      res.status(404).json({ error: error instanceof Error ? error.message : 'Asset not found' });
    }
  });

  app.get('/api/projects', (_req, res) => {
    const projectsDir = path.join(rootDir, 'projects');
  const projects: any[] = [];

  const scanDir = (dir: string, basePath: string = ''): void => {
    if (!fs.existsSync(dir)) return;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) {
        const configPath = path.join(dir, entry.name, 'config.json');
        if (fs.existsSync(configPath)) {
          try {
            const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
            const dataDir = path.join(dir, entry.name, 'data');
            const projectPath = basePath ? `${basePath}/${entry.name}` : entry.name;
            projects.push({
              name: entry.name,
              path: projectPath,
              config,
              hasTrainingInfo: fs.existsSync(path.join(dataDir, 'training_info.json')),
              hasLinearResponse: fs.existsSync(path.join(dataDir, 'linear_response.json')),
              hasModelInfo: fs.existsSync(path.join(dataDir, 'model_info.json')),
              hasComputeAnalysis: fs.existsSync(path.join(dataDir, 'compute_analysis.json')),
              hasMetricsSummary: fs.existsSync(path.join(dataDir, 'metrics.json')),
            });
          } catch (e) {
            // skip invalid config
          }
        } else {
          scanDir(path.join(dir, entry.name), basePath ? `${basePath}/${entry.name}` : entry.name);
        }
      }
    }
  };

    scanDir(projectsDir);
    res.json({ projects, total: projects.length });
  });

  app.get('/api/projects/:name/data/:file', (req, res) => {
  const { name, file } = req.params;
  const safeFile = path.basename(file);
  const filePath = path.join(rootDir, 'projects', name, 'data', safeFile);
  if (fs.existsSync(filePath)) {
    res.json(JSON.parse(fs.readFileSync(filePath, 'utf-8')));
  } else {
    res.status(404).json({ error: 'File not found' });
  }
  });

  app.get('/api/projects/*/data/:file', (req, res) => {
  const routeParams = req.params as Record<string, string | undefined>;
  const wildcardPath = typeof routeParams['0'] === 'string' ? routeParams['0'] : '';
  const pathParts = wildcardPath.split('/').filter(Boolean);
  const file = path.basename(req.params.file);
  const filePath = path.join(rootDir, 'projects', ...pathParts, 'data', file);
  if (fs.existsSync(filePath)) {
    res.json(JSON.parse(fs.readFileSync(filePath, 'utf-8')));
  } else {
    res.status(404).json({ error: 'File not found' });
  }
  });

  app.get('/api/projects/*/metrics', (req, res) => {
  const routeParams = req.params as Record<string, string | undefined>;
  const wildcardPath = typeof routeParams['0'] === 'string' ? routeParams['0'] : '';
  const pathParts = wildcardPath.split('/').filter(Boolean);
  const projectDir = path.join(rootDir, 'projects', ...pathParts);
  const metricsPath = path.join(projectDir, 'data', 'metrics.json');

  if (fs.existsSync(metricsPath)) {
    return res.json(JSON.parse(fs.readFileSync(metricsPath, 'utf-8')));
  }

    return res.status(404).json({ error: 'metrics.json not found' });
  });

  app.get('/api/projects/*/training-log', (req, res) => {
  const routeParams = req.params as Record<string, string | undefined>;
  const wildcardPath = typeof routeParams['0'] === 'string' ? routeParams['0'] : '';
  const pathParts = wildcardPath.split('/').filter(Boolean);
  const logPath = path.join(rootDir, 'projects', ...pathParts, 'data', 'training_log.jsonl');

  if (!fs.existsSync(logPath)) {
    return res.status(404).json({ error: 'training_log.jsonl not found' });
  }

  const entries = readJsonlFile(logPath);
  const availableMetrics = Array.from(
    new Set(entries.flatMap((entry) => Object.keys(entry).filter((key) => key !== 'timestamp' && key !== 'epoch')))
  );

    return res.json({
      projectPath: wildcardPath,
      projectName: pathParts[pathParts.length - 1] ?? wildcardPath,
      total: entries.length,
      availableMetrics,
      entries,
    });
  });

// Preset endpoints
  app.get('/api/presets', (_req, res) => {
  try {
    const files = fs.readdirSync(presetsDir).filter(f => f.endsWith('.json'));
    const presets = files.map(f => {
      const name = f.replace('.json', '');
      const content = JSON.parse(fs.readFileSync(path.join(presetsDir, f), 'utf-8'));
      return { name, ...content };
    });
    res.json({ presets, total: presets.length });
  } catch (e) {
    res.status(500).json({ error: 'Failed to list presets' });
  }
  });

  app.get('/api/presets/:name', (req, res) => {
  const safeName = path.basename(req.params.name);
  const filePath = path.join(presetsDir, safeName + '.json');
  if (fs.existsSync(filePath)) {
    res.json(JSON.parse(fs.readFileSync(filePath, 'utf-8')));
  } else {
    res.status(404).json({ error: 'Preset not found' });
  }
  });

  app.post('/api/presets/:name', (req, res) => {
  const safeName = path.basename(req.params.name);
  const filePath = path.join(presetsDir, safeName + '.json');
  try {
    fs.writeFileSync(filePath, JSON.stringify(req.body, null, 2));
    res.json({ success: true, name: safeName });
  } catch (e) {
    res.status(500).json({ error: 'Failed to save preset' });
  }
  });

  app.delete('/api/presets/:name', (req, res) => {
  const safeName = path.basename(req.params.name);
  const filePath = path.join(presetsDir, safeName + '.json');
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    res.json({ success: true });
  } else {
    res.status(404).json({ error: 'Preset not found' });
  }
  });

  app.patch('/api/presets/:name', (req, res) => {
  const oldName = path.basename(req.params.name);
  const newName = req.body.newName;
  if (!newName || typeof newName !== 'string' || newName.trim() === '') {
    res.status(400).json({ error: 'Invalid new name' });
    return;
  }
  const safeOldName = path.basename(oldName);
  const safeNewName = path.basename(newName.trim());
  const oldFilePath = path.join(presetsDir, safeOldName + '.json');
  const newFilePath = path.join(presetsDir, safeNewName + '.json');
  if (!fs.existsSync(oldFilePath)) {
    res.status(404).json({ error: 'Preset not found' });
    return;
  }
  if (fs.existsSync(newFilePath) && safeOldName !== safeNewName) {
    res.status(409).json({ error: 'Preset with new name already exists' });
    return;
  }
  try {
    const content = JSON.parse(fs.readFileSync(oldFilePath, 'utf-8'));
    content.name = safeNewName;
    fs.writeFileSync(newFilePath, JSON.stringify(content, null, 2));
    if (safeOldName !== safeNewName) {
      fs.unlinkSync(oldFilePath);
    }
    res.json({ success: true, name: safeNewName });
  } catch (e) {
    res.status(500).json({ error: 'Failed to rename preset' });
  }
  });

// Auto-save state endpoint
  app.get('/api/state', (_req, res) => {
    if (fs.existsSync(stateFile)) {
      res.json(JSON.parse(fs.readFileSync(stateFile, 'utf-8')));
    } else {
      res.json(null);
    }
  });

  app.post('/api/state', (req, res) => {
    try {
      console.log('[State] POST /api/state received, selectedProjects:', req.body.selectedProjects);
      fs.writeFileSync(stateFile, JSON.stringify(req.body, null, 2));
      res.json({ success: true });
    } catch (e) {
      console.error('[State] Failed to save state:', e);
      res.status(500).json({ error: 'Failed to save state' });
    }
  });

  app.get('/api/paper-figures/catalog', (_req, res) => {
    try {
      const catalog = listPaperFigures(rootDir, paperConfigPath);
      res.json(catalog);
    } catch (error) {
      res.status(500).json({ error: error instanceof Error ? error.message : 'Failed to load paper figure catalog' });
    }
  });

  app.put('/api/paper-figures/config/:id', (req, res) => {
    try {
      const updated = updatePaperFigureConfig(rootDir, paperConfigPath, req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update paper figure config';
      const status = /not found/i.test(message) ? 404 : 500;
      res.status(status).json({ error: message });
    }
  });

  app.post('/api/paper-figures/render', (req, res) => {
    const figureIds = Array.isArray(req.body?.figureIds)
      ? req.body.figureIds.filter((value: unknown): value is string => typeof value === 'string' && value.trim().length > 0)
      : [];
    try {
      const job = startRenderJob(rootDir, paperConfigPath, figureIds);
      res.status(202).json(job);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start render job';
      const status = /required|not found/i.test(message) ? 400 : 500;
      res.status(status).json({ error: message });
    }
  });

  app.get('/api/paper-figures/render/:jobId', (req, res) => {
    const job = getRenderJob(req.params.jobId);
    if (!job) {
      return res.status(404).json({ error: 'Render job not found' });
    }
    return res.json(job);
  });

  if (fs.existsSync(distWebui)) {
    app.use(express.static(distWebui));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distWebui, 'index.html'));
    });
  } else {
    app.get('/', (_req, res) => {
      res.json({
        message: 'MET Nonlinear API Server',
        note: 'WebUI not built. Run: cd src/webui && npm install && npm run build',
        endpoints: [
          'GET /api/health',
          'GET /api/projects',
          'GET /api/projects/:name/data/:file',
        ]
      });
    });
  }
  return app;
}

const PORT = 3000;
const app = createApp();
const server = process.env.MET_NONLINEAR_DISABLE_AUTO_LISTEN === '1'
  ? null
  : app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });

export { app, server };
