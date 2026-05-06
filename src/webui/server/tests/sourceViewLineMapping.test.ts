import { describe, expect, test } from 'bun:test';
import { buildWrappedSourceView } from '../src/sourceViewLineMapping';

describe('wrapped source view', () => {
  test('buildWrappedSourceView returns deterministic wrapped text and hard-break flags', () => {
    const source = ['abcdefgh', 'xy', 'tail'].join('\n');
    const wrapped = buildWrappedSourceView(source, 4, 2);

    expect(wrapped.text).toBe(['abcd', 'efgh', 'xy', 'tail'].join('\n'));
    expect(wrapped.totalViewLines).toBe(4);
    expect(wrapped.viewLineToLatex.slice(1)).toEqual([1, 1, 2, 3]);
    expect(wrapped.latexToViewLineStart.slice(1)).toEqual([1, 3, 4]);
    expect(wrapped.latexToViewLineEnd.slice(1)).toEqual([2, 3, 4]);
    expect(wrapped.viewLineEndsWithSourceBreak.slice(1)).toEqual([false, true, true, false]);
  });

  test('buildWrappedSourceView counts CJK characters as double-width cells', () => {
    const wrapped = buildWrappedSourceView('ab中文cd', 4, 2);

    expect(wrapped.text).toBe(['ab中', '文cd'].join('\n'));
    expect(wrapped.totalViewLines).toBe(2);
    expect(wrapped.viewLineToLatex.slice(1)).toEqual([1, 1]);
    expect(wrapped.latexToViewLineStart.slice(1)).toEqual([1]);
    expect(wrapped.latexToViewLineEnd.slice(1)).toEqual([2]);
    expect(wrapped.viewLineEndsWithSourceBreak.slice(1)).toEqual([false, false]);
  });
});