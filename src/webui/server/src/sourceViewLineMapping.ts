export interface SourceViewLineMappings {
  columns: number;
  tabSize: number;
  totalViewLines: number;
  viewLineToLatex: number[];
  latexToViewLineStart: number[];
  latexToViewLineEnd: number[];
}

export interface WrappedSourceView extends SourceViewLineMappings {
  text: string;
  viewLineEndsWithSourceBreak: boolean[];
}

function isFullwidthCodePoint(codePoint: number): boolean {
  return codePoint >= 0x1100 && (
    codePoint <= 0x115f
    || codePoint === 0x2329
    || codePoint === 0x232a
    || (codePoint >= 0x2e80 && codePoint <= 0x3247 && codePoint !== 0x303f)
    || (codePoint >= 0x3250 && codePoint <= 0x4dbf)
    || (codePoint >= 0x4e00 && codePoint <= 0xa4c6)
    || (codePoint >= 0xa960 && codePoint <= 0xa97c)
    || (codePoint >= 0xac00 && codePoint <= 0xd7a3)
    || (codePoint >= 0xf900 && codePoint <= 0xfaff)
    || (codePoint >= 0xfe10 && codePoint <= 0xfe19)
    || (codePoint >= 0xfe30 && codePoint <= 0xfe6b)
    || (codePoint >= 0xff01 && codePoint <= 0xff60)
    || (codePoint >= 0xffe0 && codePoint <= 0xffe6)
    || (codePoint >= 0x1b000 && codePoint <= 0x1b001)
    || (codePoint >= 0x1f200 && codePoint <= 0x1f251)
    || (codePoint >= 0x20000 && codePoint <= 0x3fffd)
  );
}

function isZeroWidthCodePoint(codePoint: number): boolean {
  return (
    (codePoint >= 0x0300 && codePoint <= 0x036f)
    || (codePoint >= 0x1ab0 && codePoint <= 0x1aff)
    || (codePoint >= 0x1dc0 && codePoint <= 0x1dff)
    || (codePoint >= 0x20d0 && codePoint <= 0x20ff)
    || (codePoint >= 0xfe20 && codePoint <= 0xfe2f)
  );
}

function getCodePointWidth(character: string): number {
  const codePoint = character.codePointAt(0);
  if (codePoint == null) {
    return 0;
  }

  if (isZeroWidthCodePoint(codePoint)) {
    return 0;
  }

  return isFullwidthCodePoint(codePoint) ? 2 : 1;
}

function getCharacterWidth(character: string, column: number, tabSize: number): number {
  if (character === '\t') {
    return tabSize - (column % tabSize || 0);
  }
  return getCodePointWidth(character);
}

function wrapSourceLine(line: string, columns: number, tabSize: number): string[] {
  if (!line) {
    return [''];
  }

  const wrapped: string[] = [];
  let current = '';
  let currentWidth = 0;

  for (const character of Array.from(line)) {
    const characterWidth = getCharacterWidth(character, currentWidth, tabSize);
    if (current && currentWidth + characterWidth > columns) {
      wrapped.push(current);
      current = character;
      currentWidth = getCharacterWidth(character, 0, tabSize);
      continue;
    }
    current += character;
    currentWidth += characterWidth;
  }

  wrapped.push(current);
  return wrapped;
}

export function buildWrappedSourceView(source: string, columns: number, tabSize = 2): WrappedSourceView {
  const safeColumns = Math.max(1, columns);
  const safeTabSize = Math.max(1, tabSize);
  const sourceLines = source.split(/\r?\n/);
  const viewLineToLatex = [0];
  const latexToViewLineStart = [0];
  const latexToViewLineEnd = [0];
  const viewLineEndsWithSourceBreak = [false];
  const wrappedLines: string[] = [];
  let viewLineCursor = 1;

  for (let index = 0; index < sourceLines.length; index += 1) {
    const latexLine = index + 1;
    const wrappedViewLines = wrapSourceLine(sourceLines[index] ?? '', safeColumns, safeTabSize);
    latexToViewLineStart[latexLine] = viewLineCursor;
    latexToViewLineEnd[latexLine] = viewLineCursor + wrappedViewLines.length - 1;
    for (let offset = 0; offset < wrappedViewLines.length; offset += 1) {
      wrappedLines.push(wrappedViewLines[offset] ?? '');
      viewLineToLatex.push(latexLine);
      viewLineEndsWithSourceBreak.push(offset === wrappedViewLines.length - 1 && index < sourceLines.length - 1);
    }
    viewLineCursor += wrappedViewLines.length;
  }

  return {
    text: wrappedLines.join('\n'),
    columns: safeColumns,
    tabSize: safeTabSize,
    totalViewLines: Math.max(1, viewLineCursor - 1),
    viewLineToLatex,
    latexToViewLineStart,
    latexToViewLineEnd,
    viewLineEndsWithSourceBreak,
  };
}

export function buildSourceViewLineMappings(source: string, columns: number, tabSize = 2): SourceViewLineMappings {
  const wrapped = buildWrappedSourceView(source, columns, tabSize);
  return {
    columns: wrapped.columns,
    tabSize: wrapped.tabSize,
    totalViewLines: wrapped.totalViewLines,
    viewLineToLatex: wrapped.viewLineToLatex,
    latexToViewLineStart: wrapped.latexToViewLineStart,
    latexToViewLineEnd: wrapped.latexToViewLineEnd,
  };
}