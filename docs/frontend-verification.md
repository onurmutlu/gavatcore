# Frontend doğrulama ve karar — 17 Eylül 2026

## Önceki arayüzlerin sonucu

| Kontrol | Sonuç |
| --- | --- |
| Flutter `flutter build web --no-pub` | Başarılı; `main.dart` Telegram giriş ekranını açıyor. |
| Flutter `flutter build web --no-pub --target lib/main_updated.dart --output build/web-updated` | Başarısız; eski paket importu, nullable tipler, auth model uyuşmazlığı ve `dynamic.fromJson` üretim hataları. |
| Flutter `flutter test --no-pub` | Başarısız; test `gavatcore_mobile/app.dart` paketini ve olmayan `App` sınıfını kullanıyor. |
| Derlenen Flutter'ın Chrome kontrolü | Giriş ekranı açıldı. Telegram backend girişinin tamamlandığı doğrulanmadı. |
| Eski HTML panelinin Chrome kontrolü | Başlık ve yenileme düğmesi açıldı; bot verileri yüklenmedi. |
| HTML/API sözleşmesi | HTML `/api/bots/demo` uçlarını çağırıyor; mevcut SaaS router bu yolları tanımlamıyor. |
| Eski HTML düzenleme akışı | Kaydetme isteği olmadan başarı mesajı veriyor. |
| SaaS veritabanı | Ortam ayarını kullanmayan sabit PostgreSQL adresi tespit edildi; yeni panel çalışması kapsamında düzeltildi. |
| Eski bot launcher | Stop yalnızca veritabanını güncelliyor; gerçek süreç sonlandırması TODO. Yeni panelde kontrol kapalı. |

## Karar ve uygulama

Web odaklı ilk sürüm için yeni, modüler ve bağımlılıksız bir frontend; mevcut
FastAPI kullanıcı/bot modellerinin yeniden kullanılması. Eski arayüzler silinmedi.
Bu karar derlenebilen Flutter giriş ekranının bir yönetim paneli olmadığı ve
geniş panelin derleme/entegrasyon maliyeti nedeniyle alındı.

Yeni frontend: `gavatcore-api/frontend/`. Sunum: `/panel/`. Yeni ayar uçları:
`GET/PUT /api/panel/bots/{id}/settings`. Liste/detay ve kimlik doğrulama mevcut API'yi kullanır.
Bu uçlar bot sahibini kontrol eder ve tip/aralık doğrulaması yapar.

## Yeni panel test sonuçları

`npm run build`: başarılı. Chrome/Playwright, gerçek yerel FastAPI ve ayrı SQLite ile:

1. Giriş → liste → detay → ayar kaydı → sayfa yenileme → kayıt doğrulama → çıkış.
2. Yanlış şifre: HTTP 401 ve görünür hata.
3. Arama, durum filtresi, sonuç bulunamaması ve geri dönüş.
4. Kontrollü ağ kesintisi, eski veri uyarısı ve yeniden deneme.
5. Geçersiz oturumda giriş ekranına dönüş ve token temizliği.
6. Başka kullanıcının botuna GET/PUT için 404, geçersiz ayarlarda 422,
   refresh token ile kaynak erişiminde 401, boş hesabın doğru gösterimi.
7. 390 px mobil görünüm: yatay taşma yok, detay diyaloğu çalışıyor.
8. 1440 px masaüstü görünüm: JavaScript çalışma hatası yok, ekran görüntüsü alındı.

İlk koşu: **8/8 başarılı**. Örnek botlar gerçek Telegram hesapları değildir.
Canlı bot başlatma/durdurma ve mesaj gönderme doğrulanmadı; bu panelde kapalıdır.
