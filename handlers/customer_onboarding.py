"""
👋 Customer Onboarding Handler - Müşteri kayıt ve yönlendirme
"""
from telethon import events
from core.controller import Controller
from core.gpt_system import GPTSystem

class CustomerOnboardingHandler:
    def __init__(self, controller: Controller, gpt_system: GPTSystem):
        self.controller = controller
        self.gpt_system = gpt_system
        self.steps = {
            'welcome': self.handle_welcome,
            'name': self.handle_name,
            'email': self.handle_email,
            'phone': self.handle_phone,
            'preferences': self.handle_preferences,
            'confirmation': self.handle_confirmation
        }
        
    async def handle_onboarding(self, event: events.NewMessage.Event):
        """Onboarding sürecini yönet"""
        try:
            # Kullanıcı durumunu kontrol et
            user_state = await self.controller.get_user_state(event.sender_id)
            
            # İlk kez mi?
            if not user_state:
                await self.start_onboarding(event)
                return
                
            # Hangi adımdaysa o adımı işle
            if user_state in self.steps:
                await self.steps[user_state](event)
            else:
                await self.handle_unknown_state(event)
                
        except Exception as e:
            print(f"Onboarding Handler Error: {e}")
            await event.respond("❌ Bir hata oluştu! Lütfen tekrar deneyin.")
            
    async def start_onboarding(self, event: events.NewMessage.Event):
        """Onboarding sürecini başlat"""
        try:
            welcome_msg = """
🌟 GAVATCore'a Hoş Geldiniz! 🌟

🤖 Ben yapay zeka destekli bir Telegram botuyum.
📱 Size en iyi hizmeti sunmak için birkaç bilgiye ihtiyacım var.

👤 İsminiz nedir?
            """
            await event.respond(welcome_msg)
            await self.controller.set_user_state(event.sender_id, 'name')
            
        except Exception as e:
            print(f"Start Onboarding Error: {e}")
            
    async def handle_welcome(self, event: events.NewMessage.Event):
        """Karşılama adımı"""
        try:
            welcome_msg = """
🌟 GAVATCore'a Hoş Geldiniz! 🌟

🤖 Ben yapay zeka destekli bir Telegram botuyum.
📱 Size en iyi hizmeti sunmak için birkaç bilgiye ihtiyacım var.

👤 İsminiz nedir?
            """
            await event.respond(welcome_msg)
            await self.controller.set_user_state(event.sender_id, 'name')
            
        except Exception as e:
            print(f"Welcome Step Error: {e}")
            
    async def handle_name(self, event: events.NewMessage.Event):
        """İsim adımı"""
        try:
            name = event.message.text.strip()
            if len(name) < 2:
                await event.respond("❌ Lütfen geçerli bir isim girin!")
                return
                
            await self.controller.set_user_data(event.sender_id, 'name', name)
            
            email_msg = f"""
✅ Teşekkürler {name}!

📧 E-posta adresinizi paylaşır mısınız?
            """
            await event.respond(email_msg)
            await self.controller.set_user_state(event.sender_id, 'email')
            
        except Exception as e:
            print(f"Name Step Error: {e}")
            
    async def handle_email(self, event: events.NewMessage.Event):
        """E-posta adımı"""
        try:
            email = event.message.text.strip()
            if '@' not in email or '.' not in email:
                await event.respond("❌ Lütfen geçerli bir e-posta adresi girin!")
                return
                
            await self.controller.set_user_data(event.sender_id, 'email', email)
            
            phone_msg = """
✅ E-posta adresiniz kaydedildi!

📱 Telefon numaranızı paylaşır mısınız?
(Örnek: +90 555 123 4567)
            """
            await event.respond(phone_msg)
            await self.controller.set_user_state(event.sender_id, 'phone')
            
        except Exception as e:
            print(f"Email Step Error: {e}")
            
    async def handle_phone(self, event: events.NewMessage.Event):
        """Telefon adımı"""
        try:
            phone = event.message.text.strip()
            if not phone.replace('+', '').replace(' ', '').isdigit():
                await event.respond("❌ Lütfen geçerli bir telefon numarası girin!")
                return
                
            await self.controller.set_user_data(event.sender_id, 'phone', phone)
            
            preferences_msg = """
✅ Telefon numaranız kaydedildi!

⚙️ Tercihlerinizi seçin:
1. Grup Yönetimi
2. Spam Koruması
3. GPT Entegrasyonu
4. Tümü

Numarayı yazarak seçim yapın (örn: 1,2,4)
            """
            await event.respond(preferences_msg)
            await self.controller.set_user_state(event.sender_id, 'preferences')
            
        except Exception as e:
            print(f"Phone Step Error: {e}")
            
    async def handle_preferences(self, event: events.NewMessage.Event):
        """Tercihler adımı"""
        try:
            preferences = event.message.text.strip().split(',')
            valid_prefs = []
            
            for pref in preferences:
                pref = pref.strip()
                if pref in ['1', '2', '3', '4']:
                    valid_prefs.append(pref)
                    
            if not valid_prefs:
                await event.respond("❌ Lütfen geçerli tercihler seçin!")
                return
                
            await self.controller.set_user_data(event.sender_id, 'preferences', valid_prefs)
            
            # Kullanıcı bilgilerini göster
            user_data = await self.controller.get_user_data(event.sender_id)
            
            confirmation_msg = f"""
✅ Tercihleriniz kaydedildi!

📋 Bilgilerinizi kontrol edin:

👤 İsim: {user_data.get('name', 'Belirtilmedi')}
📧 E-posta: {user_data.get('email', 'Belirtilmedi')}
📱 Telefon: {user_data.get('phone', 'Belirtilmedi')}
⚙️ Tercihler: {', '.join(valid_prefs)}

✅ Onaylıyor musunuz? (Evet/Hayır)
            """
            await event.respond(confirmation_msg)
            await self.controller.set_user_state(event.sender_id, 'confirmation')
            
        except Exception as e:
            print(f"Preferences Step Error: {e}")
            
    async def handle_confirmation(self, event: events.NewMessage.Event):
        """Onay adımı"""
        try:
            response = event.message.text.strip().lower()
            
            if response == 'evet':
                # Kullanıcıyı kaydet
                await self.controller.save_user(event.sender_id)
                
                success_msg = """
🎉 Kaydınız tamamlandı! 🎉

🌟 GAVATCore'u kullanmaya başlayabilirsiniz.
📱 Yardım için /help yazabilirsiniz.

İyi kullanımlar! 😊
                """
                await event.respond(success_msg)
                await self.controller.set_user_state(event.sender_id, 'active')
                
            elif response == 'hayır':
                restart_msg = """
🔄 Kayıt sürecini yeniden başlatalım.

👤 İsminiz nedir?
                """
                await event.respond(restart_msg)
                await self.controller.set_user_state(event.sender_id, 'name')
                
            else:
                await event.respond("❌ Lütfen 'Evet' veya 'Hayır' yazın!")
                
        except Exception as e:
            print(f"Confirmation Step Error: {e}")
            
    async def handle_unknown_state(self, event: events.NewMessage.Event):
        """Bilinmeyen durum"""
        try:
            error_msg = """
❌ Bir hata oluştu!

🔄 Kayıt sürecini yeniden başlatalım.

👤 İsminiz nedir?
            """
            await event.respond(error_msg)
            await self.controller.set_user_state(event.sender_id, 'name')
            
        except Exception as e:
            print(f"Unknown State Error: {e}") 