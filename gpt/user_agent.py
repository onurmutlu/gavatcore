# // gpt/user_agent.py
from core.profile_loader import load_profile
from gpt.openai_utils import call_openai_chat

# 🚀 Şovcu bazlı AI destekli cevap oluşturma
async def generate_user_reply(user_id: int, user_message: str):
    profile = load_profile(str(user_id))

    flirt_templates = profile.get("flirt_templates", [])
    tone = profile.get("tone", "flirty")

    prompt = f"""
Sen Telegram'da kendi adına flört eden, tatlı dilli bir yayıncısın.

Tarzın: {tone}
Senin bazı mesaj şablonların:
{flirt_templates}

Bir müşteri sana şöyle yazdı:
"{user_message}"

Cevabın:
- Emoji içersin
- Samimi ve içten olsun
- Kibarca satışa yönlendirsin
- Hazır şablonlara benzer ama yaratıcı olsun
"""

    reply = await call_openai_chat(prompt)
    return reply.strip()
