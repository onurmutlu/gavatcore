# 🧪 GAVATCORE Test Sistemi

Bu klasör GAVATCORE bot sisteminin tüm test dosyalarını ve geçici test verilerini içerir.

## 📁 Klasör Yapısı

```
tests/
├── README.md                    # Bu dosya
│
├── 🗄️ DATABASE TESTLERI
├── test_multidb.py              # Multi-database sistem testi
├── test_integration.py          # Database entegrasyon testleri
├── test_db_creation.py          # Database tablo oluşturma testi
├── test_sqlmodel_logs.py        # SQLModel log testleri
├── test_mongo_profile.py        # MongoDB profil testleri
├── test_redis_state.py          # Redis state testleri
├── test_complete_system.py      # Tam sistem testleri
│
├── 🤖 BOT TESTLERI
├── test_anti_spam_system.py     # Anti-spam sistemi testleri
├── test_hybrid_mode.py          # Hybrid mode testleri
├── test_dm_handler.py           # DM handler testleri
├── test_dm_debug.py             # DM debug testleri
├── test_gavatbaba_dm_flow.py    # GavatBaba DM akış testleri
├── test_event_handler.py        # Event handler testleri
├── test_manual_intervention.py  # Manuel müdahale testleri
│
├── 🧠 GPT TESTLERI
├── test_gpt_panel.py            # GPT kontrol paneli testleri
├── test_gpt_system.py           # GPT sistem testleri
│
├── 📋 MENU TESTLERI
├── test_gavatbaba_menu.py       # GavatBaba menu testleri
├── test_geisha_menu.py          # Geisha menu testleri
├── test_auto_menu.py            # Otomatik menu testleri
├── test_show_menus.py           # Menu gösterim testleri
├── test_show_system.py          # Sistem gösterim testleri
│
├── 📤 SPAM TESTLERI
├── test_spam_await.py           # Spam await testleri
├── test_spam_direct.py          # Direkt spam testleri
├── test_spam_loop.py            # Spam loop testleri
├── test_mixed_messages.py       # Karışık mesaj testleri
│
├── 🔧 UTILITY TESTLERI
├── test_file_utils.py           # File utilities testleri
│
├── 📁 TEST VERILERI
├── data/                        # Test veri klasörü
├── logs/                        # Test log klasörü
├── *.session                    # Test session dosyaları
└── *.json.lock                  # Geçici test verileri
```

## 🚀 Test Çalıştırma

### Tek Test Çalıştırma
```bash
cd tests
python test_anti_spam_system.py
```

### Tüm Testleri Çalıştırma
```bash
cd tests
python -m pytest test_*.py -v
```

### Belirli Kategori Testleri
```bash
# 🗄️ Database testleri (ÖNEMLİ - İlk çalıştırılmalı)
python test_multidb.py           # Multi-database sistem testi
python test_integration.py       # Tam entegrasyon testi (5/5)
python test_db_creation.py       # Database oluşturma testi

# 🤖 Bot testleri
python test_anti_spam_system.py  # Anti-spam sistemi
python test_hybrid_mode.py       # Hybrid mode
python test_gavatbaba_dm_flow.py # DM akış testleri

# 🧠 GPT testleri
python test_gpt_panel.py         # GPT kontrol paneli
python test_gpt_system.py        # GPT sistem testleri

# 📋 Menu testleri
python test_gavatbaba_menu.py    # GavatBaba menu
python test_auto_menu.py         # Otomatik menu

# 📤 Spam testleri
python test_spam_loop.py         # Spam loop
python test_spam_direct.py       # Direkt spam
python test_spam_await.py        # Async spam

# 🔧 DM handler testleri
python test_dm_handler.py        # DM handler
python test_dm_debug.py          # DM debug
```

## 🛡️ Ana Test Kategorileri

### 🗄️ Database Testleri

#### 1. Multi-Database Sistemi (`test_multidb.py`)
- ✅ PostgreSQL/SQLite bağlantı testi
- ✅ MongoDB/File-based profil sistemi testi
- ✅ Redis state management testi
- ✅ Tüm database'lerin senkronize çalışması

#### 2. Database Entegrasyonu (`test_integration.py`)
- ✅ PostgreSQL/SQLite log sistemi (5/5 test)
- ✅ MongoDB/File-based profil sistemi (5/5 test)
- ✅ Redis state management (5/5 test)
- ✅ Log utils entegrasyonu (5/5 test)
- ✅ DM handler state entegrasyonu (5/5 test)
- 🎯 **%100 başarı oranı**

#### 3. Database Oluşturma (`test_db_creation.py`)
- ✅ Tablo oluşturma testi
- ✅ Model doğrulama testi

### 🤖 Bot Testleri

#### 4. Anti-Spam Sistemi (`test_anti_spam_system.py`)
- ✅ Hesap yaşı kontrolü
- ✅ Spam güvenlik testi
- ✅ Dinamik cooldown hesaplama
- ✅ Trafik analizi
- ✅ Mesaj varyasyonları
- ✅ VIP satış mesajları
- ✅ GPT entegrasyonu
- ✅ Çeşitlilik analizi

### 2. Hybrid Mode (`test_hybrid_mode.py`)
- 🎭 %60 GPT, %30 Bot Profili, %10 Genel dağılım
- 💎 VIP satış odaklı testler
- 🤖 Bot karakteri uyumu

### 3. DM Handler (`test_dm_handler.py`, `test_dm_debug.py`)
- 📱 Özel mesaj işleme
- 👤 Manuel müdahale tespiti
- ⏰ Timeout yönetimi

### 4. Spam Sistemi (`test_spam_*.py`)
- 🔄 Spam loop testleri
- 📤 Direkt spam testleri
- ⏳ Async spam testleri

### 5. Menu Sistemi (`test_*_menu*.py`)
- 📋 Menu gösterim testleri
- 🎯 Otomatik menu testleri
- 🖥️ Sistem durumu testleri

## 📊 Test Sonuçları

### Başarılı Test Örneği:
```
🛡️ ANTI-SPAM SİSTEMİ TEST BAŞLIYOR...
============================================================
🤖 Test Bot: bot_gavatbaba
📱 Test Grup ID: 123456789

1️⃣ HESAP YAŞI TESTİ
   Hesap yaşı: 0.0 saat
   🔰 Yeni hesap - sadece reply mode

2️⃣ SPAM GÜVENLİK TESTİ
   Spam güvenli: False
   Sebep: 🔰 Yeni hesap (yaş: 0.0h) - sadece reply mode

✅ ANTI-SPAM SİSTEMİ TESTİ TAMAMLANDI!
```

## 🔧 Test Geliştirme

### Yeni Test Ekleme
1. `tests/` klasöründe `test_yeni_ozellik.py` oluştur
2. Import yollarını düzelt:
```python
#!/usr/bin/env python3
# tests/test_yeni_ozellik.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Şimdi normal import'ları yap
from utils.module import function
```

### Test Dosyası Şablonu
```python
#!/usr/bin/env python3
# tests/test_example.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from utils.example_module import example_function

async def test_example_feature():
    """Örnek özellik testi"""
    
    print("🧪 ÖRNEK TEST BAŞLIYOR...")
    print("=" * 50)
    
    try:
        result = await example_function()
        print(f"✅ Test başarılı: {result}")
    except Exception as e:
        print(f"❌ Test başarısız: {e}")
    
    print("🎉 TEST TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(test_example_feature())
```

## 📝 Test Verileri

### Session Dosyaları
- `test_*.session`: Test için kullanılan Telegram session'ları
- `temp_*.session`: Geçici test session'ları

### Lock Dosyaları
- `*.json.lock`: Test sırasında oluşturulan geçici veri dosyaları
- Testler tamamlandıktan sonra otomatik temizlenir

## ⚠️ Önemli Notlar

1. **Import Yolları**: Tüm test dosyaları parent directory'yi sys.path'e ekler
2. **Session Güvenliği**: Test session'ları production'dan ayrı tutulur
3. **Geçici Dosyalar**: Test verileri tests/ klasöründe kalır
4. **Async Testler**: Async fonksiyonlar için `asyncio.run()` kullanılır

## 🎯 Test Stratejisi

### Unit Testler
- Tek fonksiyon/modül testleri
- Hızlı ve izole testler

### Integration Testler  
- Modüller arası etkileşim testleri
- Anti-spam + GPT entegrasyonu

### End-to-End Testler
- Tam sistem testleri
- Bot davranış testleri

## 📈 Test Metrikleri

- **Kapsama**: %90+ kod kapsaması hedefi
- **Performans**: Test süresi < 30 saniye
- **Güvenilirlik**: %95+ başarı oranı
- **Bakım**: Haftalık test güncellemeleri

---

**Son Güncelleme**: 26 Mayıs 2025  
**Test Sayısı**: 15+ test dosyası  
**Kapsama**: Anti-spam, Hybrid Mode, DM Handler, Spam Sistemi  
**Durum**: ✅ Aktif ve Güncel 