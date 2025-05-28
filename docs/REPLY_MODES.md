# GAVATCORE Reply Mode Sistemi

## Genel Bakış

GAVATCORE'da her bot kendi profil dosyasında tanımlı `reply_mode` ayarına göre DM ve grup mesajlarına yanıt verir. Bu sistem hem DM'lerde hem de grup reply/mention'larında çalışır.

## Reply Mode Seçenekleri

### 1. `gpt` - Direkt GPT Yanıtı
- **DM'de**: Gelen her mesaja direkt GPT yanıtı üretir ve gönderir
- **Grup'ta**: Reply veya mention'da direkt GPT yanıtı üretir ve gönderir
- **Kullanım**: Tam otomatik bot davranışı için ideal

### 2. `manual` - Manuel Yanıt
- **DM'de**: Hiç yanıt vermez, içerik üretici manuel yanıt vermeli
- **Grup'ta**: Hiç yanıt vermez, içerik üretici manuel yanıt vermeli
- **Kullanım**: Tam manuel kontrol için

### 3. `manualplus` - Timeout'lu Manuel
- **DM'de**: Belirli süre (default 180s) bekler, yanıt gelmezse fallback mesaj gönderir
- **Grup'ta**: Belirli süre bekler, yanıt gelmezse fallback mesaj gönderir
- **Kullanım**: Manuel kontrol ama güvenlik ağı ile

### 4. `hybrid` - GPT Önerisi
- **DM'de**: GPT önerisi üretir ve "💬 GPT önerisi: ..." şeklinde gösterir
- **Grup'ta**: "📬 Yanıt önerisi (onaylanması gerek):" şeklinde öneri gösterir
- **Kullanım**: İçerik üreticiye yardım ama son karar onlarda

## Profil Ayarları

Her bot profilinde (`data/personas/bot_*.json`) şu ayarlar bulunur:

```json
{
  "reply_mode": "gpt|manual|manualplus|hybrid",
  "manualplus_timeout_sec": 180,
  "reply_messages": [
    "Fallback mesaj 1",
    "Fallback mesaj 2"
  ]
}
```

## Mevcut Bot Ayarları

| Bot | Reply Mode | Açıklama |
|-----|------------|----------|
| **Geisha** | `gpt` | Direkt GPT yanıtı, tam otomatik |
| **Lara** | `manualplus` | 180s timeout sonrası fallback |
| **Gavat Baba** | `hybrid` | GPT önerisi gösterir |

## Teknik Detaylar

### DM Handler
- Bot kendi profilini `_load_bot_profile()` ile yükler
- `reply_mode` bot profilinden alınır (kullanıcı profilinden değil)
- manualplus için unique key: `dm:{bot_username}:{user_id}`

### Grup Handler
- Reply veya mention kontrolü yapar
- Bot kendi profilini `_load_bot_profile()` ile yükler
- manualplus için unique key: `group:{bot_username}:{chat_id}:{message_id}`

### Fallback Mesajları
- `reply_messages` dizisinden rastgele seçim
- Bot profilinde yoksa sistem default'ları kullanılır
- `utils/template_utils.py` içinde `get_profile_reply_message()`

## Lisans Kontrolü

Sistem botları (`owner_id: "system"`) için lisans kontrolü yapılmaz. Müşteri botları için owner'ın lisansı kontrol edilir.

## Kullanım Örnekleri

### DM Senaryosu
1. Kullanıcı Geisha'ya DM atar
2. Geisha profili yüklenir (`reply_mode: "gpt"`)
3. GPT yanıtı üretilir ve direkt gönderilir

### Grup Senaryosu
1. Kullanıcı grupta Lara'yı mention eder
2. Lara profili yüklenir (`reply_mode: "manualplus"`)
3. 180 saniye beklenir
4. Yanıt gelmezse `reply_messages`'dan rastgele mesaj gönderilir

### Hybrid Senaryosu
1. Kullanıcı Gavat Baba'ya DM atar
2. GPT önerisi üretilir
3. "💬 GPT önerisi: [öneri]" şeklinde gönderilir
4. İçerik üretici isterse manuel yanıt verebilir

## Geliştirici Notları

- manualplus pending dictionary global olarak paylaşılır
- Timeout task'leri asyncio ile yönetilir
- Her bot/kullanıcı kombinasyonu için unique key kullanılır
- Session restart durumunda pending task'ler temizlenir 