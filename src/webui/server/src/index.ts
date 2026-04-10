import express, { Express } from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '../../../..');
const DIST_WEBUI = path.join(ROOT_DIR, 'src', 'webui', 'dist');
const CACHE_WEBUI_DIR = path.join(ROOT_DIR, 'cache', 'webui');
const PRESETS_DIR = path.join(CACHE_WEBUI_DIR, 'presets');
const STATE_FILE = path.join(CACHE_WEBUI_DIR, 'state.json');

// Ensure directories exist
if (!fs.existsSync(CACHE_WEBUI_DIR)) {
  fs.mkdirSync(CACHE_WEBUI_DIR, { recursive: true });
}
if (!fs.existsSync(PRESETS_DIR)) {
  fs.mkdirSync(PRESETS_DIR, { recursive: true });
}

const app: Express = express();
app.use(cors());
app.use(express.json());

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/api/projects', (_req, res) => {
  const projectsDir = path.join(ROOT_DIR, 'projects');
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
  const filePath = path.join(ROOT_DIR, 'projects', name, 'data', safeFile);
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
  const filePath = path.join(ROOT_DIR, 'projects', ...pathParts, 'data', file);
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
  const projectDir = path.join(ROOT_DIR, 'projects', ...pathParts);
  const metricsPath = path.join(projectDir, 'data', 'metrics.json');

  if (fs.existsSync(metricsPath)) {
    return res.json(JSON.parse(fs.readFileSync(metricsPath, 'utf-8')));
  }

  return res.status(404).json({ error: 'metrics.json not found' });
});

// Preset endpoints
app.get('/api/presets', (_req, res) => {
  try {
    const files = fs.readdirSync(PRESETS_DIR).filter(f => f.endsWith('.json'));
    const presets = files.map(f => {
      const name = f.replace('.json', '');
      const content = JSON.parse(fs.readFileSync(path.join(PRESETS_DIR, f), 'utf-8'));
      return { name, ...content };
    });
    res.json({ presets, total: presets.length });
  } catch (e) {
    res.status(500).json({ error: 'Failed to list presets' });
  }
});

app.get('/api/presets/:name', (req, res) => {
  const safeName = path.basename(req.params.name);
  const filePath = path.join(PRESETS_DIR, safeName + '.json');
  if (fs.existsSync(filePath)) {
    res.json(JSON.parse(fs.readFileSync(filePath, 'utf-8')));
  } else {
    res.status(404).json({ error: 'Preset not found' });
  }
});

app.post('/api/presets/:name', (req, res) => {
  const safeName = path.basename(req.params.name);
  const filePath = path.join(PRESETS_DIR, safeName + '.json');
  try {
    fs.writeFileSync(filePath, JSON.stringify(req.body, null, 2));
    res.json({ success: true, name: safeName });
  } catch (e) {
    res.status(500).json({ error: 'Failed to save preset' });
  }
});

app.delete('/api/presets/:name', (req, res) => {
  const safeName = path.basename(req.params.name);
  const filePath = path.join(PRESETS_DIR, safeName + '.json');
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    res.json({ success: true });
  } else {
    res.status(404).json({ error: 'Preset not found' });
  }
});

// Auto-save state endpoint
app.get('/api/state', (_req, res) => {
  if (fs.existsSync(STATE_FILE)) {
    res.json(JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8')));
  } else {
    res.json(null);
  }
});

app.post('/api/state', (req, res) => {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(req.body, null, 2));
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: 'Failed to save state' });
  }
});

if (fs.existsSync(DIST_WEBUI)) {
  app.use(express.static(DIST_WEBUI));
  app.get('*', (_req, res) => {
    res.sendFile(path.join(DIST_WEBUI, 'index.html'));
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

const PORT = 3000;
const server = app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

export { app, server };
