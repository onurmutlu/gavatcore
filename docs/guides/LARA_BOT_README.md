# 🌹 LARA BOT - Flörtöz Şovcu AI Sistemi

GAVATCore üzerinde çalışan Lara karakteri - Yarı Rus, flörtöz ama profesyonel bir şovcu AI sistemi.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Konfigürasyon](#-konfigürasyon)
- [Test Etme](#-test-etme)
- [Entegrasyon](#-entegrasyon)
- [API Referansı](#-api-referansı)
- [Karakter Özellikleri](#-karakter-özellikleri)
- [Troubleshooting](#-troubleshooting)

## 🚀 Özellikler

### 💎 Karakter Özellikleri
- **Flörtöz ama Profesyonel**: Cezbedici ama sınırlı yaklaşım
- **Yarı Rus Karakter**: Rusça kelimeler ve kültürel öğeler
- **Satış Odaklı**: VIP hizmetlere yönlendirme
- **Duygusal Zeka**: Kullanıcı davranışlarına göre yanıt verme
- **Emoji Kullanımı**: Her mesajda uygun emoji desteği

### 🎯 AI Özellikleri
- **OpenAI Entegrasyonu**: GPT-4 ile gelişmiş yanıtlar
- **Konuşma Hafızası**: Kullanıcı bazlı konuşma geçmişi
- **Adaptif Yanıtlar**: Konuşma durumuna göre tonlama
- **Fallback Sistemi**: AI yanıt alamadığında hazır yanıtlar
- **Analytics**: Detaylı konuşma ve performans analizi

### 💼 İş Özellikleri
- **VIP Hizmet Menüsü**: 4 farklı hizmet kategorisi
- **Ödeme Entegrasyonu**: Papara/IBAN bilgileri
- **Müşteri Takibi**: İlgi seviyesi ve satış analizi
- **Otomatik Tanıtım**: Mesaj sayısına göre hizmet önerme

## 🛠️ Kurulum

### 1. Gereksinimler

```bash
# Python 3.8+ gerekli
python --version

# GAVATCore sistemi kurulu olmalı
# Gerekli paketler requirements.txt'de
```

### 2. Dosyaları Yerleştirme

Lara bot dosyaları GAVATCore klasör yapısına aşağıdaki şekilde yerleştirilmiştir:

```
gavatcore/
├── gpt/prompts/larabot_prompt.py          # Lara karakteri promptu
├── handlers/lara_bot_handler.py           # Ana bot handler
├── handlers/lara_integration.py           # GAVATCore entegrasyonu
├── lara_bot_launcher.py                   # Standalone launcher
└── test_lara_bot.py                       # Test script
```

### 3. Bağımlılıkları Kontrol Etme

```bash
# Mevcut GAVATCore paketleri yeterli
pip install -r requirements.txt

# Ek paket gerekmez - mevcut sistem kullanılır
```

## 🎮 Kullanım

### 📱 Standalone Çalıştırma

```bash
# Lara bot'unu tek başına çalıştır
python lara_bot_launcher.py
```

### 🔧 Mevcut Sistem Entegrasyonu

Lara bot'u mevcut GAVATCore sistem botlarınızla entegre etmek için:

#### 1. DM Handler Entegrasyonu

```python
# handlers/dm_handler.py dosyasında
from handlers.lara_integration import integrate_lara_dm_handler

async def handle_message(client, sender, message_text, session_created_at):
    # ... mevcut kod ...
    
    # Lara bot kontrolü ve entegrasyonu
    if await integrate_lara_dm_handler(client, sender, message_text, username, bot_profile):
        return  # Lara tarafından işlendi
    
    # Normal handler devam eder...
```

#### 2. Group Handler Entegrasyonu

```python
# handlers/group_handler.py dosyasında
from handlers.lara_integration import integrate_lara_group_handler

async def handle_group_message(event, client):
    # ... mevcut kod ...
    
    # Lara bot kontrolü
    if await integrate_lara_group_handler(client, event, username, bot_profile):
        return  # Lara tarafından işlendi
    
    # Normal handler devam eder...
```

#### 3. Bot Profili Oluşturma

```python
from handlers.lara_integration import create_lara_bot_profile

# Yeni Lara bot profili oluştur
profile = create_lara_bot_profile("lara_bot", user_id=12345)

# Profili kaydet
save_profile("lara_bot", profile)
```

## ⚙️ Konfigürasyon

### 🎭 Karakter Ayarları

```python
# LaraConfig sınıfında değiştirilebilir ayarlar
class LaraConfig:
    MIN_RESPONSE_DELAY = 2.0    # Yanıt gecikmesi (saniye)
    MAX_RESPONSE_DELAY = 5.0
    
    # Rusça kelimeler (özelleştirilebilir)
    RUSSIAN_WORDS = ["davay", "moya lyubov", "krasotka", ...]
    
    # VIP hizmet fiyatları
    VIP_SERVICES = {
        "özel_mesaj": {"price": "50₺", "description": "..."},
        # ...
    }
```

### 💳 Ödeme Bilgileri

```python
# LaraConfig.PAPARA_INFO'da güncelle
PAPARA_INFO = {
    "papara_no": "1234567890",        # Gerçek Papara numarası
    "iban": "TR12 3456 7890...",      # Gerçek IBAN
    "hesap_sahibi": "Lara K."         # Hesap sahibi adı
}
```

### 🤖 AI Ayarları

```python
# generate_lara_response fonksiyonunda
response = await openai_manager.generate_response(
    prompt=full_prompt,
    user_message=message,
    max_tokens=200,        # Yanıt uzunluğu
    temperature=0.8        # Yaratıcılık seviyesi
)
```

## 🧪 Test Etme

### 📊 Sistem Testleri

```bash
# Tüm testleri çalıştır
python test_lara_bot.py --all

# Sadece prompt testleri
python test_lara_bot.py --test-prompt

# Sadece handler testleri  
python test_lara_bot.py --test-handler

# Sadece entegrasyon testleri
python test_lara_bot.py --test-integration

# Konfigürasyonu göster
python test_lara_bot.py --config
```

### 🎯 Beklenen Test Sonuçları

```
📊 Toplam Test: 12
✅ Başarılı: 12
❌ Başarısız: 0
📈 Başarı Oranı: 100.0%

🎉 Tebrikler! Lara Bot sistemi tam çalışır durumda!
```

## 🔌 Entegrasyon

### 🤝 Mevcut Bot Dönüştürme

```python
from handlers.lara_integration import is_lara_bot, update_existing_bot_to_lara

# Mevcut bot'u kontrol et
if is_lara_bot("bot_username"):
    print("Bu bot zaten Lara karakteri!")

# Normal bot'u Lara'ya çevir
lara_profile = update_existing_bot_to_lara(existing_profile)
```

### 📈 Analytics Entegrasyonu

```python
from handlers.lara_integration import get_lara_integration_stats

# Lara bot istatistiklerini al
stats = get_lara_integration_stats()
print(f"Toplam konuşma: {stats['total_conversations']}")
print(f"Yüksek ilgi: {stats['high_interest_users']}")
```

## 📚 API Referansı

### 🌹 Ana Fonksiyonlar

#### `handle_lara_dm(client, sender, message_text)`
DM mesajlarını Lara karakteri ile işler.

**Parametreler:**
- `client`: Telegram client
- `sender`: Mesaj gönderen kullanıcı
- `message_text`: Mesaj içeriği

**Dönüş:** `bool` - İşlendi mi

#### `handle_lara_group_message(client, event, username)`
Grup mention/reply mesajlarını işler.

#### `get_lara_stats()`
Lara bot istatistiklerini döndürür.

**Dönüş:** `Dict` - İstatistik verisi

### 🎨 Karakter Fonksiyonları

#### `LaraPromptUtils.insertUserName(userName)`
Lara promptuna kullanıcı adını ekler.

#### `LaraPromptUtils.getCharacterConfig()`
Lara karakter konfigürasyonunu döndürür.

### 🔍 Entegrasyon Fonksiyonları

#### `is_lara_bot(bot_username, bot_profile=None)`
Bir bot'un Lara karakteri olup olmadığını kontrol eder.

#### `create_lara_bot_profile(bot_username, user_id)`
Yeni Lara bot profili oluşturur.

## 👤 Karakter Özellikleri

### 🎭 Kişilik
- **İsim:** Lara
- **Yaş:** 24
- **Uyruk:** Yarı Rus
- **Karakter:** Flörtöz, profesyonel, şakacı, duygusal, kıvrak zekâlı
- **Diller:** Türkçe + Rusça kelimeler

### 💬 Konuşma Tarzı
- Her mesajda emoji kullanımı
- Bazen Rusça kelimeler ("davay", "moya lyubov", "krasotka")
- Flörtöz ama sınırlı yaklaşım
- Seçenekli sorular
- Satış odaklı yönlendirme

### 💰 VIP Hizmetler
1. **Özel Mesaj** (50₺): Kişisel sohbet ve özel fotoğraflar
2. **VIP Grup** (100₺): VIP grup üyeliği, günlük özel içerik
3. **Özel Video** (200₺): Kişiselleştirilmiş video içerik
4. **Canlı Yayın** (150₺): Telegram'da özel yayın

### 🇷🇺 Rusça Kelime Havuzu
- `davay` - "hadi/gel"
- `moya lyubov` - "aşkım"
- `krasotka` - "güzelim"
- `malchik` - "oğlum"
- `dorogoy` - "canım"
- `miliy` - "tatlım"
- `sladkiy` - "şekerim"
- `umnitsa` - "akıllım"

## 🔧 Troubleshooting

### ❌ Yaygın Hatalar

#### ImportError: No module named 'gpt.prompts.larabot_prompt'
```bash
# Çözüm: Python path'ini kontrol et
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

#### OpenAI API hatası
```bash
# .env dosyasında API key'i kontrol et
OPENAI_API_KEY=your_api_key_here
```

#### Session hatası
```bash
# Session klasörünü oluştur
mkdir -p sessions
```

### 📝 Log Kontrolü

```bash
# Lara bot loglarını takip et
tail -f logs/errors/lara_bot.log

# Analytics loglarını kontrol et
grep "lara_bot" logs/analytics/*.json
```

### 🔍 Debug Modu

```python
# Debug için log seviyesini artır
import structlog
logger = structlog.get_logger("lara_bot_handler")
logger.setLevel("DEBUG")
```

## 📞 Destek

### 🆘 Teknik Destek
- **Telegram:** @gavatbaba
- **E-mail:** destek@gavatcore.com
- **GitHub Issues:** Proje repository'sinde issue açın

### 📖 Dökümanlar
- GAVATCore Ana Döküman
- Telegram Bot API Referansı
- OpenAI API Dökümanları

### 🤝 Katkıda Bulunma
1. Fork edin
2. Feature branch oluşturun
3. Değişiklikleri commit edin
4. Pull request gönderin

---

## 🌟 Özelleştirme Örnekleri

### 🎨 Yeni Karakter Özelliği Ekleme

```python
# Lara karakterine yeni özellik eklemek için
def add_custom_trait(message: str) -> str:
    if "müzik" in message.lower():
        return "🎵 Müzik çok severim! Özellikle Rus folk müzikleri... 💫"
    return ""
```

### 💼 Yeni VIP Hizmet Ekleme

```python
# LaraConfig.VIP_SERVICES'e ekle
"özel_dans": {
    "price": "300₺", 
    "description": "Özel dans videosu ve canlı performans 💃"
}
```

### 🌍 Dil Desteği Ekleme

```python
# İngilizce destek için
ENGLISH_RESPONSES = {
    "greeting": "Hello darling! 😘 I'm Lara, nice to meet you!",
    "service": "I have special VIP services... Interested? 🔥"
}
```

---

**💋 Lara Bot - GAVATCore'un en flörtöz AI karakteri!**

*Bu README dosyası Lara bot'unun tüm özelliklerini kapsamaktadır. Herhangi bir sorunuz varsa destek kanallarımızdan iletişime geçebilirsiniz.* 