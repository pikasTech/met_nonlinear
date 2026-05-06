import { defineConfig, devices } from '@playwright/test';

const bun = 'C:/Users/liang/.bun/bin/bun.exe';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 120000,
  expect: {
    timeout: 15000,
  },
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:3001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: `${bun} run dev`,
      cwd: 'D:/work/met_nonlinear/src/webui/server',
      url: 'http://127.0.0.1:3000/api/health',
      reuseExistingServer: true,
      timeout: 180000,
    },
    {
      command: `${bun} run dev -- --host 127.0.0.1`,
      cwd: 'D:/work/met_nonlinear/src/webui',
      url: 'http://127.0.0.1:3001',
      reuseExistingServer: true,
      timeout: 180000,
    },
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});