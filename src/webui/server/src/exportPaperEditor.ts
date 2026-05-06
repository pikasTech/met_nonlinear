import fs from 'fs';
import path from 'path';
import { loadPaperEditorDocument, type PaperEditorAsset, type PaperEditorDocument } from './paperEditor.js';
import { buildSourceViewLineMappings, type SourceViewLineMappings } from './sourceViewLineMapping.js';

type OutputFormat = 'markdown' | 'html' | 'mapping' | 'diagnostic';

interface ParsedArgs {
  rootDir: string;
  entry: string;
  output: string;
  format: OutputFormat;
  wrapColumns: number | null;
  latexLines: number[];
  viewLines: number[];
  markdownLines: number[];
  htmlLines: number[];
  outlineTitles: string[];
}

interface HtmlBlockSummary {
  htmlBlockIndex: number;
  kind: string;
  htmlStartLine: number;
  htmlEndLine: number;
  markdownStartLine: number;
  markdownEndLine: number;
  latexStartLine: number;
  latexEndLine: number;
  snippet: string | null;
}

interface LatexLineChain {
  requestedLatexLine: number;
  exists: boolean;
  latexLine: number | null;
  latexText: string | null;
  viewLineStart: number | null;
  viewLineEnd: number | null;
  markdownLine: number | null;
  markdownText: string | null;
  markdownBackLatexLine: number | null;
  markdownBackDelta: number | null;
  htmlLine: number | null;
  htmlBackLatexLine: number | null;
  htmlBackDelta: number | null;
  htmlBlock: HtmlBlockSummary | null;
}

interface ViewLineChain {
  requestedViewLine: number;
  exists: boolean;
  viewLine: number | null;
  latexLine: number | null;
  latexText: string | null;
  viewLineStart: number | null;
  viewLineEnd: number | null;
  markdownLine: number | null;
  markdownText: string | null;
  markdownBackLatexLine: number | null;
  htmlLine: number | null;
  htmlBackLatexLine: number | null;
  htmlBlock: HtmlBlockSummary | null;
}

interface MarkdownLineChain {
  requestedMarkdownLine: number;
  exists: boolean;
  markdownLine: number | null;
  markdownText: string | null;
  latexLine: number | null;
  latexText: string | null;
  viewLineStart: number | null;
  viewLineEnd: number | null;
  htmlLine: number | null;
  htmlBackMarkdownLine: number | null;
  htmlBackLatexLine: number | null;
  htmlBlock: HtmlBlockSummary | null;
}

interface HtmlLineChain {
  requestedHtmlLine: number;
  exists: boolean;
  htmlLine: number | null;
  markdownLine: number | null;
  markdownText: string | null;
  latexLine: number | null;
  latexText: string | null;
  viewLineStart: number | null;
  viewLineEnd: number | null;
  htmlBlock: HtmlBlockSummary | null;
}

interface OutlineTitleChain {
  query: string;
  matchedTitle: string | null;
  matchedLevel: number | null;
  latexLine: number | null;
  latexText: string | null;
  viewLineStart: number | null;
  viewLineEnd: number | null;
  markdownLine: number | null;
  markdownText: string | null;
  htmlLine: number | null;
  htmlBlock: HtmlBlockSummary | null;
}

function ensureInside(rootDir: string, candidate: string): string {
  const normalizedRoot = path.resolve(rootDir);
  const normalizedCandidate = path.resolve(candidate);
  if (normalizedCandidate !== normalizedRoot && !normalizedCandidate.startsWith(normalizedRoot + path.sep)) {
    throw new Error(`Path escapes workspace root: ${candidate}`);
  }
  return normalizedCandidate;
}

function toPosix(filePath: string): string {
  return filePath.replace(/\\/g, '/');
}

function normalizeIntegerList(values: number[]): number[] {
  return Array.from(new Set(values.filter((value) => Number.isFinite(value) && value > 0)));
}

function consumeIntegerArgs(argv: string[], startIndex: number): { values: number[]; nextIndex: number } {
  const values: number[] = [];
  let cursor = startIndex;
  while (cursor < argv.length && !argv[cursor].startsWith('--')) {
    const parsed = Number.parseInt(argv[cursor] ?? '', 10);
    if (Number.isFinite(parsed) && parsed > 0) {
      values.push(parsed);
    }
    cursor += 1;
  }
  return {
    values: normalizeIntegerList(values),
    nextIndex: cursor - 1,
  };
}

function parseArgs(argv: string[]): ParsedArgs {
  let rootDir = process.cwd();
  let entry = 'main.tex';
  let output = path.join('cache', 'webui', 'paper-editor', 'main.preview.md');
  let format: OutputFormat = 'markdown';
  let wrapColumns: number | null = null;
  let latexLines: number[] = [];
  let viewLines: number[] = [];
  let markdownLines: number[] = [];
  let htmlLines: number[] = [];
  const outlineTitles: string[] = [];

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--root' && argv[index + 1]) {
      rootDir = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === '--entry' && argv[index + 1]) {
      entry = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === '--output' && argv[index + 1]) {
      output = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === '--format' && argv[index + 1]) {
      format = argv[index + 1] === 'html'
        ? 'html'
        : argv[index + 1] === 'mapping'
          ? 'mapping'
          : argv[index + 1] === 'diagnostic'
            ? 'diagnostic'
            : 'markdown';
      index += 1;
      continue;
    }
    if (token === '--wrap-columns' && argv[index + 1]) {
      const parsed = Number.parseInt(argv[index + 1] ?? '', 10);
      wrapColumns = Number.isFinite(parsed) && parsed > 0 ? parsed : null;
      index += 1;
      continue;
    }
    if (token === '--latex-lines') {
      const consumed = consumeIntegerArgs(argv, index + 1);
      latexLines = consumed.values;
      index = consumed.nextIndex;
      continue;
    }
    if (token === '--view-lines') {
      const consumed = consumeIntegerArgs(argv, index + 1);
      viewLines = consumed.values;
      index = consumed.nextIndex;
      continue;
    }
    if (token === '--markdown-lines') {
      const consumed = consumeIntegerArgs(argv, index + 1);
      markdownLines = consumed.values;
      index = consumed.nextIndex;
      continue;
    }
    if (token === '--html-lines') {
      const consumed = consumeIntegerArgs(argv, index + 1);
      htmlLines = consumed.values;
      index = consumed.nextIndex;
      continue;
    }
    if (token === '--outline-title' && argv[index + 1]) {
      outlineTitles.push(argv[index + 1]);
      index += 1;
      continue;
    }
  }

  return {
    rootDir: path.resolve(rootDir),
    entry,
    output,
    format,
    wrapColumns,
    latexLines,
    viewLines,
    markdownLines,
    htmlLines,
    outlineTitles,
  };
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function rewriteAssetUrls(content: string, assets: PaperEditorAsset[], rootDir: string, outputPath: string): string {
  const outputDir = path.dirname(path.resolve(rootDir, outputPath));
  let rewritten = content;

  for (const asset of assets) {
    const relativePath = toPosix(path.relative(outputDir, path.resolve(rootDir, asset.resolvedPath)));
    const escapedUrl = asset.url.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    rewritten = rewritten.replace(new RegExp(escapedUrl, 'g'), relativePath || './');
  }

  return rewritten;
}

function buildHtmlShell(bodyHtml: string, title: string): string {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${escapeHtml(title)}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css" />
    <style>
      :root {
        color-scheme: light;
        font-family: "Segoe UI", "PingFang SC", sans-serif;
      }
      body {
        margin: 0;
        background: #d5dbe1;
        color: #1f252b;
      }
      main {
        max-width: 1120px;
        margin: 0 auto;
        padding: 20px;
      }
      .paper-editor-export {
        border: 1px solid rgba(32, 38, 44, 0.2);
        background: #eef2f5;
        padding: 16px;
      }
      .paper-editor-export h1,
      .paper-editor-export h2,
      .paper-editor-export h3,
      .paper-editor-export h4,
      .paper-editor-export h5,
      .paper-editor-export h6 {
        font-family: Consolas, "Courier New", monospace;
        line-height: 1.15;
      }
      .paper-editor-export p,
      .paper-editor-export li,
      .paper-editor-export blockquote,
      .paper-editor-export td,
      .paper-editor-export th {
        line-height: 1.5;
      }
      .paper-editor-export table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        background: #f8fafb;
      }
      .paper-editor-export th,
      .paper-editor-export td {
        padding: 6px 8px;
        border: 1px solid rgba(32, 38, 44, 0.18);
        vertical-align: top;
      }
      .paper-editor-preview__figure {
        display: grid;
        gap: 6px;
        margin: 12px 0;
      }
      .paper-editor-preview__figure img {
        max-width: 100%;
        border: 1px solid rgba(32, 38, 44, 0.18);
        background: #fff;
      }
      .paper-editor-preview__figure figcaption {
        color: #596673;
        font-size: 12px;
      }
      .paper-editor-preview__missing-asset {
        display: grid;
        gap: 4px;
        padding: 10px;
        border: 1px dashed rgba(73, 84, 96, 0.4);
        background: rgba(188, 197, 205, 0.28);
      }
      .paper-editor-preview__missing-asset strong {
        text-transform: uppercase;
        font-size: 12px;
      }
      .paper-editor-preview__missing-asset span {
        font-family: Consolas, "Courier New", monospace;
        font-size: 12px;
        word-break: break-all;
      }
      code,
      pre {
        font-family: Consolas, "Courier New", monospace;
      }
      pre {
        overflow-x: auto;
      }
    </style>
  </head>
  <body>
    <main>
      <article class="paper-editor-export">
${bodyHtml}
      </article>
    </main>
  </body>
</html>
`;
}

function writeFile(rootDir: string, outputPath: string, content: string): string {
  const resolvedOutput = ensureInside(rootDir, path.resolve(rootDir, outputPath));
  fs.mkdirSync(path.dirname(resolvedOutput), { recursive: true });
  fs.writeFileSync(resolvedOutput, content, 'utf-8');
  return resolvedOutput;
}

function splitLines(text: string): string[] {
  return text.split(/\r?\n/);
}

function summarizeText(value: string | null, maxLength = 220): string | null {
  if (!value) {
    return null;
  }
  const collapsed = value.replace(/\s+/g, ' ').trim();
  if (!collapsed) {
    return null;
  }
  return collapsed.length <= maxLength ? collapsed : `${collapsed.slice(0, maxLength - 1)}…`;
}

function decodeHtmlEntities(text: string): string {
  return text
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function stripHtmlTags(text: string): string {
  return decodeHtmlEntities(text.replace(/<[^>]+>/g, ' '));
}

function getLineText(lines: string[], lineNumber: number | null): string | null {
  if (!lineNumber || lineNumber < 1 || lineNumber > lines.length) {
    return null;
  }
  return lines[lineNumber - 1] ?? null;
}

function isMonotonic(values: number[]): boolean {
  for (let index = 2; index < values.length; index += 1) {
    if (values[index] < values[index - 1]) {
      return false;
    }
  }
  return true;
}

function findHtmlBlock(
  blocks: PaperEditorDocument['lineMappings']['htmlBlocks'],
  htmlLine: number | null,
): PaperEditorDocument['lineMappings']['htmlBlocks'][number] | null {
  if (!htmlLine) {
    return null;
  }
  return blocks.find((block) => htmlLine >= block.htmlStartLine && htmlLine <= block.htmlEndLine) ?? null;
}

function buildHtmlBlockSummary(
  htmlLines: string[],
  blocks: PaperEditorDocument['lineMappings']['htmlBlocks'],
  htmlLine: number | null,
): HtmlBlockSummary | null {
  const block = findHtmlBlock(blocks, htmlLine);
  if (!block) {
    return null;
  }
  const snippet = summarizeText(
    stripHtmlTags(htmlLines.slice(block.htmlStartLine - 1, block.htmlEndLine).join(' ')),
  );
  return {
    htmlBlockIndex: block.htmlBlockIndex,
    kind: block.kind,
    htmlStartLine: block.htmlStartLine,
    htmlEndLine: block.htmlEndLine,
    markdownStartLine: block.markdownStartLine,
    markdownEndLine: block.markdownEndLine,
    latexStartLine: block.latexStartLine,
    latexEndLine: block.latexEndLine,
    snippet,
  };
}

function buildLatexLineChain(
  document: PaperEditorDocument,
  wrapMappings: SourceViewLineMappings | null,
  latexLines: string[],
  markdownLines: string[],
  htmlLines: string[],
  requestedLatexLine: number,
): LatexLineChain {
  if (requestedLatexLine < 1 || requestedLatexLine > latexLines.length) {
    return {
      requestedLatexLine,
      exists: false,
      latexLine: null,
      latexText: null,
      viewLineStart: null,
      viewLineEnd: null,
      markdownLine: null,
      markdownText: null,
      markdownBackLatexLine: null,
      markdownBackDelta: null,
      htmlLine: null,
      htmlBackLatexLine: null,
      htmlBackDelta: null,
      htmlBlock: null,
    };
  }

  const markdownLine = document.lineMappings.latexToMarkdown[requestedLatexLine] ?? null;
  const htmlLine = document.lineMappings.latexToHtml[requestedLatexLine] ?? null;
  const markdownBackLatexLine = markdownLine ? (document.lineMappings.markdownToLatex[markdownLine] ?? null) : null;
  const htmlBackLatexLine = htmlLine ? (document.lineMappings.htmlToLatex[htmlLine] ?? null) : null;

  return {
    requestedLatexLine,
    exists: true,
    latexLine: requestedLatexLine,
    latexText: summarizeText(getLineText(latexLines, requestedLatexLine)),
    viewLineStart: wrapMappings?.latexToViewLineStart[requestedLatexLine] ?? null,
    viewLineEnd: wrapMappings?.latexToViewLineEnd[requestedLatexLine] ?? null,
    markdownLine,
    markdownText: summarizeText(getLineText(markdownLines, markdownLine)),
    markdownBackLatexLine,
    markdownBackDelta: markdownBackLatexLine == null ? null : markdownBackLatexLine - requestedLatexLine,
    htmlLine,
    htmlBackLatexLine,
    htmlBackDelta: htmlBackLatexLine == null ? null : htmlBackLatexLine - requestedLatexLine,
    htmlBlock: buildHtmlBlockSummary(htmlLines, document.lineMappings.htmlBlocks, htmlLine),
  };
}

function buildViewLineChain(
  document: PaperEditorDocument,
  wrapMappings: SourceViewLineMappings | null,
  latexLines: string[],
  markdownLines: string[],
  htmlLines: string[],
  requestedViewLine: number,
): ViewLineChain {
  if (!wrapMappings || requestedViewLine < 1 || requestedViewLine > wrapMappings.totalViewLines) {
    return {
      requestedViewLine,
      exists: false,
      viewLine: null,
      latexLine: null,
      latexText: null,
      viewLineStart: null,
      viewLineEnd: null,
      markdownLine: null,
      markdownText: null,
      markdownBackLatexLine: null,
      htmlLine: null,
      htmlBackLatexLine: null,
      htmlBlock: null,
    };
  }

  const latexLine = wrapMappings.viewLineToLatex[requestedViewLine] ?? null;
  const latexChain = latexLine
    ? buildLatexLineChain(document, wrapMappings, latexLines, markdownLines, htmlLines, latexLine)
    : null;

  return {
    requestedViewLine,
    exists: latexChain?.exists ?? false,
    viewLine: requestedViewLine,
    latexLine: latexChain?.latexLine ?? null,
    latexText: latexChain?.latexText ?? null,
    viewLineStart: latexChain?.viewLineStart ?? null,
    viewLineEnd: latexChain?.viewLineEnd ?? null,
    markdownLine: latexChain?.markdownLine ?? null,
    markdownText: latexChain?.markdownText ?? null,
    markdownBackLatexLine: latexChain?.markdownBackLatexLine ?? null,
    htmlLine: latexChain?.htmlLine ?? null,
    htmlBackLatexLine: latexChain?.htmlBackLatexLine ?? null,
    htmlBlock: latexChain?.htmlBlock ?? null,
  };
}

function buildMarkdownLineChain(
  document: PaperEditorDocument,
  wrapMappings: SourceViewLineMappings | null,
  latexLines: string[],
  markdownLines: string[],
  htmlLines: string[],
  requestedMarkdownLine: number,
): MarkdownLineChain {
  if (requestedMarkdownLine < 1 || requestedMarkdownLine > markdownLines.length) {
    return {
      requestedMarkdownLine,
      exists: false,
      markdownLine: null,
      markdownText: null,
      latexLine: null,
      latexText: null,
      viewLineStart: null,
      viewLineEnd: null,
      htmlLine: null,
      htmlBackMarkdownLine: null,
      htmlBackLatexLine: null,
      htmlBlock: null,
    };
  }

  const latexLine = document.lineMappings.markdownToLatex[requestedMarkdownLine] ?? null;
  const htmlLine = document.lineMappings.markdownToHtml[requestedMarkdownLine] ?? null;
  return {
    requestedMarkdownLine,
    exists: true,
    markdownLine: requestedMarkdownLine,
    markdownText: summarizeText(getLineText(markdownLines, requestedMarkdownLine)),
    latexLine,
    latexText: summarizeText(getLineText(latexLines, latexLine)),
    viewLineStart: latexLine ? (wrapMappings?.latexToViewLineStart[latexLine] ?? null) : null,
    viewLineEnd: latexLine ? (wrapMappings?.latexToViewLineEnd[latexLine] ?? null) : null,
    htmlLine,
    htmlBackMarkdownLine: htmlLine ? (document.lineMappings.htmlToMarkdown[htmlLine] ?? null) : null,
    htmlBackLatexLine: htmlLine ? (document.lineMappings.htmlToLatex[htmlLine] ?? null) : null,
    htmlBlock: buildHtmlBlockSummary(htmlLines, document.lineMappings.htmlBlocks, htmlLine),
  };
}

function buildHtmlLineChain(
  document: PaperEditorDocument,
  wrapMappings: SourceViewLineMappings | null,
  latexLines: string[],
  markdownLines: string[],
  htmlLines: string[],
  requestedHtmlLine: number,
): HtmlLineChain {
  if (requestedHtmlLine < 1 || requestedHtmlLine > htmlLines.length) {
    return {
      requestedHtmlLine,
      exists: false,
      htmlLine: null,
      markdownLine: null,
      markdownText: null,
      latexLine: null,
      latexText: null,
      viewLineStart: null,
      viewLineEnd: null,
      htmlBlock: null,
    };
  }

  const markdownLine = document.lineMappings.htmlToMarkdown[requestedHtmlLine] ?? null;
  const latexLine = document.lineMappings.htmlToLatex[requestedHtmlLine] ?? null;
  return {
    requestedHtmlLine,
    exists: true,
    htmlLine: requestedHtmlLine,
    markdownLine,
    markdownText: summarizeText(getLineText(markdownLines, markdownLine)),
    latexLine,
    latexText: summarizeText(getLineText(latexLines, latexLine)),
    viewLineStart: latexLine ? (wrapMappings?.latexToViewLineStart[latexLine] ?? null) : null,
    viewLineEnd: latexLine ? (wrapMappings?.latexToViewLineEnd[latexLine] ?? null) : null,
    htmlBlock: buildHtmlBlockSummary(htmlLines, document.lineMappings.htmlBlocks, requestedHtmlLine),
  };
}

function buildOutlineTitleChain(
  document: PaperEditorDocument,
  wrapMappings: SourceViewLineMappings | null,
  latexLines: string[],
  markdownLines: string[],
  htmlLines: string[],
  query: string,
): OutlineTitleChain {
  const normalized = query.trim().toLowerCase();
  const matched = document.outline.find((item) => item.title.toLowerCase() === normalized)
    ?? document.outline.find((item) => item.title.toLowerCase().includes(normalized));
  if (!matched) {
    return {
      query,
      matchedTitle: null,
      matchedLevel: null,
      latexLine: null,
      latexText: null,
      viewLineStart: null,
      viewLineEnd: null,
      markdownLine: null,
      markdownText: null,
      htmlLine: null,
      htmlBlock: null,
    };
  }

  return {
    query,
    matchedTitle: matched.title,
    matchedLevel: matched.level,
    latexLine: matched.line,
    latexText: summarizeText(getLineText(latexLines, matched.line)),
    viewLineStart: wrapMappings?.latexToViewLineStart[matched.line] ?? null,
    viewLineEnd: wrapMappings?.latexToViewLineEnd[matched.line] ?? null,
    markdownLine: matched.markdownLine ?? (document.lineMappings.latexToMarkdown[matched.line] ?? null),
    markdownText: summarizeText(getLineText(markdownLines, matched.markdownLine ?? (document.lineMappings.latexToMarkdown[matched.line] ?? null))),
    htmlLine: matched.htmlLine ?? (document.lineMappings.latexToHtml[matched.line] ?? null),
    htmlBlock: buildHtmlBlockSummary(
      htmlLines,
      document.lineMappings.htmlBlocks,
      matched.htmlLine ?? (document.lineMappings.latexToHtml[matched.line] ?? null),
    ),
  };
}

function exportMarkdown(args: ParsedArgs) {
  const document = loadPaperEditorDocument(args.rootDir, args.entry);
  const resolvedOutput = writeFile(args.rootDir, args.output, document.markdown);
  return { document, resolvedOutput };
}

function exportHtml(args: ParsedArgs) {
  const document = loadPaperEditorDocument(args.rootDir, args.entry);
  const bodyHtml = rewriteAssetUrls(document.html, document.assets, args.rootDir, args.output);
  const title = document.entry ? `Paper Editor Preview - ${document.entry}` : 'Paper Editor Preview';
  const html = buildHtmlShell(bodyHtml, title);
  const resolvedOutput = writeFile(args.rootDir, args.output, html);
  return { document, resolvedOutput };
}

function exportMapping(args: ParsedArgs) {
  const document = loadPaperEditorDocument(args.rootDir, args.entry);
  const wrapMappings = args.wrapColumns
    ? buildSourceViewLineMappings(document.source, args.wrapColumns)
    : null;
  const payload = JSON.stringify(
    {
      entry: document.entry,
      updatedAt: document.updatedAt,
      outline: document.outline,
      lineMappings: document.lineMappings,
      wrapMappings,
      performance: document.performance,
    },
    null,
    2,
  );
  const resolvedOutput = writeFile(args.rootDir, args.output, payload);
  return { document, resolvedOutput };
}

function exportDiagnostic(args: ParsedArgs) {
  const document = loadPaperEditorDocument(args.rootDir, args.entry);
  const wrapMappings = args.wrapColumns
    ? buildSourceViewLineMappings(document.source, args.wrapColumns)
    : null;

  if (args.viewLines.length > 0 && !wrapMappings) {
    throw new Error('Diagnosing view lines requires --wrap-columns so the backend can build a wrapped source view');
  }

  const latexLines = splitLines(document.source);
  const markdownLines = splitLines(document.markdown);
  const htmlLines = splitLines(document.html);
  const payload = JSON.stringify(
    {
      entry: document.entry,
      updatedAt: document.updatedAt,
      performance: document.performance,
      chainDiagnostics: {
        wrapColumns: wrapMappings?.columns ?? null,
        lineCounts: {
          latex: latexLines.length,
          markdown: markdownLines.length,
          html: htmlLines.length,
          view: wrapMappings?.totalViewLines ?? null,
          outline: document.outline.length,
        },
        monotonic: {
          latexToMarkdown: isMonotonic(document.lineMappings.latexToMarkdown),
          markdownToLatex: isMonotonic(document.lineMappings.markdownToLatex),
          latexToHtml: isMonotonic(document.lineMappings.latexToHtml),
          htmlToLatex: isMonotonic(document.lineMappings.htmlToLatex),
          markdownToHtml: isMonotonic(document.lineMappings.markdownToHtml),
          htmlToMarkdown: isMonotonic(document.lineMappings.htmlToMarkdown),
          viewLineToLatex: wrapMappings ? isMonotonic(wrapMappings.viewLineToLatex) : null,
          latexToViewLineStart: wrapMappings ? isMonotonic(wrapMappings.latexToViewLineStart) : null,
          latexToViewLineEnd: wrapMappings ? isMonotonic(wrapMappings.latexToViewLineEnd) : null,
        },
      },
      latexLineChains: args.latexLines.map((latexLine) => buildLatexLineChain(document, wrapMappings, latexLines, markdownLines, htmlLines, latexLine)),
      viewLineChains: args.viewLines.map((viewLine) => buildViewLineChain(document, wrapMappings, latexLines, markdownLines, htmlLines, viewLine)),
      markdownLineChains: args.markdownLines.map((markdownLine) => buildMarkdownLineChain(document, wrapMappings, latexLines, markdownLines, htmlLines, markdownLine)),
      htmlLineChains: args.htmlLines.map((htmlLine) => buildHtmlLineChain(document, wrapMappings, latexLines, markdownLines, htmlLines, htmlLine)),
      outlineTitleChains: args.outlineTitles.map((title) => buildOutlineTitleChain(document, wrapMappings, latexLines, markdownLines, htmlLines, title)),
    },
    null,
    2,
  );
  const resolvedOutput = writeFile(args.rootDir, args.output, payload);
  return { document, resolvedOutput };
}

const args = parseArgs(process.argv.slice(2));
const result = args.format === 'html'
  ? exportHtml(args)
  : args.format === 'mapping'
    ? exportMapping(args)
    : args.format === 'diagnostic'
      ? exportDiagnostic(args)
      : exportMarkdown(args);

console.log(
  JSON.stringify(
    {
      status: 'ok',
      entry: result.document.entry,
      format: args.format,
      output: result.resolvedOutput,
      markdownBytes: result.document.performance.markdownBytes,
      diagnostics: result.document.diagnostics,
    },
    null,
    2,
  ),
);
