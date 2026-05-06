import { describe, expect, test } from 'bun:test';
import { buildApproximateLineMap, renderPaperEditorHtml, type PaperEditorOutlineItem } from '../src/paperEditorRender';

function isMonotonic(values: number[]): boolean {
  for (let index = 2; index < values.length; index += 1) {
    if (values[index] < values[index - 1]) {
      return false;
    }
  }
  return true;
}

describe('paper editor line mappings', () => {
  const latex = [
    '\\section{Experimental Setup}',
    'Plain paragraph line for alignment.',
    '\\begin{table}[ht]',
    '\\caption{Experimental setup.}',
    '\\begin{tabular}{ll}',
    '\\textbf{Key} & \\textbf{Value} \\\\',
    'Sampling Frequency & 2000 Hz \\\\',
    '\\end{tabular}',
    '\\end{table}',
    '\\begin{figure}[ht]',
    '\\caption{Demo figure}',
    '\\includegraphics{assets/demo.png}',
    '\\end{figure}',
  ].join('\n');

  const markdown = [
    '## Experimental Setup',
    '',
    'Plain paragraph line for alignment.',
    '',
    'Table: Experimental setup.',
    '',
    '| **Key** | **Value** |',
    '| --- | --- |',
    '| Sampling Frequency | 2000 Hz |',
    '',
    '> Missing figure asset: assets/demo.png',
  ].join('\n');

  const outline: PaperEditorOutlineItem[] = [
    { id: 'experimental-setup', level: 1, title: 'Experimental Setup', line: 1 },
  ];

  test('buildApproximateLineMap returns monotonic forward and reverse maps', () => {
    const lineMap = buildApproximateLineMap(latex, markdown, 'latex', 'markdown');
    expect(isMonotonic(lineMap.forward)).toBe(true);
    expect(isMonotonic(lineMap.reverse)).toBe(true);
    expect(lineMap.forward[1]).toBeLessThanOrEqual(2);
    expect(lineMap.forward[7]).toBeGreaterThanOrEqual(7);
    expect(lineMap.forward[7]).toBeLessThanOrEqual(9);
  });

  test('renderPaperEditorHtml emits html block anchors and reverse mappings', () => {
    const lineMap = buildApproximateLineMap(latex, markdown, 'latex', 'markdown');
    const rendered = renderPaperEditorHtml(markdown, lineMap.forward, lineMap.reverse, outline);

    expect(rendered.html).toContain('data-html-block-index="1"');
    expect(rendered.html).toContain('data-md-start-line="1"');
    expect(rendered.html).toContain('data-latex-start-line="1"');
    expect(rendered.html).toContain('paper-editor-preview__missing-asset');
    expect(rendered.htmlBlocks.length).toBeGreaterThanOrEqual(3);
    expect(isMonotonic(rendered.markdownToHtml)).toBe(true);
    expect(isMonotonic(rendered.htmlToMarkdown)).toBe(true);
    expect(isMonotonic(rendered.htmlToLatex)).toBe(true);
    expect(rendered.latexToHtml[1]).toBeGreaterThanOrEqual(1);
    expect(rendered.latexToHtml[7]).toBeGreaterThanOrEqual(rendered.latexToHtml[1]);
  });

  test('outline lines survive latex to markdown to html mapping chain', () => {
    const lineMap = buildApproximateLineMap(latex, markdown, 'latex', 'markdown');
    const rendered = renderPaperEditorHtml(markdown, lineMap.forward, lineMap.reverse, outline);
    const mappedOutline = outline.map((item) => ({
      ...item,
      markdownLine: lineMap.forward[item.line] ?? 1,
      htmlLine: rendered.latexToHtml[item.line] ?? 1,
    }));

    expect(mappedOutline[0]?.markdownLine).toBeGreaterThanOrEqual(1);
    expect(mappedOutline[0]?.markdownLine).toBeLessThanOrEqual(2);
    expect(mappedOutline[0]?.htmlLine).toBeGreaterThanOrEqual(1);

    const block = rendered.htmlBlocks.find((entry) => {
      const htmlLine = mappedOutline[0]?.htmlLine ?? 1;
      return htmlLine >= entry.htmlStartLine && htmlLine <= entry.htmlEndLine;
    });

    expect(block?.markdownStartLine).toBeLessThanOrEqual(mappedOutline[0]?.markdownLine ?? 1);
    expect(block?.markdownEndLine).toBeGreaterThanOrEqual(mappedOutline[0]?.markdownLine ?? 1);
  });

  test('later heading blocks keep their own outline ids during per-block rendering', () => {
    const multiHeadingLatex = [
      '\\section{Alpha}',
      'Alpha paragraph.',
      '\\section{Beta}',
      'Beta paragraph.',
    ].join('\n');
    const multiHeadingMarkdown = [
      '## Alpha',
      '',
      'Alpha paragraph.',
      '',
      '## Beta',
      '',
      'Beta paragraph.',
    ].join('\n');
    const multiHeadingOutline: PaperEditorOutlineItem[] = [
      { id: 'alpha', level: 1, title: 'Alpha', line: 1 },
      { id: 'beta', level: 1, title: 'Beta', line: 3 },
    ];

    const lineMap = buildApproximateLineMap(multiHeadingLatex, multiHeadingMarkdown, 'latex', 'markdown');
    const rendered = renderPaperEditorHtml(multiHeadingMarkdown, lineMap.forward, lineMap.reverse, multiHeadingOutline);

    expect(rendered.html).toContain('id="alpha"');
    expect(rendered.html).toContain('id="beta"');
    expect(rendered.latexToHtml[3]).toBeGreaterThan(rendered.latexToHtml[1]);
  });
});