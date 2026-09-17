import { defineConfig } from '@playwright/test';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
const testData = mkdtempSync(join(tmpdir(), 'gavatcore-panel-e2e-'));
const python = process.env.PANEL_TEST_PYTHON || resolve(root, '.venv/bin/python');
export default defineConfig({
  testDir: './e2e', fullyParallel: false, workers: 1, retries: 0,
  timeout: 30000, reporter: 'list',
  use: { baseURL: 'http://127.0.0.1:18083', channel: 'chrome', screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  webServer: {
    command: `"${python}" "${root}/scripts/development/run_web_panel.py" --port 18083 --data-dir "${testData}"`,
    url: 'http://127.0.0.1:18083/health', reuseExistingServer: false, timeout: 30000,
  },
});
