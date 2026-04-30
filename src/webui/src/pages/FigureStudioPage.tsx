import { useCallback, useEffect, useMemo, useState, useRef, type SyntheticEvent, type WheelEvent } from 'react';
import {
  fetchPaperFigureCatalog,
  fetchPaperFigureRenderJob,
  PaperFigureCatalogItem,
  PaperFigureConfigEntry,
  PaperFigureRenderJob,
  PaperFigureKind,
  savePaperFigureConfig,
  startPaperFigureRender,
} from '../api';
import FigureConfigInspector, { type PathToken } from '../components/FigureConfigInspector';
import '../App.css';

type RenderComparisonState = {
  figureId: string;
  oldUrl: string | null;
  oldObjectUrl: string | null;
  newUrl: string | null;
  status: 'rendering' | 'completed' | 'failed';
};

type StageZoomMode = 'fit' | 'manual';

function formatDateTime(value?: string | null): string {
  if (!value) {
    return 'Not rendered yet';
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function cloneFigureConfig(config: PaperFigureConfigEntry): PaperFigureConfigEntry {
  return JSON.parse(JSON.stringify(config)) as PaperFigureConfigEntry;
}

function setNestedValue(target: unknown, path: PathToken[], value: unknown): unknown {
  if (path.length === 0) {
    return value;
  }

  const [token, ...rest] = path;
  if (typeof token === 'number') {
    const next = Array.isArray(target) ? [...target] : [];
    next[token] = setNestedValue(next[token], rest, value);
    return next;
  }

  const next = target && typeof target === 'object' && !Array.isArray(target)
    ? { ...(target as Record<string, unknown>) }
    : {};
  next[token] = setNestedValue(next[token], rest, value);
  return next;
}

function formatPath(path: PathToken[]): string {
  if (path.length === 0) {
    return 'root';
  }
  return path.map((token) => (typeof token === 'number' ? `#${token + 1}` : token)).join(' / ');
}

function getNestedValue(target: unknown, path: PathToken[]): unknown {
  if (path.length === 0) {
    return target;
  }
  const [token, ...rest] = path;
  if (typeof token === 'number') {
    const arr = Array.isArray(target) ? target : [];
    return getNestedValue(arr[token], rest);
  }
  const obj = target && typeof target === 'object' && !Array.isArray(target) ? (target as Record<string, unknown>) : {};
  return getNestedValue(obj[token], rest);
}

function deepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null) return a === b;
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    return a.every((item, index) => deepEqual(item, b[index]));
  }
  if (typeof a === 'object' && typeof b === 'object') {
    const aKeys = Object.keys(a as object);
    const bKeys = Object.keys(b as object);
    if (aKeys.length !== bKeys.length) return false;
    return aKeys.every((key) => deepEqual((a as Record<string, unknown>)[key], (b as Record<string, unknown>)[key]));
  }
  return false;
}

function figurePreviewSrc(figure: PaperFigureCatalogItem): string {
  return `${figure.previewUrl}?v=${encodeURIComponent(figure.updatedAt ?? '0')}`;
}

function configStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : [];
}

const LS_KEY_FIGURE_STUDIO = 'figureStudioSelected';
const STAGE_ZOOM_MIN = 0.25;
const STAGE_ZOOM_MAX = 6;
const STAGE_ZOOM_STEP = 1.12;

function clampStageZoom(value: number): number {
  return Math.min(STAGE_ZOOM_MAX, Math.max(STAGE_ZOOM_MIN, value));
}

function isPaperFigureKind(value: unknown): value is PaperFigureKind {
  return value === 'single' || value === 'montage';
}

function loadStudioPrefs(): { figureId: string | null; kind: PaperFigureKind } {
  try {
    const raw = localStorage.getItem(LS_KEY_FIGURE_STUDIO);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        figureId: typeof parsed?.figureId === 'string' ? parsed.figureId : null,
        kind: isPaperFigureKind(parsed?.kind) ? parsed.kind : 'single',
      };
    }
  } catch {
    // ignore malformed JSON
  }
  return { figureId: null, kind: 'single' };
}

function saveStudioPrefs(figureId: string | null, kind: PaperFigureKind) {
  try {
    localStorage.setItem(LS_KEY_FIGURE_STUDIO, JSON.stringify({ figureId, kind }));
  } catch {
    // ignore storage errors
  }
}

export default function FigureStudioPage() {
  const savedPrefs = useMemo(() => loadStudioPrefs(), []);
  const [figures, setFigures] = useState<PaperFigureCatalogItem[]>([]);
  const [selectedKind, setSelectedKind] = useState<PaperFigureKind>(savedPrefs.kind);
  const [selectedFigureId, setSelectedFigureId] = useState<string | null>(savedPrefs.figureId);
  const [libraryFilter, setLibraryFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [inspectorCollapsed, setInspectorCollapsed] = useState(false);
  const [draftConfig, setDraftConfig] = useState<PaperFigureConfigEntry | null>(null);
  const [dirty, setDirty] = useState(false);
  const [autoRedrawEnabled, setAutoRedrawEnabled] = useState(true);
  const [autoRenderDebounceMs, setAutoRenderDebounceMs] = useState(900);
  const [renderJob, setRenderJob] = useState<PaperFigureRenderJob | null>(null);
  const [renderComparison, setRenderComparison] = useState<RenderComparisonState | null>(null);
  const [stageZoom, setStageZoom] = useState(1);
  const [stageZoomMode, setStageZoomMode] = useState<StageZoomMode>('fit');
  const [stageTransformOrigin, setStageTransformOrigin] = useState('center center');
  const [stageViewportSize, setStageViewportSize] = useState({ width: 0, height: 0 });
  const [stageNaturalSize, setStageNaturalSize] = useState({ width: 0, height: 0 });
  const stageViewportRef = useRef<HTMLDivElement | null>(null);
  const [statusMessage, setStatusMessage] = useState(
    'Inspector controls are restored. Save changes, then redraw manually or keep auto redraw enabled.',
  );

  useEffect(() => {
    let cancelled = false;

    const loadCatalog = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetchPaperFigureCatalog();
        if (cancelled) {
          return;
        }
        setAutoRenderDebounceMs(response.autoRenderDebounceMs);
        setFigures(response.figures);
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : 'Failed to load figure catalog');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadCatalog();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const viewport = stageViewportRef.current;
    if (!viewport) {
      return undefined;
    }

    const updateViewportSize = () => {
      const rect = viewport.getBoundingClientRect();
      setStageViewportSize({ width: rect.width, height: rect.height });
    };

    updateViewportSize();
    const observer = new ResizeObserver(updateViewportSize);
    observer.observe(viewport);
    return () => observer.disconnect();
  }, [selectedFigureId]);

  const groupedFigures = useMemo(() => {
    const singles = figures.filter((figure) => figure.kind === 'single');
    const montages = figures.filter((figure) => figure.kind === 'montage');
    return { single: singles, montage: montages };
  }, [figures]);

  const filteredFigures = useMemo(() => {
    const query = libraryFilter.trim().toLowerCase();
    const source = groupedFigures[selectedKind];
    if (!query) {
      return source;
    }
    return source.filter((figure) =>
      [figure.title, figure.outputName, figure.id, figure.description]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(query)),
    );
  }, [groupedFigures, libraryFilter, selectedKind]);

  useEffect(() => {
    const pool = groupedFigures[selectedKind];
    if (figures.length === 0) {
      return;
    }
    if (pool.length === 0) {
      const fallback = figures[0];
      setSelectedKind(fallback.kind);
      setSelectedFigureId(fallback.id);
      return;
    }
    // Keep restored selections stable; only fall back when the current id is stale.
    if (!selectedFigureId || !pool.some((figure) => figure.id === selectedFigureId)) {
      setSelectedFigureId(pool[0].id);
    }
  }, [figures, groupedFigures, selectedFigureId, selectedKind]);

  // Persist selection to localStorage on every change
  const prevSelectedId = useRef<string | null>(null);
  const prevSelectedKind = useRef<PaperFigureKind>('single');
  useEffect(() => {
    if (selectedFigureId !== prevSelectedId.current || selectedKind !== prevSelectedKind.current) {
      prevSelectedId.current = selectedFigureId;
      prevSelectedKind.current = selectedKind;
      saveStudioPrefs(selectedFigureId, selectedKind);
    }
  }, [selectedFigureId, selectedKind]);

  const selectedFigure = useMemo(
    () => figures.find((figure) => figure.id === selectedFigureId) ?? null,
    [figures, selectedFigureId],
  );

  useEffect(() => {
    if (!selectedFigure) {
      setDraftConfig(null);
      setDirty(false);
      setRenderJob(null);
      setRenderComparison(null);
      setStatusMessage('Select a figure from the left library to restore reusable inspector controls.');
      return;
    }

    setDraftConfig(cloneFigureConfig(selectedFigure.config));
    setDirty(false);
    setRenderJob(null);
    setRenderComparison(null);
    setStageZoom(1);
    setStageZoomMode('fit');
    setStageTransformOrigin('center center');
    setStageNaturalSize({ width: 0, height: 0 });
    setStatusMessage(
      selectedFigure.editable
        ? `Editing ${selectedFigure.id}. Common adjusters are live; redraw controls target the selected bitmap.`
        : `${selectedFigure.id} is preview-only. Select a config-backed figure to edit and redraw.`,
    );
  }, [selectedFigureId]);

  const handleConfigChange = useCallback((path: PathToken[], value: unknown) => {
    setDraftConfig((current) => {
      const source = cloneFigureConfig(current ?? {});
      const currentValue = getNestedValue(source, path);
      if (deepEqual(currentValue, value)) {
        return current;
      }
      setDirty(true);
      setStatusMessage(`Draft updated: ${formatPath(path)}.`);
      return setNestedValue(source, path, value) as PaperFigureConfigEntry;
    });
  }, []);

  useEffect(() => {
    return () => {
      if (renderComparison?.oldObjectUrl) {
        URL.revokeObjectURL(renderComparison.oldObjectUrl);
      }
    };
  }, [renderComparison?.oldObjectUrl]);

  const refreshCatalog = useCallback(async () => {
    const response = await fetchPaperFigureCatalog();
    setAutoRenderDebounceMs(response.autoRenderDebounceMs);
    setFigures(response.figures);
    return response.figures;
  }, []);

  const startRenderForFigure = useCallback(async (figureId: string) => {
    setStatusMessage(`Rendering ${figureId}...`);
    const sourceFigure = figures.find((figure) => figure.id === figureId) ?? null;
    let oldUrl: string | null = sourceFigure?.exists ? figurePreviewSrc(sourceFigure) : null;
    let oldObjectUrl: string | null = null;

    if (oldUrl) {
      try {
        const response = await fetch(oldUrl, { cache: 'no-store' });
        if (response.ok) {
          oldObjectUrl = URL.createObjectURL(await response.blob());
          oldUrl = oldObjectUrl;
        }
      } catch {
        // Keep the cache-busted URL fallback if snapshot capture fails.
      }
    }

    setRenderComparison({
      figureId,
      oldUrl,
      oldObjectUrl,
      newUrl: null,
      status: 'rendering',
    });

    try {
      const nextJob = await startPaperFigureRender([figureId]);
      setRenderJob(nextJob);
    } catch (renderError) {
      setRenderComparison((current) =>
        current?.figureId === figureId ? { ...current, status: 'failed' } : current,
      );
      throw renderError;
    }
  }, [figures]);

  const handleSave = useCallback(async () => {
    if (!selectedFigure || !selectedFigure.editable || !draftConfig || !dirty) {
      return;
    }

    setStatusMessage(`Saving ${selectedFigure.id}...`);
    try {
      const savedFigure = await savePaperFigureConfig(selectedFigure.id, draftConfig);
      setFigures((current) => current.map((figure) => (figure.id === savedFigure.id ? savedFigure : figure)));
      setDraftConfig(cloneFigureConfig(savedFigure.config));
      setDirty(false);
      setStatusMessage(`Saved ${savedFigure.id} at ${formatDateTime(savedFigure.updatedAt)}.`);
      if (autoRedrawEnabled && savedFigure.renderable) {
        await startRenderForFigure(savedFigure.id);
      }
    } catch (saveError) {
      setStatusMessage(saveError instanceof Error ? saveError.message : `Failed to save ${selectedFigure.id}.`);
    }
  }, [autoRedrawEnabled, draftConfig, dirty, selectedFigure, startRenderForFigure]);

  const handleManualRedraw = useCallback(async () => {
    if (!selectedFigure?.renderable) {
      return;
    }
    try {
      await startRenderForFigure(selectedFigure.id);
    } catch (renderError) {
      setStatusMessage(renderError instanceof Error ? renderError.message : `Failed to render ${selectedFigure.id}.`);
    }
  }, [selectedFigure, startRenderForFigure]);

  useEffect(() => {
    if (!autoRedrawEnabled || !selectedFigure?.editable || !selectedFigure.renderable || !draftConfig || !dirty) {
      return;
    }

    const timer = window.setTimeout(async () => {
      try {
        setStatusMessage(`Auto-saving ${selectedFigure.id}...`);
        const savedFigure = await savePaperFigureConfig(selectedFigure.id, draftConfig);
        setFigures((current) => current.map((figure) => (figure.id === savedFigure.id ? savedFigure : figure)));
        setDraftConfig(cloneFigureConfig(savedFigure.config));
        setDirty(false);
        await startRenderForFigure(savedFigure.id);
      } catch (autoError) {
        setStatusMessage(autoError instanceof Error ? autoError.message : `Auto redraw failed for ${selectedFigure.id}.`);
      }
    }, autoRenderDebounceMs);

    return () => window.clearTimeout(timer);
  }, [autoRedrawEnabled, autoRenderDebounceMs, dirty, draftConfig, selectedFigure, startRenderForFigure]);

  useEffect(() => {
    if (!renderJob || (renderJob.status !== 'queued' && renderJob.status !== 'running')) {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const nextJob = await fetchPaperFigureRenderJob(renderJob.id);
        setRenderJob(nextJob);
        if (nextJob.status === 'completed') {
          setStatusMessage(`Render completed: ${nextJob.figureIds.join(', ')}.`);
          window.clearInterval(timer);
          const refreshedFigures = await refreshCatalog();
          const renderedFigureId = nextJob.figureIds[0];
          const updatedFigure = refreshedFigures.find((figure) => figure.id === renderedFigureId);
          if (updatedFigure) {
            setRenderComparison((current) =>
              current?.figureId === renderedFigureId
                ? { ...current, newUrl: figurePreviewSrc(updatedFigure), status: 'completed' }
                : current,
            );
          }
        } else if (nextJob.status === 'failed') {
          setStatusMessage(nextJob.error ?? `Render failed: ${nextJob.figureIds.join(', ')}.`);
          const failedFigureId = nextJob.figureIds[0];
          setRenderComparison((current) =>
            current?.figureId === failedFigureId ? { ...current, status: 'failed' } : current,
          );
          window.clearInterval(timer);
        }
      } catch (pollError) {
        setStatusMessage(pollError instanceof Error ? pollError.message : 'Failed to poll render job.');
      }
    }, 1000);

    return () => window.clearInterval(timer);
  }, [refreshCatalog, renderJob]);

  const previewUrl = selectedFigure ? figurePreviewSrc(selectedFigure) : '';
  const editableCount = useMemo(() => figures.filter((figure) => figure.editable).length, [figures]);
  const canEditConfig = Boolean(selectedFigure?.editable && draftConfig);
  const canSave = Boolean(selectedFigure?.editable && draftConfig && dirty);
  const renderStatus = renderJob?.status ?? 'idle';
  const renderLogs = renderJob?.logs.join('\n') ?? 'No render job yet.';
  const isRendering = renderStatus === 'queued' || renderStatus === 'running';
  const canRedraw = Boolean(selectedFigure?.renderable && !isRendering);
  const activeComparison = selectedFigure && renderComparison?.figureId === selectedFigure.id
    ? renderComparison
    : null;
  const showComparison = Boolean(activeComparison && (activeComparison.status === 'rendering' || activeComparison.newUrl));
  const stageFitZoom = useMemo(() => {
    if (!stageViewportSize.width || !stageViewportSize.height || !stageNaturalSize.width || !stageNaturalSize.height) {
      return 1;
    }

    const availableWidth = Math.max(120, stageViewportSize.width - 48);
    const availableHeight = Math.max(120, stageViewportSize.height - 48);
    return clampStageZoom(Math.min(availableWidth / stageNaturalSize.width, availableHeight / stageNaturalSize.height, 1));
  }, [stageNaturalSize.height, stageNaturalSize.width, stageViewportSize.height, stageViewportSize.width]);

  useEffect(() => {
    if (stageZoomMode === 'fit') {
      setStageZoom(stageFitZoom);
    }
  }, [stageFitZoom, stageZoomMode]);

  const handleStageImageLoad = useCallback((event: SyntheticEvent<HTMLImageElement>) => {
    const image = event.currentTarget;
    if (image.naturalWidth > 0 && image.naturalHeight > 0) {
      setStageNaturalSize((current) => {
        if (current.width === image.naturalWidth && current.height === image.naturalHeight) {
          return current;
        }
        return { width: image.naturalWidth, height: image.naturalHeight };
      });
    }
  }, []);

  const handleStageWheel = useCallback((event: WheelEvent<HTMLDivElement>) => {
    if (!selectedFigure || (!selectedFigure.exists && !showComparison)) {
      return;
    }

    event.preventDefault();
    const viewport = event.currentTarget;
    const previousZoom = stageZoomMode === 'fit' ? stageFitZoom : stageZoom;
    const direction = event.deltaY < 0 ? 1 : -1;
    const nextZoom = clampStageZoom(previousZoom * (direction > 0 ? STAGE_ZOOM_STEP : 1 / STAGE_ZOOM_STEP));

    if (Math.abs(nextZoom - previousZoom) < 0.001) {
      return;
    }

    const rect = viewport.getBoundingClientRect();
    const originX = ((event.clientX - rect.left) / Math.max(1, rect.width)) * 100;
    const originY = ((event.clientY - rect.top) / Math.max(1, rect.height)) * 100;
    setStageZoomMode('manual');
    setStageTransformOrigin(`${originX.toFixed(2)}% ${originY.toFixed(2)}%`);
    setStageZoom(nextZoom);
  }, [selectedFigure, showComparison, stageFitZoom, stageZoom, stageZoomMode]);
  const setStageFitZoom = useCallback(() => {
    setStageZoomMode('fit');
    setStageTransformOrigin('center center');
    setStageZoom(stageFitZoom);
  }, [stageFitZoom]);
  const setStageActualZoom = useCallback(() => {
    setStageZoomMode('manual');
    setStageTransformOrigin('center center');
    setStageZoom(1);
  }, []);
  const navigateToFigure = useCallback((figureId: string) => {
    const target = figures.find((figure) => figure.id === figureId);
    if (!target) {
      setStatusMessage(`Related figure not found in Studio catalog: ${figureId}.`);
      return;
    }
    setLibraryFilter('');
    setSelectedKind(target.kind);
    setSelectedFigureId(target.id);
    setStatusMessage(`Jumped to ${target.id}.`);
  }, [figures]);
  const relatedSubfigures = useMemo(() => {
    if (!selectedFigure) {
      return [];
    }
    const ids = configStringArray(selectedFigure.config.subfigures);
    return ids
      .map((id) => figures.find((figure) => figure.id === id))
      .filter((figure): figure is PaperFigureCatalogItem => Boolean(figure));
  }, [figures, selectedFigure]);
  const parentMontages = useMemo(() => {
    if (!selectedFigure) {
      return [];
    }
    const explicit = configStringArray(selectedFigure.config.parent_montages);
    const discovered = figures
      .filter((figure) => figure.kind === 'montage' && configStringArray(figure.config.subfigures).includes(selectedFigure.id))
      .map((figure) => figure.id);
    const ids = Array.from(new Set([...explicit, ...discovered]));
    return ids
      .map((id) => figures.find((figure) => figure.id === id))
      .filter((figure): figure is PaperFigureCatalogItem => Boolean(figure));
  }, [figures, selectedFigure]);

  if (loading) {
    return <div className="loading">Loading figure studio...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="studio-admin-page">
      <div className="studio-admin-app">
        <header className="studio-admin-header">
          <div className="studio-admin-header__identity">
            <div className="studio-admin-header__eyebrow">Reusable adjuster rebuild</div>
            <h1>Figure Studio</h1>
            <div className="studio-admin-header__stats">
              <span>{figures.length} figures</span>
              <span>{editableCount} editable</span>
              <span>{figures.length - editableCount} preview only</span>
              <span>{selectedKind}</span>
              <span>{dirty ? 'Unsaved draft' : 'Draft synced'}</span>
            </div>
          </div>

          <div className="studio-admin-header__actions">
            <label className="studio-admin-toggle">
              <input
                type="checkbox"
                data-testid="studio-auto-redraw-toggle"
                checked={autoRedrawEnabled}
                onChange={(event) => setAutoRedrawEnabled(event.target.checked)}
              />
              Auto redraw
            </label>
            <button
              type="button"
              className="studio-admin-button studio-admin-button--primary"
              data-testid="studio-save-config"
              disabled={!canSave}
              onClick={handleSave}
            >
              Save config
            </button>
            <button
              type="button"
              className="studio-admin-button"
              data-testid="studio-redraw"
              disabled={!canRedraw}
              onClick={handleManualRedraw}
            >
              Redraw
            </button>
            <button
              type="button"
              className="studio-admin-button"
              data-testid="studio-inspector-toggle"
              onClick={() => setInspectorCollapsed((current) => !current)}
            >
              {inspectorCollapsed ? 'Show inspector' : 'Hide inspector'}
            </button>
          </div>
        </header>

        <div className="studio-admin-status" data-testid="studio-status-message">
          {statusMessage}
        </div>

        <div className={`studio-admin-main ${inspectorCollapsed ? 'is-inspector-collapsed' : ''}`}>
          <aside className="studio-admin-sidebar">
            <div className="studio-admin-panel__header">
              <div>
                <h2>Figure library</h2>
                <p>Selection stays lightweight on the left so the preview and inspector can share one stable workbench.</p>
              </div>
              <span className="studio-admin-panel__badge">
                {filteredFigures.length}/{groupedFigures[selectedKind].length}
              </span>
            </div>

            <div className="studio-admin-sidebar__controls">
              <div className="studio-admin-tabs" role="tablist" aria-label="Figure kind">
                {(['single', 'montage'] as PaperFigureKind[]).map((kind) => (
                  <button
                    key={kind}
                    type="button"
                    className={`studio-admin-tab ${selectedKind === kind ? 'is-active' : ''}`}
                    data-testid={`studio-tab-${kind}`}
                    onClick={() => setSelectedKind(kind)}
                  >
                    {kind === 'single' ? 'Single' : 'Montage'}
                  </button>
                ))}
              </div>
              <input
                className="studio-admin-search"
                type="text"
                placeholder="Filter by title, id, or output file"
                value={libraryFilter}
                onChange={(event) => setLibraryFilter(event.target.value)}
              />
            </div>

            <div className="studio-admin-sidebar__list">
              {filteredFigures.length > 0 ? (
                filteredFigures.map((figure) => (
                  <button
                    key={figure.id}
                    type="button"
                    className={`studio-admin-asset ${figure.id === selectedFigureId ? 'is-active' : ''}`}
                    data-testid={`studio-thumb-${figure.id}`}
                    onClick={() => setSelectedFigureId(figure.id)}
                  >
                    <div className="studio-admin-asset__thumb">
                      {figure.exists ? (
                        <img
                          src={`${figure.previewUrl}?thumb=${encodeURIComponent(figure.updatedAt ?? '0')}`}
                          alt={figure.title}
                        />
                      ) : (
                        <div className="studio-thumb__placeholder">No render yet</div>
                      )}
                    </div>
                    <div className="studio-admin-asset__meta">
                      <strong>{figure.title}</strong>
                      <span>{figure.outputName}</span>
                      <span className="studio-admin-asset__id">{figure.id}</span>
                      {!figure.editable && <em className="studio-thumb__tag">Preview only</em>}
                    </div>
                  </button>
                ))
              ) : (
                <div className="studio-admin-empty">No figures match the current filter.</div>
              )}
            </div>
          </aside>

          <section className="studio-admin-stage">
            {selectedFigure ? (
              <>
                <div className="studio-admin-panel__header studio-admin-stage__header">
                  <div>
                    <div className="studio-admin-stage__eyebrow">
                      {selectedFigure.kind === 'single' ? 'Single figure' : 'Montage'}
                    </div>
                    <h2>{selectedFigure.title}</h2>
                    <p>{selectedFigure.description}</p>
                  </div>
                  <div className="studio-admin-stage__meta">
                    <span>{selectedFigure.editable ? 'Config-backed' : 'Preview only'}</span>
                    <span>{selectedFigure.outputName}</span>
                    <span>{formatDateTime(selectedFigure.updatedAt)}</span>
                  </div>
                </div>

                {relatedSubfigures.length > 0 || parentMontages.length > 0 ? (
                  <div className="studio-admin-links" data-testid="studio-related-links">
                    {relatedSubfigures.length > 0 ? (
                      <div className="studio-admin-links__group">
                        <span>Subfigures</span>
                        <div className="studio-admin-links__buttons">
                          {relatedSubfigures.map((figure) => (
                            <button
                              key={figure.id}
                              type="button"
                              className="studio-admin-linkchip"
                              data-testid={`studio-link-subfigure-${figure.id}`}
                              onClick={() => navigateToFigure(figure.id)}
                            >
                              {figure.id}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {parentMontages.length > 0 ? (
                      <div className="studio-admin-links__group">
                        <span>Used in montage</span>
                        <div className="studio-admin-links__buttons">
                          {parentMontages.map((figure) => (
                            <button
                              key={figure.id}
                              type="button"
                              className="studio-admin-linkchip studio-admin-linkchip--parent"
                              data-testid={`studio-link-parent-${figure.id}`}
                              onClick={() => navigateToFigure(figure.id)}
                            >
                              {figure.id}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </div>
                ) : null}

                <div
                  ref={stageViewportRef}
                  className={`studio-admin-stage__viewport ${showComparison ? 'is-comparing' : ''} ${
                    stageZoomMode === 'manual' ? 'is-manual-zoom' : 'is-fit-zoom'
                  }`}
                  onWheel={handleStageWheel}
                  data-testid="studio-preview-viewport"
                >
                  {(selectedFigure.exists || showComparison) ? (
                    <div className="studio-admin-stage__zoom-controls" aria-label="Preview zoom controls">
                      <span className="studio-admin-stage__zoom-readout">
                        {stageZoomMode === 'fit' ? 'Fit' : `${Math.round(stageZoom * 100)}%`}
                      </span>
                      <button
                        type="button"
                        className={`studio-admin-stage__zoom-button ${stageZoomMode === 'fit' ? 'is-active' : ''}`}
                        onClick={setStageFitZoom}
                        title="Fit the bitmap to the main drawing area."
                      >
                        适应窗口
                      </button>
                      <button
                        type="button"
                        className={`studio-admin-stage__zoom-button ${
                          stageZoomMode === 'manual' && Math.abs(stageZoom - 1) < 0.001 ? 'is-active' : ''
                        }`}
                        onClick={setStageActualZoom}
                        title="Show the bitmap at 100%."
                      >
                        100%
                      </button>
                    </div>
                  ) : null}
                  <div
                    className="studio-admin-stage__zoom-surface"
                    style={{
                      transform: stageZoomMode === 'manual' ? `scale(${stageZoom})` : 'none',
                      transformOrigin: stageTransformOrigin,
                    }}
                  >
                    {showComparison && activeComparison ? (
                      <div className="studio-admin-stage__compare" data-testid="studio-preview-comparison">
                        <div className="studio-admin-compare-pane">
                          <div className="studio-admin-compare-pane__label">Old bitmap</div>
                          {activeComparison.oldUrl ? (
                            <img
                              src={activeComparison.oldUrl}
                            alt={`Old ${selectedFigure.title}`}
                            className="studio-admin-stage__image"
                            data-testid="studio-compare-old-image"
                            onLoad={handleStageImageLoad}
                          />
                          ) : (
                            <div className="studio-admin-empty">No previous bitmap to compare.</div>
                          )}
                        </div>
                        <div className="studio-admin-compare-pane">
                          <div className="studio-admin-compare-pane__label">
                            {activeComparison.newUrl ? 'New bitmap' : 'Rendering new bitmap'}
                          </div>
                          {activeComparison.newUrl ? (
                            <img
                              src={activeComparison.newUrl}
                            alt={`New ${selectedFigure.title}`}
                            className="studio-admin-stage__image"
                            data-testid="studio-compare-new-image"
                            onLoad={handleStageImageLoad}
                          />
                          ) : (
                            <div className="studio-admin-render-wait" data-testid="studio-render-spinner">
                              <span className="studio-admin-spinner" aria-hidden="true" />
                              <strong>Rendering...</strong>
                              <p>The old bitmap remains pinned on the left until the new render is available.</p>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : selectedFigure.exists ? (
                      <img
                        src={previewUrl}
                      alt={selectedFigure.title}
                      className="studio-admin-stage__image"
                      data-testid="studio-preview-image"
                      onLoad={handleStageImageLoad}
                    />
                    ) : (
                      <div className="studio-admin-empty">This figure has no rendered bitmap yet.</div>
                    )}
                  </div>
                </div>

                <div className="studio-admin-console">
                  <div className="studio-admin-console__header">
                    <span>Render status</span>
                    <strong data-testid="studio-render-status">{renderStatus}</strong>
                  </div>
                  <pre className="studio-admin-console__body" data-testid="studio-render-console">
                    {renderLogs}
                  </pre>
                </div>
              </>
            ) : (
              <div className="studio-admin-empty">Select a figure from the left library.</div>
            )}
          </section>

          {inspectorCollapsed ? (
            <aside className="studio-admin-rail">
              <button
                type="button"
                className="studio-admin-rail__button"
                data-testid="studio-inspector-hide"
                onClick={() => setInspectorCollapsed(false)}
              >
                Inspector
              </button>
            </aside>
          ) : (
            <aside className="studio-admin-inspector">
              <div className="studio-admin-panel__header">
                <div>
                  <h2>{canEditConfig ? 'Common adjusters' : 'Inspector'}</h2>
                  <p>
                    {canEditConfig
                      ? 'Reusable field groups edit the selected figure config directly.'
                      : 'This figure is preview-only, so there is no editable config for this bitmap.'}
                  </p>
                </div>
                <button
                  type="button"
                  className="studio-admin-button studio-admin-button--small"
                  data-testid="studio-inspector-hide"
                  onClick={() => setInspectorCollapsed(true)}
                >
                  Hide
                </button>
              </div>

              <div className="studio-admin-inspector__body" data-testid="studio-scroll-body">
                {selectedFigure?.editable && draftConfig ? (
                  <FigureConfigInspector config={draftConfig} onChange={handleConfigChange} />
                ) : (
                  <div className="studio-admin-note">
                    No editable config for this figure.
                  </div>
                )}
              </div>
            </aside>
          )}
        </div>
      </div>
    </div>
  );
}
