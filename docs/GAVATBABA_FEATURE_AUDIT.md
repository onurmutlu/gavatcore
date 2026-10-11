# GavatBaba Özellik Denetimi (Faz 1 / P0)

| Alan | Değer |
|---|---|
| Denetlenen commit | `051e154afee883ce1875664f8f16e2152d26fc25` (main, 2026-09-17) |
| Denetim tarihi | 2026-10-11 |
| Çalışma dalı | `claude/gavatbaba-sales-engine-v2` |
| Yöntem | Kod okuma + gerçek test çalıştırma. Eski dokümanlara (CLAUDE.md, README) güvenilmedi; her iddia kodla doğrulandı. |

Durum etiketleri: **Working** (kodla doğrulandı), **Partial**, **Missing**, **Unknown** (doğrulanamadı).

---

## 1. Yönetici özeti

1. **GavatBaba bir Telethon userbot'udur**, Bot API botu değil. Bir telefon numarası/oturum dosyasıyla kullanıcı hesabı olarak çalışır (`babagavat_simple_launcher.py`, `services/telegram/bot_manager/bot_system.py`). Launcher DM'leri yalnızca `print` ile loglar, **hiç yanıt vermez**.
2. **Görevde adı geçen `handlers/dm_handler.py` ağırlıklı olarak stub'tır.** Üretim mantığı `services/telegram/dm_handler.py` içindedir (1051 satır). Mevcut testler yanlış modülü hedefliyor.
3. **Bu commit'te `core.controller` → `handlers.dm_handler` zinciri import edilemiyordu** (`config.GAVATCORE_ADMIN_ID` yoktu). P0 olarak düzeltildi (bkz. §5).
4. **Doğrulanmış ödeme yok.** Telegram tarafı IBAN/Papara + "dekont gönder" akışıdır; hiçbir doğrulama mekanizması yoktur. Stripe webhook'u idempotent değildir ve hataları yutar. Stars/TON uçları `TODO` stub'ıdır.
5. **Çok-yaratıcı (multi-creator), workspace/tenant, rol (SUPERADMIN/CREATOR/CUSTOMER), komisyon, payout, ledger, iade, refund-erişim iptali: hiçbiri yok.** Kodda `workspace_id`, `tenant`, `creator_id` geçmiyor; `User` modelinde rol alanı yok. Dolayısıyla "mevcut workspace/yetki modelini çoğaltma" kısıtı için çoğaltılacak bir şey yok; sıfırdan tasarlanacak.
6. **Telegram kuralı:** Telegram'ın Stars dokümanına göre (2026-10-11'de okundu) bot ve mini-app içinde dijital ürün/hizmet satışı **yalnızca Telegram Stars (XTR)** ile yapılabilir; üçüncü taraf sağlayıcı ve kripto yasaktır. IBAN/Papara/Stripe ile DM içinde dijital ürün satışı bu kurala aykırı görünüyor.
7. **İçerik kategorisi bloklayıcısı:** `data/show_menus.json` içindeki `gavat_show_menu`, görev kapsamının açıkça yasakladığı bir kategoriyi ("kız bağlantı/tanıştırma" hizmetleri = aracılık/eşleştirme) fiyatlı ürün olarak sunuyor. Yeni satış motoruna **alınmayacak**; ayrıntı §4.3.
8. **Gizli bilgi sızıntısı:** İzlenen dosyalarda gerçek kimlik bilgisi biçiminde sabit değerler var (§4.1). Değerler bu raporda maskelendi.

---

## 2. Çalışma modeli (entry point'ler)

| Soru | Cevap | Kanıt |
|---|---|---|
| Telethon userbot? | **Evet** | `babagavat_simple_launcher.py:28` `TelegramClient(session_path, …)`; `core/controller.py:52` |
| Telegram Bot API? | Bu akışta **hayır** (`BOT_TOKEN` yalnızca admin/panel botlarında) | launcher'larda `start(bot_token=…)` yok |
| FastAPI backend? | **Evet, ayrı süreç** (`gavatcore-api/app/main.py`, port 8000) | `payment.py`, `dashboard.py` |
| Paylaşılan GavatCore servisleri | **Evet** | `core/`, `utilities/`, Redis state |
| Çoklu süreç | **Evet**: `run.py` + `bot_system.py` her bot için ayrı launcher süreci; API ayrı | `bot_system.py:46-50`, `run.py:314` |

Önemli sonuç: **Satış mantığının yaşadığı süreç (userbot) ile ödeme/abonelik DB'si (FastAPI) arasında hiçbir entegrasyon yok.** DM akışı yalnızca Redis `conv:*` anahtarlarına yazar; `Payment`/`Subscription` tablolarına dokunmaz.

---

## 3. Özellik tablosu

### F1 – Userbot başlatma ve oturum yönetimi
- **Uygulama:** `core/controller.py::launch_all_sessions`, `babagavat_simple_launcher.py::BabaGavatSimpleLauncher.start`
- **Durum:** Partial. Controller oturumları açıp handler bağlar; GavatBaba launcher'ı yalnızca loglar.
- **Testler:** Yok. **Çalıştırma:** n/a.
- **Eksik:** Launcher'da yanıt/akış yok. `Controller.handle_message` ve `Controller.handle_inline_bank_choice` **boş stub** (`return True`, "gerçek iş mantığını ekleyebilirsin").
- **Risk:** Launcher'da varsayılan telefon numarası sabit yazılı (kişisel veri; maskelendi: `+90551…`). Userbot ile otomatik satış mesajlaşması Telegram ToS/spam riski taşır.
- **Öneri:** Satış akışını Bot API (Stars ile) tarafına taşı; userbot'u operatör/devralma kanalı olarak sınırla.

### F2 – DM işleme (`handlers/dm_handler.py`)
- **Uygulama:** `DMHandler.handle_dm/handle_command/process_message` → gövdeleri `pass`. `handle_message` çalışır ama `handle_inline_bank_choice` "Banka 1/2 seçildi." döndüren sahte koddur.
- **Durum:** Partial/Stub.
- **Testler:** `test_gavatbaba_dm_flow.py`, `test_vip_sales_funnel.py` (bu modülü import eder).
- **Çalıştırma:** FAILED (bkz. §6).
- **Eksik:** Gerçek komut işleme, gerçek mesaj gönderimi (`schedule_followup_message` yalnızca log yazar, "gerçek mesaj gönderme mantığı olmalı" notu var), `setup_dm_handlers` handler kaydetmez.
- **Risk:** `except Exception: print(...)` ile hatalar sessizce yutuluyor.
- **Öneri:** Tek bir DM katmanı seç (aşağıdaki F3 ile birleştir); stub'ları gerçeğiyle değiştirme yerine kaldır.

### F3 – DM işleme (üretim: `services/telegram/dm_handler.py`)
- **Uygulama:** 1051 satır; `bot_username:user_id` anahtarlı cooldown, VIP huni aşamaları (`interested/pricing/payment`), IBAN/Papara yönlendirmesi, `manualplus` modu, bot filtreleme.
- **Durum:** Partial/Unknown (çalıştırılabilir test yok, derinlemesine akış doğrulanmadı).
- **Testler:** Doğrudan yok (testler `handlers.dm_handler`'ı hedefliyor).
- **Risk:** Ödeme bilgisini (IBAN) anahtar kelimeyle (`iban`, `papara`, `para`…) otomatik gönderir → yanlış tetikleme; "ödeme sonrası" erişim akışı doğrulanmıyor.
- **Öneri:** Mevcut kod referans alınıp consent-tabanlı yeni akışa (Faz 7) taşınacak.

### F4 – VIP huni / niyet tespiti
- **Uygulama:** `check_vip_interest`, `check_payment_intent`, `update_vip_interest`, `get_vip_interest_stage` (iki ayrı modülde, **iki ayrı imza**).
- **Durum:** Partial. Anahtar kelime eşleştirme çalışır; huni "ödeme"ye kadar gider, sonrası yok.
- **Testler:** `test_vip_sales_funnel.py` (6 test).
- **Çalıştırma:** 4 geçti, 2 FAILED. Geçenlerin hiçbirinde `assert` yok (bkz. §6), yani kanıt değeri sıfır.
- **Risk:** Mesajda "para", "transfer" gibi kelime geçmesi satış bilgisi gönderiyor (yanlış-pozitif).

### F5 – Rate limit / cooldown
- **Uygulama:** `handlers/dm_handler.py::check_dm_cooldown/update_dm_cooldown`, `cleanup_dm_cooldowns`.
- **Durum:** **Partial (fiilen devre dışı).** `handle_message` cooldown'ı *kontrol eder* ama `update_dm_cooldown`'ı hiç çağırmaz → sayaç hiç dolmaz, limit asla tetiklenmez. Sözlükler süreç-içi (restart'ta sıfırlanır, çoklu süreçte paylaşılmaz).
- **Ek defekt:** `core/controller.py:227-228` `dm_cooldown_cleanup_task`'ı import edip **çağırıyor**, ancak modülde bu ad `None` placeholder; çağrı `TypeError` verir ve `except` ile "başlatılamadı" uyarısına düşer. Temizlik görevi hiç çalışmıyor.
- **Testler:** `test_dm_cooldown_system.py` var; bu denetimde çalıştırılmadı.
- **Öneri:** Redis tabanlı kalıcı rate-limit (Faz 7).

### F6 – Opt-out / abonelikten çıkma
- **Durum:** **Missing.** `/stop`, "rahatsız etme", "çık" gibi bir akış yok (grep ile doğrulandı).
- **Öneri:** Faz 7'de zorunlu.

### F7 – Manuel operatör devralma
- **Uygulama:** `services/telegram/dm_handler.py` içinde `manual_mode_active`, `manual_intervention_time` alanları ve `manualplus` (90 sn timeout).
- **Durum:** Partial/Unknown. `core/controller.py:178-185`'te **outgoing mesaj ile devralma tespiti bilerek devre dışı bırakılmış** ("her otomatik mesajı manuel algılıyor").
- **Test:** Yok.
- **Risk:** Operatör yazarken bot da cevap verebilir (çift yanıt).
- **Öneri:** Bot tarafından gönderilen mesaj ID'lerini işaretleyerek ayrım; Faz 7 testi.

### F8 – Gösteri menüsü (`data/show_menus.json`)
- **Uygulama:** Statik içerik: `lara_show_menu`, `geisha_show_menu`, `gavat_show_menu`, kompakt sürümler, `test_bot_show_menu`.
- **Durum:** Working (statik veri; yüklenir). **Doğruluk/uyum:** bkz. §4.3.
- **Testler:** `test_gavatbaba_menu.py` (1 test), `test_show_menus.py`, `test_geisha_menu.py`.
- **Çalıştırma:** `test_gavatbaba_menu.py` 1 geçti (ama `assert` içermiyor; menü içeriğini doğrulamaz).
- **Risk:** Fiyatlar metin içinde gömülü (TRY, serbest metin); bir ledger/ürün kataloğuyla bağlantısı yok.

### F9 – Kullanıcı güven analizi
- **Uygulama:** `core/gavatbaba_analyzer.py::gavatbaba_analyzer` → her zaman `UserTrustLevel.TRUSTED` döner ("Basit örnek").
- **Durum:** **Stub.** Güven/dolandırıcılık kontrolü sağlamıyor.
- **Risk:** Biri bunu güvenlik kontrolü sanırsa yanlış güven doğar.

### F10 – Manuel ödeme (IBAN/Papara/dekont)
- **Uygulama:** `utilities/payment_utils.py::generate_payment_message`, `data/banks.json`.
- **Durum:** Working ama **yetersiz ve riskli**: yalnızca IBAN metni üretir.
- **Eksik:** Tutar/sipariş eşleştirme, doğrulama, kayıt, erişim verme, iade yok.
- **Güvenlik:** Dekont/"ödedim" ile erişim açan kod **bulunmadı** (olumlu); ancak doğrulama yolu da yok, yani süreç tamamen elle. IBAN/hesap sahibi bilgisi profil JSON'larından geliyor.
- **Uyum:** Telegram Stars kuralıyla çelişir (bot/mini-app içinde dijital ürün).
- **Öneri:** Telegram içi satışta Stars; manuel doğrulama gerekiyorsa denetimli, rolle sınırlı onay akışı.

### F11 – Stripe ödeme (FastAPI)
- **Uygulama:** `gavatcore-api/app/routes/payment.py` (`/stripe/create-checkout`, `/stripe/webhook`, `handle_payment_success/failure`), `app/services/stripe_service.py`, `app/models/payment.py`.
- **Durum:** Partial. İmza doğrulama var (`stripe.Webhook.construct_event`). Aşağıdaki defektler doğrulandı:

| # | Defekt | Kanıt |
|---|---|---|
| a | **İdempotent değil**: aynı `payment_intent.succeeded` iki kez gelirse ikinci kez `Subscription` + bot oluşturulur | `handle_payment_success` durum kontrolü yok |
| b | **Tutar/para birimi doğrulanmıyor** (webhook'taki `amount`/`currency` DB ile karşılaştırılmıyor) | aynı fonksiyon |
| c | **Hatalar yutuluyor**: `except Exception` log basıp dönüyor, endpoint yine `{"success": True}` (200) döner → Stripe yeniden denemez, **ödeme alınıp erişim verilmeyebilir** | `payment.py:282-283`, `:204` |
| d | İşlem sınırı yok: `mark_as_completed` + `Subscription` + bot oluşturma ayrı adımlar; kısmi başarısızlık tutarsız veri bırakır | aynı |
| e | `expires_at` ödeme **oluşturulma** zamanından hesaplanıyor (`payment.created_at + days`), ödeme zamanından değil | `payment.py:252` |
| f | Geçersiz plan için 400 atılıp hemen `except Exception` ile **500'e çevriliyor** | `payment.py:150-182` |
| g | `Numeric(10,2)` + `float` kullanımı, `int(price*100)` dönüşümü; tamsayı minor-unit yok | `stripe_service.py:84`, `payment.py` modeli |
| h | `get_subscription_status` `scalar_one_or_none()`; birden fazla aktif abonelikte `MultipleResultsFound` | `payment.py:321-326` |
| i | Webhook mantığı iki yerde kopya (route + `StripeService.handle_webhook`) | paralel yol |
| j | Webhook olay ID'si saklanmıyor → tekrar oynatma koruması yok | model |

- **Testler:** Yok (`gavatcore-api/tests/` bu özellikler için bulunamadı).
- **Uyum:** Telegram içinde dijital ürün için kullanılamaz (Stars zorunlu); web satın alımı için ayrı değerlendirilmeli. Stripe'ın bu içerik kategorileri için iş uygunluğu doğrulanmadı (**Unknown**).

### F12 – Telegram Stars / TON
- **Uygulama:** `/stars/invoice`, `/ton/invoice` → `"TODO: implement"`, `"coming_soon"` döner. `Payment._process_stars_webhook` / `_process_ton_webhook` `status`/`confirmed` alanına **doğrulama olmadan** güvenir.
- **Durum:** **Missing** (stub).
- **Risk (yüksek):** Bu model metotları bir endpoint'e bağlanırsa, saldırgan `{"status":"paid"}` gönderip ödemeyi tamamlanmış işaretletebilir. Bağlı değil, fakat tuzak.
- **Öneri:** Stars akışı Faz 2'nin birincil yolu (`pre_checkout_query` 10 sn içinde yanıt, `successful_payment` doğrulanmadan teslimat yok, `telegram_payment_charge_id` saklanarak `refundStarPayment`).

### F13 – Abonelik modeli
- **Uygulama:** `gavatcore-api/app/models/subscription.py`.
- **Durum:** Partial. Modelde `is_active/expires_at/cancel/extend` var; bu **SaaS plan abonelikleridir** (trial/starter/pro/deluxe, `max_bots`), **yaratıcı VIP kanal aboneliği değildir**.
- **Eksik:** Süre dolumunda erişim iptali yapan arka plan işi bulunamadı (kodda `expires_at` yalnızca okuma/gösterimde). Kanal erişimi (Telegram kanal ekleme/çıkarma) yok. Yenileme akışı yok. `is_expired` `datetime.utcnow()` (naive) ile timezone-aware kolonu karşılaştırır → olası `TypeError`/yanlış sonuç.
- **Öneri:** Mevcut tabloyu yeniden kullanmak mümkün ama "VIP kanal aboneliği" için yaratıcı/ürün bağları eklenmeli (yeni paralel sistem değil, genişletme).

### F14 – Yetkilendirme / roller / tenant izolasyonu
- **Uygulama:** `app/core/dependencies.py::get_current_user`.
- **Durum:** **Missing.** `User`'da rol yok; `dependencies.py`'de `role/admin/superuser` hiç geçmiyor. `dashboard.py` uçları yalnızca `get_current_user` ister → **giriş yapmış her kullanıcı** sistem geneli özet uçlarını çağırabilir (veri kapsamı **Unknown**, gövde satır satır doğrulanmadı).
- **Risk:** Yüksek (yetki yükseltme / veri sızıntısı).

### F15 – Dashboard / raporlama
- **Uygulama:** `gavatcore-api/app/routes/dashboard.py`, `gavatcore_panel/` (Flutter).
- **Durum:** Partial. Plan-düzeyi sayımlar var (`successful_payments`, aktif abonelik). Yaratıcı kazancı, komisyon, iade, ürün bazlı gelir yok. Metrikler `Payment` tablosundan geliyor (ledger yok).

### F16 – Veritabanı migrasyonları
- **Durum:** **Missing.** Depoda Alembic yapılandırması/`versions/` yok; `database/connection.py:60` `Base.metadata.create_all` kullanıyor. CLAUDE.md `alembic upgrade head` diyor → **doküman koddan sapmış**.

### F17 – Sağlık kontrolü / log
- **Durum:** Working (FastAPI `/health`, structlog). Kapsam yalnızca "healthy" yanıtı; bağımlılık (DB/Redis) kontrolü doğrulanmadı (**Unknown**).

### F18 – Yapılandırma ve gizli bilgi yönetimi
- **Durum:** Partial. `config.py` doğrulamalı (iyi), ancak bkz. §4.1. Ayrıca `gpt/openai_utils.py` → `config` zinciri import anında `API_ID` ister; ortam değişkeni yoksa tüm `core` import'u çöker. (Test için yer tutucu değerlerle çalıştırıldı.) `ENVIRONMENT` varsayılanı `production`.

---

## 4. Güvenlik ve uyum bulguları

### 4.1 Gizli bilgi sızıntıları (P0 – rotasyon gerekir)
Değerler **maskelenmiştir**; aşağıdaki öğeler git geçmişinde kalıcıdır, bu yüzden kod düzeltmesi tek başına yetmez: **anahtarlar iptal edilip yenilenmelidir.**

| Dosya | Öğe | Not |
|---|---|---|
| `telegram_miniapp_bot.py:19-20` | `API_HASH`, `BOT_TOKEN` | Biçim olarak gerçek kimlik bilgisiyle uyumlu (32 hex / token biçimi) |
| `utilities/arayisvips_conversation_launcher.py:311`, `utilities/arayisvips_viral_launcher_ai.py:324` | `api_id` + `api_hash` | Aynı API kimliği iki dosyada |
| `gavatcore_engine/telegram_client_ornek.py` | `api_id`/`api_hash` (yorum: "Gerçek API hash") | Örnek dosya ama "gerçek" notu var |
| `babagavat_simple_launcher.py` | Varsayılan telefon numarası | Kişisel veri |
| `config/environments/*.env`, `.env.test` | İzlenen `.env` dosyaları | `.gitignore` `*.env`'i kapsıyor ama dosyalar zaten izleniyor; içerikleri bu denetimde okunmadı/açılmadı |
| `tests/*` | Sahte görünen token/hash sabitleri | Muhtemelen sahte; doğrulanmadı |

### 4.2 Ödeme güvenliği
Bkz. F10–F12. Özet: doğrulanmış ödeme olmadan erişim verme riski şu an **kodda yok** (çünkü satış→erişim bağı hiç kurulmamış), fakat Stripe webhook'unda çift teslimat, kayıp ödeme ve tutar doğrulamasızlığı var.

### 4.3 İçerik kategorisi bloklayıcısı
`data/show_menus.json` içindeki üç menü incelendi:

- **`gavat_show_menu`** – "kız tanıştırma / VIP kız bağlantısı" gibi kalemleri fiyatlı hizmet olarak sunuyor. Bu, görev tanımındaki "matchmaking or trafficking facilitation" yasağı kapsamındadır. **Yeni satış motoruna taşınmayacak.** Mevcut botlarda hâlâ sunuluyor olabilir; bu bir üretim içeriği kararıdır ve sahibinin açık onayıyla kaldırılmalıdır (bu denetimde dosya **değiştirilmedi**).
- **`lara_show_menu`, `geisha_show_menu`** – cinsel içerikli canlı gösteri, "sexting" ve ekstra kalemleri satıyor. Bunlar yetişkin içerik kategorisidir; Telegram ve ödeme sağlayıcı kuralları doğrulanmadan etkinleştirilmeyecek (Faz 4 koşulu). Menüde "REAL sadece devamlı müşterilerime var" gibi ifadeler var; yaratıcı sahiplik/yaş/rıza doğrulaması ürün kataloğunda zorunlu hale getirilmeli.

### 4.4 Telegram uyumu
- Dijital ürün için Stars zorunluluğu (yukarıda).
- Userbot ile otomatik satış/DM → spam ve hesap kısıtlaması riski; `spam_loop`/`autospam` (`core/controller.py:203`) toplu mesaj davranışı içeriyor. Görev kapsamı toplu DM'yi yasaklıyor; satış motoru bu mekanizmayı **kullanmayacak**.

---

## 5. Bu denetimde yapılan kod değişikliği (P0)

| Dosya | Değişiklik | Gerekçe |
|---|---|---|
| `config.py` | `GAVATCORE_ADMIN_ID` modül-düzeyi takma adı (`_parse_admin_id`, geçersiz/boşsa `0`) + `__all__` | `core/onboarding_flow.py`, `core/session_watcher.py`, `adminbot/commands.py`, `tests/test_complete_system.py` bu adı import ediyordu; ad yoktu → `ImportError` ile `core.controller`/`dm_handler` yüklenemiyordu. `0` geçerli Telegram kullanıcı ID'si olamaz → eşleşme yok (kapalı-güvenli). |

**Regresyon kontrolü:** `config.py`'yi içe aktaran `tests/test_config.py` + `tests/test_config_full.py` (273 test) düzeltmeli ve düzeltmesiz (`git stash`) çalıştırıldı: ikisinde de **14 failed, 4 error**, başarısız test kümeleri özdeş; düzeltme kaynaklı yeni başarısızlık **yok**. (Bu 18 sorun önceden vardı ve bu fazda ele alınmadı.)

Başka kod değişikliği yapılmadı. İçerik dosyaları ve gizli değerler dokunulmadan bırakıldı (karar/rotasyon sahibin).

---

## 6. Test çalıştırma sonuçları

**Ortam:** Python 3.13.16, yalıtılmış venv; `pytest 9.1.1`, `pytest-asyncio 1.4.0`. Canlı ağ/ödeme çağrısı yapılmadı. Import için yer tutucu ortam değişkenleri (`OPENAI_API_KEY=dummy…`, `TELEGRAM_API_ID=1234567`, 32 sıfırlı `API_HASH`, `ENVIRONMENT=testing`) kullanıldı; gerçek kimlik bilgisi kullanılmadı.

**Komut:**
```
pytest tests/test_gavatbaba.py tests/test_gavatbaba_dm_flow.py \
       tests/test_gavatbaba_menu.py tests/test_vip_sales_funnel.py \
       -p no:cacheprovider -q --junitxml=baseline.xml
```

| Aşama | Sonuç |
|---|---|
| Düzeltmeden önce | 2 dosya **toplama hatası** (`ImportError: GAVATCORE_ADMIN_ID`), 0 çalıştırma |
| Düzeltmeden sonra | **8 test toplandı: 5 geçti, 3 başarısız** |

| Dosya | Sonuç | Not |
|---|---|---|
| `tests/test_gavatbaba.py` | **0 test toplandı** | Betik sınıfı (`GavatBabaTestSuite` + `main()`); pytest'in toplayacağı `test_*` fonksiyonu yok. Canlı Telegram'a bağlanabileceği için çalıştırılmadı. |
| `tests/test_gavatbaba_menu.py` | 1 geçti | |
| `tests/test_gavatbaba_dm_flow.py` | 1 **FAILED** | `update_conversation_state() got an unexpected keyword argument 'user_responded'` (imza kayması) |
| `tests/test_vip_sales_funnel.py` | 4 geçti, 2 **FAILED** | `get_vip_interest_stage() takes 1 positional argument but 2 were given` (test `services` imzasını bekliyor, import `handlers` modülünden) |

**Hiçbir testte `assert` yok.** Dört dosyadaki 8 `test_*` fonksiyonunun tamamı AST ile tarandı: `assert` sayısı **0** (bkz. `ast.walk` taraması). Bu yüzden "geçti" yalnızca "istisna fırlatmadı" anlamına gelir; **5 geçen testin hiçbiri kodun doğruluğunu kanıtlamaz**. Ek olarak `test_vip_interest_detection` ve `test_payment_intent_detection` `async` fonksiyonları `await` etmeden çağırıyor (`RuntimeWarning: coroutine … was never awaited`), yani işlevi hiç çalıştırmıyor. Dürüst sayım: **anlamlı doğrulama veren test sayısı 0**; 3 test gerçek bir imza uyumsuzluğunu açığa çıkardığı için başarısız oluyor. Hata gerekçesi: testler `services/telegram/dm_handler.py` API'sine (senkron, `bot_username` parametreli) göre yazılmış, ama `handlers/dm_handler.py`'ı import ediyor.

---

## 7. Öneri özeti (öncelik sırasıyla)

| Öncelik | Eylem |
|---|---|
| **P0 – sahip** | §4.1'deki anahtarları iptal/yenile; git geçmişini temizleme kararı ver |
| **P0 – sahip** | `gavat_show_menu` ("kız bağlantı") içeriğinin kaldırılmasına karar ver; yetişkin menüleri için platform kurallarını doğrula |
| P1 | Sağlayıcıdan bağımsız ledger + durum makinesi; Stars birincil yol; Stripe webhook'u idempotent/transaction'lı/tutar-doğrulamalı hale getir veya devre dışı bırak |
| P1 | Alembic ekle (mevcut `payments`/`subscriptions` tablolarını başlangıç şeması olarak al) |
| P2 | Teslimat (tam-bir-kez) ve süre dolumu/iade ile erişim iptali işi |
| P3 | Rol + workspace/creator modeli, tamsayı minor-unit komisyon |
| P4 | Ledger kaynaklı yaratıcı paneli |
| P5 | DM akışı: opt-out, kalıcı rate-limit, çift yanıt önleme, operatör devralma; testleri `services` yerine yeni akışa yaz |

## 8. Doğrulanamayanlar (Unknown)
- `services/telegram/dm_handler.py` içindeki tüm huni akışının davranışı (çalıştırılmadı).
- Dashboard uçlarının sistem geneli mi kullanıcı kapsamlı mı veri döndürdüğü.
- Stripe'ın bu içerik kategorileri için iş uygunluğu; ödeme sağlayıcılarının yetişkin içerik politikaları.
- `config/environments/*.env` ve `.env.test` içeriği (açılmadı).
- Üretimde hangi launcher'ın gerçekten çalıştığı (kodda üç farklı yol var: `run.py`, `bot_system.py`, tekil launcher'lar).
