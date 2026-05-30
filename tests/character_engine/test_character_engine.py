"""
🧪 Character Engine Test & Integration Example
"""

import asyncio
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from character_engine.character_manager import CharacterManager
from character_engine.gpt_reply_generator import GPTReplyGenerator
from character_engine.personality_router import PersonalityRouter
from character_engine.fallback_reply_manager import FallbackReplyManager
from character_engine.memory_context_tracker import MemoryContextTracker

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_character_engine():
    """Character Engine test fonksiyonu"""
    
    print("🧪 CHARACTER ENGINE TEST BAŞLIYOR...")
    print("="*50)
    
    # 1. Character Manager Test
    print("\n1️⃣ CHARACTER MANAGER TEST")
    char_manager = CharacterManager()
    
    # Karakterleri listele
    characters = char_manager.list_characters()
    print(f"✅ Yüklenen karakterler: {characters}")
    
    # Lara'yı yükle
    lara = char_manager.load_character("lara")
    if lara:
        print(f"✅ Lara yüklendi: {lara.name} - Ton: {lara.tone}")
    
    # 2. Memory Context Tracker Test
    print("\n2️⃣ MEMORY CONTEXT TRACKER TEST")
    memory_tracker = MemoryContextTracker()
    
    # Test kullanıcısı için mesaj ekle
    test_user = "test_user_123"
    memory_tracker.add_message(test_user, "user", "Merhaba Lara, nasılsın?")
    memory_tracker.add_message(test_user, "assistant", "Merhaba canım, iyiyim sen nasılsın? 😊")
    memory_tracker.add_message(test_user, "user", "Ben de iyiyim, seninle konuşmak güzel")
    
    # Bağlamı al
    context = memory_tracker.get_context(test_user)
    print(f"✅ Bağlam mesajları: {len(context)} adet")
    
    # Kullanıcı bağlamını al
    user_context = memory_tracker.get_user_context(test_user)
    print(f"✅ Kullanıcı bağlamı - Trust Index: {user_context['trust_index']:.2f}")
    
    # 3. Personality Router Test
    print("\n3️⃣ PERSONALITY ROUTER TEST")
    personality_router = PersonalityRouter()
    
    # Test mesajı için yanıt tipi belirle
    test_message = "Seni özledim, neden yazmıyorsun?"
    message_analysis = {
        "emotion": "desperate",
        "intent": "flirt",
        "urgency": "high"
    }
    
    reply_type, strategy_params = personality_router.route_reply(
        test_message,
        lara.to_dict(),
        user_context,
        message_analysis
    )
    print(f"✅ Belirlenen yanıt tipi: {reply_type.value}")
    print(f"✅ Strateji parametreleri: {strategy_params}")
    
    # 4. GPT Reply Generator Test
    print("\n4️⃣ GPT REPLY GENERATOR TEST")
    gpt_generator = GPTReplyGenerator()
    
    if gpt_generator.client:
        # GPT yanıtı üret
        gpt_reply = await gpt_generator.generate_reply(
            test_message,
            lara.to_dict(),
            context,
            strategy="flirt"
        )
        
        if gpt_reply:
            print(f"✅ GPT yanıtı: {gpt_reply}")
            
            # Personality router ile strateji uygula
            final_reply = personality_router.apply_strategy(
                gpt_reply,
                reply_type,
                strategy_params
            )
            print(f"✅ Strateji uygulanmış yanıt: {final_reply}")
        else:
            print("❌ GPT yanıtı alınamadı")
    else:
        print("⚠️ GPT client yok - API key eksik")
    
    # 5. Fallback Reply Manager Test
    print("\n5️⃣ FALLBACK REPLY MANAGER TEST")
    fallback_manager = FallbackReplyManager()
    
    # Fallback yanıt al
    fallback_reply = await fallback_manager.get_fallback_reply(
        test_user,
        lara.to_dict(),
        "timeout",
        user_context=user_context
    )
    
    if fallback_reply:
        print(f"✅ Fallback yanıt: {fallback_reply}")
    
    # 6. Entegre Kullanım Örneği
    print("\n6️⃣ ENTEGRE KULLANIM ÖRNEĞİ")
    print("-"*50)
    
    async def generate_character_reply(user_id: str, user_message: str, character_username: str):
        """Tam entegre yanıt üretimi"""
        
        # 1. Karakteri yükle
        character = char_manager.load_character(character_username)
        if not character:
            return "Karakter bulunamadı!"
        
        # 2. Mesajı hafızaya ekle
        memory_tracker.add_message(user_id, "user", user_message)
        
        # 3. Bağlamları al
        context_messages = memory_tracker.get_context(user_id)
        user_context = memory_tracker.get_user_context(user_id)
        
        # 4. Mesajı analiz et (GPT varsa)
        message_analysis = None
        if gpt_generator.client:
            message_analysis = await gpt_generator.analyze_user_message(user_message)
            print(f"📊 Mesaj analizi: {message_analysis}")
        
        # 5. Yanıt tipini belirle
        reply_type, strategy_params = personality_router.route_reply(
            user_message,
            character.to_dict(),
            user_context,
            message_analysis
        )
        
        # 6. Reply mode'a göre yanıt üret
        final_reply = None
        
        if character.reply_mode == "gpt" and gpt_generator.client:
            # Sadece GPT
            gpt_reply = await gpt_generator.generate_reply(
                user_message,
                character.to_dict(),
                context_messages,
                strategy=reply_type.value
            )
            if gpt_reply:
                final_reply = personality_router.apply_strategy(
                    gpt_reply,
                    reply_type,
                    strategy_params
                )
        
        elif character.reply_mode == "manual":
            # Sadece template
            templates = character.template_replies
            if templates:
                import random
                final_reply = random.choice(templates)
        
        elif character.reply_mode == "hybrid":
            # Karma mod - %50 GPT, %50 template
            import random
            if random.random() > 0.5 and gpt_generator.client:
                # GPT kullan
                gpt_reply = await gpt_generator.generate_reply(
                    user_message,
                    character.to_dict(),
                    context_messages,
                    strategy=reply_type.value
                )
                if gpt_reply:
                    final_reply = personality_router.apply_strategy(
                        gpt_reply,
                        reply_type,
                        strategy_params
                    )
            
            if not final_reply and character.template_replies:
                # Template kullan
                final_reply = random.choice(character.template_replies)
        
        # 7. Yanıt yoksa fallback
        if not final_reply:
            final_reply = await fallback_manager.get_fallback_reply(
                user_id,
                character.to_dict(),
                "no_reply",
                user_context=user_context
            )
        
        # 8. Yanıtı hafızaya ekle
        if final_reply:
            memory_tracker.add_message(user_id, "assistant", final_reply)
        
        return final_reply or "..."
    
    # Test et
    test_reply = await generate_character_reply(
        "test_user_123",
        "Seninle tanışmak istiyorum, biraz kendinden bahseder misin?",
        "lara"
    )
    
    print(f"\n🎯 FINAL YANIT: {test_reply}")
    
    print("\n✅ TÜM TESTLER TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(test_character_engine()) 