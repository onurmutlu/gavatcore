const TOKEN_KEY = 'gavatcore.panel.access';
export const session = {
  get token() { return sessionStorage.getItem(TOKEN_KEY); },
  set(token) { sessionStorage.setItem(TOKEN_KEY, token); },
  clear() { sessionStorage.removeItem(TOKEN_KEY); },
};

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

export async function api(path, { method = 'GET', body, authenticated = true } = {}) {
  let response;
  try {
    response = await fetch(`/api${path}`, {
      method, cache: 'no-store', signal: AbortSignal.timeout(12000),
      headers: {
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...(authenticated && session.token ? { Authorization: `Bearer ${session.token}` } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch {
    throw new ApiError('Sunucuya ulaşılamadı. Bağlantıyı kontrol edip yeniden deneyin.', 0);
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = response.status === 401
      ? (authenticated ? 'Oturumunuz sona erdi. Tekrar giriş yapın.' : 'Kullanıcı adı veya şifre hatalı.')
      : response.status === 422 ? 'Alanları kontrol edin; gönderilen değerler geçersiz.'
      : response.status >= 500 ? 'Sunucu işlemi tamamlayamadı. Yeniden deneyin.'
      : (typeof data?.detail === 'string' ? data.detail : 'İşlem tamamlanamadı.');
    if (authenticated && [401, 403].includes(response.status)) {
      session.clear();
      window.dispatchEvent(new CustomEvent('session-expired'));
    }
    throw new ApiError(message, response.status);
  }
  if (data === null) throw new ApiError('Sunucudan geçersiz yanıt alındı.', response.status);
  return data;
}
