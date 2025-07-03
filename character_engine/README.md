# 🧠 GAVATCore Character Engine v2.0

Modüler karakter yönetim sistemi - Her bot için özel kişilik ve GPT destekli yanıt motoru

## 🚀 Özellikler

- **Modüler Karakter Sistemi**: JSON tabanlı karakter konfigürasyonları
- **GPT-4 Entegrasyonu**: Akıllı ve bağlama uygun yanıtlar
- **Kişilik Yönlendirmesi**: Her karaktere özel yanıt stratejileri
- **Hafıza Sistemi**: Kullanıcı bazlı konuşma geçmişi ve bağlam takibi
- **Fallback Yönetimi**: Zaman aşımı ve yanıtsızlık durumları için otomatik mesajlar
- **Çoklu Reply Mode**: Manual, GPT, Hybrid, ManualPlus modları

## 📦 Kurulum

```bash
# Gerekli paketleri yükle
pip install openai

# OpenAI API key'i ayarla
export OPENAI_API_KEY="your-api-key"
```

## 🏗️ Mimari

```
character_engine/
├── character_manager.py       # Karakter config yönetimi
├── gpt_reply_generator.py     # GPT yanıt üretimi
├── personality_router.py      # Kişilik bazlı yönlendirme
├── fallback_reply_manager.py  # Yedek yanıt sistemi
├── memory_context_tracker.py  # Hafıza ve bağlam takibi
└── character_config/
    ├── lara.json
    ├── babagavat.json
    └── geisha.json
```

## 💡 Kullanım Örnekleri

### 1. Basit Karakter Yükleme

```python
from character_engine import CharacterManager

# Manager'ı başlat
char_manager = CharacterManager()

# Karakteri yükle
lara = char_manager.load_character("lara")
print(f"Karakter: {lara.name}, Ton: {lara.tone}")
```

### 2. GPT ile Yanıt Üretme

```python
from character_engine import GPTReplyGenerator

# Generator'ı başlat
gpt_gen = GPTReplyGenerator()

# Yanıt üret
reply = await gpt_gen.generate_reply(
    user_message="Merhaba, nasılsın?",
    character_config=lara.to_dict(),
    strategy="flirt"
)
```

### 3. Tam Entegre Kullanım

```python
async def handle_user_message(user_id: str, message: str, character: str):
    # 1. Karakteri yükle
    char_config = char_manager.load_character(character)
    
    # 2. Hafızaya ekle
    memory_tracker.add_message(user_id, "user", message)
    
    # 3. Bağlamı al
    context = memory_tracker.get_context(user_id)
    user_context = memory_tracker.get_user_context(user_id)
    
    # 4. Yanıt tipini belirle
    reply_type, params = personality_router.route_reply(
        message, char_config.to_dict(), user_context
    )
    
    # 5. GPT yanıtı üret
    gpt_reply = await gpt_gen.generate_reply(
        message, char_config.to_dict(), context
    )
    
    # 6. Strateji uygula
    final_reply = personality_router.apply_strategy(
        gpt_reply, reply_type, params
    )
    
    # 7. Hafızaya kaydet
    memory_tracker.add_message(user_id, "assistant", final_reply)
    
    return final_reply
```

## 🎭 Karakter Konfigürasyonu

### Örnek JSON Yapısı

```json
{
  "name": "Lara",
  "username": "lara",
  "system_prompt": "Sen Lara, baştan çıkarıcı ve gizemli...",
  "reply_mode": "hybrid",
  "tone": "flirty",
  "cooldown_seconds": 45,
  "trust_index": 0.7,
  "fallback_strategy": "template_or_gpt",
  "template_replies": [
    "Canım ben şimdi biraz meşgulüm..."
  ],
  "personality_traits": {
    "mystery_level": "high",
    "flirt_intensity": "medium-high"
  },
  "gpt_settings": {
    "model": "gpt-4-turbo-preview",
    "temperature": 0.8
  }
}
```

### Reply Mode'lar

- **manual**: Sadece template yanıtlar
- **gpt**: Sadece GPT yanıtlar
- **hybrid**: %50 GPT, %50 template
- **manualplus**: Önce template, başarısız olursa GPT

### Ton Seçenekleri

- **flirty**: Flörtöz ve çekici
- **soft**: Yumuşak ve anlayışlı
- **dark**: Karanlık ve gizemli
- **mystic**: Mistik ve ruhsal
- **aggressive**: Agresif ve dominant

## 📊 Hafıza ve Bağlam

### Trust Index Hesaplama

Trust Index, aşağıdaki faktörlere göre hesaplanır:
- Toplam mesaj sayısı
- Pozitif/negatif duygu oranı
- İletişim sürekliliği
- Karma skoru

### Relationship Depth Seviyeleri

1. **stranger**: < 10 mesaj
2. **acquaintance**: 10-50 mesaj
3. **friend**: 50-200 mesaj
4. **close_friend**: 200-500 mesaj
5. **intimate**: > 500 mesaj veya > 30 gün

## 🔧 Admin Panel Entegrasyonu

```python
# Yeni karakter ekle
new_char = char_manager.create_character(
    username="yeni_karakter",
    name="Yeni Karakter",
    system_prompt="Karakter açıklaması...",
    tone="flirty",
    reply_mode="hybrid"
)

# Karakter güncelle
char_manager.update_character(
    "lara",
    tone="aggressive",
    cooldown_seconds=30
)

# Karakter sil
char_manager.delete_character("eski_karakter")
```

## 🚨 Fallback Stratejileri

### Fallback Tipleri

- **timeout**: Kullanıcı belli süre yazmadığında
- **no_reply**: Bot mesajına yanıt gelmediğinde
- **re_engage**: Uzun süre iletişim olmadığında

### Strateji Seçenekleri

- **progressive**: Giderek artan yoğunluk
- **random**: Rastgele seçim
- **adaptive**: Kullanıcı davranışına göre
- **persistent**: Israrcı ve sürekli

## 📈 Performans İpuçları

1. **Hafıza Yönetimi**: Aktif olmayan kullanıcı hafızalarını düzenli temizle
2. **GPT Cache**: Benzer sorular için yanıtları önbellekle
3. **Batch Processing**: Çoklu GPT isteklerini grupla
4. **Rate Limiting**: API limitlerini takip et

## 🐛 Debug ve Test

```bash
# Test scriptini çalıştır
python character_engine/test_character_engine.py

# Logging seviyesini ayarla
export LOG_LEVEL=DEBUG
```

## 🤝 Katkıda Bulunma

1. Yeni karakter eklemek için `character_config/` dizinine JSON dosyası ekle
2. Yeni yanıt stratejileri için `personality_router.py` dosyasını genişlet
3. Yeni fallback şablonları için `fallback_reply_manager.py` dosyasını güncelle

## 📝 Lisans

GAVATCore projesi kapsamında geliştirilmiştir. 