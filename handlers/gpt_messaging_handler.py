#!/usr/bin/env python3
"""
🤖 GPT Messaging Handler - GPT mesaj yönetimi
"""
from telethon import events
from core.controller import Controller
from core.gpt_system import GPTSystem

import structlog
from gpt.flirt_agent import generate_reply
from gpt.system_prompt_manager import get_menu_prompt

logger = structlog.get_logger("gavatcore.gpt_messaging_handler")

class GPTMessagingHandler:
    def __init__(self, controller: Controller, gpt_system: GPTSystem):
        self.controller = controller
        self.gpt_system = gpt_system
        
    async def handle_gpt_message(self, event: events.NewMessage.Event):
        """GPT mesajlarını işle"""
        try:
            # Mesaj içeriğini al
            message = event.message.text
            
            # GPT yanıtı al
            response = await self.gpt_system.get_response(message)
            
            # Yanıtı gönder
            await event.respond(response)
            
        except Exception as e:
            print(f"GPT Handler Error: {e}")
            await event.respond("Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.")
            
    async def handle_gpt_command(self, event: events.NewMessage.Event):
        """GPT komutlarını işle"""
        try:
            # Komut işleme mantığı
            pass
        except Exception as e:
            print(f"GPT Command Error: {e}")
            
    async def process_gpt_message(self, event: events.NewMessage.Event):
        """GPT mesajlarını işle"""
        try:
            # Mesaj işleme mantığı
            pass
        except Exception as e:
            print(f"GPT Message Processing Error: {e}")

async def gpt_messaging_handler(message: str, context: dict = None) -> str:
    """
    GPT ile mesaj oluşturur ve yanıtlar
    
    Args:
        message (str): Kullanıcı mesajı
        context (dict, optional): Ek bağlam bilgileri
        
    Returns:
        str: GPT yanıtı
    """
    try:
        # Sistem promptunu al
        system_prompt = get_menu_prompt()
        
        # Bağlam bilgilerini ekle
        if context:
            system_prompt += f"\nBağlam: {context}"
            
        # GPT yanıtı oluştur
        response = await generate_reply(message, system_prompt)
        
        if not response:
            return "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."
            
        return response
        
    except Exception as e:
        logger.error(f"GPT mesajlaşma hatası: {e}")
        return "Bir hata oluştu. Lütfen daha sonra tekrar deneyin." 