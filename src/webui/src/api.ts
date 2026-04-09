import { Project, ProjectsResponse, TrainingInfo, ModelInfo, ComputeAnalysis, LinearityByFrequency, ProjectMetricsSummary } from './types';

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

export async function fetchModelInfo(projectName: string): Promise<ModelInfo> {
  return fetchProjectData<ModelInfo>(projectName, 'model_info.json');
}

export async function fetchComputeAnalysis(projectName: string): Promise<ComputeAnalysis> {
  return fetchProjectData<ComputeAnalysis>(projectName, 'compute_analysis.json');
}

export async function fetchLinearityByFrequency(projectName: string): Promise<LinearityByFrequency> {
  return fetchProjectData<LinearityByFrequency>(projectName, 'linearity_by_frequency.json');
}

export async function fetchProjectMetricsSummary(projectName: string): Promise<ProjectMetricsSummary> {
  return fetchProjectData<ProjectMetricsSummary>(projectName, 'metrics.json');
}
