import { expect, test } from '@playwright/test';

test('paper editor loads main.tex and updates preview without saving', async ({ page }) => {
  await page.goto('/paper-editor');

  await expect(page.getByRole('heading', { name: 'LaTeX quick preview editor' })).toBeVisible();
  await expect(page.getByTestId('paper-editor-source')).toContainText('\\documentclass[sn-nature]{sn-jnl}');
  await expect(page.getByTestId('paper-editor-outline')).toContainText('Introduction');
  await expect(page.getByTestId('paper-editor-preview')).toContainText('On-Board Real-Time AI Compensation');

  const sourceEditor = page.getByTestId('paper-editor-source');
  await sourceEditor.evaluate((node) => {
    const element = node as HTMLTextAreaElement;
    const marker = '\\end{document}';
    const index = element.value.lastIndexOf(marker);
    element.focus();
    element.setSelectionRange(index, index);
  });
  await page.keyboard.type('\n\\section{Playwright Probe}\nPreview body with inline math $a+b$.\n');

  await expect(page.getByTestId('paper-editor-status')).toContainText('Unsaved changes');
  await expect(page.getByTestId('paper-editor-outline')).toContainText('Playwright Probe');
  await expect(page.getByTestId('paper-editor-preview')).toContainText('Preview body with inline math');

  await page.getByRole('button', { name: 'Markdown output' }).click();
  await expect(page.getByTestId('paper-editor-preview')).toContainText('## Playwright Probe');

  await page.getByRole('button', { name: 'Rendered preview' }).click();
  await page.getByTestId('paper-editor-outline').getByRole('button', { name: /Playwright Probe/ }).click();
  await expect(page.getByTestId('paper-editor-preview')).toContainText('Playwright Probe');

  const figureSurfaces = page.getByTestId('paper-editor-preview').locator('img, [data-testid="paper-editor-missing-figure"]');
  await expect(figureSurfaces.first()).toBeVisible();
});