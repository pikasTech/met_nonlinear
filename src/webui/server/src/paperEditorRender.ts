import rehypeKatex from 'rehype-katex';
import rehypeStringify from 'rehype-stringify';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import { unified } from 'unified';
import { visit } from 'unist-util-visit';

export interface PaperEditorOutlineItem {
  id: string;
  level: number;
  title: string;
  line: number;
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

interface MarkdownBlock {
  fragment: string;
  kind: string;
  markdownStartLine: number;
  markdownEndLine: number;
  headingCount: number;
}

interface HastTextNode {
  type: 'text';
  value: string;
}

interface HASTElementNode {
  type: 'element';
  tagName: string;
  properties?: Record<string, unknown>;
  children: HASTNode[];
}

type HASTNode = HASTElementNode | HastTextNode;

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '') || 'section';
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function splitLines(text: string): string[] {
  return text.split(/\r?\n/);
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

function normalizeLine(text: string, kind: 'latex' | 'markdown' | 'html'): string {
  let output = text;
  if (kind === 'latex') {
    output = output
      .replace(/(?<!\\)%.*$/g, '')
      .replace(/\\(?:section|subsection|subsubsection|paragraph|caption|title|author|affil|keywords|textbf|textit|emph|underline|texttt|makecell|multicolumn|multirow)\*?(?:\[[^\]]*\])?\{([\s\S]*?)\}/g, '$1')
      .replace(/\\(?:includegraphics)(?:\[[^\]]*\])?\{([^}]+)\}/g, '$1')
      .replace(/\\(?:begin|end)\{[^}]+\}/g, ' ')
      .replace(/\\(?:hline|toprule|midrule|bottomrule|hdashline|item|centering|small|footnotesize|scriptsize|normalsize|maketitle|label|cite|ref|eqref|bibliography|bibliographystyle)\b/g, ' ')
      .replace(/[{}]/g, ' ')
      .replace(/\\\\/g, ' ');
  } else if (kind === 'markdown') {
    output = output
      .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '$1 $2')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 $2')
      .replace(/^#{1,6}\s+/g, '')
      .replace(/^>\s+/g, '')
      .replace(/^\|?|\|?$/g, ' ')
      .replace(/[*_`~|]/g, ' ');
  } else {
    output = decodeHtmlEntities(output.replace(/<[^>]+>/g, ' '));
  }

  return output.replace(/\s+/g, ' ').trim().toLowerCase();
}

function tokenize(text: string): string[] {
  const matches = text.match(/[\p{L}\p{N}._-]+/gu);
  return matches ?? [];
}

function scoreLineMatch(sourceLine: string, targetLine: string): number {
  if (!sourceLine || !targetLine) {
    return 0;
  }
  if (sourceLine === targetLine) {
    return 1;
  }

  const sourceTokens = new Set(tokenize(sourceLine));
  const targetTokens = new Set(tokenize(targetLine));
  if (sourceTokens.size === 0 || targetTokens.size === 0) {
    return sourceLine.includes(targetLine) || targetLine.includes(sourceLine) ? 0.5 : 0;
  }

  let intersection = 0;
  for (const token of sourceTokens) {
    if (targetTokens.has(token)) {
      intersection += 1;
    }
  }
  const union = new Set([...sourceTokens, ...targetTokens]).size;
  const jaccard = union > 0 ? intersection / union : 0;
  const substringBonus = sourceLine.includes(targetLine) || targetLine.includes(sourceLine) ? 0.2 : 0;
  return Math.min(1, jaccard + substringBonus);
}

function interpolateMap(forwardMap: number[], sourceCount: number, targetCount: number): number[] {
  const anchors: Array<{ sourceLine: number; targetLine: number }> = [];
  for (let line = 1; line <= sourceCount; line += 1) {
    if (forwardMap[line] > 0) {
      anchors.push({ sourceLine: line, targetLine: forwardMap[line] });
    }
  }

  if (anchors.length === 0) {
    for (let line = 1; line <= sourceCount; line += 1) {
      forwardMap[line] = Math.max(1, Math.min(targetCount, Math.round((line / Math.max(sourceCount, 1)) * Math.max(targetCount, 1))));
    }
    return forwardMap;
  }

  const first = anchors[0];
  for (let line = 1; line < first.sourceLine; line += 1) {
    forwardMap[line] = Math.max(1, Math.round((line / Math.max(first.sourceLine, 1)) * first.targetLine));
  }

  for (let index = 0; index < anchors.length - 1; index += 1) {
    const current = anchors[index];
    const next = anchors[index + 1];
    const span = Math.max(1, next.sourceLine - current.sourceLine);
    for (let line = current.sourceLine; line <= next.sourceLine; line += 1) {
      const ratio = (line - current.sourceLine) / span;
      const mapped = Math.round(current.targetLine + (next.targetLine - current.targetLine) * ratio);
      forwardMap[line] = clamp(mapped, current.targetLine, next.targetLine);
    }
  }

  const last = anchors[anchors.length - 1];
  for (let line = last.sourceLine; line <= sourceCount; line += 1) {
    const ratio = sourceCount === last.sourceLine ? 1 : (line - last.sourceLine) / Math.max(sourceCount - last.sourceLine, 1);
    const mapped = Math.round(last.targetLine + (targetCount - last.targetLine) * ratio);
    forwardMap[line] = clamp(mapped, last.targetLine, Math.max(targetCount, last.targetLine));
  }

  let previous = 1;
  for (let line = 1; line <= sourceCount; line += 1) {
    previous = Math.max(previous, forwardMap[line] || previous);
    forwardMap[line] = clamp(previous, 1, Math.max(targetCount, 1));
  }
  return forwardMap;
}

function invertForwardMap(forwardMap: number[], sourceCount: number, targetCount: number): number[] {
  const reversed = new Array(targetCount + 1).fill(1);
  let sourceCursor = 1;
  for (let targetLine = 1; targetLine <= targetCount; targetLine += 1) {
    while (sourceCursor < sourceCount && forwardMap[sourceCursor] < targetLine) {
      sourceCursor += 1;
    }
    const previous = Math.max(1, sourceCursor - 1);
    const currentDistance = Math.abs((forwardMap[sourceCursor] ?? targetLine) - targetLine);
    const previousDistance = Math.abs((forwardMap[previous] ?? targetLine) - targetLine);
    reversed[targetLine] = previousDistance <= currentDistance ? previous : sourceCursor;
  }
  return reversed;
}

export function buildApproximateLineMap(
  sourceText: string,
  targetText: string,
  sourceKind: 'latex' | 'markdown' | 'html',
  targetKind: 'latex' | 'markdown' | 'html',
): { forward: number[]; reverse: number[] } {
  const sourceLines = splitLines(sourceText);
  const targetLines = splitLines(targetText);
  const normalizedSource = sourceLines.map((line) => normalizeLine(line, sourceKind));
  const normalizedTarget = targetLines.map((line) => normalizeLine(line, targetKind));
  const forward = new Array(sourceLines.length + 1).fill(0);
  let targetCursor = 1;

  for (let sourceLine = 1; sourceLine <= sourceLines.length; sourceLine += 1) {
    const signature = normalizedSource[sourceLine - 1];
    if (!signature) {
      continue;
    }

    let bestLine = 0;
    let bestScore = 0;
    const windowEnd = Math.min(targetLines.length, targetCursor + 48);
    for (let targetLine = targetCursor; targetLine <= windowEnd; targetLine += 1) {
      const candidate = normalizedTarget[targetLine - 1];
      if (!candidate) {
        continue;
      }
      const score = scoreLineMatch(signature, candidate);
      if (score > bestScore) {
        bestScore = score;
        bestLine = targetLine;
      }
      if (score >= 0.98) {
        break;
      }
    }

    if (bestLine > 0 && bestScore >= 0.26) {
      forward[sourceLine] = bestLine;
      targetCursor = bestLine;
    }
  }

  const interpolated = interpolateMap(forward, sourceLines.length, targetLines.length);
  return {
    forward: interpolated,
    reverse: invertForwardMap(interpolated, sourceLines.length, targetLines.length),
  };
}

function getTextContent(node: HASTNode | undefined): string {
  if (!node) {
    return '';
  }
  if (node.type === 'text') {
    return node.value;
  }
  return node.children.map((child: HASTNode) => getTextContent(child)).join('');
}

function createElement(tagName: string, className: string | string[] | undefined, children: HASTNode[] = []): HASTElementNode {
  return {
    type: 'element',
    tagName,
    properties: className ? { className: Array.isArray(className) ? className : [className] } : {},
    children,
  };
}

function rehypePaperEditorPreview(outline: PaperEditorOutlineItem[]) {
  return (tree: HASTElementNode) => {
    let headingIndex = 0;

    visit(tree, 'element', (node: HASTElementNode) => {
      if (/^h[1-6]$/.test(node.tagName)) {
        const outlineItem = outline[headingIndex] ?? null;
        headingIndex += 1;
        const headingText = getTextContent(node);
        const existingProperties = node.properties ?? {};
        node.properties = {
          ...existingProperties,
          id: outlineItem?.id ?? slugify(headingText),
        };
      }
    });

    visit(tree, 'element', (node: HASTElementNode, index: number | undefined, parent: HASTElementNode | undefined) => {
      if (!parent || index == null || node.tagName !== 'blockquote') {
        return;
      }
      const text = getTextContent(node).replace(/\s+/g, ' ').trim();
      if (!text.startsWith('Missing figure asset:')) {
        return;
      }

      const assetPath = text.replace('Missing figure asset:', '').trim();
      parent.children[index] = createElement('figure', ['paper-editor-preview__figure', 'paper-editor-preview__figure--missing'], [
        createElement('div', 'paper-editor-preview__missing-asset', [
          createElement('strong', undefined, [{ type: 'text', value: 'Missing figure asset' }]),
          createElement('span', undefined, [{ type: 'text', value: assetPath }]),
        ]),
      ]);
    });

    visit(tree, 'element', (node: HASTElementNode, index: number | undefined, parent: HASTElementNode | undefined) => {
      if (!parent || index == null || node.tagName !== 'p') {
        return;
      }
      const meaningfulChildren = node.children.filter((child) => child.type !== 'text' || child.value.trim());
      if (meaningfulChildren.length !== 1) {
        return;
      }
      const imageNode = meaningfulChildren[0];
      if (imageNode.type !== 'element' || imageNode.tagName !== 'img') {
        return;
      }

      const altText = typeof imageNode.properties?.alt === 'string' ? imageNode.properties.alt : '';
      parent.children[index] = createElement('figure', 'paper-editor-preview__figure', [
        imageNode,
        ...(altText ? [createElement('figcaption', undefined, [{ type: 'text', value: altText }])] : []),
      ]);
    });
  };
}

function parseMarkdownBlocks(markdown: string): MarkdownBlock[] {
  const tree = unified().use(remarkParse).use(remarkGfm).use(remarkMath).parse(markdown) as {
    children?: Array<{ type?: string; position?: { start?: { line?: number }; end?: { line?: number } } }>;
  };
  const markdownLines = splitLines(markdown);
  const blocks: MarkdownBlock[] = [];

  for (const node of tree.children ?? []) {
    const markdownStartLine = node.position?.start?.line ?? 1;
    const markdownEndLine = node.position?.end?.line ?? markdownStartLine;
    const fragment = markdownLines.slice(markdownStartLine - 1, markdownEndLine).join('\n').trim();
    if (!fragment) {
      continue;
    }
    blocks.push({
      fragment,
      kind: node.type ?? 'unknown',
      markdownStartLine,
      markdownEndLine,
      headingCount: node.type === 'heading' ? 1 : 0,
    });
  }

  if (blocks.length === 0 && markdown.trim()) {
    blocks.push({
      fragment: markdown.trim(),
      kind: 'root',
      markdownStartLine: 1,
      markdownEndLine: markdownLines.length,
      headingCount: 0,
    });
  }
  return blocks;
}

function rangeMap(line: number, sourceStart: number, sourceEnd: number, targetStart: number, targetEnd: number): number {
  if (sourceEnd <= sourceStart) {
    return targetStart;
  }
  const ratio = (line - sourceStart) / Math.max(sourceEnd - sourceStart, 1);
  return Math.round(targetStart + (targetEnd - targetStart) * ratio);
}

function renderMarkdownFragment(fragment: string, outline: PaperEditorOutlineItem[]): string {
  return String(
    unified()
      .use(remarkParse)
      .use(remarkGfm)
      .use(remarkMath)
      .use(remarkRehype)
      .use(rehypeKatex)
      .use(rehypePaperEditorPreview, outline)
      .use(rehypeStringify)
      .processSync(fragment),
  );
}

export function renderPaperEditorHtml(
  markdown: string,
  latexToMarkdown: number[],
  markdownToLatex: number[],
  outline: PaperEditorOutlineItem[],
): {
  html: string;
  htmlBlocks: PaperEditorHtmlBlock[];
  markdownToHtml: number[];
  htmlToMarkdown: number[];
  htmlToLatex: number[];
  latexToHtml: number[];
} {
  const blocks = parseMarkdownBlocks(markdown);
  const htmlParts: string[] = [];
  const markdownLineCount = splitLines(markdown).length;
  const htmlBlocks: PaperEditorHtmlBlock[] = [];
  let htmlLineCursor = 1;
  let headingCursor = 0;

  for (let index = 0; index < blocks.length; index += 1) {
    const block = blocks[index];
    const latexStartLine = markdownToLatex[block.markdownStartLine] ?? 1;
    const latexEndLine = markdownToLatex[block.markdownEndLine] ?? latexStartLine;
    const blockOutline = block.headingCount > 0 ? outline.slice(headingCursor, headingCursor + block.headingCount) : [];
    headingCursor += block.headingCount;
    const innerHtml = renderMarkdownFragment(block.fragment, blockOutline);
    const wrappedHtml = [
      `<section class="paper-editor-preview__block" data-html-block-index="${index + 1}" data-md-start-line="${block.markdownStartLine}" data-md-end-line="${block.markdownEndLine}" data-latex-start-line="${latexStartLine}" data-latex-end-line="${latexEndLine}" data-block-kind="${block.kind}">`,
      innerHtml,
      '</section>',
    ].join('\n');
    const lineCount = splitLines(wrappedHtml).length;
    const htmlStartLine = htmlLineCursor;
    const htmlEndLine = htmlLineCursor + lineCount - 1;

    htmlBlocks.push({
      htmlBlockIndex: index + 1,
      htmlStartLine,
      htmlEndLine,
      markdownStartLine: block.markdownStartLine,
      markdownEndLine: block.markdownEndLine,
      latexStartLine,
      latexEndLine,
      kind: block.kind,
    });
    htmlParts.push(wrappedHtml);
    htmlLineCursor = htmlEndLine + 1;
  }

  const html = htmlParts.join('\n');
  const totalHtmlLines = Math.max(1, splitLines(html).length);
  const markdownToHtml = new Array(markdownLineCount + 1).fill(0);

  for (const block of htmlBlocks) {
    for (let markdownLine = block.markdownStartLine; markdownLine <= block.markdownEndLine; markdownLine += 1) {
      markdownToHtml[markdownLine] = rangeMap(markdownLine, block.markdownStartLine, block.markdownEndLine, block.htmlStartLine, block.htmlEndLine);
    }
  }

  interpolateMap(markdownToHtml, markdownLineCount, totalHtmlLines);

  const htmlToMarkdown = invertForwardMap(markdownToHtml, markdownLineCount, totalHtmlLines);
  const latexLineCount = Math.max(1, latexToMarkdown.length - 1, markdownToLatex.reduce((maxValue, line) => Math.max(maxValue, line || 1), 1));
  const htmlToLatex = new Array(totalHtmlLines + 1).fill(0);
  const latexToHtml = new Array(latexLineCount + 1).fill(0);

  for (let htmlLine = 1; htmlLine <= totalHtmlLines; htmlLine += 1) {
    const markdownLine = htmlToMarkdown[htmlLine] ?? 1;
    htmlToLatex[htmlLine] = markdownToLatex[markdownLine] ?? 1;
  }

  for (let latexLine = 1; latexLine <= latexLineCount; latexLine += 1) {
    const markdownLine = latexToMarkdown[latexLine] ?? 1;
    latexToHtml[latexLine] = markdownToHtml[markdownLine] ?? 1;
  }

  interpolateMap(htmlToLatex, totalHtmlLines, latexLineCount);
  interpolateMap(latexToHtml, latexLineCount, totalHtmlLines);

  for (let htmlLine = 1; htmlLine <= totalHtmlLines; htmlLine += 1) {
    if (htmlToLatex[htmlLine] < 1) {
      htmlToLatex[htmlLine] = 1;
    }
  }

  for (let latexLine = 1; latexLine <= latexLineCount; latexLine += 1) {
    if (latexToHtml[latexLine] < 1) {
      latexToHtml[latexLine] = 1;
    }
  }

  return {
    html,
    htmlBlocks,
    markdownToHtml,
    htmlToMarkdown,
    htmlToLatex,
    latexToHtml,
  };
}