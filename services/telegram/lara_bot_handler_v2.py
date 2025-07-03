#!/usr/bin/env python3
"""
LARA BOT HANDLER V2 - Character Engine Entegreli
==============================================

Lara karakteri için Character Engine ile güçlendirilmiş mesaj işleme sistemi.
GPT-4 destekli dinamik yanıtlar ve gelişmiş kişilik yönetimi.

Yenilikler:
- Character Engine entegrasyonu
- Memory Context Tracker ile konuşma hafızası
- Personality Router ile dinamik yanıt stratejileri
- Fallback Manager ile timeout yönetimi
- Admin komutları (/mode, /character)
- Humanizer ile insan gibi davranış
"""

import asyncio
import random
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import structlog
import os
import sys

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Character Engine imports
from character_engine import (
    CharacterManager,
    GPTReplyGenerator,
    PersonalityRouter,
    FallbackReplyManager,
    MemoryContextTracker
)

# Humanizer import
from utilities.humanizer import create_humanizer

# Core imports
from core.advanced_ai_manager import advanced_ai_manager, AITaskType, AIPriority
from core.user_analyzer import babagavat_user_analyzer
from utilities.log_utils import log_event

# Behavioral tracker import
try:
    from character_engine.behavioral_tracker import behavioral_tracker
    BEHAVIORAL_TRACKING = True
except ImportError:
    BEHAVIORAL_TRACKING = False

logger = structlog.get_logger("lara_bot_handler_v2")

# ==================== CHARACTER ENGINE SETUP ====================

# Global instances
character_manager = CharacterManager()
gpt_generator = GPTReplyGenerator()
personality_router = PersonalityRouter()
fallback_manager = FallbackReplyManager()
memory_tracker = MemoryContextTracker()

# Load Lara character
lara_character = character_manager.load_character("lara")
if not lara_character:
    logger.error("❌ Lara karakteri yüklenemedi!")
    # Fallback config
    lara_character = character_manager.create_character(
        username="lara",
        name="Lara",
        system_prompt="Sen Lara, yarı Rus kökenli baştan çıkarıcı bir karaktersin.",
        reply_mode="hybrid",
        tone="flirty"
    )

# Humanizer instance
lara_humanizer = create_humanizer("lara")

logger.info(f"✅ Lara karakteri yüklendi - Mode: {lara_character.reply_mode}, Ton: {lara_character.tone}")

# ==================== ADMIN COMMANDS ====================

async def handle_admin_commands(client, sender, message_text: str) -> Optional[str]:
    """Admin komutlarını işle"""
    
    # Admin kontrolü (buraya admin user ID'leri eklenebilir)
    ADMIN_IDS = [123456789]  # Admin user ID'leri
    
    if sender.id not in ADMIN_IDS:
        return None
    
    message_lower = message_text.lower().strip()
    
    # /mode komutu
    if message_lower.startswith("/mode "):
        mode = message_lower.replace("/mode ", "").strip()
        valid_modes = ["manual", "gpt", "hybrid", "manualplus"]
        
        if mode in valid_modes:
            character_manager.update_character("lara", reply_mode=mode)
            return f"✅ Reply mode değiştirildi: {mode}"
        else:
            return f"❌ Geçersiz mode. Geçerli modlar: {', '.join(valid_modes)}"
    
    # /tone komutu
    elif message_lower.startswith("/tone "):
        tone = message_lower.replace("/tone ", "").strip()
        valid_tones = ["flirty", "soft", "dark", "mystic", "aggressive"]
        
        if tone in valid_tones:
            character_manager.update_character("lara", tone=tone)
            return f"✅ Ton değiştirildi: {tone}"
        else:
            return f"❌ Geçersiz ton. Geçerli tonlar: {', '.join(valid_tones)}"
    
    # /stats komutu
    elif message_lower == "/stats":
        stats = memory_tracker.get_conversation_summary(str(sender.id))
        character_stats = f"📊 Karakter: {lara_character.name}\n"
        character_stats += f"Mode: {lara_character.reply_mode}\n"
        character_stats += f"Ton: {lara_character.tone}\n"
        character_stats += f"Cooldown: {lara_character.cooldown_seconds}s\n\n"
        character_stats += f"📝 {stats}"
        return character_stats
    
    # /tokenstats komutu - GPT kullanım istatistikleri
    elif message_lower == "/tokenstats":
        try:
            from character_engine.token_usage_logger import token_logger
            return token_logger.format_stats_message()
        except ImportError:
            return "❌ Token logger modülü bulunamadı"
    
    # /humanizer komutu - doğallık ayarları
    elif message_lower.startswith("/humanizer "):
        setting = message_lower.replace("/humanizer ", "").strip()
        
        if setting == "on":
            character_manager.update_character("lara", humanizer_enabled=True)
            return "✅ Humanizer aktif - Lara artık daha insansı"
        elif setting == "off":
            character_manager.update_character("lara", humanizer_enabled=False)
            return "❌ Humanizer kapalı - Normal bot modu"
        else:
            return "❓ Kullanım: /humanizer on|off"
    
    # /clear komutu - hafızayı temizle
    elif message_lower == "/clear":
        memory_tracker.clear_user_memory(str(sender.id))
        return "🗑️ Konuşma hafızası temizlendi"
    
    return None

# ==================== MAIN HANDLER WITH CHARACTER ENGINE ====================

async def handle_lara_dm_v2(client, sender, message_text: str) -> bool:
    """
    Lara DM mesajlarını Character Engine ile işle
    
    Returns:
        bool: İşlem başarılı mı
    """
    try:
        user_id = str(sender.id)
        user_name = sender.first_name or "tatlım"
        
        # Admin komutlarını kontrol et
        admin_response = await handle_admin_commands(client, sender, message_text)
        if admin_response:
            await client.send_message(sender, admin_response)
            return True
        
        # Behavioral tracking
        if BEHAVIORAL_TRACKING:
            behavioral_tracker.track_message(
                user_id,
                message_text,
                sentiment="neutral",  # GPT analizi ile güncellenebilir
                is_bot_message=False
            )
        
        # Humanizer ile yanıt verip vermeme kararı
        if not lara_humanizer.should_respond():
            logger.info(f"🤐 Lara sessiz kalmayı seçti - User: {user_name}")
            return True
        
        # Mesajı hafızaya ekle
        memory_tracker.add_message(
            user_id,
            "user",
            message_text,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "user_name": user_name
            }
        )
        
        # Kullanıcı bağlamını al
        user_context = memory_tracker.get_user_context(user_id)
        context_messages = memory_tracker.get_context(user_id)
        
        # Karakteri yeniden yükle (güncellemeler için)
        current_character = character_manager.get_active_character() or lara_character
        
        logger.info(f"💬 Lara DM - User: {user_name}, Mode: {current_character.reply_mode}")
        
        # Reply mode'a göre yanıt üret
        final_reply = None
        
        if current_character.reply_mode == "manual":
            # Sadece template yanıtlar
            if current_character.template_replies:
                final_reply = random.choice(current_character.template_replies)
            else:
                final_reply = "💋 Canım sana sonra yazacağım..."
        
        elif current_character.reply_mode == "gpt":
            # Sadece GPT yanıtlar
            if gpt_generator.client:
                # Mesajı analiz et
                message_analysis = await gpt_generator.analyze_user_message(message_text)
                
                # Behavioral tracker'a analizi kaydet
                if BEHAVIORAL_TRACKING and message_analysis:
                    behavioral_tracker.track_message(
                        user_id,
                        message_text,
                        sentiment=message_analysis.get("emotion", "neutral"),
                        is_bot_message=False
                    )
                
                # Strateji belirle
                if BEHAVIORAL_TRACKING:
                    # Behavioral tracker'dan strateji önerisi al
                    tone, strategy_params = behavioral_tracker.get_strategy_for_message(
                        user_id,
                        message_text,
                        current_character.tone
                    )
                    # Karakterin tone'unu geçici olarak güncelle
                    current_character.tone = tone
                
                # Yanıt tipini belirle
                reply_type, strategy_params = personality_router.route_reply(
                    message_text,
                    current_character.to_dict(),
                    user_context,
                    message_analysis
                )
                
                logger.info(f"🎯 Reply type: {reply_type.value}")
                
                # GPT yanıtı üret
                gpt_reply = await gpt_generator.generate_reply(
                    message_text,
                    current_character.to_dict(),
                    context_messages,
                    strategy=reply_type.value,
                    user_id=user_id  # Token loglama için
                )
                
                if gpt_reply:
                    # Strateji uygula
                    final_reply = personality_router.apply_strategy(
                        gpt_reply,
                        reply_type,
                        strategy_params
                    )
            else:
                final_reply = "🔥 AI sistemim şu an bakımda canım..."
        
        elif current_character.reply_mode == "hybrid":
            # %50 GPT, %50 template
            use_gpt = random.random() > 0.5 and gpt_generator.client
            
            if use_gpt:
                # GPT kullan
                message_analysis = await gpt_generator.analyze_user_message(message_text)
                
                # Behavioral tracking
                if BEHAVIORAL_TRACKING:
                    tone, _ = behavioral_tracker.get_strategy_for_message(
                        user_id,
                        message_text,
                        current_character.tone
                    )
                    current_character.tone = tone
                
                reply_type, strategy_params = personality_router.route_reply(
                    message_text,
                    current_character.to_dict(),
                    user_context,
                    message_analysis
                )
                
                gpt_reply = await gpt_generator.generate_reply(
                    message_text,
                    current_character.to_dict(),
                    context_messages,
                    strategy=reply_type.value,
                    user_id=user_id
                )
                
                if gpt_reply:
                    final_reply = personality_router.apply_strategy(
                        gpt_reply,
                        reply_type,
                        strategy_params
                    )
            
            # GPT başarısızsa veya template seçildiyse
            if not final_reply and current_character.template_replies:
                final_reply = random.choice(current_character.template_replies)
        
        elif current_character.reply_mode == "manualplus":
            # Önce template, 60 saniye sonra GPT fallback
            if current_character.template_replies:
                final_reply = random.choice(current_character.template_replies)
            
            # Fallback zamanlaması ayarla (ayrı task olarak)
            asyncio.create_task(
                schedule_fallback_reply(client, sender, user_id, current_character)
            )
        
        # Yanıt yoksa fallback kullan
        if not final_reply:
            final_reply = await fallback_manager.get_fallback_reply(
                user_id,
                current_character.to_dict(),
                "no_reply",
                user_context=user_context
            )
        
        # Final yanıt yoksa default
        if not final_reply:
            final_reply = "💋 Canım, sana ne anlatsam..."
        
        # Yanıtı hafızaya ekle
        memory_tracker.add_message(
            user_id,
            "assistant",
            final_reply,
            metadata={
                "reply_mode": current_character.reply_mode,
                "character": current_character.name
            }
        )
        
        # Behavioral tracking - bot mesajı
        if BEHAVIORAL_TRACKING:
            behavioral_tracker.track_message(
                user_id,
                final_reply,
                sentiment="neutral",
                is_bot_message=True
            )
        
        # Humanizer ile doğal mesaj gönderimi
        humanizer_enabled = current_character.to_dict().get("humanizer_enabled", True)
        
        if humanizer_enabled:
            # Humanizer kullan
            await lara_humanizer.send_typing_then_message(
                client,
                sender.id,
                final_reply
            )
        else:
            # Normal gönderim (humanizer kapalı)
            delay = random.uniform(
                current_character.cooldown_seconds * 0.5,
                current_character.cooldown_seconds
            )
            await asyncio.sleep(delay)
            await client.send_message(sender, final_reply)
        
        logger.info(f"✅ Lara yanıt gönderildi: {final_reply[:50]}...")
        
        # Analytics
        log_event("lara_bot_v2", "dm_handled", {
            "user_id": user_id,
            "reply_mode": current_character.reply_mode,
            "message_length": len(message_text),
            "reply_length": len(final_reply),
            "humanizer_enabled": humanizer_enabled
        })
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Lara DM handler error: {e}")
        return False

async def schedule_fallback_reply(client, sender, user_id: str, character):
    """ManualPlus mode için fallback yanıt zamanla"""
    try:
        # 60 saniye bekle
        await asyncio.sleep(60)
        
        # Son mesaj zamanını kontrol et
        user_context = memory_tracker.get_user_context(user_id)
        last_message_time = user_context.get("last_contact")
        
        if last_message_time:
            last_time = datetime.fromisoformat(last_message_time)
            time_diff = (datetime.now() - last_time).total_seconds()
            
            # Eğer 60 saniyeden fazla geçtiyse ve yanıt yoksa
            if time_diff >= 60:
                # GPT ile fallback yanıt üret
                fallback_reply = await gpt_generator.generate_fallback_reply(
                    character.to_dict(),
                    context="Kullanıcı beklemeye devam ediyor"
                )
                
                if fallback_reply:
                    # Humanizer ile gönder
                    await lara_humanizer.send_typing_then_message(
                        client,
                        sender.id,
                        fallback_reply
                    )
                    logger.info(f"⏰ Fallback yanıt gönderildi: {fallback_reply[:50]}...")
                    
                    # Hafızaya ekle
                    memory_tracker.add_message(
                        user_id,
                        "assistant",
                        fallback_reply,
                        metadata={"type": "fallback"}
                    )
    
    except Exception as e:
        logger.error(f"❌ Fallback schedule error: {e}")

# ==================== GROUP MESSAGE HANDLER ====================

async def handle_lara_group_message_v2(client, event, username: str) -> bool:
    """Grup mesajlarını Character Engine ile işle"""
    try:
        sender = await event.get_sender()
        if not sender:
            return False
        
        user_id = str(sender.id)
        user_name = sender.first_name or "arkadaş"
        message_text = event.raw_text
        
        # Mention'ı temizle
        clean_message = message_text.replace(f"@{username}", "").strip()
        
        # Kısa ve öz grup yanıtları için özel prompt
        group_character = character_manager.get_active_character() or lara_character
        
        # Grup için daha kısa yanıtlar
        if gpt_generator.client:
            # Basit GPT yanıt (grup için optimize)
            group_prompt = f"Sen {group_character.name}, bir grupta mention edildin. Çok kısa ve etkili yanıt ver. Maksimum 1-2 cümle."
            
            response = await gpt_generator.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Gruplar için daha hızlı model
                messages=[
                    {"role": "system", "content": group_prompt},
                    {"role": "user", "content": clean_message}
                ],
                max_tokens=100,
                temperature=0.9
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Emoji ekle
            reply += f" {random.choice(['💋', '😘', '🔥', '✨'])}"
        else:
            # Template yanıt
            templates = [
                "Canım bana DM'den yaz, orada daha rahat konuşuruz 💋",
                "Burada değil tatlım, gel özele 😘",
                "DM'ye gel, sana özel şeyler var 🔥",
                "Özelden konuşalım canım ✨"
            ]
            reply = random.choice(templates)
        
        # Humanizer ile yanıt (gruplar için daha hızlı)
        await event.reply(reply)
        
        logger.info(f"✅ Grup yanıtı: {reply}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Grup mesajı hatası: {e}")
        return False

# ==================== STATS FUNCTION ====================

def get_lara_stats_v2() -> Dict[str, Any]:
    """Character Engine ile gelişmiş istatistikler"""
    
    # Temel stats
    stats = {
        "character_name": lara_character.name,
        "reply_mode": lara_character.reply_mode,
        "tone": lara_character.tone,
        "total_conversations": len(memory_tracker.active_memories),
        "active_character": character_manager.active_character,
        "loaded_characters": character_manager.list_characters(),
        "humanizer_enabled": True
    }
    
    # Memory stats
    total_messages = 0
    for user_id, memory in memory_tracker.active_memories.items():
        if "messages" in memory:
            total_messages += len(memory["messages"])
    
    stats["total_messages_in_memory"] = total_messages
    stats["gpt_enabled"] = gpt_generator.client is not None
    
    # Behavioral stats
    if BEHAVIORAL_TRACKING:
        stats["behavioral_tracking"] = "active"
        stats["tracked_users"] = len(behavioral_tracker.active_behaviors)
    
    return stats

# ==================== EXPORTS ====================

# V1 uyumluluğu için eski fonksiyon isimlerini de export et
handle_lara_dm = handle_lara_dm_v2
handle_lara_group_message = handle_lara_group_message_v2
get_lara_stats = get_lara_stats_v2 