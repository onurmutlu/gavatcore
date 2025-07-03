# 🤖 GAVATCore™ – Telegram İçerik Platformları İçin Otomasyon Sistemi

**GAVATCore™**, Telegram üzerinden içerik yönetimi, etkileşim ve otomatik müşteri ilişkileri için geliştirilmiş bir ⚡️otomasyon altyapısıdır.  
Yapay zekâ destekli yayıncı profilleri, otomatik mesajlaşma, ödeme takip ve detaylı loglama ile dijital içerik üreticileri ve ajanslar için eksiksiz bir çözüm sunar.

## 🚀 **PRODUCTION READY** - v2.0.0

✅ **%100 Test Coverage** - 44/44 test başarılı  
✅ **Role-Based Komut Sistemi** - Admin/Producer/Client rolleri  
✅ **GPT Kontrol Paneli** - Inline button ile kolay yönetim  
✅ **Gelişmiş Log Sistemi** - Arama ve istatistik özellikleri  
✅ **Güvenlik Önlemleri** - State yönetimi ve erişim kontrolü  
✅ **Performans Optimizasyonu** - Hızlı profil ve log işlemleri

---

## 🚀 Özellikler

- 🤖 **AI Destekli Karakterler**: Lara, Geisha gibi kişiselleştirilmiş sohbet botları (GPT).
- 🛠️ **GPT Kontrol Paneli**: Inline button'lar ile kolay GPT modu, spam hızı ve VIP mesaj yönetimi.
- 👑 **Role-Based Komut Sistemi**: Admin/Producer/Client rolleri ile güvenli komut erişimi.
- 🔍 **Gelişmiş Log Sistemi**: Anahtar kelime, seviye ve tarih filtreli log arama.
- 🎭 **Profesyonel Show Menü Sistemi**: Bot'lara özel, detaylı hizmet menüleri ve fiyat listeleri.
- 📊 **Kapsamlı Test Coverage**: %100 başarı oranı ile 44 farklı test kategorisi.
- 📣 **Grup & DM Mesajlaşma**: Otomatik içerik paylaşımı, mention ve cevap yönetimi.
- 💸 **Papara & IBAN Entegrasyonu**: Güvenli ve kolay ödeme sistemi desteği.
- 🧠 **Akıllı Yanıt Modları**: Manuel, AI, Hibrit ve otomatik yedekleme (fallback) desteği.
- 🍽️ **Otomatik Menü Gönderme**: 2-3 mesaj sonrası akıllı hizmet menüsü sunumu.
- 📡 **Telegram Üzerinden Tam Yönetim**: Web panel gerektirmeden, sadece Telegram ile.
- 🔐 **Lisans ve Kullanıcı Yönetimi**: Demo süresi, aktif kullanım ve izinler.
- 🧾 **Kişisel Loglama**: Her yayıncı/bot için ayrı takip ve denetim imkanı.
- 🛍 **Bot Market Hazırlığı**: Hazır karakterlerle dağıtıma uygun altyapı.

---

## ⚙️ Komutlar

Aşağıdaki komutlar doğrudan Telegram üzerinden kullanılabilir.  
**Bazı komutlar geliştirme aşamasında olup, yakın zamanda eklenecektir.**

### 👑 Yönetici Komutları

| Komut                       | Açıklama                                                         | Durum      |
|-----------------------------|-------------------------------------------------------------------|------------|
| `/lisans [user_id]`         | Kullanıcı lisansını aktif eder                                   | ✅ Hazır   |
| `/kapat [user_id]`          | Kullanıcı lisansını devre dışı bırakır                           | ✅ Hazır   |
| `/durum [user_id]`          | Kullanıcı lisans durumunu gösterir                               | ✅ Hazır   |
| `/mod [user_id] [mod]`      | Yanıt modunu değiştir (manual, ai, hybrid, fallback)              | ✅ Hazır   |
| `/profil [user_id]`         | Kullanıcının profilini görüntüler                                | ✅ Hazır   |
| `/klonla [id1] [id2]`       | Kullanıcı profilini kopyalar                                     | ✅ Hazır   |
| `/bots`                     | Aktif botları listeler                                           | ✅ Hazır   |
| `/log [user_id]`            | Son logları gösterir                                             | ✅ Hazır   |
| `/session_durum [username]` | Bot oturumunun teknik durumunu kontrol eder                      | ✅ Hazır   |
| `/durum_ozet`               | Genel sistem özet raporu                                         | ✅ Hazır   |
| `/panel [@username]`        | GPT kontrol panelini açar                                         | ✅ Hazır   |
| `/logara [@username]`       | Log dosyasında gelişmiş arama yapar                              | ✅ Hazır   |
| `/log_stats [@username]`    | Log istatistiklerini gösterir                                    | ✅ Hazır   |
| `/show_menu_list`           | Mevcut show menülerini listeler                                  | ✅ Hazır   |
| `/show_menu_view [bot]`     | Bot'un show menüsünü görüntüler                                  | ✅ Hazır   |
| `/show_menu_update [bot]`   | Bot'un show menüsünü günceller                                   | ✅ Hazır   |
| `/metrik [tarih]`           | Günlük metrik raporu gösterir                                    | ⚠️ Yakında|
| `/performans`               | Sistem performans metriklerini gösterir                          | ⚠️ Yakında|

### 👤 Yayıncı / İçerik Üretici Komutları

| Komut                | Açıklama                                                     | Durum      |
|----------------------|--------------------------------------------------------------|------------|
| `/menü [metin]`      | Hizmet menüsünü günceller                                    | ✅ Hazır   |
| `/show_menu [metin]` | Show menüsünü günceller (profesyonel)                       | ✅ Hazır   |
| `/show_compact`      | Kısa show menüsünü görüntüler                               | ✅ Hazır   |
| `/flört [mesajlar]`  | Flört mesaj şablonlarını günceller                          | ✅ Hazır   |
| `/mod [mode]`        | Yanıt modunu değiştirir (manual/gpt/hybrid/manualplus)      | ✅ Hazır   |
| `/bilgilerim`        | Profil bilgilerini ve ayarları gösterir                     | ✅ Hazır   |
| `/profilim`          | Kendi profilini ve istatistiklerini gösterir                 | ⚠️ Yakında |
| `/ayarlar`           | Hesap/bot ayarlarını yönetir                                 | ⚠️ Yakında |
| `/ödemelerim`        | Ödeme ve bakiye bilgilerini gösterir                         | ⚠️ Yakında |
| `/kazanç`            | Güncel kazanç bilgisini verir                                | ⚠️ Yakında |
| `/mesaj [metin]`     | Kitleye veya müşteriye toplu mesaj gönderir                  | ⚠️ Yakında |
| `/referanslarım`     | Referans kodunu veya bağlantısını görüntüler                 | ⚠️ Yakında |
| `/görevlerim`        | Güncel görev/misyon listesini gösterir                       | ⚠️ Yakında |
| `/istatistik`        | Mesaj, etkileşim, gelir istatistikleri                       | ⚠️ Yakında |
| `/yardım`            | Yardım menüsü ve kullanım rehberi                            | ✅ Hazır   |

### 🙋‍♂️ Müşteri Komutları

| Komut                | Açıklama                                                      | Durum      |
|----------------------|---------------------------------------------------------------|------------|
| `/bilgi`             | Sistem ve hizmetler hakkında temel bilgi verir                | ⚠️ Yakında |
| `/başlat`            | Botu başlatır veya hesabı aktive eder                        | ⚠️ Yakında |
| `/yardım`            | Müşteri destek menüsünü ve komut listesini gösterir           | ⚠️ Yakında |
| `/mesaj [metin]`     | Yayıncıya/destek hattına mesaj göndermek için kullanılır      | ⚠️ Yakında |
| `/ödeme`             | Ödeme seçeneklerini ve talimatlarını görüntüler               | ⚠️ Yakında |
| `/abonelik`          | Mevcut abonelik ve kampanya bilgilerini gösterir              | ⚠️ Yakında |
| `/içerik`            | Özel içerik veya promosyonlara ulaşmak için kullanılır        | ⚠️ Yakında |

> **Not:** “Yakında” olarak işaretlenen komutlar roadmap’te planlanmış olup, geliştirme süreci devam etmektedir.  
> Güncellemeler için projenin Github sayfasını takip ediniz.

---

## 🛡 Anonimlik ve Ödeme Sistemi

- ✅ Desteklenen bankalarda *Papara ID* ile anonim ödeme mümkündür.
- ⚠️ Bazı bankalarda *gerçek isim girişi* gerekebilir.
- 🔒 İçerik üreticileri dilerse kendi IBAN’larını tanımlayabilir.

---

## 🧪 Test Sistemi

GAVATCore kapsamlı bir test sistemi ile gelir. **Tüm test dosyaları `tests/` klasöründe organize edilmiştir.**

### Test Çalıştırma
```bash
# 🗄️ Database testleri (ÖNEMLİ - İlk çalıştırılmalı)
cd tests
python test_multidb.py           # Multi-database sistem testi
python test_integration.py       # Tam entegrasyon testi (5/5)

# 🤖 Tam sistem testi (%100 başarı oranı)
python test_complete_system.py

# 📊 Tek test çalıştırma
python test_anti_spam_system.py

# 🔄 Tüm testleri çalıştırma
python -m pytest test_*.py -v
```

### Test Sonuçları (v2.0.0)
```
🚀 GAVATCORE TAM SİSTEM TESTİ
============================================================

📊 Test İstatistikleri:
   ✅ Başarılı: 44
   ❌ Başarısız: 0
   📈 Başarı Oranı: 100.0%
   🔢 Toplam Test: 44

🚀 SİSTEM PRODUCTION'A HAZIR!
```

### Ana Test Kategorileri
- 👑 **Role-Based Komut Sistemi**: Admin/Producer/Client rol testleri
- 🛠️ **GPT Kontrol Paneli**: Inline button ve state yönetimi
- 🔍 **Gelişmiş Log Sistemi**: Arama, filtreleme ve istatistik
- 🛡️ **Anti-Spam Sistemi**: Dinamik cooldown, hesap yaşı kontrolü
- 🎭 **Hybrid Mode**: GPT/Bot/Genel mesaj dağılımı testleri
- 📱 **DM Handler**: Özel mesaj işleme ve manuel müdahale tespiti
- 🔄 **Spam Sistemi**: Spam loop, direkt spam ve async testleri
- 📋 **Menu Sistemi**: Otomatik menu ve sistem durumu testleri

Detaylı bilgi için: [`docs/GPT_CONTROL_PANEL_GUIDE.md`](docs/GPT_CONTROL_PANEL_GUIDE.md)

---

## 📚 Dokümantasyon

Tüm sistem dokümantasyonu `docs/` klasöründe organize edilmiştir:

### 🔗 Hızlı Erişim
- **[📋 Dokümantasyon İndeksi](docs/README.md)** - Tüm dokümantasyon listesi
- **[🚀 Proje Yol Haritası](docs/ROADMAP.md)** - Gelecek planları
- **[📝 Değişiklik Geçmişi](docs/CHANGELOG.md)** - Versiyon notları
- **[🏗️ Sistem Mimarisi](docs/MULTIDB_MIGRATION_SUMMARY.md)** - Database yapısı

### 📖 Ana Kategoriler
- **🤖 Bot Yönetimi**: Handler'lar, yanıt modları, komutlar
- **🛡️ Güvenlik**: Anti-spam, rate limiting, acil durum prosedürleri  
- **🧠 AI Sistemi**: GPT kontrol paneli, hybrid mode, DM iyileştirmeleri
- **🔧 Teknik**: Sistem optimizasyonları, bug düzeltmeleri, raporlar

**Tam liste için**: [`docs/README.md`](docs/README.md)

---

## ❤️ Katkıda Bulunmak

Pull request gönderebilir, yıldız bırakabilir ya da öneri sunabilirsiniz.  
Açık kaynak projeye her katkı memnuniyetle kabul edilir!

---

## ⚠️ Uyarı

> Bu proje, prototip ve AR-GE amaçlı geliştirilmiştir.  
> Telegram’ın topluluk kurallarına ve yasal çerçeveye uygun şekilde kullanılmalıdır.  
> Sistem üzerinde gerçek para işlemleri yapılmadan önce, tüm entegrasyonlar ve güvenlik önlemleri dikkatlice test edilmelidir.

---

## ✨ Lisans

MIT License – “Yazılım herkese açık, güvenliğe ve etik ilkelere dikkat edilmelidir.”
