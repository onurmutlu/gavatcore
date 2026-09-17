import { mkdir, copyFile, rm } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
process.chdir(fileURLToPath(new URL('.', import.meta.url)));
for (const file of ['app.js', 'api.js']) execFileSync(process.execPath, ['--check', file], { stdio: 'inherit' });
await rm('dist', { recursive: true, force: true });
await mkdir('dist');
for (const file of ['index.html', 'styles.css', 'app.js', 'api.js']) await copyFile(file, `dist/${file}`);
console.log('Panel build ready: dist/ (no runtime dependencies)');
