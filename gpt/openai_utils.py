# gpt/openai_utils.py

import openai
from config import OPENAI_API_KEY, OPENAI_MODEL

openai.api_key = OPENAI_API_KEY

def call_openai_chat(prompt: str, system_prompt: str = "Sen eğlenceli bir flört botusun.") -> str:
    """
    GPT üzerinden yanıt üretir.

    :param prompt: Kullanıcı mesajı
    :param system_prompt: Karakterin GPT personası (persona dosyasından gelir)
    :return: GPT yanıtı
    """
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT cevabı alınamadı: {str(e)}"
