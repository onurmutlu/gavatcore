# gpt/flirt_agent.py

import json
import os
from gpt.openai_utils import generate_gpt_reply
from gpt.system_prompt_manager import get_sales_prompt  # 🧠 Yeni entegre edilen sistem prompt kaynağı

AGENT_DIR = "data/agents"

# ✅ Karakter profilini yükle
def load_agent_profile(agent_name: str) -> dict:
    path = os.path.join(AGENT_DIR, f"{agent_name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Agent profile bulunamadı: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 🔄 Geriye dönük uyumluluk için eski sistem prompt oluşturucu
def build_system_prompt(profile: dict, agent_name: str) -> str:
    persona = profile.get("persona", "Flörtöz ve eğlenceli bir karakter.")
    style_tags = profile.get("style_tags", "")
    intro = profile.get("intro_message", "")
    templates = profile.get("flirt_templates", [])

    system_prompt = f"""
Sen bir Telegram karakter botusun.

🧬 İsmin: {agent_name}
🎭 Kişiliğin: {persona}
🔖 Stil etiketlerin: {style_tags}
💌 Tanıtım mesajın: {intro}

🎯 Görevlerin:
- Karakterine sadık kal
- Mesajlara içten, etkileyici ve flörtöz cevap ver
- Emoji kullanmayı ihmal etme
- Sohbeti devam ettir
- Gerekirse flirt_templates listesinden esinlen

💡 Şablon örneklerin:
{json.dumps(templates, ensure_ascii=False, indent=2)}
"""
    return system_prompt.strip()

# ✨ Kullanıcı mesajına yanıt üret
async def generate_reply(agent_name: str, user_message: str) -> str:
    profile = load_agent_profile(agent_name)

    # 🧠 system_prompt_manager entegrasyonu: karakter profiline özel gelişmiş satış promptu
    system_prompt = get_sales_prompt(agent_name) or build_system_prompt(profile, agent_name)

    prompt = f'Kullanıcı şöyle dedi: "{user_message}"\nYanıtın ne olurdu?'
    response = await generate_gpt_reply(prompt, system_prompt)
    return response.strip()
