# 🎭 Universal Character System - Tüm Karakterler İçin Genel Sistem

GAVATCore üzerinde çalışan **Universal Character System** - Lara, Geisha, BabaGavat ve herhangi bir karakter için genişletilebilir AI bot sistemi.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Karakterler](#-karakterler)
- [Entegrasyon](#-entegrasyon)
- [Yeni Karakter Ekleme](#-yeni-karakter-ekleme)
- [API Referansı](#-api-referansı)
- [Test Etme](#-test-etme)
- [Konfigürasyon](#-konfigürasyon)

---

## 🚀 Özellikler

### 🎭 Universal Karakter Sistemi
- **Modüler Yapı**: Tüm karakterler aynı sistem üzerinde
- **8 Karakter Tipi**: Flirty, Seductive, Leader, Friendly, Professional, Playful, Mysterious, Dominant
- **Otomatik Prompt Üretimi**: Her karakter için özelleştirilmiş AI promptları
- **Dinamik Konfigürasyon**: Runtime'da karakter ayarları değiştirme

### 🤖 AI Özellikleri
- **OpenAI Entegrasyonu**: GPT-4 ile gelişmiş yanıtlar
- **Karakter Bazlı Hafıza**: Her karakter için ayrı konuşma geçmişi
- **Adaptif Yanıtlar**: Konuşma durumuna göre tonlama
- **Fallback Sistemi**: AI yanıt alamadığında hazır yanıtlar
- **Multi-Language**: Karakter özelliklerine göre dil desteği

### 💼 İş Özellikleri
- **VIP Hizmet Yönetimi**: Her karakter için özel hizmet menüsü
- **Ödeme Entegrasyonu**: Karakter bazlı ödeme bilgileri
- **Satış Analytics**: Detaylı konuşma ve performans analizi
- **Customer Journey**: Kullanıcı ilgi seviyesi takibi

### 🔌 Entegrasyon
- **Mevcut Sistem Uyumlu**: GAVATCore botlarıyla kolay entegrasyon
- **Backward Compatibility**: Eski API'lerle uyumluluk
- **Auto Detection**: Profil'den otomatik karakter tespit
- **Plug & Play**: Tek satır kod ile entegrasyon

---

## 🛠️ Kurulum

### 1. Sistem Gereksinimleri

```bash
# Python 3.8+ gerekli
python --version

# GAVATCore sistemi kurulu olmalı
# Mevcut requirements.txt yeterli
```

### 2. Dosya Yerleştirme

Universal Character System GAVATCore klasör yapısına aşağıdaki şekilde entegre edilmiştir:

```
gavatcore/
├── handlers/
│   ├── universal_character_system.py          # Ana framework
│   ├── character_definitions.py               # Karakter tanımları
│   ├── universal_character_integration.py     # Entegrasyon sistemi
│   └── lara_integration.py                   # Eski Lara sistemi (uyumluluk için)
└── test_universal_characters.py              # Test sistemi
```

### 3. Sistem Başlatma

```python
# Otomatik başlatma (import ile)
from handlers.universal_character_integration import initialize_universal_characters

# Manuel başlatma
initialize_universal_characters()
```

---

## ⚡ Hızlı Başlangıç

### 1. Sistem Testi

```bash
# Tüm testleri çalıştır
python test_universal_characters.py --all

# Demo çalıştır
python test_universal_characters.py --demo
```

### 2. Mevcut Bot'a Entegrasyon

```python
# DM handler'da
from handlers.universal_character_integration import integrate_universal_dm_handler

async def handle_dm(client, sender, message_text, bot_username, bot_profile):
    # Universal karakter kontrolü
    if await integrate_universal_dm_handler(client, sender, message_text, bot_username, bot_profile):
        return  # Universal karakter tarafından işlendi
    
    # Normal handler devam eder...
```

### 3. Grup Handler'da

```python
# Group handler'da
from handlers.universal_character_integration import integrate_universal_group_handler

async def handle_group_message(client, event, bot_username, bot_profile):
    # Universal karakter kontrolü
    if await integrate_universal_group_handler(client, event, bot_username, bot_profile):
        return  # Universal karakter tarafından işlendi
    
    # Normal handler devam eder...
```

---

## 🎭 Karakterler

### Mevcut Karakterler

#### 🌹 Lara (Flirty)
- **Tip**: Flörtöz şovcu
- **Yaş**: 24, Yarı Rus
- **Özellikler**: Rusça kelimeler, flörtöz ama profesyonel
- **VIP Hizmetler**: 4 adet (50₺-200₺)

#### 🌸 Geisha (Seductive)
- **Tip**: Baştan çıkarıcı
- **Yaş**: 25, Japon-Türk karışımı
- **Özellikler**: Hikaye anlatma, erotik içerik
- **VIP Hizmetler**: 4 adet (75₺-300₺)

#### 👑 BabaGavat (Leader)
- **Tip**: Otorite/Lider
- **Yaş**: 35, Türk
- **Özellikler**: Deneyimli, karizmatik, organizasyon
- **VIP Hizmetler**: 4 adet (200₺-500₺)

#### 😊 Maya (Friendly)
- **Tip**: Arkadaş canlısı
- **Yaş**: 22, Türk
- **Özellikler**: Samimi, duygusal destek
- **VIP Hizmetler**: 3 adet (25₺-50₺)

#### 🖤 Noir (Mysterious)
- **Tip**: Gizemli
- **Yaş**: 28, Belirsiz uyruk
- **Özellikler**: Felsefik, derin konuşma
- **VIP Hizmetler**: 3 adet (75₺-125₺)

### Karakter Tipleri

```python
class CharacterType(Enum):
    FLIRTY = "flirty"              # Lara gibi
    SEDUCTIVE = "seductive"        # Geisha gibi
    LEADER = "leader"              # BabaGavat gibi
    FRIENDLY = "friendly"          # Maya gibi
    PROFESSIONAL = "professional"  # İş odaklı
    PLAYFUL = "playful"           # Şakacı
    MYSTERIOUS = "mysterious"      # Noir gibi
    DOMINANT = "dominant"         # Baskın karakter
```

---

## 🔌 Entegrasyon

### Otomatik Tespit

Sistem bot kullanıcı adı ve profilinden otomatik karakter tespit eder:

```python
# Username'den tespit
"lara" -> "lara"
"yayincilara" -> "lara"
"xxxgeisha" -> "geisha"
"babagavat" -> "babagavat"

# Profile'dan tespit
{"type": "lara_bot"} -> "lara"
{"display_name": "🌸 Geisha"} -> "geisha"
{"personality": ["lider", "güçlü"]} -> "babagavat"
```

### Mevcut Handler Entegrasyonu

#### 1. DM Handler Entegrasyonu

```python
# handlers/dm_handler.py'ye ekle
from handlers.universal_character_integration import integrate_universal_dm_handler

async def handle_message(client, sender, message_text, session_created_at, username, bot_profile=None):
    # ... mevcut kod ...
    
    # Universal karakter kontrolü (YENİ)
    if await integrate_universal_dm_handler(client, sender, message_text, username, bot_profile):
        log_analytics("universal_character", "dm_handled", {"username": username})
        return
    
    # Mevcut handler'lar devam eder
    # ... geri kalan kod ...
```

#### 2. Group Handler Entegrasyonu

```python
# handlers/group_handler.py'ye ekle
from handlers.universal_character_integration import integrate_universal_group_handler

async def handle_group_message(event, client, username, bot_profile=None):
    # ... mevcut kod ...
    
    # Universal karakter kontrolü (YENİ)
    if await integrate_universal_group_handler(client, event, username, bot_profile):
        log_analytics("universal_character", "group_handled", {"username": username})
        return
    
    # Mevcut handler'lar devam eder
    # ... geri kalan kod ...
```

### Bot Profili Oluşturma

```python
from handlers.universal_character_integration import create_universal_character_profile

# Yeni bot profili oluştur
profile = create_universal_character_profile(
    character_id="lara",
    bot_username="yeni_lara_bot",
    user_id=12345
)

# Profili kaydet
save_profile("yeni_lara_bot", profile)
```

### Mevcut Bot Dönüştürme

```python
from handlers.universal_character_integration import update_existing_bot_to_universal

# Mevcut bot'u universal'e çevir
existing_profile = load_profile("eski_bot")
universal_profile = update_existing_bot_to_universal(existing_profile, character_id="geisha")

if universal_profile:
    save_profile("eski_bot", universal_profile)
    print("✅ Bot universal sisteme çevrildi!")
```

---

## ➕ Yeni Karakter Ekleme

### 1. Karakter Tanımı Oluştur

```python
# handlers/character_definitions.py'ye ekle
def create_my_character() -> CharacterConfig:
    return CharacterConfig(
        name="MyCharacter",
        display_name="⭐ MyChar",
        age=30,
        nationality="Türk",
        character_type=CharacterType.PLAYFUL,  # Tip seç
        personality=[
            "şakacı ve eğlenceli",
            "pozitif enerji",
            "yaratıcı"
        ],
        languages=["Türkçe", "İngilizce"],
        
        # Davranış ayarları
        min_response_delay=1.0,
        max_response_delay=3.0,
        emoji_usage=True,
        special_words=["harika", "muhteşem", "süper"],
        
        # VIP Hizmetler
        vip_services={
            "özel_oyun": {
                "price": "75₺",
                "description": "Özel oyun ve eğlence 🎮"
            },
            "yaratıcı_içerik": {
                "price": "100₺",
                "description": "Yaratıcı içerik üretimi 🎨"
            }
        },
        
        # Ödeme bilgileri
        payment_info={
            "papara_no": "9999888777",
            "iban": "TR99 9888 7777 6666 5555 4444 33",
            "hesap_sahibi": "MyChar K."
        }
    )
```

### 2. Karakteri Kaydet

```python
# register_all_characters() fonksiyonuna ekle
def register_all_characters():
    # ... mevcut karakterler ...
    
    # Yeni karakter
    register_character("mychar", create_my_character())
```

### 3. Username Mapping Ekle

```python
# get_character_by_username() fonksiyonuna ekle
def get_character_by_username(username: str) -> str:
    username_mappings = {
        # ... mevcut mappings ...
        
        # Yeni karakter
        "mychar": "mychar",
        "mycharbot": "mychar",
        "my_character": "mychar"
    }
    # ... geri kalan kod ...
```

### 4. Test Et

```bash
# Yeni karakterle test
python test_universal_characters.py --demo
```

---

## 📚 API Referansı

### Ana Fonksiyonlar

#### `integrate_universal_dm_handler(client, sender, message_text, bot_username, bot_profile=None)`
DM mesajlarını universal karakter sistemi ile işler.

**Dönüş:** `bool` - İşlendi mi

#### `integrate_universal_group_handler(client, event, bot_username, bot_profile=None)`
Grup mesajlarını universal karakter sistemi ile işler.

**Dönüş:** `bool` - İşlendi mi

#### `is_universal_character(bot_username, bot_profile=None)`
Bir bot'un universal karakter olup olmadığını kontrol eder.

**Dönüş:** `bool`

### Karakter Yönetimi

#### `register_character(character_id, character_config)`
Yeni karakter kaydeder.

#### `get_character_stats(character_id)`
Karakter istatistiklerini getirir.

**Dönüş:** `Dict` - İstatistik verisi

#### `list_all_characters()`
Tüm karakterlerin bilgilerini listeler.

**Dönüş:** `Dict[str, Dict]`

### Backward Compatibility

```python
# Eski Lara API'si hala çalışır
from handlers.universal_character_integration import (
    handle_lara_dm_compatibility,
    handle_lara_group_message_compatibility,
    get_lara_stats_compatibility
)

# Geisha ve BabaGavat için de mevcut
handle_geisha_dm_compatibility()
handle_babagavat_dm_compatibility()
```

---

## 🧪 Test Etme

### Test Komutları

```bash
# Tüm testleri çalıştır
python test_universal_characters.py --all

# Sadece sistem testleri
python test_universal_characters.py --test-system

# Sadece karakter testleri
python test_universal_characters.py --test-characters

# Sadece entegrasyon testleri
python test_universal_characters.py --test-integration

# Demo çalıştır
python test_universal_characters.py --demo
```

### Beklenen Test Sonuçları

```
📊 Toplam Test: 15
✅ Başarılı: 15
❌ Başarısız: 0
📈 Başarı Oranı: 100.0%

🎉 Mükemmel! Universal Character System tam çalışır durumda!
```

### Manual Test

```python
# Python REPL'de test
from handlers.universal_character_integration import *

# Sistem başlat
initialize_universal_characters()

# Karakterleri listele
chars = list_all_characters()
print(f"Kayıtlı karakter sayısı: {len(chars)}")

# İstatistikleri al
stats = get_universal_integration_stats()
print(f"Toplam konuşma: {stats['summary']['total_conversations']}")
```

---

## ⚙️ Konfigürasyon

### Karakter Ayarları

```python
# Karakter bazlı ayarlar
character_config = {
    "min_response_delay": 2.0,      # Yanıt gecikmesi
    "max_response_delay": 5.0,
    "emoji_usage": True,            # Emoji kullanımı
    "special_words": ["kelime1"],   # Özel kelimeler
    "sales_focus": True             # Satış odaklı mı
}
```

### VIP Hizmet Ayarları

```python
vip_services = {
    "hizmet_adi": {
        "price": "50₺",
        "description": "Hizmet açıklaması 💎"
    }
}
```

### Ödeme Bilgileri

```python
payment_info = {
    "papara_no": "1234567890",
    "iban": "TR12 3456 7890 1234 5678 9012 34",
    "hesap_sahibi": "Karakter Adı"
}
```

### Prompt Özelleştirme

```python
# PromptTemplate.BASE_TEMPLATE'i değiştir
# Karakter tipine göre otomatik prompt üretimi
```

---

## 📊 Analytics & Monitoring

### İstatistik Toplama

```python
from handlers.universal_character_integration import get_universal_integration_stats

stats = get_universal_integration_stats()
print(f"Toplam karakter: {stats['total_registered_characters']}")
print(f"Toplam konuşma: {stats['summary']['total_conversations']}")
print(f"Aktif kullanıcı: {stats['summary']['total_active_conversations']}")
```

### Karakter Bazlı İstatistikler

```python
from handlers.universal_character_system import get_character_stats

lara_stats = get_character_stats("lara")
print(f"Lara konuşma sayısı: {lara_stats['total_conversations']}")
print(f"Yüksek ilgi: {lara_stats['high_interest_users']}")
print(f"Ödeme sorgusu: {lara_stats['payment_inquiries']}")
```

---

## 🔧 Troubleshooting

### Yaygın Hatalar

#### ImportError: universal_character_system
```bash
# Çözüm: Python path kontrolü
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

#### Karakter kayıtlı değil hatası
```python
# Çözüm: Sistemi yeniden başlat
from handlers.universal_character_integration import initialize_universal_characters
initialize_universal_characters()
```

#### AI yanıt alamama
```bash
# OpenAI API key kontrol et
echo $OPENAI_API_KEY

# Advanced AI manager kontrolü
# core/advanced_ai_manager.py dosyasını kontrol et
```

### Debug Modu

```python
# Log seviyesini artır
import structlog
logger = structlog.get_logger("universal_character")
logger.setLevel("DEBUG")

# Test modunda çalıştır
python test_universal_characters.py --demo
```

### Performance İzleme

```python
# Karakter yanıt sürelerini izle
# character_config.min_response_delay/max_response_delay ayarla

# Memory kullanımını kontrol et
# conversation_context max 20 mesaj tutulur
```

---

## 🚀 Gelecek Özellikler

### Planlanan Özellikler
- **Voice Integration**: Karakter sesli yanıtları
- **Multi-Modal**: Görsel ve video içerik desteği
- **AI Learning**: Konuşmalardan öğrenme
- **Group Dynamics**: Karakter arası etkileşim
- **Advanced Analytics**: ML tabanlı analiz

### Karakter Geliştirme
- **Emotion System**: Duygu durumu takibi
- **Memory Enhancement**: Gelişmiş hafıza sistemi
- **Personality Evolution**: Zaman içinde karakter gelişimi
- **Cross-Character Learning**: Karakterler arası öğrenme

---

## 📞 Destek

### Teknik Destek
- **Telegram:** @gavatbaba
- **E-mail:** destek@gavatcore.com
- **GitHub Issues:** Proje repository'sinde issue açın

### Geliştirici Kaynakları
- Universal Character System API Docs
- Character Development Guide
- Integration Best Practices
- Performance Optimization Guide

---

## 🤝 Katkıda Bulunma

### Yeni Karakter Ekleme
1. Character definition oluştur
2. Username mapping ekle
3. Test et
4. Pull request gönder

### Bug Report
1. Test script'i çalıştır
2. Hata loglarını topla
3. Minimal reproduction case oluştur
4. Issue aç

### Feature Request
1. Use case tanımla
2. API design öner
3. Implementation plan yaz
4. Community feedback al

---

**🎭 Universal Character System - Sınırsız karakter, sınırsız imkan!**

*Bu README dosyası Universal Character System'in tüm özelliklerini kapsamaktadır. Herhangi bir sorunuz varsa destek kanallarımızdan iletişime geçebilirsiniz.* 