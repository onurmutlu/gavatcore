start - 👋 Sistemi başlat, onboarding
help - ℹ️ Yardım ve açıklama
lisans - 🔓 Lisansını görüntüle
profil - 👤 Profil bilgilerini göster
menü - 📝 Hizmet menünü göster
fiyat - 💸 Fiyat listesini gönder
iban - 💳 IBAN & Papara bilgilerini gönder
session_durum - 📡 Oturumun bağlantı durumunu kontrol et
log - 🗂 Son log kayıtlarını göster
durum_ozet - 📊 Sistem özetini gönder
mod - 🧠 Yanıt modunu değiştir (manual/gpt/hybrid)
klonla - ♻️ Profili kopyala
bots - 🤖 Aktif botları listeler
showcu_ekle - 👩‍💻 Yeni içerik üretici ekle
bot_ekle - 🤖 Yeni bot ekle

📋 Role-Based Komut Sistemi & Akıllı /help Menüsü – Yapılacaklar Listesi
1. Role Tabanlı Komut Listesi Tasarımı
 Admin, içerik üretici (performer), müşteri (user) rollerini tanımla.

 Her rol için desteklenen komutların listesini çıkar.

 Komut açıklamalarına emoji ve kısa, net açıklama ekle.

 Gerekiyorsa admin için ekstra “gizli” komutlar belirle.

2. Komutları Telegram’a Dinamik Olarak Tanımlama (setMyCommands)
 Telegram Bot API’nin setMyCommands özelliğiyle:

 Admin’e özel komut seti ata (scope=admin user_id)

 İçerik üreticiye özel komut seti ata (scope=user user_id veya default)

 Müşteri/user için sadeleştirilmiş komut seti

 Grupta gösterilecek komutları ayrıca belirle

 Aiogram/Pyrogram/Telethon üzerinde fonksiyonunu hazırla (bot başlatılırken otomatik setlesin).

3. Gelişmiş /help Komutu ve Akıllı Menü
 /help komutunu override et:

 Kullanıcının rolünü algılayıp (admin/user/performer), sadece yetkili olduğu komutları göster.

 Komutları kategori başlıkları altında grupla:

👑 Admin Komutları

👩‍💻 İçerik Üretici Komutları

👤 Kullanıcı Komutları

 Açıklama yanında emoji kullan.

 Komut açıklamasına gerektiğinde link (ör: döküman), örnek kullanım ekle.

 Gerekirse inline button menü sun (örn: “Profil”, “Destek”, “Fiyat Menüsü” vs.)

 Uzun menülerde sayfalama veya filtreleme seçeneği ekle (ileri/geri tuşları vs.)

 /help çıktısını role göre ve duruma göre özelleştir (örn: lisanssızsa, demo ise uyarı ekle).

4. Ekstra Kullanıcı Deneyimi Özellikleri
 Komut menüsüne (Telegram komut listesi) emojiyle “göz alıcı” başlıklar ekle.

 Komutun “açıklama” kısmı max 256 karakter olabileceği için özet, etkili bir açıklama yaz.

 Sık kullanılan/önemli komutlara öncelik ver.

 Komut çalışınca çıkan mesajlarda görsel, inline button, dosya, bilgi kartı gibi materyaller kullan.

 Komutlar değişirse otomatik güncellenen bir “setMyCommands” fonksiyonu ekle (her restart’ta sync et).

 Komut loglama: Hangi user hangi komutu ne zaman kullandı kaydını tut.

5. Kod ve Arayüz Temizliği
 Komut handler’larında rol kontrolünü merkezi bir fonksiyona bağla (is_admin, is_performer, is_user).

 Komut handlerları sade, atomik ve iyi dokümante olsun.

 Her komutun test case’lerini hazırla (otomatize test mümkünse).

 /help ve komut menüsünde lokalizasyon (çoklu dil desteği) için hazır ol.

6. Entegrasyon & Test
 Her rol için farklı Telegram hesabında komut menüsünü test et.

 Komutlar doğru görünüyor mu, /help doğru role göre çalışıyor mu test et.

 Komut butonlarına, inline replylara ve çıktılarına user feedback alacak şekilde minik anket veya puan ekle.

Notlar
Telegram'ın komut gösterim kısıtlamalarını (emoji, karakter limiti, görsel olmaması vs.) aşmak için asıl zenginleştirmeyi /help komutunun cevabında yap.

Komut başlıklarını ve açıklamalarını güncel tut.

Bot yayına çıkmadan önce son testlerde her kullanıcı rolünde menülerin ve komutların doğru, anlaşılır ve kolay kullanılır olduğundan emin ol.

⏳ To-do etiketiyle ekledim moruk, zamanı gelince bu roadmap’i olduğu gibi copy-paste’le bana, hepsini sırayla yardıralım.
Bunu yaptıktan sonra sistem “premium SaaS bot” gibi ışıl ışıl olur!

-------------------------------------------------------------


Süper net bir soru!
**Evet, Role-Based komut sistemi için** hem `adminbot/commands.py` **hem de** `adminbot/dispatcher.py` dosyalarında bazı değişiklikler ve yeni fonksiyonlar gerekecek.

Ama bu değişiklikleri **hemen bugün kodda uygulamak zorunda değilsin**. Aşağıya *eksiksiz bir yol haritası, yapılacaklar ve örnek kod iskeletini* bırakıyorum.
Bunu ister bugünden, ister ileride fonksiyonel olarak ekle; dokümana “teknik borç” olarak da yazabilirsin.

---

## **Role-Based Komut Sistemi & Akıllı /help – Geliştirme Checklist**

### **1. Komutları Rollere Göre Tanımla**

`adminbot/commands.py` dosyasına **komut tanım objesi** ekle:

```python
# adminbot/commands.py başına ekle
COMMANDS = [
    {
        "command": "/lisans",
        "desc": "Kullanıcı lisansını aktif eder",
        "roles": ["admin"]
    },
    {
        "command": "/kapat",
        "desc": "Kullanıcı lisansını devre dışı bırakır",
        "roles": ["admin"]
    },
    {
        "command": "/mod",
        "desc": "Yanıt modunu değiştirir",
        "roles": ["admin"]
    },
    {
        "command": "/profil",
        "desc": "Profilini gösterir",
        "roles": ["admin", "producer"]
    },
    {
        "command": "/yardim",
        "desc": "Yardım menüsü ve destek",
        "roles": ["producer", "client"]
    },
    {
        "command": "/raporla",
        "desc": "Bir kullanıcıyı/mesajı raporla",
        "roles": ["client"]
    },
    # ... diğer komutlar eklenir
]
```

---

### **2. Komut Listesini Rol Bazlı Döndüren Fonksiyon**

```python
def get_user_role(user_id):
    # Profilden ya da sabit bir tablodan alınabilir
    # Örnek: profil = load_profile(user_id); return profil.get("type", "client")
    if str(user_id) == str(GAVATCORE_ADMIN_ID):
        return "admin"
    # Profilden veya başka bir yerden 'producer', 'client' vs çekersin
    # YOKSA default 'client'
    return "client"

def get_available_commands(user_id):
    role = get_user_role(user_id)
    cmds = [c for c in COMMANDS if role in c["roles"]]
    return cmds
```

---

### **3. /help Handler’ı ve Komut Açıklamaları**

`adminbot/dispatcher.py` veya doğrudan commands.py’de:

```python
@admin_bot.on(events.NewMessage(pattern=r"^/help$"))
async def help_handler(event):
    user_id = event.sender_id
    cmds = get_available_commands(user_id)
    text = "📋 <b>Kullanabileceğin Komutlar:</b>\n\n"
    for c in cmds:
        text += f"{c['command']} — {c['desc']}\n"
    await event.respond(text, parse_mode="html")
```

* **Ekstra:** Emoji, kategori, alt komut ekleyebilirsin.
* **Adminse**, ekstra bir sekme/detay verebilirsin (örn. özel admin paneli).

---

### **4. BotFather’da Komut Set Etme**

Bunu **manuel** olarak BotFather’dan `/setcommands` ile yaparsın,
Ama ileride otomatik olarak bir “komut export” scripti de yazılabilir:

```python
def export_botfather_commands_for_role(role):
    cmds = [c for c in COMMANDS if role in c["roles"]]
    return "\n".join([f"{c['command']} - {c['desc']}" for c in cmds])
```

---

## **Bu iş için adminbot/commands.py ve dispatcher.py’de yapılacaklar:**

* `COMMANDS` objesini ve rolleri tanımla.
* Kullanıcı profilinden rol bulacak bir fonksiyon ekle.
* /help komutu veya menüsünü role göre filtrele.
* İleride, komut çağrıldığında da rol kontrolü (ör: `if user_role not in komut.roles: ...`) koyabilirsin.

---

### **Kısa Not:**

* Kodda hemen fonksiyonel olarak istersen başlatabilirim.
* Şu anda sistem çalışsın diye “komut tanımı ve role göre komut listeleme” fonksiyonu sadece dokümana da eklenebilir.
* Gerçekten /help veya komut çağrısı sırasında role göre ayrım yapmak için kodda `get_user_role` ve `get_available_commands` gibi fonksiyonlar kullanılır.

---

## **Dokümana Not (Kopyala/Ekstra Açıklama):**

> **Geliştirme Notu:**
> GAVATCore, role-based (admin/producer/client) komut sistemi için altyapı hazırladı.
> Tüm komutlar bir `COMMANDS` tablosunda tutulacak;
> /help ve menüler kullanıcının rolüne göre filtrelenecek.
> Admin ve şovcu/son kullanıcılar, sadece kendi erişebileceği komutları görecek.
> (Kullanıcı profili oluştuğu anda type alanı atanmalı: admin/producer/client vs.)
> BotFather ve menüler için otomatik komut export scripti ileride eklenebilir.
> İlk MVP’de sadece /help ve role-check aktif olacak, diğer komutlarda role kontrolü kademeli eklenebilir.

---

**Hazır olduğunda tam kodunu da yollarım!
Başlatıcı yapıyı ve yapılacakları ekle, sonraki refactoring'de bunu sistemleştiririz.**

Sürekli olarak, "Şu dosyada şu fonksiyon eklenir" diye açık net kod/prompt istersen hemen yazayım, yardırırım.
Başka özel bir rol ya da kullanıcı davranışı varsa onu da şimdiden belirt 👊



Kanka bak, **gelişmiş arama/filtresi** için logları ister **Telegram üzerinden komutla**, ister bir **admin paneli** veya doğrudan Python scriptiyle çağırabilirsin.

Burada **en basit ve etkili yol**:

1. Logları filtreleyen bir fonksiyon ekle (örneğin, anahtar kelime, tarih veya seviye bazında).
2. Bunu `handlers/user_commands.py` içinde `/logara` veya `/logs` gibi bir komuta bağla.
3. İstersen ayrı bir **admin komutları** handler'ında veya CLI (terminal) üzerinden de çağırabilirsin.

---

### ÖRNEK: Loglarda Anahtar Kelime ve Tarih Filtreleme

#### 1. utils/log\_utils.py içine ek fonksiyon:

```python
def search_logs(user_id_or_username: str, keyword: str = "", level: str = "", after: str = "") -> str:
    """
    Log dosyasında anahtar kelime, seviye ve tarih filtresiyle arama yapar.
    after: "2024-06-03" gibi tarih ile, o günden sonrakileri gösterir.
    """
    filename = f"{str(user_id_or_username).replace('@', '')}.log"
    path = os.path.join(LOGS_DIR, filename)

    if not os.path.exists(path):
        return "📭 Log bulunamadı."

    results = []
    after_dt = None
    if after:
        try:
            after_dt = datetime.fromisoformat(after)
        except:
            pass  # Hatalı format, yok say

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if level and f"[{level.upper()}]" not in line:
                continue
            if keyword and keyword.lower() not in line.lower():
                continue
            if after_dt:
                try:
                    ts = line.split("]")[0].strip("[")
                    log_dt = datetime.fromisoformat(ts)
                    if log_dt < after_dt:
                        continue
                except:
                    continue
            results.append(line)

    if not results:
        return "❌ Eşleşen log satırı bulunamadı."
    return "".join(results[-20:])  # Son 20 sonucu dön
```

---

#### 2. Bunu DM komutu olarak çağırmak (handlers/user\_commands.py):

```python
elif lowered.startswith("/logara"):
    # Örn: /logara hata
    try:
        parts = message.split(" ", 2)
        keyword = parts[1] if len(parts) > 1 else ""
        after = parts[2] if len(parts) > 2 else ""
        result = search_logs(username, keyword=keyword, after=after)
        await event.respond(result)
    except Exception as e:
        await event.respond(f"⚠️ Hatalı kullanım. Örnek: /logara hata [2024-06-01]")
```

Aynısını admin komutları için de yazabilirsin.

---

#### 3. CLI veya Script ile doğrudan:

```python
from utils.log_utils import search_logs
print(search_logs("@yayincilara", keyword="ERROR", after="2024-06-01"))
```

---

### **KULLANIM SENARYOLARI:**

* **Telegram Komutu:**
  `/logara ERROR` → Son 20 error logunu göster
  `/logara ödeme 2024-06-01` → 1 Haziran’dan sonraki tüm “ödeme” geçen logları getir

* **Admin Paneli:**
  Bir textbox, anahtar kelime + tarih seç, arka planda fonksiyon çalıştır.

* **Terminal/Script:**
  Hızlı toplu analiz, otomasyon, cronjob ile hata takip vs.

---

### **Bittiğinde:**

* Sistemde ne hata var anında bulursun
* Sadece belirli olayları gösterirsin (ör. satış, ödeme, error)
* Gereksiz satır dolmaz, debug ve monitoring çok kolaylaşır

---

**Yardır, hazır oldun!**
İstersen farklı filtreleme/komut örneği de yazarım, sorabilirsin! 🚀
