# 🤖 GAVATCore™ – Telegram İçerik Platformları İçin Otomasyon Sistemi

**GAVATCore™**, Telegram üzerinden içerik yönetimi, etkileşim ve otomatik müşteri ilişkileri için geliştirilmiş bir ⚡️otomasyon altyapısıdır.  
Yapay zekâ destekli yayıncı profilleri, otomatik mesajlaşma, ödeme takip ve detaylı loglama ile dijital içerik üreticileri ve ajanslar için eksiksiz bir çözüm sunar.

---

## 🚀 Özellikler

- 🤖 **AI Destekli Karakterler**: Lara, Geisha gibi kişiselleştirilmiş sohbet botları (GPT).
- 📊 **Gelişmiş Metrik ve Log Sistemi**: Kullanıcı davranışları ve işlem geçmişi takibi.
- 📣 **Grup & DM Mesajlaşma**: Otomatik içerik paylaşımı, mention ve cevap yönetimi.
- 💸 **Papara & IBAN Entegrasyonu**: Güvenli ve kolay ödeme sistemi desteği.
- 🧠 **Akıllı Yanıt Modları**: Manuel, AI, Hibrit ve otomatik yedekleme (fallback) desteği.
- 📡 **Telegram Üzerinden Tam Yönetim**: Web panel gerektirmeden, sadece Telegram ile.
- 🔐 **Lisans ve Kullanıcı Yönetimi**: Demo süresi, aktif kullanım ve izinler.
- 🧾 **Kişisel Loglama**: Her yayıncı/bot için ayrı takip ve denetim imkanı.
- 🛍 **Bot Market Hazırlığı**: Hazır karakterlerle dağıtıma uygun altyapı.
- 📈 **Dashboard Entegrasyonu (Yakında)**: Gerçek zamanlı performans izleme.

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
| `/metrik [tarih]`           | Günlük metrik raporu gösterir                                    | ⚠️ Yakında|
| `/performans`               | Sistem performans metriklerini gösterir                          | ⚠️ Yakında|

### 👤 Yayıncı / İçerik Üretici Komutları

| Komut                | Açıklama                                                     | Durum      |
|----------------------|--------------------------------------------------------------|------------|
| `/profilim`          | Kendi profilini ve istatistiklerini gösterir                 | ⚠️ Yakında |
| `/ayarlar`           | Hesap/bot ayarlarını yönetir                                 | ⚠️ Yakında |
| `/ödemelerim`        | Ödeme ve bakiye bilgilerini gösterir                         | ⚠️ Yakında |
| `/kazanç`            | Güncel kazanç bilgisini verir                                | ⚠️ Yakında |
| `/mesaj [metin]`     | Kitleye veya müşteriye toplu mesaj gönderir                  | ⚠️ Yakında |
| `/referanslarım`     | Referans kodunu veya bağlantısını görüntüler                 | ⚠️ Yakında |
| `/görevlerim`        | Güncel görev/misyon listesini gösterir                       | ⚠️ Yakında |
| `/istatistik`        | Mesaj, etkileşim, gelir istatistikleri                       | ⚠️ Yakında |
| `/yardım`            | Yardım menüsü ve kullanım rehberi                            | ⚠️ Yakında |

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
