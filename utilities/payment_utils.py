# utils/payment_utils.py

import json
from pathlib import Path

BANKS_FILE = Path("data/banks.json")

def load_banks():
    if not BANKS_FILE.exists():
        return {}
    with open(BANKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_bank_by_name(bank_name: str):
    banks = load_banks()
    return banks.get(bank_name)

def get_safe_banks():
    banks = load_banks()
    return {k: v for k, v in banks.items() if not v.get("requires_name", True)}

def list_safe_banks_for_buttons():
    """
    Inline menu için sadece güvenli bankaları listeler
    (alıcı adı istemeyenler)
    """
    return list(get_safe_banks().keys())

def generate_payment_message(bank_name, profile, banks_data):
    bank = banks_data.get(bank_name)
    if not bank:
        return "⚠️ Banka bulunamadı."

    papara_iban = profile.get("papara_iban", "")
    papara_note = profile.get("papara_note", "")
    papara_name = profile.get("papara_name", "Papara")

    personal_iban_info = profile.get("personal_iban", {})
    personal_iban = personal_iban_info.get("iban")
    personal_iban_name = personal_iban_info.get("name")
    personal_iban_bank = personal_iban_info.get("bank_name", "Banka Bilinmiyor")

    dekont_notu = "📌 *Lütfen gönderim yaptıktan sonra dekontu DM’den ilet canım 💖*"

    if bank["requires_name"] and bank["iban"] == papara_iban:
        explanation = f"📝 Açıklama kısmına herhangi bir not bırakabilirsin canım 💬\n{dekont_notu}"
        name_to_show = papara_name
        iban_to_show = papara_iban
    elif personal_iban:
        explanation = dekont_notu
        name_to_show = personal_iban_name
        iban_to_show = personal_iban
        bank_name = personal_iban_bank
    else:
        explanation = f"📝 Açıklamaya şu Papara ID'yi yaz: `{papara_note}`\n{dekont_notu}"
        name_to_show = papara_name
        iban_to_show = bank["iban"]

    return f"""
🏦 Banka: {bank_name}
💳 IBAN: `{iban_to_show}`
👤 Hesap Sahibi: {name_to_show}
{explanation}
"""
