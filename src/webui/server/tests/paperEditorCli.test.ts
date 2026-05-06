import { afterEach, describe, expect, test } from 'bun:test';
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'node:child_process';

const repoRoot = path.resolve(import.meta.dir, '..', '..', '..', '..');
const exportCliPath = path.resolve(import.meta.dir, '..', 'src', 'exportPaperEditor.ts');
const bunExecutable = Bun.which('bun') ?? 'bun';

function isMonotonic(values: number[]): boolean {
  for (let index = 2; index < values.length; index += 1) {
    if (values[index] < values[index - 1]) {
      return false;
    }
  }
  return true;
}

const tempPaths: string[] = [];

afterEach(() => {
  for (const filePath of tempPaths.splice(0)) {
    if (fs.existsSync(filePath)) {
      const stats = fs.lstatSync(filePath);
      if (stats.isDirectory()) {
        fs.rmSync(filePath, { recursive: true, force: true });
      } else {
        fs.unlinkSync(filePath);
      }
    }
  }
});

describe('paper editor CLI wrap mappings', () => {
  test('bun ts export CLI emits wrapMappings for view-line to latex-line diagnostics', () => {
    const outputPath = path.join(repoRoot, 'cache', 'webui', 'paper-editor', `paper-editor-wrap-map-${Date.now()}.json`);
    tempPaths.push(outputPath);

    const result = spawnSync(
      bunExecutable,
      [
        exportCliPath,
        '--root',
        repoRoot,
        '--entry',
        'main.tex',
        '--output',
        outputPath,
        '--format',
        'mapping',
        '--wrap-columns',
        '24',
      ],
      {
        cwd: repoRoot,
        encoding: 'utf-8',
      },
    );

    expect(result.status, `${result.stderr ?? ''}\n${result.stdout ?? ''}`).toBe(0);
    expect(fs.existsSync(outputPath)).toBe(true);

    const payload = JSON.parse(fs.readFileSync(outputPath, 'utf-8')) as {
      wrapMappings?: {
        columns: number;
        totalViewLines: number;
        viewLineToLatex: number[];
        latexToViewLineStart: number[];
        latexToViewLineEnd: number[];
      };
    };

    expect(payload.wrapMappings).toBeDefined();
    expect(payload.wrapMappings?.columns).toBe(24);
    expect(payload.wrapMappings?.totalViewLines).toBeGreaterThan(0);
    expect(payload.wrapMappings?.viewLineToLatex.length).toBe((payload.wrapMappings?.totalViewLines ?? 0) + 1);
    expect(isMonotonic(payload.wrapMappings?.viewLineToLatex ?? [])).toBe(true);
    expect(isMonotonic(payload.wrapMappings?.latexToViewLineStart ?? [])).toBe(true);
    expect(isMonotonic(payload.wrapMappings?.latexToViewLineEnd ?? [])).toBe(true);
    expect(
      (payload.wrapMappings?.latexToViewLineStart ?? []).some((start, index) => {
        if (index === 0) {
          return false;
        }
        return (payload.wrapMappings?.latexToViewLineEnd[index] ?? start) > start;
      }),
    ).toBe(true);
  });

  test('bun ts export CLI emits strict chain diagnostics for selected lines and outline titles', () => {
    const fixtureRoot = fs.mkdtempSync(path.join(repoRoot, 'cache', 'webui', 'paper-editor', 'diagnostic-fixture-'));
    tempPaths.push(fixtureRoot);
    fs.mkdirSync(path.join(fixtureRoot, 'docs', 'paper', 'latex'), { recursive: true });

    const fixtureLatex = [
      '\\documentclass{article}',
      '\\begin{document}',
      '\\section{Alpha}',
      'This is a very long source line that should wrap when the backend uses a narrow diagnostic width.',
      '\\subsection{Beta}',
      'Another paragraph for reverse mapping diagnostics.',
      '\\end{document}',
    ].join('\n');
    fs.writeFileSync(path.join(fixtureRoot, 'docs', 'paper', 'latex', 'main.tex'), fixtureLatex, 'utf-8');

    const outputPath = path.join(fixtureRoot, 'cache', 'paper-editor-diagnostic.json');
    const result = spawnSync(
      bunExecutable,
      [
        exportCliPath,
        '--root',
        fixtureRoot,
        '--entry',
        'main.tex',
        '--output',
        outputPath,
        '--format',
        'diagnostic',
        '--wrap-columns',
        '20',
        '--latex-lines',
        '3',
        '4',
        '5',
        '--view-lines',
        '1',
        '2',
        '--markdown-lines',
        '1',
        '3',
        '--html-lines',
        '1',
        '2',
        '--outline-title',
        'Alpha',
        '--outline-title',
        'Beta',
      ],
      {
        cwd: repoRoot,
        encoding: 'utf-8',
      },
    );

    expect(result.status, `${result.stderr ?? ''}\n${result.stdout ?? ''}`).toBe(0);
    expect(fs.existsSync(outputPath)).toBe(true);

    const payload = JSON.parse(fs.readFileSync(outputPath, 'utf-8')) as {
      chainDiagnostics: {
        lineCounts: {
          latex: number;
          markdown: number;
          html: number;
          view: number | null;
        };
        monotonic: {
          latexToMarkdown: boolean;
          markdownToLatex: boolean;
          latexToHtml: boolean;
          htmlToLatex: boolean;
          viewLineToLatex: boolean | null;
        };
      };
      latexLineChains: Array<{
        latexLine: number | null;
        viewLineStart: number | null;
        viewLineEnd: number | null;
      }>;
      viewLineChains: Array<{
        viewLine: number | null;
        latexLine: number | null;
      }>;
      outlineTitleChains: Array<{
        query: string;
        matchedTitle: string | null;
      }>;
    };

    expect(payload.chainDiagnostics.lineCounts.latex).toBe(7);
    expect(payload.chainDiagnostics.lineCounts.markdown).toBeGreaterThan(0);
    expect(payload.chainDiagnostics.lineCounts.html).toBeGreaterThan(0);
    expect(payload.chainDiagnostics.lineCounts.view).toBeGreaterThan(0);
    expect(payload.chainDiagnostics.monotonic.latexToMarkdown).toBe(true);
    expect(payload.chainDiagnostics.monotonic.markdownToLatex).toBe(true);
    expect(payload.chainDiagnostics.monotonic.latexToHtml).toBe(true);
    expect(payload.chainDiagnostics.monotonic.htmlToLatex).toBe(true);
    expect(payload.chainDiagnostics.monotonic.viewLineToLatex).toBe(true);

    expect(payload.latexLineChains).toHaveLength(3);
    expect(payload.latexLineChains[0]?.latexLine).toBe(3);
    expect((payload.latexLineChains[1]?.viewLineEnd ?? 0)).toBeGreaterThan(payload.latexLineChains[1]?.viewLineStart ?? 0);

    expect(payload.viewLineChains).toHaveLength(2);
    expect(payload.viewLineChains[0]?.viewLine).toBe(1);
    expect(payload.viewLineChains[0]?.latexLine).toBe(1);

    expect(payload.outlineTitleChains).toHaveLength(2);
    expect(payload.outlineTitleChains.map((entry) => entry.matchedTitle)).toEqual(['Alpha', 'Beta']);
  });
});