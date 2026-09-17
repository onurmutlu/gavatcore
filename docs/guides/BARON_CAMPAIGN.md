# Baron grup paylaşımı ve Stars mağazası

`config/baron_campaign.json` tek yapılandırma dosyasıdır. Varsayılan olarak
grup paylaşımı ve satış kapalıdır. Örnek mesajlar kullanıcı onayına hazır taslaktır.

- `broadcast.groups`: yalnızca paylaşım izni olan grupları
  `{"id": -1001234567890, "permission_confirmed": true}` biçiminde ekleyin.
- `broadcast.messages`: sırayla gönderilecek metinler.
- `broadcast.interval_seconds`: grup başına süre; varsayılan 4 saat, en az 1 saat.
- `broadcast.enabled`: gerçek gönderimi açar. Yeniden başlatma için zamanlama SQLite'ta korunur.
- `shop_username`: BotFather ödeme botunun kullanıcı adı; kişisel Baron hesabından farklıdır.
- `support`: ödeme/iade talepleri için gerçek iletişim bilgisi.
- `products`: ürün kimliğinden ürün bilgisine sözlük. Ürün örneği:

```json
{"guide": {"title": "Sohbet rehberi", "description": "Dijital sohbet rehberi", "stars": 25, "content": "TESLİM EDİLECEK GERÇEK METİN VEYA ERİŞİM BAĞLANTISI"}}
```

Yalnızca sunma hakkınız olan, açık cinsel içerik içermeyen gerçek ürünleri ekleyin.
Fiyat ve teslimat içeriği sipariş oluşturulurken kaydedilir. `sales_enabled` ile
satış açılır. Ayar değişikliğinden sonra süreçleri yeniden başlatın.

BotFather tokenını sohbet veya kaynak koda koymadan `.env` içine
`BARON_SHOP_BOT_TOKEN` olarak ekleyin. Mevcut `OPENAI_API_KEY` DM için kullanılır;
Baron önce `XAI_API_KEY` kullanır ve xAI'nin OpenAI uyumlu uç noktasına bağlanır.
`XAI_BASE_URL` varsayılan olarak `https://api.x.ai/v1`, `XAI_MODEL` ise
`grok-4.6` değerini kullanır. Kısa grup mesajlarında maliyet ve gecikmeyi sınırlamak
için `XAI_REASONING_EFFORT=low` varsayılır. Grok reasoning modellerinde
desteklenmeyen presence/frequency penalty alanları gönderilmez. xAI anahtarı yoksa
`OPENAI_API_KEY` yedeği devreye
girer. `BARON_GPT_MODEL` yalnızca Baron için model adını geçersiz kılabilir.

```sh
.venv/bin/python launchers/baron_bot_launcher.py start
.venv/bin/python launchers/baron_stars_shop.py
```

Baron: `/start`, `/stop`, `/shop`. Mağaza: `/shop`, `/buy ürün_id`, `/orders`,
`/paysupport`. Ödeme botunda başka polling/webhook tüketicisi çalıştırmayın.
Kişisel hesapta daha önceki launcher aynı anda çalıştırılmamalıdır.

Stars faturaları XTR ile açılır. Alıcı, tutar, para birimi ve sipariş kontrol edilir;
içerik yalnızca Telegram `successful_payment` sonrasında gönderilir. Charge ID,
teslimat durumu ve polling konumu `data/baron_campaign.sqlite3` içinde saklanır.
Bu dosyayı koruyun ve yedekleyin. Başarısız teslimat yeniden denenir; `/orders`
yalnızca ödenmiş, teslim edilmemiş içerikleri yeniden dener. Telegram gönderimi ile
yerel kayıt arasındaki çökmede aynı içerik iki kez teslim edilebilir; ek ücret alınmaz.
Beklenmeyen ödeme/veri hatası polling'i o kayıtta tutar ve operatör incelemesi gerektirir.
İadeler operatör tarafından kayıtlı charge ID ile `refundStarPayment` üzerinden yapılır;
otomatik iade arayüzü bu sürüme dahil değildir.

DM'ler mevcut GPT altyapısını, sınırlı sohbet yönergesini ve şeffaf asistan kimliğini
kullanır. Eski AI blending Baron için uygulanmaz. Canlı model davranışı ve gerçek
ödeme teslimatı, kimlik bilgileri ve ürünler sağlandıktan sonra uçtan uca doğrulanmalıdır.

Telegram referansı: https://core.telegram.org/bots/payments-stars

Yerel test: `.venv/bin/python -m unittest discover -s tests -p test_baron_campaign.py -v`

## Grup keşfi ve adaptif mesaj seçimi

```sh
.venv/bin/python launchers/baron_bot_launcher.py scan-groups
.venv/bin/python launchers/baron_bot_launcher.py preview-group -1001234567890 --source template
.venv/bin/python launchers/baron_bot_launcher.py preview-group -1001234567890 --source gpt
```

Tarama, mevcut Baron oturumunun üye olduğu tüm grup diyaloglarını dolaşır;
Telegram genelinde arama veya yeni gruplara katılma yapmaz. Grup başlığı ve
son 12 saatteki en fazla 40 mesajdan sosyal sohbet/tanışma adaylığı çıkarır.
Puan bir anahtar kelime sezgisidir, doğrulanmış sınıflandırıcı doğruluğu değildir.
İş/eleman/emlak arayışı gibi başlıklar dışlanır. Her adayın nedenleri, konu
etiketleri ve örnek sayısı `reports/baron_group_discovery.json` dosyasına yazılır.
Boş veya az örnekli adayları ayrıca değerlendirin. Hız sınırı veya erişim
hatasında rapor `complete: false` olur. Tarama hiçbir gruba gönderim izni vermez;
gönderim için `broadcast.groups` içindeki açık izin listesi kullanılır.

`adaptive.enabled: true` iken `broadcast.messages` yerine
`config/baron_messages.json` içindeki 48 mesaj kullanılır. Set; genel sohbet,
tanışma, müzik, film, yemek, hobi, gezi ve gündelik hayat için altışar mesaj içerir.
GPT sırası aynı kısa bağlamdan yeni bir mesaj üretir. Mesaj gövdesine sabit bir
etiket eklenmez; hesabın `profile_about` alanı yapay zekâ ajanı ve otomatik yayın
hesabı olduğunu açıklar. Launcher başlangıçta bu biyografiyi doğrular ve gerekirse
Telegram profilinde günceller. Önizleme gönderim yapmaz, sayaçları değiştirmez;
GPT önizlemesi mevcut API anahtarıyla ücretli model çağrısı yapabilir.

Her grupta başarıyla kaydedilen **zamanlanmış** gönderimler şablon/GPT olarak
sırayla ilerler: her iki iletide birer tane, tek sayıda en fazla bir fark.
DM ve mention yanıtları bu orana dahil değildir. Sayaç SQLite'ta korunur.
GPT hata verir, uygun konu bulamaz, aynı çıktıyı yineler veya yetersiz bağlam
olursa o tur atlanır; şablona dönülmez. Sonraki deneme normal grup aralığında yapılır.
Gönderim ile SQLite kaydı arasındaki çökmede sayaç geride kalabilir; dağıtık
işlem olmadan mutlak yüzde garantisi yoktur. Yalnızca tek launcher çalıştırın.

Öğrenme, model ağırlıklarını değiştirmek yerine grup/şablon puanlarını günceller:

- Son sohbetin konu eşleşmesi seçim puanına eklenir.
- Son 12 gönderimde kullanılan şablonlar tekrar seçilmez.
- Baron'un gönderisine 24 saat içinde gelen doğrudan yanıtlar olumlu sinyal;
  spam/reklam/rahatsızlık ifadeleri olumsuz sinyal sayılır. Bu basit sezgi
  duygu analizi veya insan memnuniyetinin güvenilir ölçümü değildir.
- Yanıt sayısı katkısı sınırlandırılır; az denenmiş şablonlara keşif puanı verilir.
- Geri bildirim olayları mesaj ID'siyle tekilleştirilir. Grup bazında tutulur;
  kişi bazında arayış, tercih veya ilişki profili oluşturulmaz.

Adaptif katman ham sohbeti diske yazmaz. Yaygın kullanıcı adı, URL, e-posta ve
telefon kalıpları yerel konu tespitinden önce maskelenir; bu eksiksiz
anonimleştirme değildir. Ham grup mesajları GPT sağlayıcısına gönderilmez. GPT
yalnızca yerelde çıkarılan genel konu etiketini (`music`, `film`, `daily` gibi)
ve yakın dönem mesaj sayısını alır; bu nedenle belirli cümlelere değil, sohbetin
genel konusuna uyum sağlar.
Gönderi özeti (konu/kaynak/şablon ID/metin özeti hash'i) ve geri bildirimler
30 gün tutulur; ömür boyu kaynak sayaçları oranı korumak için kalır.
Bu saklama politikası mevcut DM bellek modülünün politikasını değiştirmez.

DM yanıtları 3,5 saniyelik kısa bir pencerede gelen iletileri tek model turunda
birleştirir ve tek Telegram mesajı gönderir. Bir kullanıcı için yerel geçmiş boşsa
ilk DM'de mevcut sohbetten, güncel iletiden önceki en fazla 24 metin mesajı alınır.
Sonrasında kullanıcı başına son 40 mesaj yerel SQLite'ta en fazla 30 gün saklanır.
Bu içerik Baron'un Grok konuşma bağlamına dahil edilir. `/stop` hafıza kaydını
silmez; yalnızca yeni otomatik yanıtları durdurur.

Doğrulama: `.venv/bin/python -m unittest discover -s tests -p 'test_baron_*.py' -v`
