# 🪙 GavatCoin Token Engine (Closed Loop)

**OnlyVips v6.0 Token Economy System**  
*Kapalı döngü token ekonomisi - Dışa çıkmayan, sadece iç harcama sistemi*

---

## 🔄 Token Mantığı

### 💰 Temel Kurallar:
- **1 XP = 1 Token** (Sabit dönüşüm oranı)
- **Token dışarı çıkmaz** (Kapalı ekonomi)
- **Token harcamaları sadece platform içi** hizmetler için kullanılır
- **Atomik işlemler** - Her token hareketi log'lanır
- **Production-safe** - aiosqlite ile güvenli async operasyonlar

### 🔐 Güvenlik Özellikleri:
- ✅ **Yetersiz bakiye koruması** - Sahip olmadığınız token'ı harcayamazsınız
- ✅ **Transaction logging** - Her işlem otomatik kayıt altına alınır  
- ✅ **Async-safe operations** - Eş zamanlı işlemler desteklenir
- ✅ **Database integrity** - SQLite ile veri tutarlılığı garantisi

---

## 🎯 Kullanım Alanları

| Hizmet | Token Maliyeti | Açıklama |
|--------|----------------|----------|
| 🎬 **Premium İçerik** | 10 token | Özel video, fotoğraf, medya satın alma |
| 👑 **VIP Statü** | 25 token | VIP üyeliğe yükseltme |
| ⚡ **Görev Boost** | 5 token | Günlük görevlerde 2x ödül |
| 🎨 **NFT Rozet** | 50 token | Özel koleksiyoner rozetleri |
| 📨 **Öncelikli DM** | 15 token | Bot'larla 24 saat öncelikli iletişim |

---

## 🚀 Kullanım Kılavuzu

### 📦 Kurulum
```bash
# aiosqlite dependency
pip install aiosqlite

# Test sistemi çalıştırma
cd xp_token_engine
python token_test.py
```

### 🧪 Test Senaryosu
```python
# 1. 50 XP kazanın → 50 token'a dönüştürün
# 2. Premium içerik satın alın (10 token)
# 3. Görev boost yapın (5 token)  
# 4. VIP olmaya çalışın (25 token gerekli)
# 5. Transaction log'larınızı kontrol edin
```

### 💻 Kod Entegrasyonu
```python
from xp_token_engine.token_manager import get_token_manager
from xp_token_engine.spend_handlers import spend_token_for_service

# XP'yi token'a çevir
async with get_token_manager() as tm:
    new_balance = await tm.xp_to_token("user123", 100)
    
# Hizmet satın al
success, message = await spend_token_for_service(
    "user123", 
    "content", 
    content_id="premium_video_001"
)
```

---

## 📊 Sistem Mimarisi

### 🗂️ Dosya Yapısı:
```
xp_token_engine/
├── token_manager.py      # Core token işlemleri
├── spend_handlers.py     # Harcama noktaları
├── token_test.py         # CLI test aracı
├── tokens.db            # SQLite veritabanı
└── README.md            # Bu dosya
```

### 🗃️ Veritabanı Schema:
```sql
-- Kullanıcı bakiyeleri
CREATE TABLE balances (
    user_id TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- İşlem geçmişi
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,        -- 'EARN' or 'SPEND'
    amount INTEGER NOT NULL,   -- Pozitif=kazanç, Negatif=harcama  
    reason TEXT,              -- İşlem açıklaması
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔐 Ekstra Özellikler

### 🚫 **Anti-Exploit Korumaları:**
- **Negatif token engeli** - Sıfırın altına düşemez
- **Invalid amount engeli** - Geçersiz miktarlar reddedilir
- **Transaction atomicity** - Yarım işlemler geri alınır

### 📈 **Analytics Ready:**
- Sistem geneli istatistikler
- Kullanıcı başına transaction history
- Top spender listeleri
- Token dolaşım miktarı

### 🔄 **Future-Proof:**
- MongoDB entegrasyonu hazır
- API endpoint'leri eklenebilir  
- Real-time dashboard desteği
- Multi-currency expansion hazır

---

## 🏆 Örnek Kullanım Senaryoları

### 💎 **Yeni Kullanıcı Journey:**
1. **Kayıt bonusu:** 50 XP → 50 token
2. **İlk görev tamamlama:** 20 XP → 20 token  
3. **Premium içerik satın alma:** -10 token
4. **Görev boost:** -5 token
5. **Kalan bakiye:** 55 token

### 🎮 **Power User Journey:**
1. **Haftalık görevler:** 200 XP → 200 token
2. **VIP upgrade:** -25 token
3. **NFT rozet:** -50 token  
4. **Öncelikli DM:** -15 token
5. **Premium içerikler:** -30 token
6. **Kalan bakiye:** 80 token

---

## 🔧 Teknik Detaylar

### ⚡ **Performance:**
- **Async/await** - Non-blocking database operations
- **Connection pooling** - Efficient SQLite usage
- **Batch operations** - Multiple transactions support
- **Error handling** - Graceful failure recovery

### 🛡️ **Security:**
- **SQL injection koruması** - Parameterized queries
- **Race condition koruması** - Atomic transactions
- **Data validation** - Input sanitization
- **Audit trail** - Complete transaction history

---

## 📞 API Entegrasyonu (Opsiyonel)

Bu token sistemi mevcut **production_bot_api.py** ile entegre edilebilir:

```python
# API endpoint örnekleri
@app.route('/api/tokens/balance/<user_id>')
@app.route('/api/tokens/spend', methods=['POST'])
@app.route('/api/tokens/earn', methods=['POST'])
@app.route('/api/tokens/history/<user_id>')
```

---

*Bu sistem tamamen kapalı döngü olarak tasarlanmıştır. Token'lar gerçek dünyaya çıkmaz, sadece platform içi değer taşır. Bu sayede yasal regülasyonlardan bağımsız çalışır ve tamamen kontrol altındadır.*

**🚀 GavatCoin ile OnlyVips v6.0 ekonomisini kontrol edin!** 💰 