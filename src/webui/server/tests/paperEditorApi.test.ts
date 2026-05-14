import { afterEach, describe, expect, test } from 'bun:test';
import fs from 'fs';
import path from 'path';
import { createServer, Server } from 'http';
import type { AddressInfo } from 'net';

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

function createPaperEditorFixture(entry = 'probe.tex') {
  const fixtureRoot = fs.mkdtempSync(path.join(repoRoot, 'cache', 'webui', 'paper-editor', 'api-fixture-'));
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
  ].join('\n');

  fs.writeFileSync(path.join(latexDir, entry), initialSource, 'utf-8');
  return { fixtureRoot, entry };
}

async function startPaperEditorApiServer(rootDir: string) {
  process.env.MET_NONLINEAR_DISABLE_AUTO_LISTEN = '1';
  const { createApp } = await import('../src/index');
  const app = createApp({ rootDir });
  const server = createServer(app);
  tempPaths.push('__server__');
  await new Promise<void>((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => resolve());
  });
  const address = server.address() as AddressInfo;
  return {
    baseUrl: `http://127.0.0.1:${address.port}`,
    async close() {
      await new Promise<void>((resolve, reject) => {
        server.close((error) => (error ? reject(error) : resolve()));
      });
    },
  };
}

async function loadDocument(baseUrl: string, entry: string) {
  const response = await fetch(`${baseUrl}/api/paper-editor/document?entry=${encodeURIComponent(entry)}&viewColumns=80`, {
    headers: {
      'X-Paper-Editor-Client-Id': 'api-test-load',
      'X-Paper-Editor-Reason': 'api-test-load',
    },
  });
  expect(response.status).toBe(200);
  return await response.json() as {
    source: string;
    revision: string;
    sourceView: { text: string; columns: number };
  };
}

async function saveDocument(baseUrl: string, entry: string, payload: Record<string, unknown>, clientId: string) {
  const response = await fetch(`${baseUrl}/api/paper-editor/document`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-Paper-Editor-Client-Id': clientId,
      'X-Paper-Editor-Reason': `${clientId}-save`,
      'X-Paper-Editor-Known-Revision': String(payload.baseRevision ?? ''),
    },
    body: JSON.stringify({ entry, ...payload }),
  });
  const body = await response.json();
  return { status: response.status, body };
}

describe('paper editor API save', () => {
  test('merges three stale non-overlapping saves through the HTTP interface', async () => {
    const { fixtureRoot, entry } = createPaperEditorFixture();
    const server = await startPaperEditorApiServer(fixtureRoot);

    try {
      const baseDocument = await loadDocument(server.baseUrl, entry);
      const baseSource = baseDocument.source;
      const sharedPayload = {
        baseSource,
        baseSourceViewText: baseDocument.sourceView.text,
        baseRevision: baseDocument.revision,
        viewColumns: baseDocument.sourceView.columns,
      };

      const [saveA, saveB, saveC] = await Promise.all([
        saveDocument(server.baseUrl, entry, {
          ...sharedPayload,
          source: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
          sourceViewText: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
        }, 'api-test-a'),
        saveDocument(server.baseUrl, entry, {
          ...sharedPayload,
          source: baseSource.replace('Anchor B base line.', 'Anchor B base line. [client-b merged]'),
          sourceViewText: baseSource.replace('Anchor B base line.', 'Anchor B base line. [client-b merged]'),
        }, 'api-test-b'),
        saveDocument(server.baseUrl, entry, {
          ...sharedPayload,
          source: baseSource.replace('Anchor C base line.', 'Anchor C base line. [client-c merged]'),
          sourceViewText: baseSource.replace('Anchor C base line.', 'Anchor C base line. [client-c merged]'),
        }, 'api-test-c'),
      ]);

      const finalDocument = await loadDocument(server.baseUrl, entry);

      expect(saveA.status).toBe(200);
      expect(saveB.status).toBe(200);
      expect(saveC.status).toBe(200);
      expect(finalDocument.source).toContain('Anchor A base line. [client-a merged]');
      expect(finalDocument.source).toContain('Anchor B base line. [client-b merged]');
      expect(finalDocument.source).toContain('Anchor C base line. [client-c merged]');
    } finally {
      await server.close();
    }
  });

  test('returns 409 for stale same-line conflicts through the HTTP interface', async () => {
    const { fixtureRoot, entry } = createPaperEditorFixture();
    const server = await startPaperEditorApiServer(fixtureRoot);

    try {
      const baseDocument = await loadDocument(server.baseUrl, entry);
      const baseSource = baseDocument.source;
      const sharedPayload = {
        baseSource,
        baseSourceViewText: baseDocument.sourceView.text,
        baseRevision: baseDocument.revision,
        viewColumns: baseDocument.sourceView.columns,
      };

      const firstSave = await saveDocument(server.baseUrl, entry, {
        ...sharedPayload,
        source: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
        sourceViewText: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-a merged]'),
      }, 'api-test-first');

      const conflictingSave = await saveDocument(server.baseUrl, entry, {
        ...sharedPayload,
        source: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-b conflicting edit]'),
        sourceViewText: baseSource.replace('Anchor A base line.', 'Anchor A base line. [client-b conflicting edit]'),
      }, 'api-test-conflict');

      expect(firstSave.status).toBe(200);
      expect(conflictingSave.status).toBe(409);
      expect(conflictingSave.body).toHaveProperty('currentRevision');
      expect(String(conflictingSave.body.error ?? '')).toContain('could not be applied cleanly');
    } finally {
      await server.close();
    }
  });
});