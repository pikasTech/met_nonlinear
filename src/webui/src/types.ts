export interface Project {
  name: string;
  path: string;
  config: ProjectConfig;
  hasTrainingInfo: boolean;
  hasLinearResponse: boolean;
  hasModelInfo: boolean;
  hasComputeAnalysis: boolean;
  hasMetricsSummary?: boolean;
}

export interface ProjectConfig {
  use_model?: string;
  H_UNITS?: number;
  INNER_KAN_UNITS?: number;
  INNER_KAN_LAYERS?: number;
  learning_rate?: number;
  epoch_train?: number;
  [key: string]: unknown;
}

export interface ProjectsResponse {
  projects: Project[];
  total: number;
}

export interface TrainingInfo {
  total_epochs: number;
  min_loss: number;
  min_val_loss: number;
  evaluation_metrics?: {
    train_loss?: number;
    val_loss?: number;
    train_mae?: number;
    train_afmae?: number;
    val_mae?: number;
    val_afmae?: number;
  };
  learning_rate_max?: number;
  learning_rate_min?: number;
}

export interface TrainingLogEntry {
  timestamp?: number;
  epoch: number;
  loss?: number;
  val_loss?: number;
  mae?: number;
  val_mae?: number;
  power_log_loss?: number;
  val_power_log_loss?: number;
  lr?: number;
}

export interface TrainingLogResponse {
  projectPath: string;
  projectName: string;
  total: number;
  availableMetrics: string[];
  entries: TrainingLogEntry[];
}

export interface ModelInfo {
  model_type: string;
  total_params: number;
  trainable_params: number;
  non_trainable_params: number;
}

export interface ComputeAnalysis {
  model_type: string;
  total_params: number;
  trainable_params: number;
  estimated_cost?: {
    weighted_units: {
      total: number;
      additions: number;
      multiplications: number;
      maps: number;
    };
  };
}

export interface LinearResponseData {
  gains_origin?: number[][];
  gains_compensated?: number[][];
  frequencies?: number[];
}

export interface DriftMetrics {
  freqDrift: number | null;
  sensDrift: number | null;
  linearity: number | null;
}

export interface ProjectMetricsSummary {
  project_name?: string;
  generated_at: string;
  status: string;
  sources?: Record<string, boolean>;
  missing_sources?: string[];
  missing_sections?: string[];
  epochs: number | null;
  min_loss: number | null;
  min_val_loss: number | null;
  train_loss: number | null;
  val_loss: number | null;
  train_mae: number | null;
  train_afmae: number | null;
  val_mae: number | null;
  val_afmae: number | null;
  weights_source?: string | null;
  freq_drift_hz: number | null;
  sens_drift_percent: number | null;
  linearity_percent: number | null;
  compute_cost: number | null;
  compute_cost_status?: string | null;
  compute_has_unsupported_layers?: boolean;
  compute_unsupported_layer_count?: number;
  compute_unsupported_layers?: string[];
  compute_unsupported_layer_details?: Array<Record<string, unknown>>;
  compute_cost_warning?: string | null;
  total_params: number | null;
  lr: number | null;
  use_cosine_annealing: boolean | null;
  loss_function?: string | null;
  display_metrics?: Record<string, number | null | boolean | string>;
}

export interface PaperEditorOutlineItem {
  id: string;
  level: number;
  title: string;
  line: number;
  markdownLine?: number;
  htmlLine?: number;
}

export interface PaperEditorAsset {
  source: string;
  resolvedPath: string;
  url: string;
  caption: string;
}

export interface PaperEditorPerformance {
  parseMs: number;
  sourceBytes: number;
  markdownBytes: number;
  macroCount: number;
  importCount: number;
  imageCount: number;
}

export interface PaperEditorHtmlBlock {
  htmlBlockIndex: number;
  htmlStartLine: number;
  htmlEndLine: number;
  markdownStartLine: number;
  markdownEndLine: number;
  latexStartLine: number;
  latexEndLine: number;
  kind: string;
}

export interface PaperEditorLineMappings {
  latexToMarkdown: number[];
  markdownToLatex: number[];
  markdownToHtml: number[];
  htmlToMarkdown: number[];
  htmlToLatex: number[];
  latexToHtml: number[];
  htmlBlocks: PaperEditorHtmlBlock[];
}

export interface PaperEditorSourceView {
  text: string;
  columns: number;
  tabSize: number;
  totalViewLines: number;
  viewLineToLatex: number[];
  latexToViewLineStart: number[];
  latexToViewLineEnd: number[];
  viewLineEndsWithSourceBreak: boolean[];
}

export interface PaperEditorDocument {
  entry: string;
  source: string;
  sourceView: PaperEditorSourceView;
  markdown: string;
  html: string;
  outline: PaperEditorOutlineItem[];
  imports: string[];
  macros: Record<string, string>;
  assets: PaperEditorAsset[];
  diagnostics: string[];
  lineMappings: PaperEditorLineMappings;
  performance: PaperEditorPerformance;
  revision: string;
  updatedAt: string | null;
}

export interface PaperEditorDocumentState {
  entry: string;
  imports: string[];
  revision: string;
  updatedAt: string | null;
}
