import fs from 'fs';
import { createHash } from 'node:crypto';
import { performance } from 'node:perf_hooks';
import path from 'path';
import { applyPatch, createPatch } from 'diff';
import {
  buildApproximateLineMap,
  renderPaperEditorHtml,
  type PaperEditorHtmlBlock,
  type PaperEditorLineMappings,
} from './paperEditorRender.js';
import { buildWrappedSourceView, type WrappedSourceView } from './sourceViewLineMapping.js';

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

export interface PaperEditorDocument {
  entry: string;
  source: string;
  sourceView: WrappedSourceView;
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

export interface PaperEditorSaveDiffSummary {
  kind: 'no-op' | 'line-range';
  oldRange: [number, number] | null;
  newRange: [number, number] | null;
  removedLineCount: number;
  addedLineCount: number;
  beforePreview: string[];
  afterPreview: string[];
}

export interface PaperEditorSaveAudit {
  changed: boolean;
  patchAppliedToStaleRevision: boolean;
  baseRevision: string | null;
  currentRevisionBeforeSave: string;
  previousSourceHash: string;
  nextSourceHash: string;
  previousBytes: number;
  nextBytes: number;
  diffSummary: PaperEditorSaveDiffSummary;
  requestedDiffSummary: PaperEditorSaveDiffSummary;
  viewDiffSummary: PaperEditorSaveDiffSummary;
}

export interface PaperEditorSaveResult {
  document: PaperEditorDocument;
  audit: PaperEditorSaveAudit;
}

export interface PaperEditorSaveInput {
  entry?: string;
  source?: string;
  sourceViewText?: string;
  baseSource?: string;
  baseSourceViewText?: string;
  baseRevision?: string | null;
  sourceViewColumns?: number;
}

export class PaperEditorSaveConflictError extends Error {
  currentRevision: string;
  updatedAt: string | null;

  constructor(message: string, currentRevision: string, updatedAt: string | null) {
    super(message);
    this.name = 'PaperEditorSaveConflictError';
    this.currentRevision = currentRevision;
    this.updatedAt = updatedAt;
  }
}

interface MacroDefinition {
  name: string;
  arity: number;
  body: string;
}

interface BuildContext {
  rootDir: string;
  latexRoot: string;
  macros: Map<string, MacroDefinition>;
  imports: Set<string>;
  diagnostics: string[];
  visited: Set<string>;
  overrides: Map<string, string>;
}

const DEFAULT_ENTRY = 'main.tex';
const DEFAULT_SOURCE_VIEW_COLUMNS = 80;
const SECTION_LEVELS: Record<string, number> = {
  section: 1,
  subsection: 2,
  subsubsection: 3,
  paragraph: 4,
};

const TEXT_COMMANDS = ['textbf', 'textit', 'emph', 'underline', 'texttt'];

function toPosix(filePath: string): string {
  return filePath.replace(/\\/g, '/');
}

function countLinesBefore(text: string, index: number): number {
  return text.slice(0, index).split(/\r?\n/).length;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '') || 'section';
}

function ensureInside(rootDir: string, candidate: string): string {
  const normalizedRoot = path.resolve(rootDir);
  const normalizedCandidate = path.resolve(candidate);
  if (normalizedCandidate !== normalizedRoot && !normalizedCandidate.startsWith(normalizedRoot + path.sep)) {
    throw new Error(`Path escapes workspace root: ${candidate}`);
  }
  return normalizedCandidate;
}

function stripComments(source: string): string {
  return source
    .split(/\r?\n/)
    .map((line) => {
      let escaped = false;
      for (let index = 0; index < line.length; index += 1) {
        const char = line[index];
        if (char === '\\') {
          escaped = !escaped;
          continue;
        }
        if (char === '%' && !escaped) {
          return line.slice(0, index);
        }
        escaped = false;
      }
      return line;
    })
    .join('\n');
}

function hashSourceSnapshot(source: string): string {
  return createHash('sha256').update(source).digest('hex').slice(0, 16);
}

function clipPreviewLine(line: string, maxLength = 120): string {
  return line.length > maxLength ? `${line.slice(0, maxLength - 1)}…` : line;
}

function toLineRange(start: number, count: number): [number, number] | null {
  if (count <= 0) {
    return null;
  }
  return [start, start + count - 1];
}

function buildSaveDiffSummary(previousSource: string, nextSource: string): PaperEditorSaveDiffSummary {
  if (previousSource === nextSource) {
    return {
      kind: 'no-op',
      oldRange: null,
      newRange: null,
      removedLineCount: 0,
      addedLineCount: 0,
      beforePreview: [],
      afterPreview: [],
    };
  }

  const previousLines = previousSource.split(/\r?\n/);
  const nextLines = nextSource.split(/\r?\n/);
  const sharedPrefix = Math.min(previousLines.length, nextLines.length);
  let prefixCount = 0;
  while (prefixCount < sharedPrefix && previousLines[prefixCount] === nextLines[prefixCount]) {
    prefixCount += 1;
  }

  const remainingPrevious = previousLines.length - prefixCount;
  const remainingNext = nextLines.length - prefixCount;
  const maxSuffix = Math.min(remainingPrevious, remainingNext);
  let suffixCount = 0;
  while (
    suffixCount < maxSuffix
    && previousLines[previousLines.length - 1 - suffixCount] === nextLines[nextLines.length - 1 - suffixCount]
  ) {
    suffixCount += 1;
  }

  const removedLineCount = Math.max(0, previousLines.length - prefixCount - suffixCount);
  const addedLineCount = Math.max(0, nextLines.length - prefixCount - suffixCount);
  const changedPreviousLines = previousLines.slice(prefixCount, previousLines.length - suffixCount);
  const changedNextLines = nextLines.slice(prefixCount, nextLines.length - suffixCount);

  return {
    kind: 'line-range',
    oldRange: toLineRange(prefixCount + 1, removedLineCount),
    newRange: toLineRange(prefixCount + 1, addedLineCount),
    removedLineCount,
    addedLineCount,
    beforePreview: changedPreviousLines.slice(0, 3).map((line) => clipPreviewLine(line)),
    afterPreview: changedNextLines.slice(0, 3).map((line) => clipPreviewLine(line)),
  };
}

function buildSaveAudit(
  previousSource: string,
  nextSource: string,
  requestedSource: string,
  baseSource: string,
  baseSourceViewText: string,
  nextSourceViewText: string,
  baseRevision: string | null,
  currentRevisionBeforeSave: string,
): PaperEditorSaveAudit {
  return {
    changed: previousSource !== nextSource,
    patchAppliedToStaleRevision: Boolean(baseRevision) && baseRevision !== currentRevisionBeforeSave,
    baseRevision,
    currentRevisionBeforeSave,
    previousSourceHash: hashSourceSnapshot(previousSource),
    nextSourceHash: hashSourceSnapshot(nextSource),
    previousBytes: Buffer.byteLength(previousSource, 'utf-8'),
    nextBytes: Buffer.byteLength(nextSource, 'utf-8'),
    diffSummary: buildSaveDiffSummary(previousSource, nextSource),
    requestedDiffSummary: buildSaveDiffSummary(baseSource, requestedSource),
    viewDiffSummary: buildSaveDiffSummary(baseSourceViewText, nextSourceViewText),
  };
}

function normalizePaperEditorLineEndings(source: string): string {
  return source.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

function detectPaperEditorLineEnding(source: string): '\r\n' | '\n' {
  return source.includes('\r\n') ? '\r\n' : '\n';
}

function applyPaperEditorLineEnding(source: string, lineEnding: '\r\n' | '\n'): string {
  if (lineEnding === '\n') {
    return source;
  }
  return source.replace(/\n/g, '\r\n');
}

function getRevisionStateForEntry(rootDir: string, entryFile: string): { revision: string; updatedAt: string | null } {
  const latexRoot = path.join(rootDir, 'docs', 'paper', 'latex');
  const ctx = buildContext(rootDir, latexRoot, new Map<string, string>());
  visitDependencies(entryFile, ctx);
  return buildDocumentRevision(latexRoot, ctx.visited);
}

function readDelimited(text: string, start: number, open: string, close: string): { value: string; end: number } | null {
  if (text[start] !== open) {
    return null;
  }
  let depth = 0;
  let value = '';
  for (let index = start; index < text.length; index += 1) {
    const char = text[index];
    if (char === open) {
      depth += 1;
      if (depth > 1) {
        value += char;
      }
      continue;
    }
    if (char === close) {
      depth -= 1;
      if (depth === 0) {
        return { value, end: index + 1 };
      }
      value += char;
      continue;
    }
    value += char;
  }
  return null;
}

function skipWhitespace(text: string, start: number): number {
  let index = start;
  while (index < text.length && /\s/.test(text[index])) {
    index += 1;
  }
  return index;
}

function resolveLatexFile(latexRoot: string, currentFile: string, request: string): string | null {
  const trimmed = request.trim();
  if (!trimmed) {
    return null;
  }
  const base = trimmed.endsWith('.tex') ? trimmed : `${trimmed}.tex`;
  const resolved = ensureInside(latexRoot, path.resolve(path.dirname(currentFile), base));
  if (fs.existsSync(resolved)) {
    return resolved;
  }
  return null;
}

function resolveWorkspaceAsset(rootDir: string, currentFile: string, request: string): string | null {
  const trimmed = request.trim();
  if (!trimmed) {
    return null;
  }
  const resolved = ensureInside(rootDir, path.resolve(path.dirname(currentFile), trimmed));
  return fs.existsSync(resolved) ? resolved : null;
}

function readSource(filePath: string, overrides: Map<string, string>): string {
  if (overrides.has(filePath)) {
    return overrides.get(filePath) ?? '';
  }
  return fs.readFileSync(filePath, 'utf-8');
}

function collectMacros(source: string, currentFile: string, ctx: BuildContext): void {
  const cleanSource = stripComments(source);
  const commandPattern = /\\(?:newcommand|renewcommand|providecommand)/g;
  for (const match of cleanSource.matchAll(commandPattern)) {
    let cursor = (match.index ?? 0) + match[0].length;
    cursor = skipWhitespace(cleanSource, cursor);
    let name = '';
    if (cleanSource[cursor] === '{') {
      const nameGroup = readDelimited(cleanSource, cursor, '{', '}');
      if (!nameGroup) {
        continue;
      }
      name = nameGroup.value.trim();
      cursor = nameGroup.end;
    } else if (cleanSource[cursor] === '\\') {
      const nameMatch = cleanSource.slice(cursor).match(/^\\[A-Za-z@]+/);
      if (!nameMatch) {
        continue;
      }
      name = nameMatch[0];
      cursor += nameMatch[0].length;
    } else {
      continue;
    }

    cursor = skipWhitespace(cleanSource, cursor);
    let arity = 0;
    if (cleanSource[cursor] === '[') {
      const arityGroup = readDelimited(cleanSource, cursor, '[', ']');
      if (arityGroup) {
        arity = Number.parseInt(arityGroup.value.trim(), 10) || 0;
        cursor = arityGroup.end;
      }
    }

    cursor = skipWhitespace(cleanSource, cursor);
    if (cleanSource[cursor] === '[') {
      const defaultArg = readDelimited(cleanSource, cursor, '[', ']');
      if (defaultArg) {
        cursor = defaultArg.end;
      }
    }

    cursor = skipWhitespace(cleanSource, cursor);
    const bodyGroup = readDelimited(cleanSource, cursor, '{', '}');
    if (!bodyGroup || !name.startsWith('\\')) {
      continue;
    }

    const macroName = name.slice(1);
    ctx.macros.set(macroName, {
      name: macroName,
      arity,
      body: bodyGroup.value,
    });
  }
}

function visitDependencies(filePath: string, ctx: BuildContext): void {
  if (ctx.visited.has(filePath)) {
    return;
  }
  ctx.visited.add(filePath);

  const source = readSource(filePath, ctx.overrides);
  collectMacros(source, filePath, ctx);
  const cleanSource = stripComments(source);

  for (const match of cleanSource.matchAll(/\\(?:input|include)\{([^}]+)\}/g)) {
    const request = match[1]?.trim() ?? '';
    const resolved = resolveLatexFile(ctx.latexRoot, filePath, request);
    if (!resolved) {
      ctx.diagnostics.push(`Missing import: ${request} (from ${path.basename(filePath)})`);
      continue;
    }
    ctx.imports.add(toPosix(path.relative(ctx.latexRoot, resolved)));
    visitDependencies(resolved, ctx);
  }

  for (const match of cleanSource.matchAll(/\\InputIfFileExists\{([^}]+)\}\{([\s\S]*?)\}\{([\s\S]*?)\}/g)) {
    const request = match[1]?.trim() ?? '';
    const resolved = resolveLatexFile(ctx.latexRoot, filePath, request);
    if (!resolved) {
      continue;
    }
    ctx.imports.add(toPosix(path.relative(ctx.latexRoot, resolved)));
    visitDependencies(resolved, ctx);
  }
}

function extractCommandBody(source: string, command: string, hasOptionalHead = false): string | null {
  const index = source.indexOf(command);
  if (index < 0) {
    return null;
  }
  let cursor = skipWhitespace(source, index + command.length);
  if (hasOptionalHead && source[cursor] === '[') {
    const head = readDelimited(source, cursor, '[', ']');
    if (head) {
      cursor = skipWhitespace(source, head.end);
    }
  }
  const body = readDelimited(source, cursor, '{', '}');
  return body?.value ?? null;
}

function replaceSingleArgMacros(text: string, macros: MacroDefinition[]): string {
  let output = text;
  for (const macro of macros) {
    const token = `\\${macro.name}`;
    let cursor = 0;
    let rebuilt = '';
    while (cursor < output.length) {
      const next = output.indexOf(token, cursor);
      if (next < 0) {
        rebuilt += output.slice(cursor);
        break;
      }

      const tail = output[next + token.length] ?? '';
      if (/[A-Za-z]/.test(tail)) {
        rebuilt += output.slice(cursor, next + token.length);
        cursor = next + token.length;
        continue;
      }

      let argStart = skipWhitespace(output, next + token.length);
      const argGroup = readDelimited(output, argStart, '{', '}');
      if (!argGroup) {
        rebuilt += output.slice(cursor, next + token.length);
        cursor = next + token.length;
        continue;
      }

      rebuilt += output.slice(cursor, next);
      rebuilt += macro.body.replace(/#1/g, argGroup.value);
      cursor = argGroup.end;
    }
    output = rebuilt;
  }
  return output;
}

function expandMacros(text: string, ctx: BuildContext): string {
  let output = text;
  const zeroArg = Array.from(ctx.macros.values()).filter((macro) => macro.arity === 0);
  const oneArg = Array.from(ctx.macros.values()).filter((macro) => macro.arity === 1);

  for (let pass = 0; pass < 4; pass += 1) {
    const before = output;
    output = replaceSingleArgMacros(output, oneArg);
    for (const macro of zeroArg) {
      output = output.replace(new RegExp(`\\\\${macro.name}(?![A-Za-z])`, 'g'), macro.body);
    }
    if (output === before) {
      break;
    }
  }

  return output;
}

function expandBodyImports(body: string, currentFile: string, ctx: BuildContext): string {
  const cleanBody = stripComments(body);
  let output = cleanBody;

  output = output.replace(/\\InputIfFileExists\{([^}]+)\}\{([\s\S]*?)\}\{([\s\S]*?)\}/g, (_match, request, whenExists, whenMissing) => {
    const resolved = resolveLatexFile(ctx.latexRoot, currentFile, request);
    if (!resolved) {
      return whenMissing || '';
    }
    ctx.imports.add(toPosix(path.relative(ctx.latexRoot, resolved)));
    const source = readSource(resolved, ctx.overrides);
    return expandBodyImports(source, resolved, ctx) || whenExists || '';
  });

  output = output.replace(/\\(?:input|include)\{([^}]+)\}/g, (_match, request) => {
    const resolved = resolveLatexFile(ctx.latexRoot, currentFile, request);
    if (!resolved) {
      ctx.diagnostics.push(`Missing import: ${request} (from ${path.basename(currentFile)})`);
      return `\n> Missing TeX import: ${request}\n`;
    }

    ctx.imports.add(toPosix(path.relative(ctx.latexRoot, resolved)));
    const source = readSource(resolved, ctx.overrides);
    return expandBodyImports(source, resolved, ctx);
  });

  return output;
}

function extractDocumentBody(source: string): string {
  const start = source.indexOf('\\begin{document}');
  const end = source.lastIndexOf('\\end{document}');
  if (start < 0 || end < 0 || end <= start) {
    return source;
  }
  return source.slice(start + '\\begin{document}'.length, end);
}

function stripFrontMatter(body: string): string {
  const firstSectionIndex = body.search(/\\section\*?\{/);
  if (firstSectionIndex < 0) {
    return body;
  }

  const preface = body.slice(0, firstSectionIndex);
  if (!/\\(?:title|author|affil|abstract|keywords|maketitle)\b/.test(preface)) {
    return body;
  }

  return body.slice(firstSectionIndex);
}

function cleanupInlineText(text: string): string {
  return text.replace(/\{\}/g, '').replace(/~+/g, ' ').replace(/\s+/g, ' ').trim();
}

function splitLatexRows(content: string): string[] {
  const rows: string[] = [];
  let current = '';
  let braceDepth = 0;
  let bracketDepth = 0;

  for (let index = 0; index < content.length; index += 1) {
    const char = content[index];
    const next = content[index + 1] ?? '';

    if (char === '{') {
      braceDepth += 1;
      current += char;
      continue;
    }
    if (char === '}') {
      braceDepth = Math.max(0, braceDepth - 1);
      current += char;
      continue;
    }
    if (char === '[') {
      bracketDepth += 1;
      current += char;
      continue;
    }
    if (char === ']') {
      bracketDepth = Math.max(0, bracketDepth - 1);
      current += char;
      continue;
    }
    if (char === '\\' && next === '\\' && braceDepth === 0 && bracketDepth === 0) {
      if (current.trim()) {
        rows.push(current.trim());
      }
      current = '';
      index += 1;
      if (content[index + 1] === '[') {
        const optional = readDelimited(content, index + 1, '[', ']');
        if (optional) {
          index = optional.end - 1;
        }
      }
      continue;
    }
    current += char;
  }

  if (current.trim()) {
    rows.push(current.trim());
  }
  return rows;
}

function splitLatexCells(row: string): string[] {
  const cells: string[] = [];
  let current = '';
  let braceDepth = 0;
  let bracketDepth = 0;

  for (let index = 0; index < row.length; index += 1) {
    const char = row[index];
    if (char === '{') {
      braceDepth += 1;
      current += char;
      continue;
    }
    if (char === '}') {
      braceDepth = Math.max(0, braceDepth - 1);
      current += char;
      continue;
    }
    if (char === '[') {
      bracketDepth += 1;
      current += char;
      continue;
    }
    if (char === ']') {
      bracketDepth = Math.max(0, bracketDepth - 1);
      current += char;
      continue;
    }
    if (char === '&' && braceDepth === 0 && bracketDepth === 0) {
      cells.push(current.trim());
      current = '';
      continue;
    }
    current += char;
  }

  cells.push(current.trim());
  return cells;
}

function extractTabularContent(block: string): string | null {
  const beginMatch = block.match(/\\begin\{tabular\*?\}/);
  if (!beginMatch || beginMatch.index == null) {
    return null;
  }

  let cursor = beginMatch.index + beginMatch[0].length;
  cursor = skipWhitespace(block, cursor);
  if (block[cursor] === '[') {
    const optional = readDelimited(block, cursor, '[', ']');
    if (optional) {
      cursor = skipWhitespace(block, optional.end);
    }
  }

  const alignment = readDelimited(block, cursor, '{', '}');
  if (!alignment) {
    return null;
  }
  cursor = alignment.end;

  const endMatch = block.slice(cursor).match(/\\end\{tabular\*?\}/);
  if (!endMatch || endMatch.index == null) {
    return null;
  }
  return block.slice(cursor, cursor + endMatch.index);
}

function normalizeTableCellText(cell: string, ctx: BuildContext): string {
  let output = expandMacros(cell, ctx).trim();
  output = output
    .replace(/\\multicolumn\{[^}]*\}\{[^}]*\}\{([\s\S]*?)\}/g, '$1')
    .replace(/\\multirow\{[^}]*\}\{[^}]*\}\{([\s\S]*?)\}/g, '$1')
    .replace(/\\makecell(?:\[[^\]]*\])?\{([\s\S]*?)\}/g, '$1')
    .replace(/\\(?:arraystretch|tabcolsep)\b/g, '')
    .replace(/\\\(([\s\S]*?)\\\)/g, (_match, inner) => `$${inner}$`)
    .replace(/\\%/g, '%')
    .replace(/\\_/g, '_')
    .replace(/\\#/g, '#')
    .replace(/\\&/g, '&')
    .replace(/\\(?:small|footnotesize|scriptsize|normalsize|centering|raggedright|raggedleft|arraybackslash)\b/g, '')
    .replace(/\\\\/g, '<br>');
  output = transformTextCommands(output);
  output = cleanupInlineText(output).replace(/\|/g, '\\|');
  return output || ' ';
}

function buildMarkdownTable(block: string, ctx: BuildContext, captionOverride?: string): string {
  const captionMatch = block.match(/\\caption\{([\s\S]*?)\}/);
  const caption = cleanupInlineText(expandMacros(captionOverride ?? captionMatch?.[1] ?? '', ctx));
  const tabularContent = extractTabularContent(block);
  if (!tabularContent) {
    return caption ? `\nTable: ${caption}\n` : '\n';
  }

  const normalizedContent = tabularContent
    .replace(/\\(?:hline|toprule|midrule|bottomrule|hdashline|cline\{[^}]*\})\s*/g, '\n')
    .replace(/\\setlength\{[^}]+\}\{[^}]+\}/g, '')
    .replace(/\\renewcommand\{[^}]+\}\{[^}]+\}/g, '')
    .replace(/\\(?:small|footnotesize|scriptsize|normalsize|centering)\b/g, '')
    .replace(/\\begingroup|\\endgroup/g, '')
    .trim();

  const rows = splitLatexRows(normalizedContent)
    .map((row) => splitLatexCells(row).map((cell) => normalizeTableCellText(cell, ctx)))
    .filter((row) => row.length > 0 && row.some((cell) => cell.trim()));

  if (rows.length === 0) {
    return caption ? `\nTable: ${caption}\n` : '\n';
  }

  const columnCount = Math.max(...rows.map((row) => row.length), 1);
  let titleRow: string | null = null;
  if (rows[0]?.length === 1 && columnCount > 1) {
    titleRow = rows.shift()?.[0] ?? null;
  }

  const hasExplicitHeader = rows[0]?.some((cell) => /\*\*/.test(cell)) ?? false;
  const header = hasExplicitHeader
    ? rows.shift() ?? []
    : Array.from({ length: columnCount }, (_value, index) => `Column ${index + 1}`);
  const normalizedHeader = Array.from({ length: columnCount }, (_value, index) => header[index] ?? `Column ${index + 1}`);
  const normalizedRows = rows.map((row) => Array.from({ length: columnCount }, (_value, index) => row[index] ?? ' '));
  const tableLines = [
    `| ${normalizedHeader.join(' | ')} |`,
    `| ${Array.from({ length: columnCount }, () => '---').join(' | ')} |`,
    ...normalizedRows.map((row) => `| ${row.join(' | ')} |`),
  ];

  const prefix = [caption ? `Table: ${caption}` : '', titleRow ?? ''].filter(Boolean).join('\n\n');
  return `\n${prefix ? `${prefix}\n\n` : ''}${tableLines.join('\n')}\n`;
}

function buildAssetUrl(rootDir: string, resolvedPath: string): string {
  return `/api/paper-editor/asset?path=${encodeURIComponent(toPosix(path.relative(rootDir, resolvedPath)))}`;
}

function transformFigures(markdown: string, currentFile: string, ctx: BuildContext, assets: PaperEditorAsset[]): string {
  const figurePattern = /\\begin\{figure\*?\}[\s\S]*?\\end\{figure\*?\}/g;
  return markdown.replace(figurePattern, (block) => {
    const imageMatch = block.match(/\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}/);
    const captionMatch = block.match(/\\caption\{([\s\S]*?)\}/);
    const caption = cleanupInlineText(expandMacros(captionMatch?.[1]?.trim() ?? 'Figure', ctx));
    if (!imageMatch) {
      return `\n> Figure: ${caption}\n`;
    }

    const resolved = resolveWorkspaceAsset(ctx.rootDir, currentFile, imageMatch[1]);
    if (!resolved) {
      ctx.diagnostics.push(`Missing figure asset: ${imageMatch[1]}`);
      return `\n> Missing figure asset: ${imageMatch[1]}\n`;
    }

    const asset: PaperEditorAsset = {
      source: imageMatch[1],
      resolvedPath: toPosix(path.relative(ctx.rootDir, resolved)),
      url: buildAssetUrl(ctx.rootDir, resolved),
      caption,
    };
    assets.push(asset);
    return `\n![${caption}](${asset.url})\n`;
  });
}

function transformLooseImages(markdown: string, currentFile: string, ctx: BuildContext, assets: PaperEditorAsset[]): string {
  return markdown.replace(/\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}/g, (_match, request) => {
    const resolved = resolveWorkspaceAsset(ctx.rootDir, currentFile, request);
    if (!resolved) {
      return `\n> Missing figure asset: ${request}\n`;
    }
    const asset: PaperEditorAsset = {
      source: request,
      resolvedPath: toPosix(path.relative(ctx.rootDir, resolved)),
      url: buildAssetUrl(ctx.rootDir, resolved),
      caption: path.basename(request),
    };
    assets.push(asset);
    return `\n![${asset.caption}](${asset.url})\n`;
  });
}

function transformMath(markdown: string): string {
  let output = markdown;
  output = output.replace(/\\begin\{(equation\*?|align\*?|gather\*?)\}([\s\S]*?)\\end\{\1\}/g, (_m, _env, inner) => {
    return `\n$$\n${inner.trim()}\n$$\n`;
  });
  output = output.replace(/\\\[([\s\S]*?)\\\]/g, (_m, inner) => `\n$$\n${inner.trim()}\n$$\n`);
  return output;
}

function transformTables(markdown: string, ctx: BuildContext): string {
  let output = markdown.replace(/\\begin\{table\*?\}[\s\S]*?\\end\{table\*?\}/g, (block) => buildMarkdownTable(block, ctx));
  output = output.replace(/(?:\\begingroup\s*)?(?:\\renewcommand\{[^}]+\}\{[^}]+\}\s*)?\\begin\{tabular\*?\}[\s\S]*?\\end\{tabular\*?\}(?:\s*\\endgroup)?/g, (block) => buildMarkdownTable(block, ctx));
  return output;
}

function extractOutlineFromSource(source: string, ctx: BuildContext): PaperEditorOutlineItem[] {
  const cleanSource = stripComments(source);
  const counters = new Map<string, number>();
  const outline: PaperEditorOutlineItem[] = [];

  for (const match of cleanSource.matchAll(/\\(section|subsection|subsubsection|paragraph)\{([\s\S]*?)\}/g)) {
    const command = match[1] ?? 'section';
    const title = match[2] ?? '';
    const expandedTitle = expandMacros(title, ctx).replace(/\s+/g, ' ').trim();
    const normalizedTitle = cleanupInlineText(expandedTitle);
    const level = SECTION_LEVELS[command] ?? 1;
    const baseId = slugify(normalizedTitle);
    const seen = (counters.get(baseId) ?? 0) + 1;
    counters.set(baseId, seen);
    const id = seen > 1 ? `${baseId}-${seen}` : baseId;
    outline.push({
      id,
      level,
      title: normalizedTitle,
      line: countLinesBefore(cleanSource, match.index ?? 0),
    });
  }

  return outline;
}

function transformSections(markdown: string, ctx: BuildContext): string {
  const counters = new Map<string, number>();
  return markdown.replace(/\\(section|subsection|subsubsection|paragraph)\{([\s\S]*?)\}/g, (_match, command, title) => {
    const expandedTitle = expandMacros(title, ctx).replace(/\s+/g, ' ').trim();
    const normalizedTitle = cleanupInlineText(expandedTitle);
    const level = SECTION_LEVELS[command] ?? 1;
    const baseId = slugify(normalizedTitle);
    const seen = (counters.get(baseId) ?? 0) + 1;
    counters.set(baseId, seen);
    const hashes = '#'.repeat(Math.min(level + 1, 6));
    return `\n${hashes} ${normalizedTitle}\n`;
  });
}

function transformTextCommands(markdown: string): string {
  let output = markdown;
  for (let pass = 0; pass < 3; pass += 1) {
    const before = output;
    output = output
      .replace(/\\textbf\{([^{}]*)\}/g, '**$1**')
      .replace(/\\textit\{([^{}]*)\}/g, '*$1*')
      .replace(/\\emph\{([^{}]*)\}/g, '*$1*')
      .replace(/\\underline\{([^{}]*)\}/g, '$1')
      .replace(/\\texttt\{([^{}]*)\}/g, '`$1`');
    if (before === output) {
      break;
    }
  }
  return output;
}

function cleanupMarkdown(markdown: string): string {
  return markdown
    .replace(/\{\}/g, '')
    .replace(/\\maketitle/g, '')
    .replace(/\\title(?:\[[^\]]*\])?\{[\s\S]*?\}/g, '')
    .replace(/\\author\*?(?:\[[^\]]*\])?\{[\s\S]*?\}(?:\\email\{[\s\S]*?\})?/g, '')
    .replace(/\\affil\*?(?:\[[^\]]*\])?\{[\s\S]*?\}/g, '')
    .replace(/\\abstract\{[\s\S]*?\}/g, '')
    .replace(/\\keywords\{[\s\S]*?\}/g, '')
    .replace(/\\email\{[^}]*\}/g, '')
    .replace(/\\label\{[^}]+\}/g, '')
    .replace(/\\bibliography\{[^}]+\}/g, '')
    .replace(/\\bibliographystyle\{[^}]+\}/g, '')
    .replace(/\\appendix\b/g, '')
    .replace(/\\FloatBarrier/g, '')
    .replace(/\\centering/g, '')
    .replace(/\\cite\{([^}]+)\}/g, '[$1]')
    .replace(/\\(?:eq|fig|tab)?ref\{([^}]+)\}/g, '$1')
    .replace(/\\item\s*/g, '- ')
    .replace(/\\begin\{(?:itemize|enumerate)\}/g, '')
    .replace(/\\end\{(?:itemize|enumerate)\}/g, '')
    .replace(/\\begin\{table\*?\}[\s\S]*?\\end\{table\*?\}/g, '\n> Table omitted in quick preview.\n')
    .replace(/\\resizebox\{[^}]+\}\{[^}]+\}\{([^{}]*)\}/g, '$1')
    .replace(/~+/g, ' ')
    .replace(/\\\\/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function findOutlineMarkdownLines(outline: PaperEditorOutlineItem[], markdown: string): number[] {
  const headingLines = markdown
    .split(/\r?\n/)
    .map((line, index) => {
      const match = /^(#{1,6})\s+(.+?)\s*$/.exec(line);
      if (!match) {
        return null;
      }
      return {
        line: index + 1,
        title: cleanupInlineText(match[2]),
      };
    })
    .filter((entry): entry is { line: number; title: string } => entry !== null);

  let headingCursor = 0;
  return outline.map((item) => {
    for (let index = headingCursor; index < headingLines.length; index += 1) {
      if (headingLines[index].title !== item.title) {
        continue;
      }
      headingCursor = index + 1;
      return headingLines[index].line;
    }
    return 0;
  });
}

function findOutlineHtmlLines(outline: PaperEditorOutlineItem[], html: string): number[] {
  return outline.map((item) => {
    const marker = `id="${item.id}"`;
    const index = html.indexOf(marker);
    if (index < 0) {
      return 1;
    }
    return countLinesBefore(html, index);
  });
}

function decorateOutlineMappings(
  outline: PaperEditorOutlineItem[],
  markdown: string,
  html: string,
  lineMappings: PaperEditorLineMappings,
): PaperEditorOutlineItem[] {
  const markdownLines = findOutlineMarkdownLines(outline, markdown);
  const htmlLines = findOutlineHtmlLines(outline, html);
  const maxMarkdownIndex = Math.max(1, lineMappings.latexToMarkdown.length - 1);
  return outline.map((item) => {
    const latexLine = Math.max(1, item.line);
    const markdownLine = markdownLines.shift() || lineMappings.latexToMarkdown[Math.min(latexLine, maxMarkdownIndex)] || 1;
    const htmlLine = htmlLines.shift() || 1;
    return {
      ...item,
      markdownLine,
      htmlLine,
    };
  });
}

function buildPreview(entryFile: string, source: string, ctx: BuildContext): Omit<PaperEditorDocument, 'entry' | 'source' | 'sourceView' | 'revision' | 'updatedAt'> {
  const outline = extractOutlineFromSource(source, ctx);
  const assets: PaperEditorAsset[] = [];

  const title = extractCommandBody(source, '\\title', true);
  const abstract = extractCommandBody(source, '\\abstract');
  let body = extractDocumentBody(source);
  body = stripFrontMatter(body);
  body = expandBodyImports(body, entryFile, ctx);
  body = expandMacros(body, ctx);

  let markdown = body;
  markdown = transformFigures(markdown, entryFile, ctx, assets);
  markdown = transformLooseImages(markdown, entryFile, ctx, assets);
  markdown = transformMath(markdown);
  markdown = transformTables(markdown, ctx);
  markdown = transformSections(markdown, ctx);
  markdown = transformTextCommands(markdown);
  markdown = cleanupMarkdown(markdown);

  const prefix: string[] = [];
  const normalizedTitle = title ? cleanupInlineText(expandMacros(title, ctx)) : null;
  const normalizedAbstract = abstract ? cleanupInlineText(expandMacros(abstract, ctx)) : null;
  if (title) {
    prefix.push(`# ${normalizedTitle}`);
    outline.unshift({ id: 'paper-title', level: 0, title: normalizedTitle ?? '', line: 1 });
  }
  if (abstract) {
    prefix.push('## Abstract');
    prefix.push(normalizedAbstract ?? '');
    outline.splice(title ? 1 : 0, 0, { id: 'abstract', level: 1, title: 'Abstract', line: 1 });
  }

  const finalMarkdown = [...prefix, markdown].filter(Boolean).join('\n\n').trim();
  const latexMarkdownMap = buildApproximateLineMap(source, finalMarkdown, 'latex', 'markdown');
  const htmlPreview = renderPaperEditorHtml(finalMarkdown, latexMarkdownMap.forward, latexMarkdownMap.reverse, outline);
  const lineMappings: PaperEditorLineMappings = {
    latexToMarkdown: latexMarkdownMap.forward,
    markdownToLatex: latexMarkdownMap.reverse,
    markdownToHtml: htmlPreview.markdownToHtml,
    htmlToMarkdown: htmlPreview.htmlToMarkdown,
    htmlToLatex: htmlPreview.htmlToLatex,
    latexToHtml: htmlPreview.latexToHtml,
    htmlBlocks: htmlPreview.htmlBlocks,
  };
  const mappedOutline = decorateOutlineMappings(outline, finalMarkdown, htmlPreview.html, lineMappings);

  return {
    markdown: finalMarkdown,
    html: htmlPreview.html,
    outline: mappedOutline,
    imports: Array.from(ctx.imports).sort(),
    macros: Object.fromEntries(Array.from(ctx.macros.entries()).map(([name, macro]) => [name, macro.body])),
    assets,
    diagnostics: Array.from(new Set(ctx.diagnostics)),
    lineMappings,
    performance: {
      parseMs: 0,
      sourceBytes: Buffer.byteLength(source, 'utf-8'),
      markdownBytes: Buffer.byteLength(finalMarkdown, 'utf-8'),
      macroCount: ctx.macros.size,
      importCount: ctx.imports.size,
      imageCount: assets.length,
    },
  };
}

function buildContext(rootDir: string, latexRoot: string, overrides: Map<string, string>): BuildContext {
  return {
    rootDir,
    latexRoot,
    macros: new Map<string, MacroDefinition>(),
    imports: new Set<string>(),
    diagnostics: [],
    visited: new Set<string>(),
    overrides,
  };
}

function getEntryFile(rootDir: string, entry: string): string {
  const latexRoot = path.join(rootDir, 'docs', 'paper', 'latex');
  const resolved = ensureInside(latexRoot, path.resolve(latexRoot, entry || DEFAULT_ENTRY));
  if (!fs.existsSync(resolved)) {
    throw new Error(`Paper entry not found: ${entry || DEFAULT_ENTRY}`);
  }
  return resolved;
}

function buildDocumentRevision(latexRoot: string, filePaths: Iterable<string>): { revision: string; updatedAt: string | null } {
  const stats = Array.from(new Set(Array.from(filePaths)))
    .filter((filePath) => fs.existsSync(filePath))
    .map((filePath) => {
      const stat = fs.statSync(filePath);
      return {
        filePath,
        relativePath: toPosix(path.relative(latexRoot, filePath)),
        mtimeMs: stat.mtimeMs,
        size: stat.size,
      };
    })
    .sort((left, right) => left.relativePath.localeCompare(right.relativePath));

  if (stats.length === 0) {
    return {
      revision: 'missing',
      updatedAt: null,
    };
  }

  const latest = stats.reduce((currentLatest, candidate) => (
    candidate.mtimeMs >= currentLatest.mtimeMs ? candidate : currentLatest
  ), stats[0]);

  return {
    revision: stats.map((entry) => `${entry.relativePath}:${Math.round(entry.mtimeMs)}:${entry.size}`).join('|'),
    updatedAt: new Date(latest.mtimeMs).toISOString(),
  };
}

function buildDocument(rootDir: string, entry: string, sourceOverride?: string, sourceViewColumns = DEFAULT_SOURCE_VIEW_COLUMNS): PaperEditorDocument {
  const startedAt = performance.now();
  const entryFile = getEntryFile(rootDir, entry || DEFAULT_ENTRY);
  const latexRoot = path.join(rootDir, 'docs', 'paper', 'latex');
  const overrides = new Map<string, string>();
  if (typeof sourceOverride === 'string') {
    overrides.set(entryFile, sourceOverride);
  }

  const ctx = buildContext(rootDir, latexRoot, overrides);
  const source = readSource(entryFile, overrides);
  visitDependencies(entryFile, ctx);
  const preview = buildPreview(entryFile, source, ctx);
  const sourceView = buildWrappedSourceView(source, sourceViewColumns);
  const revisionState = buildDocumentRevision(latexRoot, ctx.visited);

  return {
    entry: toPosix(path.relative(latexRoot, entryFile)),
    source,
    sourceView,
    markdown: preview.markdown,
    html: preview.html,
    outline: preview.outline,
    imports: preview.imports,
    macros: preview.macros,
    assets: preview.assets,
    diagnostics: preview.diagnostics,
    lineMappings: preview.lineMappings,
    performance: {
      ...preview.performance,
      parseMs: Number((performance.now() - startedAt).toFixed(2)),
    },
    revision: revisionState.revision,
    updatedAt: revisionState.updatedAt,
  };
}

export function loadPaperEditorDocument(rootDir: string, entry = DEFAULT_ENTRY, sourceViewColumns = DEFAULT_SOURCE_VIEW_COLUMNS): PaperEditorDocument {
  return buildDocument(rootDir, entry, undefined, sourceViewColumns);
}

export function loadPaperEditorDocumentState(rootDir: string, entry = DEFAULT_ENTRY): PaperEditorDocumentState {
  const entryFile = getEntryFile(rootDir, entry || DEFAULT_ENTRY);
  const latexRoot = path.join(rootDir, 'docs', 'paper', 'latex');
  const ctx = buildContext(rootDir, latexRoot, new Map<string, string>());
  visitDependencies(entryFile, ctx);
  const revisionState = buildDocumentRevision(latexRoot, ctx.visited);
  return {
    entry: toPosix(path.relative(latexRoot, entryFile)),
    imports: Array.from(ctx.imports).sort(),
    revision: revisionState.revision,
    updatedAt: revisionState.updatedAt,
  };
}

export function previewPaperEditorDocument(rootDir: string, entry = DEFAULT_ENTRY, source = '', sourceViewColumns = DEFAULT_SOURCE_VIEW_COLUMNS): PaperEditorDocument {
  return buildDocument(rootDir, entry, source, sourceViewColumns);
}

export function savePaperEditorDocument(rootDir: string, input: PaperEditorSaveInput = {}): PaperEditorSaveResult {
  const entry = input.entry ?? DEFAULT_ENTRY;
  const sourceViewColumns = input.sourceViewColumns ?? DEFAULT_SOURCE_VIEW_COLUMNS;
  const requestedSource = input.source ?? '';
  const baseSource = input.baseSource ?? '';
  const baseSourceViewText = input.baseSourceViewText ?? '';
  const nextSourceViewText = input.sourceViewText ?? '';
  const baseRevision = input.baseRevision ?? null;
  const entryFile = getEntryFile(rootDir, entry);
  const previousSourceRaw = fs.existsSync(entryFile) ? fs.readFileSync(entryFile, 'utf-8') : '';
  const preferredLineEnding = detectPaperEditorLineEnding(previousSourceRaw || baseSource || requestedSource);
  const previousSource = normalizePaperEditorLineEndings(previousSourceRaw);
  const normalizedBaseSource = normalizePaperEditorLineEndings(baseSource);
  const normalizedRequestedSource = normalizePaperEditorLineEndings(requestedSource);
  const currentRevisionState = getRevisionStateForEntry(rootDir, entryFile);

  const patch = createPatch(
    toPosix(path.basename(entryFile)),
    normalizedBaseSource,
    normalizedRequestedSource,
    'base',
    'requested',
    { context: 0 },
  );
  const nextSourceNormalized = previousSource === normalizedBaseSource
    ? normalizedRequestedSource
    : applyPatch(previousSource, patch, { fuzzFactor: 2 });

  if (nextSourceNormalized === false) {
    throw new PaperEditorSaveConflictError(
      'Paper source changed on disk and your patch could not be applied cleanly. Reload and reapply your edit.',
      currentRevisionState.revision,
      currentRevisionState.updatedAt,
    );
  }

  const nextSource = applyPaperEditorLineEnding(nextSourceNormalized, preferredLineEnding);

  const audit = buildSaveAudit(
    previousSourceRaw,
    nextSource,
    normalizedRequestedSource,
    normalizedBaseSource,
    baseSourceViewText,
    nextSourceViewText,
    baseRevision,
    currentRevisionState.revision,
  );
  fs.writeFileSync(entryFile, nextSource, 'utf-8');
  return {
    document: buildDocument(rootDir, entry, undefined, sourceViewColumns),
    audit,
  };
}

export function exportPaperEditorMarkdown(rootDir: string, entry = DEFAULT_ENTRY, outputPath?: string): PaperEditorDocument {
  const document = buildDocument(rootDir, entry);
  if (outputPath) {
    const resolvedOutput = ensureInside(rootDir, path.resolve(rootDir, outputPath));
    fs.mkdirSync(path.dirname(resolvedOutput), { recursive: true });
    fs.writeFileSync(resolvedOutput, document.markdown, 'utf-8');
  }
  return document;
}

export function resolvePaperEditorAsset(rootDir: string, requestPath: string): string {
  const resolved = ensureInside(rootDir, path.resolve(rootDir, requestPath));
  if (!fs.existsSync(resolved)) {
    throw new Error(`Asset not found: ${requestPath}`);
  }
  return resolved;
}

export const PAPER_EDITOR_TEXT_COMMANDS = TEXT_COMMANDS;