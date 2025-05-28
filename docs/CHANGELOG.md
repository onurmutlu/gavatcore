# 📑 CHANGELOG

> Her büyük güncelleme ve altyapı değişikliği burada tarihsel olarak takip edilir.  
> Tüm modül ve kod geliştirmeleri şeffaf, izlenebilir ve sürdürülebilir şekilde versiyonlanır.

---

## [v1.1.0] – Metrik Sistemi & Analytics Geliştirmesi  
**Released:** 2025-05-26

### Eklendi
- `core/metrics_collector.py` modülüne yeni özellikler:
    - Asenkron metrik toplama ve işleme desteği.
    - Gelişmiş Dashboard API entegrasyonu.
    - Günlük rapor oluşturma fonksiyonu.
    - Özelleştirilebilir metrik işleyiciler (handler altyapısı).
    - Metriklerin CSV ve JSONL formatlarında dışa aktarımı.
- Yeni metrik türleri:
    - Kullanıcı bazlı aksiyon ve etkileşim takibi.
    - Saatlik, günlük, haftalık dağılım ve segmentasyon.
    - Özelleştirilebilir etiket/tag desteği.

### İyileştirildi
- Metrik toplama performansı ve dosya yönetimi optimize edildi.
- Eski metrik dosyalarının otomatik arşivlenmesi ve temizlenmesi.
- Hata anında otomatik recovery ve raporlama desteği.
- Dashboard entegrasyonu için batch gönderim desteği ve zamanlayıcı eklemesi.

### Düzeltildi
- Metrik dosyalarında UTF-8 karakter hataları giderildi.
- Yüksek yükte metrik kaybı ve API timeout sorunları çözüldü.

---

## [v1.0.0] – İlk Yayın & PostgreSQL + Redis Geçişi  
**Released:** 2025-05-24

### Eklendi
- **Yeni modüller:**
    - `core/error_tracker.py` – Gelişmiş hata izleme, loglama ve kritik hata bildirimleri (e-posta & Telegram desteği).
    - `utils/file_utils.py` – Güvenli, atomik ve asenkron dosya işlemleri. Otomatik yedekleme, geri yükleme (recovery) ve büyük dosya yönetimi. Cluster ortamı için distributed locking.
    - `utils/security_utils.py` – Kullanıcı yetkilendirme, rate-limit, erişim loglama ve şüpheli kullanıcı takibi. JWT ve IP doğrulama desteği.
    - `core/metrics_collector.py` – Kullanıcı, mesaj, lisans ve işlem metrikleri modülü.
- Merkezi `config.py` ile yapılandırma yönetimi.
- Detaylı test fonksiyonları ve örnek kullanım kodları.
- Cross-platform dosya kilitleme, multi-process güvenli dosya güncelleme.
- Transactional multi-write ve otomatik failover recovery (yedekten otomatik kurtarma).
- Streaming JSON okuma (büyük dosyalar için).

### İyileştirildi
- `error_tracker` modülünde:
    - Admin bildirimlerine rate-limit/flood koruma (1dk/10 tekrar).
    - Uzun Telegram mesajlarını otomatik parçalayan destek (4096 karakter limiti).
    - Daha güvenli loglama, context kısaltma ve gelişmiş decorator bilgisi.
- `file_utils.py`:
    - Zstandard ile sıkıştırılmış yedekleme.
    - Redis/portalocker tabanlı distributed lock.
    - JSON şema doğrulama (`jsonschema`).
    - Recovery işlemlerinde hata loglama ve admin notification.
- `security_utils.py`:
    - Her işlem için merkezi rate-limit ve yetkilendirme kontrolü.
    - Ayrı log dosyasına ve konsola güvenlik olayı kaydı.
    - Yetkisiz erişimlerde otomatik block ve şüpheli işaretleme.

### Düzeltildi
- Bozuk/eksik JSON dosyalarında otomatik yedekten kurtarma ve geri alma mekanizması.
- Multi-process ve asenkron işlemlerde uyumluluk ve uyarılar.

---

## [v0.9.0] – Alpha Test & Modülerleşme  
**Released:** 2025-05-22

### Eklendi
- Temel dosya tabanlı JSON modülleri (`file_utils.py`, `metrics_collector.py`).
- Basit rate-limit ve kullanıcı doğrulama altyapısı.
- Log dosyası tabanlı hata izleme ve bildirim mekanizması.

### Değiştirildi
- Tüm modüller bağımsız dosyalara ve merkezi konfigürasyona bölündü.
- Daha okunabilir, async destekli IO yapısı.

### Kaldırıldı
- Tek dosya üstünden tüm IO işlemleri ve basit locking yöntemleri.

---

## [v0.8.0] – Prototip & İlk Demo  
**Released:** 2025-05-18

### Eklendi
- Temel iş akışı ve modül iskeletleri, fonksiyon prototipleri.

---

> **Not:**  
> v1.0.0 itibariyle sistem, dosya tabanlı yapıdan **PostgreSQL + Redis** altyapısına tamamen hazır ve taşınabilir hale getirilmiştir.  
> Tüm yedeklemeler, upgrade öncesinde tam olarak alınmış ve test edilmiştir.  
> Her versiyonun detaylı test senaryoları ve örnek kullanım kodları repoda yer almaktadır.

---
