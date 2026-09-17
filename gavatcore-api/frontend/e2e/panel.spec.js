import { test, expect } from '@playwright/test';

async function login(page) {
  await page.goto('/panel/');
  await page.getByLabel('Kullanıcı adı', { exact: true }).fill('panel_local');
  await page.getByLabel('Şifre', { exact: true }).fill('local-panel-only');
  await page.getByRole('button', { name: 'Giriş yap' }).click();
  await expect(page.getByRole('heading', { name: 'Bot yönetimi', exact: true })).toBeVisible();
  await expect(page.locator('.bot-row')).toHaveCount(3);
}

test('login, real list, detail, persistent settings and logout', async ({ page }) => {
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  await login(page);
  await expect(page.locator('#preview')).toBeVisible();
  await page.getByRole('button', { name: 'Lara · Yerel detay' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.getByLabel('Yanıt modu').selectOption('hybrid');
  await page.getByLabel('Zamanlayıcı etkin').check();
  await page.getByLabel('Zamanlayıcı aralığı (saniye)').fill('480');
  await page.getByRole('button', { name: 'Ayarları kaydet' }).click();
  await expect(page.getByText('Ayarlar veritabanına kaydedildi.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Başlat', exact: true })).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Durdur', exact: true })).toBeDisabled();
  await page.reload();
  await page.getByRole('button', { name: 'Lara · Yerel detay' }).click();
  await expect(page.getByLabel('Yanıt modu')).toHaveValue('hybrid');
  await expect(page.getByLabel('Zamanlayıcı aralığı (saniye)')).toHaveValue('480');
  await expect(page.getByLabel('Zamanlayıcı etkin')).toBeChecked();
  await page.getByRole('button', { name: 'Detayı kapat' }).click();
  await page.getByRole('button', { name: 'Çıkış yap' }).click();
  await expect(page.getByRole('button', { name: 'Giriş yap' })).toBeVisible();
  expect(await page.evaluate(() => sessionStorage.getItem('gavatcore.panel.access'))).toBeNull();
  expect(errors).toEqual([]);
});

test('invalid credentials return 401 with an actionable error', async ({ page }) => {
  await page.goto('/panel/');
  await page.getByLabel('Kullanıcı adı', { exact: true }).fill('panel_local');
  await page.getByLabel('Şifre', { exact: true }).fill('incorrect');
  const response = page.waitForResponse('/api/auth/login');
  await page.getByRole('button', { name: 'Giriş yap' }).click();
  expect((await response).status()).toBe(401);
  await expect(page.getByRole('alert')).toContainText('Kullanıcı adı veya şifre hatalı.');
});

test('search, filter, empty result and recovery', async ({ page }) => {
  await login(page);
  await page.getByLabel('Bot ara').fill('Lara');
  await expect(page.locator('.bot-row')).toHaveCount(1);
  await page.getByLabel('Bot ara').fill('does-not-exist');
  await expect(page.getByText('Eşleşen bot bulunamadı')).toBeVisible();
  await page.getByLabel('Bot ara').fill('');
  await page.getByLabel('Durum filtresi').selectOption('online');
  await expect(page.locator('.bot-row')).toHaveCount(0);
  await page.getByLabel('Durum filtresi').selectOption('all');
  await expect(page.locator('.bot-row')).toHaveCount(3);
});

test('API outage is shown, previous data is marked stale, retry recovers', async ({ page }) => {
  await login(page);
  await page.route('**/api/bots/', route => route.abort('failed'));
  await page.getByRole('button', { name: 'Yenile', exact: false }).click();
  await expect(page.locator('#data-error')).toContainText('güncel olmayabilir');
  await expect(page.locator('.bot-row')).toHaveCount(3);
  await page.unroute('**/api/bots/');
  await page.getByRole('button', { name: 'Yenile', exact: false }).click();
  await expect(page.locator('#data-error')).toBeHidden();
  await expect(page.getByText('API bağlantısı açık')).toBeVisible();
});

test('expired or invalid session returns to login and clears stored token', async ({ page }) => {
  await login(page);
  await page.evaluate(() => sessionStorage.setItem('gavatcore.panel.access', 'invalid'));
  await page.getByRole('button', { name: 'Yenile', exact: false }).click();
  await expect(page.getByRole('alert')).toContainText('Oturumunuz sona erdi');
  await expect(page.locator('#workspace')).toBeHidden();
});

test('owner isolation, input validation, refresh-token rejection and empty account', async ({ request, page }) => {
  const own = await request.post('/api/auth/login', { data: { username: 'panel_local', password: 'local-panel-only' } });
  const tokens = await own.json();
  const headers = { Authorization: `Bearer ${tokens.access_token}` };
  const bots = await (await request.get('/api/bots/', { headers })).json();
  const path = `/api/panel/bots/${bots[0].id}/settings`;
  expect((await request.put(path, { headers, data: { reply_mode: 'invalid', scheduler_enabled: true, scheduler_interval: 1 } })).status()).toBe(422);
  expect((await request.get('/api/bots/', { headers: { Authorization: `Bearer ${tokens.refresh_token}` } })).status()).toBe(401);
  const outsider = await request.post('/api/auth/register', { data: { username: `empty_${Date.now()}`, password: 'test-password-only' } });
  expect(outsider.ok()).toBeTruthy();
  const token = (await outsider.json()).access_token;
  const otherHeaders = { Authorization: `Bearer ${token}` };
  expect((await request.get(path, { headers: otherHeaders })).status()).toBe(404);
  expect((await request.put(path, { headers: otherHeaders, data: { reply_mode: 'gpt', scheduler_enabled: false, scheduler_interval: 60 } })).status()).toBe(404);
  await page.goto('/panel/');
  await page.evaluate(token => sessionStorage.setItem('gavatcore.panel.access', token), token);
  await page.reload();
  await expect(page.getByText('Henüz bot yok')).toBeVisible();
});

test('mobile layout and screenshot have no horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  await page.screenshot({ path: 'test-results/panel-mobile.png', fullPage: true });
  await page.getByRole('button', { name: 'Lara · Yerel detay' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.getByRole('button', { name: 'Detayı kapat' }).click();
});

test('desktop screenshot and JavaScript error check', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  await login(page);
  await page.screenshot({ path: 'test-results/panel-desktop.png', fullPage: true });
  expect(errors).toEqual([]);
});
