import time
import asyncio
from openai import OpenAI
from openai.types.chat import ChatCompletion
from config import OPENAI_API_KEY, OPENAI_MODEL
import logging

logger = logging.getLogger("gavatcore.openai")

client = OpenAI(api_key=OPENAI_API_KEY)

# Rate limiting için global değişkenler - Daha sıkı
last_request_time = 0
min_request_interval = 15.0  # Minimum 15 saniye aralık (çok sıkı)
max_retries = 1  # Sadece 1 deneme
base_delay = 30.0  # Uzun başlangıç gecikmesi

# Emergency mode - GPT'yi tamamen kapat
EMERGENCY_MODE = False  # True = GPT kapalı, False = GPT açık
EMERGENCY_RESPONSE = "🤖 Şu an sistem bakımda, biraz sonra tekrar dene canım!"

# Basit cache sistemi
response_cache = {}
cache_ttl = 300  # 5 dakika cache

def get_cache_key(prompt: str, system_prompt: str) -> str:
    """Cache key oluştur"""
    return f"{hash(prompt)}_{hash(system_prompt)}"

def is_cache_valid(timestamp: float) -> bool:
    """Cache'in geçerli olup olmadığını kontrol et"""
    return time.time() - timestamp < cache_ttl

def call_openai_chat(prompt: str, system_prompt: str = "Sen eğlenceli bir flört botusun.") -> str:
    """
    GPT üzerinden yanıt üretir - Rate limiting ve cache ile.
    :param prompt: Kullanıcı mesajı
    :param system_prompt: Karakterin GPT personası (persona dosyasından gelir)
    :return: GPT yanıtı
    """
    global last_request_time
    
    # Emergency mode kontrolü
    if EMERGENCY_MODE:
        logger.warning("Emergency mode aktif - GPT çağrısı engellendi")
        return EMERGENCY_RESPONSE
    
    # Cache kontrolü
    cache_key = get_cache_key(prompt, system_prompt)
    if cache_key in response_cache:
        cached_response, timestamp = response_cache[cache_key]
        if is_cache_valid(timestamp):
            logger.info("Cache'den yanıt döndürülüyor")
            return cached_response
        else:
            # Eski cache'i temizle
            del response_cache[cache_key]
    
    # Rate limiting
    current_time = time.time()
    time_since_last = current_time - last_request_time
    if time_since_last < min_request_interval:
        sleep_time = min_request_interval - time_since_last
        logger.info(f"Rate limiting: {sleep_time:.2f}s bekleniyor...")
        time.sleep(sleep_time)
    
    # Retry mekanizması
    for attempt in range(max_retries):
        try:
            last_request_time = time.time()
            
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100,  # Daha az token
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0.6,
            )
            
            result = response.choices[0].message.content.strip()
            
            # Cache'e kaydet
            response_cache[cache_key] = (result, time.time())
            
            # Cache temizliği (100'den fazla entry varsa eski olanları sil)
            if len(response_cache) > 100:
                oldest_keys = sorted(response_cache.keys(), 
                                   key=lambda k: response_cache[k][1])[:20]
                for key in oldest_keys:
                    del response_cache[key]
            
            return result
            
        except Exception as e:
            error_str = str(e).lower()
            
            if "rate limit" in error_str or "too many requests" in error_str:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limit hatası, {delay}s bekleniyor... (Deneme {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    logger.error("Rate limit hatası: Max deneme sayısına ulaşıldı")
                    return "🤖 Şu an çok yoğunum, biraz sonra tekrar dene canım!"
            
            elif "quota" in error_str or "billing" in error_str:
                logger.error("OpenAI quota/billing hatası")
                return "🤖 Sistem bakımda, biraz sonra tekrar dene!"
            
            else:
                if attempt < max_retries - 1:
                    delay = base_delay * (attempt + 1)
                    logger.warning(f"GPT hatası: {e}, {delay}s sonra tekrar deneniyor...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"GPT hatası (son deneme): {e}")
                    return f"⚠️ GPT cevabı alınamadı: {str(e)}"
    
    return "🤖 Yanıt üretilemedi, lütfen tekrar dene."

# Eski API ile uyum için alias fonksiyon
def generate_gpt_reply(prompt: str, system_prompt: str = "Sen eğlenceli bir flört botusun.") -> str:
    return call_openai_chat(prompt, system_prompt)

# Cache temizleme fonksiyonu
def clear_cache():
    """Cache'i temizle"""
    global response_cache
    response_cache.clear()
    logger.info("GPT cache temizlendi")

# Cache istatistikleri
def get_cache_stats():
    """Cache istatistiklerini döndür"""
    valid_entries = sum(1 for _, (_, timestamp) in response_cache.items() 
                       if is_cache_valid(timestamp))
    return {
        "total_entries": len(response_cache),
        "valid_entries": valid_entries,
        "cache_hit_ratio": valid_entries / max(len(response_cache), 1)
    }
