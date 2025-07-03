# // gpt/user_agent.py
from core.profile_loader import load_profile
from gpt.openai_utils import call_openai_chat

# 🚀 Şovcu bazlı AI destekli cevap oluşturma
async def generate_user_reply(user_key: str, user_message: str):
    """
    user_key: user_id (int veya str) ya da username (str) olabilir.
    """
    try:
        profile = load_profile(str(user_key))
    except Exception as e:
        print(f"[user_agent] Profil yüklenemedi: {e}")
        return "Şu an cevap veremiyorum, birazdan tekrar yaz canım! 🫦"

    # Şablonları bul, fallback’li şekilde
    flirt_templates = (
        profile.get("flirt_templates")
        or profile.get("engaging_messages")
        or profile.get("reply_messages")
        or []
    )

    # Tonu belirle, persona’dan çek fallback’li
    tone = (
        profile.get("tone")
        or (profile.get("persona", {}).get("style") if isinstance(profile.get("persona"), dict) else None)
        or "flirty"
    )

    prompt = f"""
Sen Telegram'da kendi adına flört eden, tatlı dilli bir yayıncısın.

Tarzın: {tone}
Senin bazı mesaj şablonların:
{flirt_templates}

Bir müşteri sana şöyle yazdı:
\"{user_message}\"

Cevabın:
- Emoji içersin
- Samimi ve içten olsun
- Kibarca satışa yönlendirsin
- Hazır şablonlara benzer ama yaratıcı olsun
"""

    try:
        reply = await call_openai_chat(prompt)
        return reply.strip()
    except Exception as e:
        print(f"[user_agent] Yanıt üretilemedi: {e}")
        return "Sanırım biraz dalgınım, lütfen tekrar yaz tatlım! 😇"
