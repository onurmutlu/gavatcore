# GavatCore web panel

Modüler HTML/CSS/JavaScript paneli, mevcut FastAPI uygulaması tarafından `/panel/`
adresinde sunulur. Üretimde JavaScript framework veya Node sunucusu gerektirmez.
API çağrıları aynı origin üzerindedir; frontend içinde sabit port veya servis adresi yoktur.

## Yerel çalıştırma

Depo kökünde (Node 20+, Python 3.13 ile doğrulandı):

```sh
python3 -m venv .local/panel-venv
.local/panel-venv/bin/python -m pip install -r gavatcore-api/requirements-panel.txt
npm --prefix gavatcore-api/frontend ci
npm --prefix gavatcore-api/frontend run build
.local/panel-venv/bin/python scripts/development/run_web_panel.py
```

Adres: http://127.0.0.1:18082/panel/

Yerel hesap: `panel_local` / `local-panel-only`.

Bu komut yalnızca `127.0.0.1` üzerinde dinler; `.env` dosyasını okumaz, canlı
Telegram/API kimlik bilgilerini kullanmaz. `.local/web-panel/panel.sqlite3`
dosyasında ayrı ve kalıcı bir SQLite veritabanı oluşturur. Üç örnek bot kaydı
ilk açılışta eklenir. Örnek kayıtlar üst bantta açıkça belirtilir; tüm istatistikler
bu veritabanından gelir, botlar çevrimiçiymiş gibi gösterilmez. Ayarlar sonraki
açılışlarda korunur; sunucu yeniden başlayınca yeniden giriş gerekir.

## Mevcut API ile kullanım

Paneli derleyip mevcut `app.main:app` uygulamasını normal yapılandırmasıyla
başlatın. `DATABASE_URL` artık gerçekten kullanılır; PostgreSQL varsayılanı korunur.
`PANEL_LOCAL_PREVIEW` varsayılan olarak kapalıdır. Yerel çalıştırma komutunu canlı
ortamda kullanmayın; normal API kullanıcıları kendi hesaplarıyla giriş yapar.

Giriş tokenı sekme kapsamındaki `sessionStorage` içinde tutulur; çıkışta veya
401/403 yanıtında temizlenir. Refresh-token yenileme mevcut API'de tamamlanmadığı
için süresi dolan oturum yeniden giriş ister.

## Doğrulama

```sh
PANEL_TEST_PYTHON="$PWD/.local/panel-venv/bin/python" npm --prefix gavatcore-api/frontend run test:e2e
```

Yerel Google Chrome kurulumu gerekir. Testler ayrı geçici SQLite veritabanı ve
18083 portundaki gerçek FastAPI sunucusuyla çalışır. Preview veritabanını değiştirmez.
Sadece bağlantı kesintisi testinde ağ hatası kontrollü olarak enjekte edilir.
Testler giriş, kalıcı ayar kaydı, yetkilendirme, yanlış şifre, arama, filtre,
boş hesap, bağlantı kesilmesi, oturum sonlanması ve mobil görünümü kapsar.
Ekran görüntüleri `test-results/` altına yazılır.

## Bu sürümün kapsamı

- Kullanıcı girişi / çıkışı, bot listesi, arama ve durum filtresi.
- Bot detayı, veritabanındaki son hata, mesaj sayıları.
- Yanıt modu ve zamanlayıcı ayarlarının sahiplik kontrolüyle kalıcı kaydı.
- API hatası, boş durum, eski veri uyarısı ve 30 saniyelik yenileme.
- Mobil ve masaüstü görünüm.

Başlat/durdur ve bot oluşturma bu panelde açılmadı. Eski bot launcher'ı gerçek
süreç sonlandırmasını uygulamıyor; panel yanlış başarı bildirmemek için bu işlemleri
sunmuyor. Eski API yaşam döngüsü uçları bu değişiklikte yeniden yazılmadı.
Canlı Telegram oturumu, mesaj gönderimi, ödeme, gerçek süreç kontrolü ve canlı log
akışı bu doğrulamanın kapsamı dışındadır. Son kayıtlı hata, canlı log akışı değildir.

Eski Flutter ve kök `index.html` korunmuştur. Yeni panel bağımsız olarak devreye alınabilir.
