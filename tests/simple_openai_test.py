#!/usr/bin/env python3
"""
🤖 SIMPLE OPENAI TEST 🤖

GPT-4o bağlantısını test et
"""

import os
import openai

def test_openai():
    """🤖 OpenAI bağlantısını test et"""
    try:
        print("🤖 OpenAI GPT-4o test başlıyor...")
        
        # API key kontrol
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY bulunamadı!")
            return False
        
        print(f"✅ API Key bulundu: {api_key[:10]}...")
        
        # OpenAI client oluştur
        client = openai.OpenAI(api_key=api_key)
        
        # Test mesajı
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Merhaba! Sen kimsin?"}
            ],
            max_tokens=50
        )
        
        gpt_response = response.choices[0].message.content
        print(f"✅ GPT-4o Cevabı: {gpt_response}")
        
        print("""
🎯 OPENAI TEST BAŞARILI!

🤖 GPT-4o bağlantısı çalışıyor
💬 API calls başarılı
🧠 Model responses alınıyor

💪 ONUR METODU: AI POWER ACTIVE!
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test error: {e}")
        return False

if __name__ == "__main__":
    test_openai() 