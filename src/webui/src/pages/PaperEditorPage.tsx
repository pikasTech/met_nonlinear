import {
  startTransition,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import 'katex/dist/katex.min.css';
import '../App.css';
import {
  fetchPaperEditorDocument,
  fetchPaperEditorDocumentState,
  previewPaperEditorDocument,
  savePaperEditorDocument,
} from '../clientApi';
import type { PaperEditorDocument, PaperEditorOutlineItem } from '../types';

type ViewMode = 'split' | 'source' | 'preview';
type PreviewMode = 'rendered' | 'markdown';
type SidebarSection = 'outline' | 'performance' | 'diagnostics' | 'imports' | 'macros';

interface SourceLineMetric {
  top: number;
  height: number;
}

interface EditorSelectionSnapshot {
  rawStart: number;
  rawEnd: number;
  rawLine: number;
  hadFocus: boolean;
  scrollTop: number;
}

const DEFAULT_ENTRY = 'main.tex';
const IDLE_PREVIEW_DEBOUNCE_MS = 5000;
const EXTERNAL_STATE_POLL_MS = 1000;
const SCROLL_ANCHOR_RATIO = 0.24;

function formatTimestamp(value: string | null): string {
  if (!value) {
    return 'Unknown';
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function buildLineOffsets(source: string): number[] {
  const offsets = [0];
  for (let index = 0; index < source.length; index += 1) {
    if (source[index] === '\n') {
      offsets.push(index + 1);
    }
  }
  return offsets;
}

function countCurrentLine(source: string, caretIndex: number): number {
  return source.slice(0, caretIndex).split(/\r?\n/).length;
}

function buildLineNumbers(source: string): number[] {
  return Array.from({ length: source.split(/\r?\n/).length }, (_value, index) => index + 1);
}

function buildFallbackSourceLineMetrics(lineCount: number, lineHeight: number): SourceLineMetric[] {
  return Array.from({ length: lineCount }, (_value, index) => ({
    top: index * lineHeight,
    height: lineHeight,
  }));
}

function getSourceScrollTopForRawLine(viewStartMap: number[], lineHeight: number, lineNumber: number, viewportHeight: number): number {
  if (viewStartMap.length <= 1) {
    return 0;
  }
  const safeLine = clamp(lineNumber, 1, viewStartMap.length - 1);
  const viewLine = Math.max(1, viewStartMap[safeLine] ?? 1);
  return Math.max(0, (viewLine - 1) * lineHeight - viewportHeight * SCROLL_ANCHOR_RATIO);
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function getLineIndexForOffset(offsets: number[], textLength: number, offset: number): number {
  const safeOffset = clamp(offset, 0, textLength);
  let low = 0;
  let high = offsets.length - 1;
  while (low < high) {
    const middle = Math.floor((low + high + 1) / 2);
    if ((offsets[middle] ?? 0) <= safeOffset) {
      low = middle;
    } else {
      high = middle - 1;
    }
  }
  return low;
}

function getRawOffsetFromViewOffset(
  sourceViewText: string,
  sourceView: PaperEditorDocument['sourceView'] | null,
  viewOffset: number,
): number {
  const safeOffset = clamp(viewOffset, 0, sourceViewText.length);
  if (!sourceView) {
    return safeOffset;
  }

  const viewLines = sourceViewText.split(/\r?\n/);
  const viewLineOffsets = buildLineOffsets(sourceViewText);
  const viewLineIndex = getLineIndexForOffset(viewLineOffsets, sourceViewText.length, safeOffset);
  const viewColumn = Math.min(
    safeOffset - (viewLineOffsets[viewLineIndex] ?? 0),
    viewLines[viewLineIndex]?.length ?? 0,
  );

  let rawOffset = 0;
  for (let index = 0; index < viewLineIndex; index += 1) {
    rawOffset += viewLines[index]?.length ?? 0;
    if (sourceView.viewLineEndsWithSourceBreak[index + 1] ?? true) {
      rawOffset += 1;
    }
  }

  return rawOffset + viewColumn;
}

function getRawLineNumberForOffset(source: string, rawOffset: number): number {
  const offsets = buildLineOffsets(source);
  return getLineIndexForOffset(offsets, source.length, rawOffset) + 1;
}

function getViewOffsetFromRawOffset(
  source: string,
  sourceView: PaperEditorDocument['sourceView'] | null,
  rawOffset: number,
): number {
  const safeRawOffset = clamp(rawOffset, 0, source.length);
  if (!sourceView) {
    return safeRawOffset;
  }

  const rawLines = source.split(/\r?\n/);
  const rawLineOffsets = buildLineOffsets(source);
  const rawLineIndex = getLineIndexForOffset(rawLineOffsets, source.length, safeRawOffset);
  const rawLineNumber = rawLineIndex + 1;
  const rawLineStart = rawLineOffsets[rawLineIndex] ?? 0;
  const rawLineText = rawLines[rawLineIndex] ?? '';
  let remainingColumn = Math.min(safeRawOffset - rawLineStart, rawLineText.length);

  const viewLines = sourceView.text.split(/\r?\n/);
  const viewLineOffsets = buildLineOffsets(sourceView.text);
  const viewStart = sourceView.latexToViewLineStart[rawLineNumber] ?? rawLineNumber;
  const viewEnd = sourceView.latexToViewLineEnd[rawLineNumber] ?? viewStart;

  for (let viewLine = viewStart; viewLine <= viewEnd; viewLine += 1) {
    const fragment = viewLines[viewLine - 1] ?? '';
    if (remainingColumn <= fragment.length) {
      return (viewLineOffsets[viewLine - 1] ?? 0) + remainingColumn;
    }
    remainingColumn -= fragment.length;
  }

  return (viewLineOffsets[viewEnd - 1] ?? 0) + (viewLines[viewEnd - 1]?.length ?? 0);
}

function getEditorLineHeight(editor: HTMLTextAreaElement): number {
  return Number.parseFloat(getComputedStyle(editor).lineHeight) || 24;
}

function getEditorWrapColumns(editor: HTMLTextAreaElement): number {
  const styles = getComputedStyle(editor);
  const paddingLeft = Number.parseFloat(styles.paddingLeft) || 0;
  const paddingRight = Number.parseFloat(styles.paddingRight) || 0;
  const contentWidth = Math.max(1, editor.clientWidth - paddingLeft - paddingRight);
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  const fontSize = styles.fontSize || '14px';
  const fontFamily = styles.fontFamily || 'monospace';
  const fontWeight = styles.fontWeight || '400';
  if (context) {
    context.font = `${fontWeight} ${fontSize} ${fontFamily}`;
  }
  const measuredWidth = context?.measureText('0').width ?? Number.parseFloat(fontSize) * 0.62;
  return Math.max(1, Math.floor(contentWidth / Math.max(measuredWidth, 1)));
}

function getElementScrollTop(container: HTMLElement, element: HTMLElement): number {
  const containerRect = container.getBoundingClientRect();
  const elementRect = element.getBoundingClientRect();
  return container.scrollTop + elementRect.top - containerRect.top;
}

function buildSourceLineMetrics(
  lineCount: number,
  sourceView: PaperEditorDocument['sourceView'] | null,
  lineHeight: number,
): SourceLineMetric[] {
  if (!sourceView) {
    return buildFallbackSourceLineMetrics(lineCount, lineHeight);
  }

  return Array.from({ length: lineCount }, (_value, index) => {
    const rawLine = index + 1;
    const viewStart = sourceView.latexToViewLineStart[rawLine] ?? rawLine;
    const viewEnd = sourceView.latexToViewLineEnd[rawLine] ?? viewStart;
    return {
      top: (viewStart - 1) * lineHeight,
      height: Math.max(1, viewEnd - viewStart + 1) * lineHeight,
    };
  });
}

function unwrapSourceViewText(
  sourceViewText: string,
  sourceView: PaperEditorDocument['sourceView'] | null,
): string {
  if (!sourceView) {
    return sourceViewText;
  }

  const viewLines = sourceViewText.split(/\r?\n/);
  let rawSource = '';
  for (let index = 0; index < viewLines.length; index += 1) {
    rawSource += viewLines[index] ?? '';
    if (index === viewLines.length - 1) {
      continue;
    }
    const viewLine = index + 1;
    if (sourceView.viewLineEndsWithSourceBreak[viewLine] ?? true) {
      rawSource += '\n';
    }
  }
  return rawSource;
}

function getLineHeight(element: HTMLElement): number {
  return Number.parseFloat(getComputedStyle(element).lineHeight) || 22;
}

function findHtmlBlockByHtmlLine(
  htmlBlocks: PaperEditorDocument['lineMappings']['htmlBlocks'],
  htmlLine: number,
) {
  return htmlBlocks.find((block) => htmlLine >= block.htmlStartLine && htmlLine <= block.htmlEndLine) ?? htmlBlocks[htmlBlocks.length - 1] ?? null;
}

function findHtmlBlockByScroll(
  htmlBlocks: PaperEditorDocument['lineMappings']['htmlBlocks'],
  preview: HTMLDivElement,
) {
  if (htmlBlocks.length === 0) {
    return null;
  }

  const anchorScroll = preview.scrollTop + preview.clientHeight * SCROLL_ANCHOR_RATIO;
  let activeBlock = htmlBlocks[0];
  for (const block of htmlBlocks) {
    const element = preview.querySelector<HTMLElement>(`[data-html-block-index="${block.htmlBlockIndex}"]`);
    if (!element) {
      continue;
    }
    const blockTop = getElementScrollTop(preview, element);
    if (blockTop <= anchorScroll) {
      activeBlock = block;
      continue;
    }
    break;
  }
  return activeBlock;
}

function findOutlineSegmentByLine(outline: PaperEditorOutlineItem[], targetLine: number) {
  if (outline.length === 0) {
    return null;
  }

  let current = outline[0];
  let next: PaperEditorOutlineItem | null = null;
  for (let index = 0; index < outline.length; index += 1) {
    const item = outline[index];
    if (item.line <= targetLine) {
      current = item;
      next = outline[index + 1] ?? null;
      continue;
    }
    next = item;
    break;
  }

  return { current, next };
}

export default function PaperEditorPage() {
  const [documentData, setDocumentData] = useState<PaperEditorDocument | null>(null);
  const [previewData, setPreviewData] = useState<PaperEditorDocument | null>(null);
  const [source, setSource] = useState('');
  const [sourceViewText, setSourceViewText] = useState('');
  const [editorLocked, setEditorLocked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [previewing, setPreviewing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState('Loading docs/paper/latex/main.tex ...');
  const [autoPreview, setAutoPreview] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('split');
  const [previewMode, setPreviewMode] = useState<PreviewMode>('rendered');
  const [activeOutlineId, setActiveOutlineId] = useState<string | null>(null);
  const [editorLine, setEditorLine] = useState(1);
  const [roundTripMs, setRoundTripMs] = useState(0);
  const [clientRenderMs, setClientRenderMs] = useState(0);
  const [measureToken, setMeasureToken] = useState(0);
  const [editorLineHeight, setEditorLineHeight] = useState(23.2);
  const [viewColumns, setViewColumns] = useState(80);
  const [sidebarOpen, setSidebarOpen] = useState<Record<SidebarSection, boolean>>({
    outline: true,
    performance: true,
    diagnostics: false,
    imports: false,
    macros: false,
  });

  const previewRequestIdRef = useRef(0);
  const renderStartRef = useRef(0);
  const syncSourceRef = useRef<'editor' | 'preview' | null>(null);
  const latestSourceRef = useRef('');
  const latestRevisionRef = useRef<string | null>(null);
  const pendingSelectionRestoreRef = useRef<EditorSelectionSnapshot | null>(null);
  const externalReloadInFlightRef = useRef(false);
  const editorRef = useRef<HTMLTextAreaElement | null>(null);
  const gutterRef = useRef<HTMLDivElement | null>(null);
  const previewRef = useRef<HTMLDivElement | null>(null);

  const displayedDocument = previewData ?? documentData;
  const displayedSourceView = displayedDocument?.sourceView ?? null;
  const sourceLines = useMemo(() => source.split(/\r?\n/), [source]);
  const sourceViewLineOffsets = useMemo(() => buildLineOffsets(sourceViewText), [sourceViewText]);
  const lineNumbers = useMemo(() => buildLineNumbers(source), [source]);
  const sourceLineMetrics = useMemo(
    () => buildSourceLineMetrics(sourceLines.length, displayedSourceView, editorLineHeight),
    [displayedSourceView, editorLineHeight, sourceLines.length],
  );
  const isDirty = source !== (documentData?.source ?? '');

  const toggleSidebarSection = useCallback((section: SidebarSection) => {
    setSidebarOpen((current) => ({
      ...current,
      [section]: !current[section],
    }));
  }, []);

  const syncGutterScroll = useCallback((nextScrollTop: number) => {
    const gutter = gutterRef.current;
    if (!gutter) {
      return;
    }
    gutter.scrollTop = nextScrollTop;
  }, []);

  const captureEditorSelection = useCallback((): EditorSelectionSnapshot | null => {
    const editor = editorRef.current;
    if (!editor) {
      return null;
    }

    const rawStart = getRawOffsetFromViewOffset(sourceViewText, displayedSourceView, editor.selectionStart);
    const rawEnd = getRawOffsetFromViewOffset(sourceViewText, displayedSourceView, editor.selectionEnd);
    return {
      rawStart,
      rawEnd,
      rawLine: getRawLineNumberForOffset(source, rawStart),
      hadFocus: document.activeElement === editor,
      scrollTop: editor.scrollTop,
    };
  }, [displayedSourceView, source, sourceViewText]);

  const queueSelectionRestore = useCallback((snapshot: EditorSelectionSnapshot | null) => {
    pendingSelectionRestoreRef.current = snapshot;
  }, []);

  useEffect(() => {
    latestSourceRef.current = source;
  }, [source]);

  useEffect(() => {
    latestRevisionRef.current = documentData?.revision ?? null;
  }, [documentData?.revision]);

  const loadDocument = useCallback(async (options?: { reason?: 'initial' | 'manual' | 'external'; preserveSelection?: boolean }) => {
    const reason = options?.reason ?? 'manual';
    const selectionSnapshot = options?.preserveSelection ? captureEditorSelection() : null;
    if (reason === 'initial') {
      setLoading(true);
    }
    if (reason === 'external') {
      setEditorLocked(true);
      setStatus('External .tex change detected. Reloading source from disk...');
    }
    setError(null);
    try {
      const document = await fetchPaperEditorDocument(DEFAULT_ENTRY, viewColumns);
      latestRevisionRef.current = document.revision;
      queueSelectionRestore(selectionSnapshot);
      renderStartRef.current = performance.now();
      startTransition(() => {
        setDocumentData(document);
        setPreviewData(document);
        setSource(document.source);
        setSourceViewText(document.sourceView.text);
        setActiveOutlineId((current) => current ?? document.outline[0]?.id ?? null);
      });
      if (reason === 'external') {
        setStatus(`External .tex change detected. Reloaded ${document.entry} from disk.`);
      } else {
        setStatus(`Loaded ${document.entry}. Imported ${document.imports.length} tex files.`);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load paper document');
      setStatus('Failed to load paper source.');
    } finally {
      if (reason === 'initial') {
        setLoading(false);
      }
      if (reason === 'external') {
        setEditorLocked(false);
      }
    }
  }, [captureEditorSelection, queueSelectionRestore, viewColumns]);

  useEffect(() => {
    void loadDocument({ reason: 'initial' });
  }, [loadDocument]);

  useLayoutEffect(() => {
    if (!renderStartRef.current) {
      return;
    }
    setClientRenderMs(Number((performance.now() - renderStartRef.current).toFixed(2)));
    renderStartRef.current = 0;
  }, [displayedDocument?.markdown, previewMode]);

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor || typeof ResizeObserver === 'undefined') {
      return undefined;
    }

    const observer = new ResizeObserver(() => {
      setMeasureToken((current) => current + 1);
    });
    observer.observe(editor);
    return () => observer.disconnect();
  }, [viewMode]);

  useLayoutEffect(() => {
    const editor = editorRef.current;
    if (!editor) {
      return;
    }

    const nextLineHeight = getEditorLineHeight(editor);
    setEditorLineHeight((current) => (Math.abs(current - nextLineHeight) > 0.5 ? nextLineHeight : current));

    const nextColumns = getEditorWrapColumns(editor);
    setViewColumns((current) => (current !== nextColumns ? nextColumns : current));
  }, [measureToken, viewMode]);

  useLayoutEffect(() => {
    const snapshot = pendingSelectionRestoreRef.current;
    const editor = editorRef.current;
    if (!snapshot || !editor) {
      return;
    }

    const nextSelectionStart = getViewOffsetFromRawOffset(source, displayedSourceView, snapshot.rawStart);
    const nextSelectionEnd = getViewOffsetFromRawOffset(source, displayedSourceView, snapshot.rawEnd);
    if (snapshot.hadFocus) {
      editor.focus();
    }
    editor.setSelectionRange(nextSelectionStart, nextSelectionEnd);
    const targetScrollTop = displayedSourceView
      ? getSourceScrollTopForRawLine(displayedSourceView.latexToViewLineStart, editorLineHeight, snapshot.rawLine, editor.clientHeight)
      : snapshot.scrollTop;
    editor.scrollTop = clamp(targetScrollTop, 0, Math.max(editor.scrollHeight - editor.clientHeight, 0));
    syncGutterScroll(editor.scrollTop);
    setEditorLine(getRawLineNumberForOffset(source, snapshot.rawStart));
    pendingSelectionRestoreRef.current = null;
  }, [displayedSourceView, editorLineHeight, source, sourceViewText, syncGutterScroll, viewMode]);

  useLayoutEffect(() => {
    const editor = editorRef.current;
    if (!editor) {
      return;
    }
    syncGutterScroll(editor.scrollTop);
  }, [sourceLineMetrics, sourceViewText, syncGutterScroll]);

  const runPreview = useCallback(
    async (nextSource: string, nextViewColumns = viewColumns) => {
      const requestId = ++previewRequestIdRef.current;
      const startedAt = performance.now();
      const requestedSource = nextSource;
      setPreviewing(true);
      setError(null);
      try {
        const preview = await previewPaperEditorDocument(DEFAULT_ENTRY, nextSource, nextViewColumns);
        if (requestId !== previewRequestIdRef.current || requestedSource !== latestSourceRef.current) {
          return;
        }
        queueSelectionRestore(captureEditorSelection());
        renderStartRef.current = performance.now();
        setRoundTripMs(Number((performance.now() - startedAt).toFixed(2)));
        startTransition(() => {
          setPreviewData(preview);
          setSourceViewText(preview.sourceView.text);
          setActiveOutlineId((current) => current ?? preview.outline[0]?.id ?? null);
        });
        setStatus(`Preview refreshed in ${preview.performance.parseMs.toFixed(2)} ms on server.`);
      } catch (previewError) {
        if (requestId !== previewRequestIdRef.current) {
          return;
        }
        setError(previewError instanceof Error ? previewError.message : 'Failed to preview paper document');
        setStatus('Preview refresh failed.');
      } finally {
        if (requestId === previewRequestIdRef.current) {
          setPreviewing(false);
        }
      }
    },
    [captureEditorSelection, queueSelectionRestore, viewColumns],
  );

  useEffect(() => {
    if (!autoPreview || !documentData || source === documentData.source) {
      return undefined;
    }
    const handle = window.setTimeout(() => {
      void runPreview(source, viewColumns);
    }, IDLE_PREVIEW_DEBOUNCE_MS);
    return () => window.clearTimeout(handle);
  }, [autoPreview, documentData, runPreview, source, viewColumns]);

  useEffect(() => {
    if (!documentData) {
      return undefined;
    }

    const handle = window.setInterval(() => {
      if (externalReloadInFlightRef.current || loading || saving) {
        return;
      }

      externalReloadInFlightRef.current = true;
      void (async () => {
        try {
          const state = await fetchPaperEditorDocumentState(DEFAULT_ENTRY);
          const currentRevision = latestRevisionRef.current;
          if (!currentRevision) {
            latestRevisionRef.current = state.revision;
            return;
          }
          if (state.revision !== currentRevision) {
            await loadDocument({ reason: 'external', preserveSelection: true });
          }
        } catch {
          // Ignore transient polling failures; editor state should remain usable.
        } finally {
          externalReloadInFlightRef.current = false;
        }
      })();
    }, EXTERNAL_STATE_POLL_MS);

    return () => window.clearInterval(handle);
  }, [documentData, loadDocument, loading, saving]);

  useEffect(() => {
    if (!documentData || (displayedSourceView?.columns ?? 0) === viewColumns) {
      return undefined;
    }

    const handle = window.setTimeout(() => {
      void runPreview(source, viewColumns);
    }, 80);
    return () => window.clearTimeout(handle);
  }, [documentData, displayedSourceView?.columns, runPreview, source, viewColumns]);

  const handleSave = useCallback(async () => {
    queueSelectionRestore(captureEditorSelection());
    setSaving(true);
    setError(null);
    try {
      const saved = await savePaperEditorDocument(DEFAULT_ENTRY, source, viewColumns);
      latestRevisionRef.current = saved.revision;
      renderStartRef.current = performance.now();
      startTransition(() => {
        setDocumentData(saved);
        setPreviewData(saved);
        setSource(saved.source);
        setSourceViewText(saved.sourceView.text);
      });
      setStatus(`Saved ${saved.entry} at ${formatTimestamp(saved.updatedAt)}.`);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to save paper document');
      setStatus('Save failed.');
    } finally {
      setSaving(false);
    }
  }, [captureEditorSelection, queueSelectionRestore, source, viewColumns]);

  const handleEditorScroll = useCallback(() => {
    const editor = editorRef.current;
    const preview = previewRef.current;
    const outline = displayedDocument?.outline ?? [];
    const lineMappings = displayedDocument?.lineMappings;
    if (!editor || !preview || syncSourceRef.current === 'preview') {
      return;
    }

    syncGutterScroll(editor.scrollTop);
    const lineHeight = editorLineHeight || getEditorLineHeight(editor);
    const totalViewLines = displayedSourceView?.totalViewLines ?? Math.max(1, sourceViewText.split(/\r?\n/).length);
    const anchorOffset = editor.scrollTop + editor.clientHeight * SCROLL_ANCHOR_RATIO;
    const anchorViewLine = clamp(Math.floor(anchorOffset / Math.max(lineHeight, 1)) + 1, 1, totalViewLines);
    const targetLine = displayedSourceView?.viewLineToLatex[anchorViewLine]
      ?? clamp(anchorViewLine, 1, Math.max(1, sourceLines.length));
    const maxPreviewScroll = Math.max(preview.scrollHeight - preview.clientHeight, 0);

    syncSourceRef.current = 'editor';
    if (!lineMappings) {
      const maxEditorScroll = Math.max(editor.scrollHeight - editor.clientHeight, 1);
      preview.scrollTop = (editor.scrollTop / maxEditorScroll) * maxPreviewScroll;
    } else if (previewMode === 'markdown') {
      const markdownLine = lineMappings.latexToMarkdown[clamp(targetLine, 1, Math.max(1, lineMappings.latexToMarkdown.length - 1))] ?? 1;
      const previewLineHeight = getLineHeight(preview);
      preview.scrollTop = clamp((markdownLine - 1) * previewLineHeight - preview.clientHeight * SCROLL_ANCHOR_RATIO, 0, maxPreviewScroll);
    } else {
      const htmlLine = lineMappings.latexToHtml[clamp(targetLine, 1, Math.max(1, lineMappings.latexToHtml.length - 1))] ?? 1;
      const htmlBlock = findHtmlBlockByHtmlLine(lineMappings.htmlBlocks, htmlLine);
      if (htmlBlock) {
        const blockElement = preview.querySelector<HTMLElement>(`[data-html-block-index="${htmlBlock.htmlBlockIndex}"]`);
        if (blockElement) {
          const blockTop = getElementScrollTop(preview, blockElement);
          const blockHeight = Math.max(blockElement.offsetHeight, 1);
          const ratio = clamp(
            (htmlLine - htmlBlock.htmlStartLine) / Math.max(1, htmlBlock.htmlEndLine - htmlBlock.htmlStartLine),
            0,
            1,
          );
          preview.scrollTop = clamp(blockTop + blockHeight * ratio - preview.clientHeight * SCROLL_ANCHOR_RATIO, 0, maxPreviewScroll);
        }
      }
    }

    const segment = findOutlineSegmentByLine(outline, targetLine);
    if (segment) {
      setActiveOutlineId(segment.current.id);
    }

    window.requestAnimationFrame(() => {
      syncSourceRef.current = null;
    });
  }, [displayedDocument, displayedSourceView, editorLineHeight, previewMode, sourceLines.length, sourceViewText]);

  const handlePreviewScroll = useCallback(() => {
    const editor = editorRef.current;
    const preview = previewRef.current;
    const outline = displayedDocument?.outline ?? [];
    const lineMappings = displayedDocument?.lineMappings;
    if (!editor || !preview || syncSourceRef.current === 'editor') {
      return;
    }

    const maxEditorScroll = Math.max(editor.scrollHeight - editor.clientHeight, 0);
    syncSourceRef.current = 'preview';

    if (!lineMappings) {
      const maxPreviewScroll = Math.max(preview.scrollHeight - preview.clientHeight, 1);
      editor.scrollTop = (preview.scrollTop / maxPreviewScroll) * maxEditorScroll;
    } else {
      let targetLatexLine = 1;
      if (previewMode === 'markdown') {
        const previewLineHeight = getLineHeight(preview);
        const markdownLine = Math.round((preview.scrollTop + preview.clientHeight * SCROLL_ANCHOR_RATIO) / previewLineHeight) + 1;
        targetLatexLine = lineMappings.markdownToLatex[clamp(markdownLine, 1, Math.max(1, lineMappings.markdownToLatex.length - 1))] ?? 1;
      } else {
        const htmlBlock = findHtmlBlockByScroll(lineMappings.htmlBlocks, preview);
        if (htmlBlock) {
          const blockElement = preview.querySelector<HTMLElement>(`[data-html-block-index="${htmlBlock.htmlBlockIndex}"]`);
          if (blockElement) {
            const blockTop = getElementScrollTop(preview, blockElement);
            const blockHeight = Math.max(blockElement.offsetHeight, 1);
            const anchorScroll = preview.scrollTop + preview.clientHeight * SCROLL_ANCHOR_RATIO;
            const ratio = clamp((anchorScroll - blockTop) / blockHeight, 0, 1);
            const htmlLine = Math.round(
              htmlBlock.htmlStartLine + (htmlBlock.htmlEndLine - htmlBlock.htmlStartLine) * ratio,
            );
            targetLatexLine = lineMappings.htmlToLatex[clamp(htmlLine, 1, Math.max(1, lineMappings.htmlToLatex.length - 1))] ?? htmlBlock.latexStartLine;
          }
        }
      }

      const targetScrollTop = displayedSourceView
        ? getSourceScrollTopForRawLine(displayedSourceView.latexToViewLineStart, editorLineHeight, targetLatexLine, editor.clientHeight)
        : Math.max(0, (targetLatexLine - 1) * editorLineHeight - editor.clientHeight * SCROLL_ANCHOR_RATIO);
      editor.scrollTop = clamp(targetScrollTop, 0, maxEditorScroll);
      syncGutterScroll(editor.scrollTop);
      const segment = findOutlineSegmentByLine(outline, targetLatexLine);
      if (segment) {
        setActiveOutlineId(segment.current.id);
      }
    }

    window.requestAnimationFrame(() => {
      syncSourceRef.current = null;
    });
  }, [displayedDocument, displayedSourceView, editorLineHeight, previewMode, syncGutterScroll]);

  useEffect(() => {
    const editor = editorRef.current;
    const preview = previewRef.current;
    if (!editor || !preview) {
      return undefined;
    }

    editor.addEventListener('scroll', handleEditorScroll, { passive: true });
    preview.addEventListener('scroll', handlePreviewScroll, { passive: true });

    return () => {
      editor.removeEventListener('scroll', handleEditorScroll);
      preview.removeEventListener('scroll', handlePreviewScroll);
    };
  }, [handleEditorScroll, handlePreviewScroll]);

  const handleOutlineJump = useCallback(
    (item: PaperEditorOutlineItem) => {
      setActiveOutlineId(item.id);
      const preview = previewRef.current;
      const editor = editorRef.current;
      const lineMappings = displayedDocument?.lineMappings;
      if (preview && lineMappings) {
        if (previewMode === 'markdown') {
          const markdownLine = item.markdownLine ?? lineMappings.latexToMarkdown[item.line] ?? 1;
          const previewLineHeight = getLineHeight(preview);
          const maxPreviewScroll = Math.max(preview.scrollHeight - preview.clientHeight, 0);
          preview.scrollTop = clamp((markdownLine - 1) * previewLineHeight - preview.clientHeight * 0.12, 0, maxPreviewScroll);
        } else {
          const heading = preview.querySelector<HTMLElement>(`#${CSS.escape(item.id)}`);
          if (heading) {
            const previewRect = preview.getBoundingClientRect();
            const headingRect = heading.getBoundingClientRect();
            preview.scrollTop += headingRect.top - previewRect.top - preview.clientHeight * 0.12;
          }
        }
      }
      if (editor) {
        const viewLine = displayedSourceView?.latexToViewLineStart[item.line] ?? item.line;
        const cursor = sourceViewLineOffsets[Math.max(0, Math.min(viewLine - 1, sourceViewLineOffsets.length - 1))] ?? 0;
        editor.focus();
        editor.setSelectionRange(cursor, cursor);
        const targetScrollTop = displayedSourceView
          ? getSourceScrollTopForRawLine(displayedSourceView.latexToViewLineStart, editorLineHeight, item.line, editor.clientHeight)
          : Math.max(0, (item.line - 1) * getEditorLineHeight(editor) - editor.clientHeight * 0.2);
        editor.scrollTop = targetScrollTop;
        syncGutterScroll(editor.scrollTop);
        setEditorLine(item.line);
      }
    },
    [displayedDocument?.lineMappings, displayedSourceView, editorLineHeight, previewMode, sourceViewLineOffsets, syncGutterScroll],
  );

  const handleCaretTracking = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) {
      return;
    }
    const currentViewLine = countCurrentLine(sourceViewText, editor.selectionStart);
    setEditorLine(displayedSourceView?.viewLineToLatex[currentViewLine] ?? currentViewLine);
  }, [displayedSourceView, sourceViewText]);

  const visibleOutline = displayedDocument?.outline ?? [];
  const diagnostics = displayedDocument?.diagnostics ?? [];
  const macros = displayedDocument?.macros ?? {};

  return (
    <div className="paper-editor-page">
      <header className="paper-editor-header">
        <div>
          <p className="paper-editor-header__eyebrow">Paper Workshop / Bun Runtime</p>
          <h1 className="paper-editor-header__title">LaTeX quick preview editor</h1>
          <p className="paper-editor-header__body">
            Target document: docs/paper/latex/main.tex. The server resolves imported tex files, expands simple macros,
            preserves KaTeX math and keeps the preview pipeline measurable for optimization work.
          </p>
        </div>
        <div className="paper-editor-header__actions">
          <div className="paper-editor-pill">
            <span>Entry</span>
            <strong>{displayedDocument?.entry ?? DEFAULT_ENTRY}</strong>
          </div>
          <label className="paper-editor-pill paper-editor-pill--toggle">
            <input type="checkbox" checked={autoPreview} onChange={(event) => setAutoPreview(event.target.checked)} />
            <span>Auto preview</span>
          </label>
          <button type="button" className="paper-editor-button" onClick={() => void loadDocument({ reason: 'manual', preserveSelection: true })} disabled={loading || saving || editorLocked}>
            Reload
          </button>
          <button type="button" className="paper-editor-button" onClick={() => void runPreview(source, viewColumns)} disabled={loading || previewing || editorLocked}>
            {previewing ? 'Previewing…' : 'Preview now'}
          </button>
          <button type="button" className="paper-editor-button paper-editor-button--accent" onClick={() => void handleSave()} disabled={loading || saving || editorLocked || !isDirty}>
            {saving ? 'Saving…' : 'Save source'}
          </button>
        </div>
      </header>

      <section className="paper-editor-toolbar">
        <div className="paper-editor-toolbar__group">
          {(['split', 'source', 'preview'] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              type="button"
              className={`paper-editor-chip ${viewMode === mode ? 'is-active' : ''}`}
              onClick={() => setViewMode(mode)}
            >
              {mode === 'split' ? 'Split' : mode === 'source' ? 'Source' : 'Preview'}
            </button>
          ))}
        </div>
        <div className="paper-editor-toolbar__group">
          {(['rendered', 'markdown'] as PreviewMode[]).map((mode) => (
            <button
              key={mode}
              type="button"
              className={`paper-editor-chip ${previewMode === mode ? 'is-active' : ''}`}
              onClick={() => setPreviewMode(mode)}
            >
              {mode === 'rendered' ? 'Rendered preview' : 'Markdown output'}
            </button>
          ))}
        </div>
        <div className="paper-editor-toolbar__status" data-testid="paper-editor-status">
          <strong>{isDirty ? 'Unsaved changes' : 'Saved'}</strong>
          <span>{status}</span>
        </div>
      </section>

      <div className="paper-editor-shell">
        <aside className="paper-editor-sidebar">
          <div className="paper-editor-sidebar__scroll">
            <section className="paper-editor-sidebar__section">
              <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: 600, color: '#1f252b' }}>Outline</h3>
              <div className="paper-editor-outline__list" data-testid="paper-editor-outline">
                {visibleOutline.map((item) => (
                  <button
                    key={`${item.id}-${item.line}`}
                    type="button"
                    className={`paper-editor-outline__item ${activeOutlineId === item.id ? 'is-active' : ''}`}
                    style={{ paddingLeft: `${Math.max(0.8, item.level * 0.9)}rem` }}
                    onClick={() => handleOutlineJump(item)}
                  >
                    <strong>{item.title}</strong>
                    <span>L{item.line}</span>
                  </button>
                ))}
              </div>
            </section>

            <section className="paper-editor-sidebar__section">
              <button type="button" className="paper-editor-panel__toggle" onClick={() => toggleSidebarSection('performance')} aria-expanded={sidebarOpen.performance}>
                <p>Performance</p>
                <span>{sidebarOpen.performance ? 'Live telemetry' : 'Show'}</span>
              </button>
              {sidebarOpen.performance ? (
                <div className="paper-editor-metrics">
                  <article>
                    <strong>{displayedDocument?.performance.parseMs.toFixed(2) ?? '0.00'} ms</strong>
                    <span>Server parse</span>
                  </article>
                  <article>
                    <strong>{roundTripMs.toFixed(2)} ms</strong>
                    <span>Preview round trip</span>
                  </article>
                  <article>
                    <strong>{clientRenderMs.toFixed(2)} ms</strong>
                    <span>Client render</span>
                  </article>
                  <article>
                    <strong>{formatBytes(displayedDocument?.performance.sourceBytes ?? 0)}</strong>
                    <span>Source size</span>
                  </article>
                  <article>
                    <strong>{formatBytes(displayedDocument?.performance.markdownBytes ?? 0)}</strong>
                    <span>Markdown size</span>
                  </article>
                  <article>
                    <strong>{displayedDocument?.performance.macroCount ?? 0}</strong>
                    <span>Resolved macros</span>
                  </article>
                </div>
              ) : null}
            </section>

            <section className="paper-editor-sidebar__section">
              <button type="button" className="paper-editor-panel__toggle" onClick={() => toggleSidebarSection('diagnostics')} aria-expanded={sidebarOpen.diagnostics}>
                <p>Diagnostics</p>
                <span>{sidebarOpen.diagnostics ? `${diagnostics.length}` : 'Show'}</span>
              </button>
              {sidebarOpen.diagnostics ? (
                <div className="paper-editor-diagnostics">
                  {diagnostics.length === 0 ? <p>No parser diagnostics.</p> : diagnostics.map((item) => <p key={item}>{item}</p>)}
                </div>
              ) : null}
            </section>

            <section className="paper-editor-sidebar__section">
              <button type="button" className="paper-editor-panel__toggle" onClick={() => toggleSidebarSection('imports')} aria-expanded={sidebarOpen.imports}>
                <p>Imports</p>
                <span>{sidebarOpen.imports ? `${displayedDocument?.imports.length ?? 0}` : 'Show'}</span>
              </button>
              {sidebarOpen.imports ? (
                <div className="paper-editor-list">
                  {(displayedDocument?.imports ?? []).map((item) => (
                    <p key={item}>{item}</p>
                  ))}
                </div>
              ) : null}
            </section>

            <section className="paper-editor-sidebar__section">
              <button type="button" className="paper-editor-panel__toggle" onClick={() => toggleSidebarSection('macros')} aria-expanded={sidebarOpen.macros}>
                <p>Macro preview</p>
                <span>{sidebarOpen.macros ? `${Object.keys(macros).length}` : 'Show'}</span>
              </button>
              {sidebarOpen.macros ? (
                <div className="paper-editor-list paper-editor-list--mono">
                  {Object.entries(macros)
                    .slice(0, 24)
                    .map(([name, value]) => (
                      <p key={name}>
                        <strong>\{name}</strong> {value}
                      </p>
                    ))}
                </div>
              ) : null}
            </section>

            <div className="paper-editor-footer">
              <span>Updated</span>
              <strong>{formatTimestamp(displayedDocument?.updatedAt ?? null)}</strong>
            </div>
          </div>
        </aside>

        <main className={`paper-editor-workspace paper-editor-workspace--${viewMode}`}>
          {viewMode !== 'preview' ? (
            <section className="paper-editor-pane paper-editor-pane--source">
              <div className="paper-editor-panel__header">
                <p>Source mode</p>
                <span>Line {editorLine}</span>
              </div>
              <div className="paper-editor-pane__body paper-editor-pane__body--source">
                <div ref={gutterRef} className="paper-editor-gutter" aria-hidden="true">
                  <div className="paper-editor-gutter__inner">
                    {lineNumbers.map((lineNumber, index) => (
                      <div
                        key={lineNumber}
                        className={`paper-editor-gutter__line ${lineNumber === editorLine ? 'is-active' : ''}`}
                        style={{ height: `${sourceLineMetrics[index]?.height ?? 23.2}px` }}
                      >
                        {lineNumber}
                      </div>
                    ))}
                  </div>
                </div>
                <div className={`paper-editor-source-shell ${editorLocked ? 'is-locked' : ''}`}>
                  <textarea
                    ref={editorRef}
                    className="paper-editor-textarea"
                    data-testid="paper-editor-source"
                    value={sourceViewText}
                    wrap="off"
                    readOnly={editorLocked || loading || saving}
                    spellCheck={false}
                    onChange={(event) => {
                      const nextSourceViewText = event.target.value;
                      setSourceViewText(nextSourceViewText);
                      setSource(unwrapSourceViewText(nextSourceViewText, displayedSourceView));
                    }}
                    onClick={handleCaretTracking}
                    onKeyUp={handleCaretTracking}
                    onSelect={handleCaretTracking}
                  />
                  {editorLocked ? <div className="paper-editor-source-lock">External update detected. Reloading…</div> : null}
                </div>
              </div>
            </section>
          ) : null}

          {viewMode !== 'source' ? (
            <section className="paper-editor-pane paper-editor-pane--preview">
              <div className="paper-editor-panel__header">
                <p>{previewMode === 'rendered' ? 'Rendered preview' : 'Markdown compiler output'}</p>
                <span>{displayedDocument?.performance.imageCount ?? 0} figures</span>
              </div>
              <div ref={previewRef} className="paper-editor-preview" data-testid="paper-editor-preview">
                {previewMode === 'markdown' ? (
                  <pre className="paper-editor-preview__markdown">{displayedDocument?.markdown ?? ''}</pre>
                ) : (
                  <div dangerouslySetInnerHTML={{ __html: displayedDocument?.html ?? '' }} />
                )}
              </div>
            </section>
          ) : null}
        </main>

      </div>

      {error ? <div className="paper-editor-error">{error}</div> : null}
      {loading ? <div className="paper-editor-loading">Loading paper editor…</div> : null}
    </div>
  );
}