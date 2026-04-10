import { Project, ProjectsResponse, TrainingInfo, TrainingLogResponse, ModelInfo, ComputeAnalysis, ProjectMetricsSummary } from './types';

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
