import { api, session } from './api.js';

const $ = (id) => document.getElementById(id);
const number = new Intl.NumberFormat('tr-TR');
let bots = [], user = null, selectedId = null, refreshing = false, generation = 0, detailRequest = 0;
const modeNames = { manual: 'Manuel', manualplus: 'Manuel Plus', hybrid: 'Hibrit', gpt: 'GPT' };
function text(id, value) { $(id).textContent = value; }
function notice(message) { text('notice', message); $('notice').hidden = !message; }
function reset(message = '') {
  generation++; detailRequest++; user = null; bots = []; selectedId = null; session.clear();
  $('detail-dialog').close(); $('workspace').hidden = true; $('login-view').hidden = false;
  $('password').value = ''; text('login-error', message); $('login-error').hidden = !message;
  $('bot-list').replaceChildren(); notice('');
}
window.addEventListener('session-expired', () => reset('Oturumunuz sona erdi. Tekrar giriş yapın.'));
$('logout').addEventListener('click', () => reset());

async function capabilities() {
  try {
    const data = await api('/panel/capabilities', { authenticated: false });
    $('preview').hidden = !data.local_preview; $('preview-login').hidden = !data.local_preview;
    text('capability-reason', data.process_control_reason);
  } catch { text('capability-reason', 'Sunucu yetenekleri alınamadı. Süreç kontrolü kullanılamıyor.'); }
}

async function enter() {
  const epoch = generation;
  const profile = await api('/auth/me');
  if (epoch !== generation) return;
  user = profile;
  text('account-name', user.full_name || user.username); text('avatar', user.username.slice(0, 1).toUpperCase());
  $('login-view').hidden = true; $('workspace').hidden = false; notice('');
  await refresh();
}
$('login-form').addEventListener('submit', async (event) => {
  event.preventDefault(); $('login-submit').disabled = true; $('login-error').hidden = true;
  try {
    const result = await api('/auth/login', { method: 'POST', authenticated: false, body: {
      username: $('username').value.trim(), password: $('password').value,
    } });
    session.set(result.access_token); $('password').value = ''; await enter();
  } catch (error) { text('login-error', error.message); $('login-error').hidden = false; }
  finally { $('login-submit').disabled = false; }
});

function status(bot) {
  if ((bot.session_status || bot.status) === 'error') return ['Hatalı', 'error'];
  if (bot.is_online) return ['Çevrimiçi', 'online'];
  return ['Çevrimdışı', 'offline'];
}
function render() {
  text('total', number.format(bots.length)); text('online', number.format(bots.filter(b => b.is_online).length));
  text('messages', number.format(bots.reduce((sum, b) => sum + b.messages_sent, 0)));
  text('errors', number.format(bots.filter(b => b.session_status === 'error').length)); text('count', bots.length);
  const query = $('search').value.toLocaleLowerCase('tr-TR');
  const filtered = bots.filter(b => `${b.bot_name} ${b.personality}`.toLocaleLowerCase('tr-TR').includes(query)
    && ($('filter').value === 'all' || status(b)[1] === $('filter').value));
  $('bot-list').replaceChildren(); $('empty').hidden = filtered.length > 0;
  $('empty').querySelector('h3').textContent = bots.length ? 'Eşleşen bot bulunamadı' : 'Henüz bot yok';
  $('empty').querySelector('p').textContent = bots.length ? 'Arama veya durum filtresini değiştirebilirsiniz.' : 'Bu hesaba bağlı bir bot kaydı bulunamadı.';
  for (const bot of filtered) {
    const row = document.createElement('article'); row.className = 'bot-row';
    row.innerHTML = '<div class="bot-identity"><span class="bot-avatar"></span><div><h3></h3><p></p></div></div><span class="badge"></span><div class="row-stat"><strong></strong><span>gönderilen mesaj</span></div><span class="mode"></span><button class="detail-button">Detay <span aria-hidden="true">↗</span></button>';
    row.querySelector('h3').textContent = bot.bot_name;
    row.querySelector('.bot-avatar').textContent = bot.bot_name.slice(0, 1).toUpperCase();
    row.querySelector('.bot-identity p').textContent = bot.personality;
    const [label, css] = status(bot); const badge = row.querySelector('.badge'); badge.textContent = label; badge.classList.add(css);
    row.querySelector('.row-stat strong').textContent = number.format(bot.messages_sent);
    row.querySelector('.mode').textContent = modeNames[bot.reply_mode] || bot.reply_mode;
    const button = row.querySelector('button'); button.setAttribute('aria-label', `${bot.bot_name} detay`);
    button.addEventListener('click', () => openDetail(bot, button)); $('bot-list').append(row);
  }
}
async function refresh() {
  if (!user || refreshing) return;
  const epoch = generation; refreshing = true; $('refresh').disabled = true;
  try {
    const records = await api('/bots/');
    if (epoch !== generation) return;
    if (!Array.isArray(records)) throw new Error('Bot listesi geçersiz bir biçimde geldi.');
    bots = records; render(); $('data-error').hidden = true;
    text('connection', 'API bağlantısı açık'); $('connection').classList.remove('failed');
    text('updated', `Son güncelleme: ${new Date().toLocaleTimeString('tr-TR')}`);
  } catch (error) {
    if (epoch !== generation) return;
    text('data-error', `${error.message} ${bots.length ? 'Gösterilen kayıtlar güncel olmayabilir.' : ''}`);
    $('data-error').hidden = false; text('connection', 'Bağlantı sorunu'); $('connection').classList.add('failed');
    $('empty').hidden = true;
  } finally { refreshing = false; $('refresh').disabled = false; $('loading').hidden = true; }
}
$('refresh').addEventListener('click', refresh);
for (const id of ['search', 'filter']) $(id).addEventListener('input', render);
setInterval(() => { if (!document.hidden) refresh(); }, 30000);

async function openDetail(bot, button) {
  const request = ++detailRequest, epoch = generation; button.disabled = true; notice('');
  try {
    const [details, settings] = await Promise.all([api(`/bots/${bot.id}`), api(`/panel/bots/${bot.id}/settings`)]);
    if (epoch !== generation || request !== detailRequest) return;
    selectedId = bot.id; text('detail-name', bot.bot_name); text('detail-status', `${bot.personality} · ${status(details)[0]}`);
    $('detail-metrics').replaceChildren();
    for (const [label, value] of [['Gönderilen', details.messages_sent], ['Alınan', details.messages_received], ['Hata sayısı', details.error_count]]) {
      const cell = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
      dt.textContent = label; dd.textContent = number.format(value); cell.append(dt, dd); $('detail-metrics').append(cell);
    }
    text('last-error', details.last_error || 'Kayıtlı hata bulunmuyor.');
    $('reply-mode').value = settings.reply_mode; $('scheduler-enabled').checked = settings.scheduler_enabled;
    $('scheduler-interval').value = settings.scheduler_interval; text('save-message', '');
    $('detail-dialog').showModal();
  } catch (error) { if (epoch === generation) notice(error.message); }
  finally { button.disabled = false; }
}
$('close-detail').addEventListener('click', () => $('detail-dialog').close());
$('detail-dialog').addEventListener('close', () => { selectedId = null; });
$('settings-form').addEventListener('submit', async (event) => {
  event.preventDefault(); const id = selectedId, epoch = generation;
  if (id === null) return;
  $('save-settings').disabled = true; text('save-message', 'Kaydediliyor…');
  try {
    await api(`/panel/bots/${id}/settings`, { method: 'PUT', body: {
      reply_mode: $('reply-mode').value, scheduler_enabled: $('scheduler-enabled').checked,
      scheduler_interval: Number($('scheduler-interval').value),
    } });
    if (epoch === generation && selectedId === id) text('save-message', 'Ayarlar veritabanına kaydedildi.');
    await refresh();
  } catch (error) { if (epoch === generation && selectedId === id) text('save-message', error.message); }
  finally { $('save-settings').disabled = false; }
});

capabilities();
if (session.token) enter().catch(error => { if (session.token) { notice(error.message); } });
