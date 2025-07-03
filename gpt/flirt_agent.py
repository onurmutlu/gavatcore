# gpt/flirt_agent.py

import json
import os
from gpt.openai_utils import generate_gpt_reply
from gpt.system_prompt_manager import get_sales_prompt  # Sistem prompt merkezi

AGENT_DIR = "data/personas"

def normalize_agent_name(agent_name: str) -> str:
    """@ işareti varsa kaldır, dosya uyumluluğu için."""
    return agent_name.lstrip('@')

def load_agent_profile(agent_name: str) -> dict:
    """
    Karakter profilini yükler.
    Bot profilleri için bot_ prefix'i ile de dener.
    """
    agent_name = normalize_agent_name(agent_name)
    possible_names = [
        f"bot_{agent_name}",  # bot_geishaniz, bot_yayincilara gibi
        agent_name, 
        f"@{agent_name}"
    ]

    for name in possible_names:
        path = os.path.join(AGENT_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"Agent profile bulunamadı: {possible_names}")

def build_system_prompt(profile: dict, agent_name: str) -> str:
    # Yeni format: persona altında gpt_prompt varsa onu kullan!
    persona = profile.get("persona", {})
    if isinstance(persona, dict) and "gpt_prompt" in persona:
        prompt = persona["gpt_prompt"]
    elif isinstance(persona, str):
        prompt = persona
    else:
        prompt = "Flörtöz ve eğlenceli bir karakter."

    style_tags = profile.get("style_tags", "")
    intro = profile.get("intro_message", "")
    # Karışık mesaj sistemi ile template'leri hazırla
    from utilities.smart_reply import smart_reply
    
    bot_engaging_messages = profile.get("flirt_templates", []) or profile.get("engaging_messages", [])
    bot_reply_messages = profile.get("reply_messages", [])
    
    # Karışık örnekler oluştur
    mixed_engaging_examples = []
    mixed_reply_examples = []
    
    if bot_engaging_messages:
        for _ in range(5):  # 5 karışık engaging örneği
            mixed_engaging_examples.append(smart_reply.get_mixed_messages(bot_engaging_messages, "engaging"))
    
    if bot_reply_messages:
        for _ in range(5):  # 5 karışık reply örneği
            mixed_reply_examples.append(smart_reply.get_mixed_messages(bot_reply_messages, "reply"))

    system_prompt = f"""
Sen bir Telegram karakter botusun.

🧬 İsmin: {agent_name}
🎭 Kişiliğin: {prompt}
🔖 Stil etiketlerin: {style_tags}
💌 Tanıtım mesajın: {intro}

🎯 Görevlerin:
- Karakterine sadık kal
- Mesajlara içten, etkileyici ve flörtöz cevap ver
- Emoji kullanmayı ihmal etme
- Sohbeti devam ettir
- Aşağıdaki örneklerden esinlen ama birebir kopyalama

💡 Engaging mesaj örneklerin:
{json.dumps(mixed_engaging_examples, ensure_ascii=False, indent=2)}

💬 Reply mesaj örneklerin:
{json.dumps(mixed_reply_examples, ensure_ascii=False, indent=2)}
"""
    return system_prompt.strip()

async def generate_reply(agent_name: str, user_message: str) -> str:
    try:
        profile = load_agent_profile(agent_name)
    except Exception as e:
        print(f"[flirt_agent] Profil yüklenemedi: {e}")
        return "Şu an cevap veremiyorum, birazdan tekrar dene canım!"

    # Gelişmiş prompt öncelikli, yoksa fallback
    try:
        system_prompt = get_sales_prompt(agent_name) or build_system_prompt(profile, agent_name)
    except Exception as e:
        print(f"[flirt_agent] Sistem prompt üretilemedi: {e}")
        system_prompt = build_system_prompt(profile, agent_name)

    prompt = f'Kullanıcı şöyle dedi: "{user_message}"\nYanıtın ne olurdu?'

    try:
        response = generate_gpt_reply(prompt, system_prompt)
        return response.strip()
    except Exception as e:
        print(f"[flirt_agent] Yanıt üretilemedi: {e}")
        return "Bugün biraz utangaç oldum, lütfen tekrar yaz 🫦"

