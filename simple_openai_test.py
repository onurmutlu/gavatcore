#!/usr/bin/env python3
"""
Basit OpenAI API Test
"""

import asyncio
import json
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL

async def test_openai_direct():
    """Doğrudan OpenAI API test"""
    print("🧪 Doğrudan OpenAI API Test...")
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY bulunamadı!")
        return
    
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    try:
        print(f"📡 Model: {OPENAI_MODEL}")
        print("📝 Test mesajı gönderiliyor...")
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Sen bir duygu analizi uzmanısın. Yanıtını SADECE geçerli JSON formatında ver, markdown kullanma."},
                {"role": "user", "content": "Bugün çok mutluyum! Harika bir gün geçiriyorum. Bu metni analiz et ve duygu durumunu JSON formatında ver."}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        print(f"📥 Ham yanıt: {content}")
        
        # Markdown temizle
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        print(f"🧹 Temizlenmiş yanıt: {content}")
        
        # JSON parse
        try:
            result = json.loads(content)
            print("✅ JSON parsing başarılı!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing hatası: {e}")
            
    except Exception as e:
        print(f"❌ OpenAI API hatası: {e}")

if __name__ == "__main__":
    asyncio.run(test_openai_direct()) 