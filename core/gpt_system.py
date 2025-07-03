"""
🤖 GPT System - GPT entegrasyonu
"""
from telethon import events
import openai
import json
import os

class GPTSystem:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000
        self.temperature = 0.7
        self.conversation_history = {}  # {user_id: [messages]}
        
    async def process_message(self, event: events.NewMessage.Event) -> str:
        """GPT ile mesajı işle"""
        try:
            user_id = event.sender_id
            message = event.message.text
            
            # Konuşma geçmişini kontrol et
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
                
            # Mesajı geçmişe ekle
            self.conversation_history[user_id].append({
                "role": "user",
                "content": message
            })
            
            # GPT'ye gönder
            response = await self.get_gpt_response(user_id)
            
            # Yanıtı geçmişe ekle
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": response
            })
            
            return response
            
        except Exception as e:
            print(f"Process Message Error: {e}")
            return "❌ Bir hata oluştu! Lütfen tekrar deneyin."
            
    async def get_gpt_response(self, user_id: int) -> str:
        """GPT'den yanıt al"""
        try:
            # API anahtarını kontrol et
            if not self.api_key:
                return "❌ API anahtarı bulunamadı!"
                
            # OpenAI istemcisini oluştur
            client = openai.OpenAI(api_key=self.api_key)
            
            # Son 10 mesajı al
            messages = self.conversation_history[user_id][-10:]
            
            # GPT'ye gönder
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"GPT Response Error: {e}")
            return "❌ GPT yanıt veremedi! Lütfen tekrar deneyin."
            
    async def clear_history(self, user_id: int):
        """Konuşma geçmişini temizle"""
        try:
            if user_id in self.conversation_history:
                self.conversation_history[user_id] = []
                print(f"✅ {user_id} için konuşma geçmişi temizlendi!")
                
        except Exception as e:
            print(f"Clear History Error: {e}")
            
    async def set_model(self, model: str):
        """GPT modelini değiştir"""
        try:
            self.model = model
            print(f"✅ GPT modeli '{model}' olarak değiştirildi!")
            
        except Exception as e:
            print(f"Set Model Error: {e}")
            
    async def set_max_tokens(self, tokens: int):
        """Maksimum token sayısını ayarla"""
        try:
            self.max_tokens = tokens
            print(f"✅ Maksimum token sayısı {tokens} olarak ayarlandı!")
            
        except Exception as e:
            print(f"Set Max Tokens Error: {e}")
            
    async def set_temperature(self, temp: float):
        """Sıcaklık değerini ayarla"""
        try:
            self.temperature = temp
            print(f"✅ Sıcaklık değeri {temp} olarak ayarlandı!")
            
        except Exception as e:
            print(f"Set Temperature Error: {e}")
            
    async def get_stats(self) -> dict:
        """GPT istatistiklerini getir"""
        try:
            return {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "active_users": len(self.conversation_history)
            }
            
        except Exception as e:
            print(f"Stats Error: {e}")
            return {}

    async def generate(self, prompt: str, context: dict = None) -> str:
        """Prompt ile içerik üretir (context opsiyonel)."""
        try:
            messages = []
            if context and isinstance(context, dict):
                # Context'i sistem mesajı olarak ekle
                messages.append({"role": "system", "content": str(context)})
            messages.append({"role": "user", "content": prompt})
            
            # OpenAI istemcisi
            if not self.api_key:
                return "❌ API anahtarı bulunamadı!"
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT generate error: {e}")
            return f"❌ GPT generate error: {e}" 