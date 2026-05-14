import { afterEach, describe, expect, test } from 'bun:test';
import fs from 'fs';
import path from 'path';
import {
  loadPaperEditorDocument,
  PaperEditorSaveConflictError,
  savePaperEditorDocument,
} from '../src/paperEditor';

const repoRoot = path.resolve(import.meta.dir, '..', '..', '..', '..');
const tempPaths: string[] = [];

afterEach(() => {
  for (const filePath of tempPaths.splice(0)) {
    if (!fs.existsSync(filePath)) {
      continue;
    }
    const stats = fs.lstatSync(filePath);
    if (stats.isDirectory()) {
      fs.rmSync(filePath, { recursive: true, force: true });
    } else {
      fs.unlinkSync(filePath);
    }
  }
});

function createPaperEditorFixture(entry = 'probe.tex', lineEnding = '\n') {
  const fixtureRoot = fs.mkdtempSync(path.join(repoRoot, 'cache', 'webui', 'paper-editor', 'save-fixture-'));
  tempPaths.push(fixtureRoot);

  const latexDir = path.join(fixtureRoot, 'docs', 'paper', 'latex');
  fs.mkdirSync(latexDir, { recursive: true });

  const initialSource = [
    '\\section{Three Client Patch Probe}',
    '',
    'Anchor A base line.',
    'Anchor B base line.',
    'Anchor C base line.',
    '',
    'Footer base line.',
  ].join(lineEnding);

  fs.writeFileSync(path.join(latexDir, entry), initialSource, 'utf-8');
  return { fixtureRoot, entry, initialSource };
}

describe('paper editor patch save', () => {
  test('merges three stale non-overlapping saves from the same base revision', () => {
    const { fixtureRoot, entry } = createPaperEditorFixture();
    const baseDocument = loadPaperEditorDocument(fixtureRoot, entry, 80);
    const baseSource = baseDocument.source;
    const sharedInput = {
      entry,
      baseSource,
      baseSourceViewText: baseDocument.sourceView.text,
      baseRevision: baseDocument.revision,
      sourceViewColumns: baseDocument.sourceView.columns,
    };

    const saveA = savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
      sourceViewText: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
    });
    const saveB = savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: baseSource.replace('Anchor B base line.', 'Anchor B base line. [client-b merged]'),
      sourceViewText: baseSource.replace('Anchor B base line.', 'Anchor B base line. [client-b merged]'),
    });
    const saveC = savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: baseSource.replace('Anchor C base line.', 'Anchor C base line. [client-c merged]'),
      sourceViewText: baseSource.replace('Anchor C base line.', 'Anchor C base line. [client-c merged]'),
    });

    const finalSource = fs.readFileSync(path.join(fixtureRoot, 'docs', 'paper', 'latex', entry), 'utf-8');

    expect(saveA.audit.patchAppliedToStaleRevision).toBe(false);
    expect(saveB.audit.patchAppliedToStaleRevision).toBe(true);
    expect(saveC.audit.patchAppliedToStaleRevision).toBe(true);
    expect(finalSource).toContain('Anchor A base line. [client-a merged]');
    expect(finalSource).toContain('Anchor B base line. [client-b merged]');
    expect(finalSource).toContain('Anchor C base line. [client-c merged]');
  });

  test('rejects stale saves that edit the same line differently', () => {
    const { fixtureRoot, entry } = createPaperEditorFixture();
    const baseDocument = loadPaperEditorDocument(fixtureRoot, entry, 80);
    const baseSource = baseDocument.source;
    const sharedInput = {
      entry,
      baseSource,
      baseSourceViewText: baseDocument.sourceView.text,
      baseRevision: baseDocument.revision,
      sourceViewColumns: baseDocument.sourceView.columns,
    };

    savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
      sourceViewText: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
    });

    expect(() => savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-b conflicting edit]'),
      sourceViewText: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-b conflicting edit]'),
    })).toThrow(PaperEditorSaveConflictError);
  });

  test('merges stale saves when browser-normalized LF edits target a CRLF file', () => {
    const { fixtureRoot, entry } = createPaperEditorFixture('probe-crlf.tex', '\r\n');
    const baseDocument = loadPaperEditorDocument(fixtureRoot, entry, 80);
    const browserBaseSource = baseDocument.source.replace(/\r\n/g, '\n');
    const browserBaseView = baseDocument.sourceView.text.replace(/\r\n/g, '\n');
    const sharedInput = {
      entry,
      baseSource: browserBaseSource,
      baseSourceViewText: browserBaseView,
      baseRevision: baseDocument.revision,
      sourceViewColumns: baseDocument.sourceView.columns,
    };

    savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: browserBaseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
      sourceViewText: browserBaseView,
    });
    savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: browserBaseSource.replace('Anchor B base line.', 'Anchor B base line. [client-b merged]'),
      sourceViewText: browserBaseView,
    });
    savePaperEditorDocument(fixtureRoot, {
      ...sharedInput,
      source: browserBaseSource.replace('Anchor C base line.', 'Anchor C base line. [client-c merged]'),
      sourceViewText: browserBaseView,
    });

    const finalSource = fs.readFileSync(path.join(fixtureRoot, 'docs', 'paper', 'latex', entry), 'utf-8');

    expect(finalSource).toContain('Anchor A base line. [client-a merged]');
    expect(finalSource).toContain('Anchor B base line. [client-b merged]');
    expect(finalSource).toContain('Anchor C base line. [client-c merged]');
    expect(finalSource).toContain('\r\n');
  });
});