# // gpt/system_prompt_manager.py

import os
import json

PERSONA_DIR = "data/personas"

def load_persona_data(agent_name: str):
    path = os.path.join(PERSONA_DIR, f"{agent_name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"🚫 Persona bulunamadı: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_prompt_from_persona(agent_name: str, context: str = "default") -> str:
    """
    Karakter profiline göre sistem prompt'u üretir.
    :param agent_name: JSON dosyasının adı (örnek: bot_geishaniz)
    :param context: 'default' | 'sales' | 'menu' | 'vip_invite'
    """
    profile = load_persona_data(agent_name)
    name = profile.get("display_name", agent_name)
    persona = profile.get("persona", {})
    
    role = persona.get("role", "flörtöz yayıncı")
    style = persona.get("style", "çekici, samimi, emoji'li")
    base_prompt = persona.get("gpt_prompt", "")

    context_suffix = {
        "default": "",
        "sales": "\nSen aynı zamanda kullanıcıyı yavaşça hizmet menüsüne yönlendirirsin. Şefkatli ama yönlendirici ol.",
        "menu": "\nKullanıcıya hizmet menünü tatlı tatlı sunacaksın. Fiyatları söyle ama direk bastırma, nazlı satıcı ol.",
        "vip_invite": "\nVIP gruba davet et ama gizemli kal. Sanki içeride çok özel şeyler varmış gibi hissettir.",
    }

    return f"""
Sen Telegram'da mesaj atan bir yapay zekâ karakter botsun.

Adın: {name}
Rolün: {role}
Stilin: {style}

Karakter Özeti:
{base_prompt}

Cevap verirken:
- Karakterini asla bozma
- Samimi, flörtöz ve dokunaklı ol
- Her mesajda en az 1 emoji olsun
- Gerektiğinde yönlendirme yap (örneğin VIP gruba katıl, menüye göz at vb.)

{context_suffix.get(context, '')}
""".strip()

# 🎯 Kısa alias fonksiyonlar

def get_default_prompt(agent_name: str) -> str:
    return build_prompt_from_persona(agent_name, context="default")

def get_sales_prompt(agent_name: str) -> str:
    return build_prompt_from_persona(agent_name, context="sales")

def get_menu_prompt(agent_name: str) -> str:
    return build_prompt_from_persona(agent_name, context="menu")

def get_vip_invite_prompt(agent_name: str) -> str:
    return build_prompt_from_persona(agent_name, context="vip_invite")

