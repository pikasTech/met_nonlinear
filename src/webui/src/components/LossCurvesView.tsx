import { useEffect, useMemo, useRef, useState } from 'react';
import Plot from 'react-plotly.js';
import { Config, Data, Dash, Layout } from 'plotly.js';
import { fetchTrainingLog, LossCurvesState, defaultLossCurvesState } from '../clientApi';
import { Project, TrainingLogEntry } from '../types';

interface ProjectData {
  name: string;
  project: Project;
}

interface Props {
  projects: ProjectData[];
  lossCurvesState?: LossCurvesState;
  onLossCurvesStateChange?: (state: LossCurvesState) => void;
}

type LossMetricKey = 'loss' | 'val_loss';

interface TraceDescriptor {
  key: string;
  label: string;
  metricKey: LossMetricKey;
  color: string;
  x: number[];
  y: number[];
  dash?: Dash;
}

const PROJECT_COLORS = [
  '#2563eb',
  '#dc2626',
  '#059669',
  '#d97706',
  '#7c3aed',
  '#0891b2',
  '#e11d48',
  '#4f46e5',
  '#65a30d',
  '#c2410c',
  '#0f766e',
  '#9333ea',
];

function toFiniteNumber(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function formatAxisValue(value: number): string {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(6).replace(/0+$/, '').replace(/\.$/, '');
}

function parseAxisInput(value: string): number | null {
  if (!value.trim()) {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function isRelayoutNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function toPlotRange(range: [number, number] | null, isLogScale: boolean): [number, number] | undefined {
  if (range == null) {
    return undefined;
  }
  if (!isLogScale) {
    return range;
  }
  if (range[0] <= 0 || range[1] <= 0) {
    return undefined;
  }
  return [Math.log10(range[0]), Math.log10(range[1])];
}

function fromPlotRange(range: [number, number], isLogScale: boolean): [number, number] {
  if (!isLogScale) {
    return range;
  }
  return [10 ** range[0], 10 ** range[1]];
}

interface LossPlotPanelProps {
  title: string;
  axisTitle: string;
  hoverLabel: string;
  emptyMessage: string;
  traces: TraceDescriptor[];
  normalize: boolean;
  xLogScale: boolean;
  yLogScale: boolean;
  onNormalizeToggle: () => void;
  onXLogScaleToggle: () => void;
  onYLogScaleToggle: () => void;
}

function LossPlotPanel({
  title, axisTitle, hoverLabel, emptyMessage, traces, normalize,
  xLogScale, yLogScale, onNormalizeToggle, onXLogScaleToggle, onYLogScaleToggle
}: LossPlotPanelProps) {
  const [hiddenTraces, setHiddenTraces] = useState<Set<string>>(new Set());
  const [xRange, setXRange] = useState<[number, number] | null>(null);
  const [yRange, setYRange] = useState<[number, number] | null>(null);
  const [xMinInput, setXMinInput] = useState('');
  const [xMaxInput, setXMaxInput] = useState('');
  const [yMinInput, setYMinInput] = useState('');
  const [yMaxInput, setYMaxInput] = useState('');

  // Track the last user-set range to detect Plotly's internal cleanup events
  const lastXRangeRef = useRef<[number, number] | null>(null);
  const lastYRangeRef = useRef<[number, number] | null>(null);

  useEffect(() => {
    const availableKeys = new Set(traces.map((trace) => trace.key));
    setHiddenTraces((prev) => new Set(Array.from(prev).filter((key) => availableKeys.has(key))));
  }, [traces]);

  const plotData = useMemo<Data[]>(() => {
    return traces.map((trace) => ({
      type: 'scatter',
      mode: 'lines',
      name: trace.label,
      x: trace.x,
      y: trace.y,
      line: {
        color: trace.color,
        width: 2.4,
        dash: trace.dash,
      },
      visible: hiddenTraces.has(trace.key) ? 'legendonly' : true,
      hovertemplate: `Epoch %{x}<br>${hoverLabel} %{y:.6f}<extra>%{fullData.name}</extra>`,
    }));
  }, [hiddenTraces, hoverLabel, traces]);

  const layout = useMemo<Partial<Layout>>(() => ({
    autosize: true,
    dragmode: 'zoom',
    hovermode: 'x unified',
    margin: { l: 72, r: 28, t: 58, b: 210 },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#ffffff',
    title: {
      text: title,
      x: 0,
      xanchor: 'left',
      font: { size: 16, color: '#1f2937' },
    },
    legend: {
      orientation: 'h',
      yanchor: 'top',
      y: -0.48,
      xanchor: 'left',
      x: 0,
      traceorder: 'normal',
    },
    xaxis: {
      title: { text: 'Epoch' },
      type: xLogScale ? 'log' : 'linear',
      showgrid: true,
      gridcolor: '#e8edf3',
      zeroline: false,
      range: toPlotRange(xRange, xLogScale),
      autorange: xRange == null,
      fixedrange: false,
    },
    yaxis: {
      title: { text: normalize ? 'Normalized Loss' : axisTitle },
      type: yLogScale ? 'log' : 'linear',
      showgrid: true,
      gridcolor: '#e8edf3',
      zeroline: false,
      range: yRange != null ? toPlotRange(yRange, yLogScale) : undefined,
      autorange: yRange == null,
      fixedrange: false,
    },
  }), [axisTitle, normalize, title, xLogScale, xRange, yLogScale, yRange]);

  const plotConfig = useMemo<Partial<Config>>(() => ({
    responsive: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    scrollZoom: true,
    doubleClick: 'reset',
  }), []);

  const visibleTraceCount = traces.length - hiddenTraces.size;

  const handleToggleTrace = (traceKey: string) => {
    const next = new Set(hiddenTraces);
    if (next.has(traceKey)) {
      next.delete(traceKey);
    } else {
      next.add(traceKey);
    }
    setHiddenTraces(next);
  };

  const handleToggleAll = (hidden: boolean) => {
    if (hidden) {
      setHiddenTraces(new Set(traces.map((trace) => trace.key)));
    } else {
      setHiddenTraces(new Set());
    }
  };

  const handleApplyAxisRanges = () => {
    const nextXMin = parseAxisInput(xMinInput);
    const nextXMax = parseAxisInput(xMaxInput);
    const nextYMin = parseAxisInput(yMinInput);
    const nextYMax = parseAxisInput(yMaxInput);

    if (nextXMin != null && nextXMax != null && nextXMin < nextXMax && (!xLogScale || (nextXMin > 0 && nextXMax > 0))) {
      const nextRange: [number, number] = [nextXMin, nextXMax];
      setXRange(nextRange);
      lastXRangeRef.current = nextRange;
    }

    if (nextYMin != null && nextYMax != null && nextYMin < nextYMax && (!yLogScale || (nextYMin > 0 && nextYMax > 0))) {
      const nextRange: [number, number] = [nextYMin, nextYMax];
      setYRange(nextRange);
      lastYRangeRef.current = nextRange;
    }
  };

  const handleResetRanges = () => {
    lastXRangeRef.current = null;
    lastYRangeRef.current = null;
    setXRange(null);
    setYRange(null);
    setXMinInput('');
    setXMaxInput('');
    setYMinInput('');
    setYMaxInput('');
  };

  const handleRelayout = (event: Readonly<Record<string, unknown>>) => {
    if (isRelayoutNumber(event['xaxis.range[0]']) && isRelayoutNumber(event['xaxis.range[1]'])) {
      const nextRange = fromPlotRange([event['xaxis.range[0]'], event['xaxis.range[1]']], xLogScale);
      setXRange(nextRange);
      lastXRangeRef.current = nextRange;
      setXMinInput(formatAxisValue(nextRange[0]));
      setXMaxInput(formatAxisValue(nextRange[1]));
    } else if (event['xaxis.autorange'] === true) {
      // If we had a user-set range before, this autorange event is likely
      // Plotly's internal cleanup and should be ignored to preserve the user's zoom
      if (lastXRangeRef.current === null) {
        setXRange(null);
        setXMinInput('');
        setXMaxInput('');
      }
    }

    if (isRelayoutNumber(event['yaxis.range[0]']) && isRelayoutNumber(event['yaxis.range[1]'])) {
      const nextRange = fromPlotRange([event['yaxis.range[0]'], event['yaxis.range[1]']], yLogScale);
      setYRange(nextRange);
      lastYRangeRef.current = nextRange;
      setYMinInput(formatAxisValue(nextRange[0]));
      setYMaxInput(formatAxisValue(nextRange[1]));
    } else if (event['yaxis.autorange'] === true) {
      // If we had a user-set range before, this autorange event is likely
      // Plotly's internal cleanup and should be ignored to preserve the user's zoom
      if (lastYRangeRef.current === null) {
        setYRange(null);
        setYMinInput('');
        setYMaxInput('');
      }
    }
  };

  if (traces.length === 0) {
    return <div className="loss-panel-empty">{emptyMessage}</div>;
  }

  return (
    <section className="loss-panel-card">
      <div className="loss-panel-toolbar">
        <div>
          <h4>{title}</h4>
          <p>{visibleTraceCount} / {traces.length} curves visible</p>
        </div>
        <div className="loss-toolbar-actions">
          <button
            type="button"
            className={`loss-btn loss-btn-secondary ${xLogScale ? 'loss-btn-active' : ''}`}
            onClick={onXLogScaleToggle}
          >
            {xLogScale ? 'X: Log' : 'X: Linear'}
          </button>
          <button
            type="button"
            className={`loss-btn loss-btn-secondary ${yLogScale ? 'loss-btn-active' : ''}`}
            onClick={onYLogScaleToggle}
          >
            {yLogScale ? 'Y: Log' : 'Y: Linear'}
          </button>
          <button
            type="button"
            className={`loss-btn ${normalize ? 'loss-btn-active' : 'loss-btn-secondary'}`}
            onClick={onNormalizeToggle}
          >
            {normalize ? 'Normalized' : 'Normalize'}
          </button>
          <button type="button" className="loss-btn" onClick={() => handleToggleAll(false)}>Show All</button>
          <button type="button" className="loss-btn" onClick={() => handleToggleAll(true)}>Hide All</button>
          <button type="button" className="loss-btn loss-btn-secondary" onClick={handleResetRanges}>Reset Axes</button>
        </div>
      </div>

      <div className="loss-panel-layout">
        <aside className="loss-sidepanel">
          <section className="loss-panel-section">
            <div className="loss-panel-title">Visible Curves</div>
            <div className="loss-panel-subtitle">该区域只控制当前这张图</div>
            <div className="loss-trace-list">
              {traces.map((trace) => {
                const checked = !hiddenTraces.has(trace.key);
                const isVal = trace.metricKey === 'val_loss';
                return (
                  <label key={trace.key} className="loss-trace-item">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => handleToggleTrace(trace.key)}
                    />
                    <span className="loss-trace-swatch" style={{ backgroundColor: trace.color, borderBottom: isVal ? `2px dashed ${trace.color}` : `2px solid ${trace.color}` }} />
                    <span>{trace.label} {isVal ? '(val)' : ''}</span>
                  </label>
                );
              })}
            </div>
          </section>

          <section className="loss-panel-section">
            <div className="loss-panel-title">Axis Range</div>
            <div className="axis-grid">
              <label>
                <span>X Min</span>
                <input value={xMinInput} onChange={(e) => setXMinInput(e.target.value)} placeholder="auto" />
              </label>
              <label>
                <span>X Max</span>
                <input value={xMaxInput} onChange={(e) => setXMaxInput(e.target.value)} placeholder="auto" />
              </label>
              <label>
                <span>Y Min</span>
                <input value={yMinInput} onChange={(e) => setYMinInput(e.target.value)} placeholder="auto" />
              </label>
              <label>
                <span>Y Max</span>
                <input value={yMaxInput} onChange={(e) => setYMaxInput(e.target.value)} placeholder="auto" />
              </label>
            </div>
            <button type="button" className="loss-btn loss-btn-full" onClick={handleApplyAxisRanges}>
              Apply Range
            </button>
          </section>
        </aside>

        <div className="loss-plot-wrap">
          <Plot
            data={plotData}
            layout={layout}
            config={plotConfig}
            onRelayout={handleRelayout}
            useResizeHandler
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      </div>
    </section>
  );
}

export default function LossCurvesView({ projects, lossCurvesState, onLossCurvesStateChange }: Props) {
  const [trainingLogs, setTrainingLogs] = useState<Record<string, TrainingLogEntry[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lcState = { ...defaultLossCurvesState, ...lossCurvesState };

  const updateLcState = (updates: Partial<LossCurvesState>) => {
    if (onLossCurvesStateChange) {
      onLossCurvesStateChange({ ...lcState, ...updates });
    }
  };

  useEffect(() => {
    let cancelled = false;

    const loadLogs = async () => {
      setLoading(true);
      setError(null);

      const entries = await Promise.all(
        projects.map(async (project) => {
          try {
            const response = await fetchTrainingLog(project.project.path);
            return [project.project.path, response.entries] as const;
          } catch {
            return [project.project.path, []] as const;
          }
        })
      );

      if (cancelled) {
        return;
      }

      const nextLogs = Object.fromEntries(entries);
      setTrainingLogs(nextLogs);
      if (entries.every(([, logEntries]) => logEntries.length === 0)) {
        setError('No training log data found for the selected projects.');
      }
      setLoading(false);
    };

    if (projects.length === 0) {
      setTrainingLogs({});
      setError(null);
      setLoading(false);
      return () => {
        cancelled = true;
      };
    }

    loadLogs().catch((loadError) => {
      if (!cancelled) {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load training logs.');
        setLoading(false);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [projects]);

  const projectColorMap = useMemo(() => {
    return Object.fromEntries(
      projects.map((project, index) => [project.project.path, PROJECT_COLORS[index % PROJECT_COLORS.length]])
    );
  }, [projects]);

  const traceDescriptors = useMemo<TraceDescriptor[]>(() => {
    return projects.flatMap((project) => {
      const logEntries = trainingLogs[project.project.path] ?? [];
      const projectColor = projectColorMap[project.project.path] ?? PROJECT_COLORS[0];

      return (['loss', 'val_loss'] as LossMetricKey[]).flatMap((metricKey) => {
        const points = logEntries
          .map((entry) => {
            const epoch = toFiniteNumber(entry.epoch);
            const value = toFiniteNumber(entry[metricKey]);
            if (epoch == null || value == null) {
              return null;
            }
            return { epoch, value };
          })
          .filter((point): point is { epoch: number; value: number } => point !== null);

        if (points.length === 0) {
          return [];
        }

        return [{
          key: `${project.project.path}::${metricKey}`,
          label: project.name,
          metricKey,
          color: projectColor,
          x: points.map((point) => point.epoch),
          y: points.map((point) => point.value),
          dash: metricKey === 'val_loss' ? 'dash' : undefined,
        }];
      });
    });
  }, [projectColorMap, projects, trainingLogs]);

  const projectNormalizationFactors = useMemo(() => {
    const factors: Record<string, number> = {};
    for (const project of projects) {
      const logEntries = trainingLogs[project.project.path] ?? [];
      let maxVal = 0;
      for (const metricKey of ['loss', 'val_loss'] as LossMetricKey[]) {
        for (const entry of logEntries) {
          const value = entry[metricKey];
          if (typeof value === 'number' && Number.isFinite(value) && value > maxVal) {
            maxVal = value;
          }
        }
      }
      factors[project.project.path] = maxVal > 0 ? maxVal : 1;
    }
    return factors;
  }, [projects, trainingLogs]);

  const normalizedTraces = useMemo(() => {
    if (!lcState.normalize) {
      return traceDescriptors;
    }
    return traceDescriptors.map((trace) => {
      const projectPath = trace.key.split('::')[0];
      const factor = projectNormalizationFactors[projectPath] ?? 1;
      return {
        ...trace,
        y: trace.y.map((v) => factor > 0 ? v / factor : v),
      };
    });
  }, [lcState.normalize, traceDescriptors, projectNormalizationFactors]);

  // Keep ref to last valid traces to prevent flash when projects/traces change
  const lastNormalizedTracesRef = useRef<TraceDescriptor[]>(normalizedTraces);

  // Update refs only when we have actual data
  if (normalizedTraces.length > 0) {
    lastNormalizedTracesRef.current = normalizedTraces;
  }

  // Use last valid traces when current is empty to prevent Plotly reset
  const displayTraces = normalizedTraces.length > 0 ? normalizedTraces : lastNormalizedTracesRef.current;

  if (loading) {
    return <div className="loss-view-status">Loading training logs...</div>;
  }

  if (error && traceDescriptors.length === 0) {
    return <div className="loss-view-status loss-view-error">{error}</div>;
  }

  if (traceDescriptors.length === 0) {
    return <div className="loss-view-status">No loss curves available for the selected projects.</div>;
  }

  return (
    <div className="loss-view">
      <div className="loss-header">
        <h3>Training Loss Curves</h3>
        <p>Loss 和 Val Loss 合并显示，同项目同色，Val Loss 为虚线。归一化后每个 project 的 loss 和 val_loss 按该项目的 max(loss, val_loss) 归一化到 1。</p>
      </div>

      <div className="loss-panels-stack">
        <LossPlotPanel
          title="Training & Validation Loss"
          axisTitle="Loss"
          hoverLabel="Loss"
          emptyMessage="No loss curves available for the selected projects."
          traces={displayTraces}
          normalize={lcState.normalize}
          xLogScale={lcState.xLogScale}
          yLogScale={lcState.yLogScale}
          onNormalizeToggle={() => updateLcState({ normalize: !lcState.normalize })}
          onXLogScaleToggle={() => updateLcState({ xLogScale: !lcState.xLogScale })}
          onYLogScaleToggle={() => updateLcState({ yLogScale: !lcState.yLogScale })}
        />
      </div>

      <style>{`
        .loss-view { display: flex; flex-direction: column; gap: 1rem; min-height: 680px; }
        .loss-header h3 { margin: 0; color: #1f2937; font-size: 1.1rem; }
        .loss-header p { margin: 0.35rem 0 0; color: #5b6472; font-size: 0.92rem; }
        .loss-panels-stack { display: grid; grid-template-rows: auto auto; gap: 1rem; }
        .loss-panel-card { border: 1px solid #d9e2ec; border-radius: 14px; background: #ffffff; padding: 1rem; display: flex; flex-direction: column; gap: 1rem; }
        .loss-panel-toolbar { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; }
        .loss-panel-toolbar h4 { margin: 0; color: #1f2937; font-size: 1rem; }
        .loss-panel-toolbar p { margin: 0.35rem 0 0; color: #5b6472; font-size: 0.88rem; }
        .loss-toolbar-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
        .loss-panel-layout { display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 1rem; min-height: 620px; }
        .loss-sidepanel { display: flex; flex-direction: column; gap: 1rem; }
        .loss-panel-section { border: 1px solid #d9e2ec; border-radius: 10px; padding: 1rem; background: #f8fafc; }
        .loss-panel-title { font-weight: 700; color: #243b53; }
        .loss-panel-subtitle { margin-top: 0.3rem; color: #5b6472; font-size: 0.85rem; }
        .loss-trace-list { display: flex; flex-direction: column; gap: 0.65rem; margin-top: 0.9rem; max-height: 320px; overflow: auto; }
        .loss-trace-item { display: grid; grid-template-columns: 18px 12px minmax(0, 1fr); gap: 0.6rem; align-items: center; font-size: 0.9rem; color: #243b53; }
        .loss-trace-swatch { width: 12px; height: 12px; border-radius: 999px; display: inline-block; }
        .axis-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; margin: 0.9rem 0; }
        .axis-grid label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; color: #334e68; }
        .axis-grid input { border: 1px solid #bcccdc; border-radius: 8px; padding: 0.55rem 0.7rem; font-size: 0.9rem; background: white; }
        .loss-btn { border: 1px solid #243b53; background: #243b53; color: white; border-radius: 8px; padding: 0.6rem 0.9rem; cursor: pointer; font-size: 0.9rem; }
        .loss-btn:hover { background: #102a43; }
        .loss-btn-secondary { background: white; color: #243b53; }
        .loss-btn-secondary:hover { background: #f0f4f8; }
        .loss-btn-active { background: #243b53; color: white; }
        .loss-btn-active:hover { background: #102a43; }
        .loss-btn-full { width: 100%; }
        .loss-plot-wrap { border: 1px solid #d9e2ec; border-radius: 12px; background: white; min-height: 660px; padding: 0.75rem; }
        .loss-panel-empty, .loss-view-status { min-height: 280px; display: flex; align-items: center; justify-content: center; color: #52606d; }
        .loss-view-error { color: #c62828; }
        @media (max-width: 1200px) {
          .loss-panel-layout { grid-template-columns: 1fr; }
          .loss-plot-wrap { min-height: 580px; }
        }
        @media (max-width: 720px) {
          .loss-panel-toolbar { flex-direction: column; }
          .axis-grid { grid-template-columns: 1fr; }
          .loss-view { min-height: 0; }
          .loss-plot-wrap { min-height: 500px; }
        }
      `}</style>
    </div>
  );
}