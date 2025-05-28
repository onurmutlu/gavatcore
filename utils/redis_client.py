#!/usr/bin/env python3
# utils/redis_client.py - Redis Async Client

import os
import asyncio
import json
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis

# Global Redis client
redis_client: Optional[redis.Redis] = None

async def init_redis():
    """Redis bağlantısını başlat"""
    global redis_client
    
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Bağlantıyı test et
        await redis_client.ping()
        
        print("✅ Redis bağlantısı başarılı")
        return True
        
    except Exception as e:
        print(f"❌ Redis bağlantı hatası: {e}")
        return False

async def close_redis():
    """Redis bağlantısını kapat"""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("✅ Redis bağlantısı kapatıldı")

def _make_key(user_id: str, key: str) -> str:
    """Redis key formatı oluştur"""
    return f"gavatcore:user:{user_id}:{key}"

def _make_global_key(key: str) -> str:
    """Global Redis key formatı oluştur"""
    return f"gavatcore:global:{key}"

# ==================== STATE OPERATIONS ====================

async def set_state(user_id: str, key: str, value: Any, 
                   expire_seconds: int = None) -> bool:
    """Kullanıcı state kaydet"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, key)
        
        # JSON serialize et
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        # Redis'e kaydet
        await redis_client.set(redis_key, value)
        
        # TTL ayarla
        if expire_seconds:
            await redis_client.expire(redis_key, expire_seconds)
        
        return True
        
    except Exception as e:
        print(f"❌ State kaydetme hatası ({user_id}.{key}): {e}")
        return False

async def get_state(user_id: str, key: str, default: Any = None) -> Any:
    """Kullanıcı state getir"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, key)
        value = await redis_client.get(redis_key)
        
        if value is None:
            return default
        
        # JSON deserialize et
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
        
    except Exception as e:
        print(f"❌ State getirme hatası ({user_id}.{key}): {e}")
        return default

async def delete_state(user_id: str, key: str) -> bool:
    """Kullanıcı state sil"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, key)
        result = await redis_client.delete(redis_key)
        
        return result > 0
        
    except Exception as e:
        print(f"❌ State silme hatası ({user_id}.{key}): {e}")
        return False

async def clear_state(user_id: str) -> int:
    """Kullanıcının tüm state'lerini sil"""
    try:
        if not redis_client:
            await init_redis()
        
        pattern = _make_key(user_id, "*")
        keys = await redis_client.keys(pattern)
        
        if keys:
            deleted = await redis_client.delete(*keys)
            return deleted
        
        return 0
        
    except Exception as e:
        print(f"❌ State temizleme hatası ({user_id}): {e}")
        return 0

async def get_all_user_states(user_id: str) -> Dict[str, Any]:
    """Kullanıcının tüm state'lerini getir"""
    try:
        if not redis_client:
            await init_redis()
        
        pattern = _make_key(user_id, "*")
        keys = await redis_client.keys(pattern)
        
        states = {}
        for key in keys:
            # Key'den state adını çıkar
            state_name = key.split(":")[-1]
            value = await redis_client.get(key)
            
            try:
                states[state_name] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                states[state_name] = value
        
        return states
        
    except Exception as e:
        print(f"❌ Tüm state'ler getirme hatası ({user_id}): {e}")
        return {}

# ==================== COOLDOWN OPERATIONS ====================

async def set_cooldown(user_id: str, action: str, seconds: int) -> bool:
    """Cooldown ayarla"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"cooldown:{action}")
        
        # Timestamp kaydet
        timestamp = datetime.utcnow().isoformat()
        await redis_client.set(redis_key, timestamp, ex=seconds)
        
        return True
        
    except Exception as e:
        print(f"❌ Cooldown ayarlama hatası ({user_id}.{action}): {e}")
        return False

async def check_cooldown(user_id: str, action: str) -> Optional[int]:
    """Cooldown kontrol et - kalan saniye döner, yoksa None"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"cooldown:{action}")
        ttl = await redis_client.ttl(redis_key)
        
        if ttl > 0:
            return ttl
        
        return None
        
    except Exception as e:
        print(f"❌ Cooldown kontrol hatası ({user_id}.{action}): {e}")
        return None

async def clear_cooldown(user_id: str, action: str) -> bool:
    """Cooldown temizle"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"cooldown:{action}")
        result = await redis_client.delete(redis_key)
        
        return result > 0
        
    except Exception as e:
        print(f"❌ Cooldown temizleme hatası ({user_id}.{action}): {e}")
        return False

# ==================== GLOBAL OPERATIONS ====================

async def set_global_state(key: str, value: Any, expire_seconds: int = None) -> bool:
    """Global state kaydet"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_global_key(key)
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        await redis_client.set(redis_key, value)
        
        if expire_seconds:
            await redis_client.expire(redis_key, expire_seconds)
        
        return True
        
    except Exception as e:
        print(f"❌ Global state kaydetme hatası ({key}): {e}")
        return False

async def get_global_state(key: str, default: Any = None) -> Any:
    """Global state getir"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_global_key(key)
        value = await redis_client.get(redis_key)
        
        if value is None:
            return default
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
        
    except Exception as e:
        print(f"❌ Global state getirme hatası ({key}): {e}")
        return default

# ==================== COUNTER OPERATIONS ====================

async def increment_counter(user_id: str, counter: str, 
                           amount: int = 1, expire_seconds: int = None) -> int:
    """Counter artır"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"counter:{counter}")
        
        # Atomic increment
        new_value = await redis_client.incrby(redis_key, amount)
        
        # TTL ayarla (sadece yeni key için)
        if expire_seconds and new_value == amount:
            await redis_client.expire(redis_key, expire_seconds)
        
        return new_value
        
    except Exception as e:
        print(f"❌ Counter artırma hatası ({user_id}.{counter}): {e}")
        return 0

async def get_counter(user_id: str, counter: str) -> int:
    """Counter değeri getir"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"counter:{counter}")
        value = await redis_client.get(redis_key)
        
        return int(value) if value else 0
        
    except Exception as e:
        print(f"❌ Counter getirme hatası ({user_id}.{counter}): {e}")
        return 0

async def reset_counter(user_id: str, counter: str) -> bool:
    """Counter sıfırla"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"counter:{counter}")
        result = await redis_client.delete(redis_key)
        
        return result > 0
        
    except Exception as e:
        print(f"❌ Counter sıfırlama hatası ({user_id}.{counter}): {e}")
        return False

# ==================== LIST OPERATIONS ====================

async def add_to_list(user_id: str, list_name: str, item: Any, 
                     max_length: int = None) -> bool:
    """Liste'ye eleman ekle"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"list:{list_name}")
        
        if isinstance(item, (dict, list)):
            item = json.dumps(item, ensure_ascii=False)
        
        # Liste'nin başına ekle
        await redis_client.lpush(redis_key, item)
        
        # Max uzunluk kontrolü
        if max_length:
            await redis_client.ltrim(redis_key, 0, max_length - 1)
        
        return True
        
    except Exception as e:
        print(f"❌ Liste ekleme hatası ({user_id}.{list_name}): {e}")
        return False

async def get_list(user_id: str, list_name: str, 
                  start: int = 0, end: int = -1) -> List[Any]:
    """Liste getir"""
    try:
        if not redis_client:
            await init_redis()
        
        redis_key = _make_key(user_id, f"list:{list_name}")
        items = await redis_client.lrange(redis_key, start, end)
        
        result = []
        for item in items:
            try:
                result.append(json.loads(item))
            except (json.JSONDecodeError, TypeError):
                result.append(item)
        
        return result
        
    except Exception as e:
        print(f"❌ Liste getirme hatası ({user_id}.{list_name}): {e}")
        return []

# ==================== STATISTICS ====================

async def get_redis_stats() -> Dict[str, Any]:
    """Redis istatistikleri getir"""
    try:
        if not redis_client:
            await init_redis()
        
        info = await redis_client.info()
        
        stats = {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0)
        }
        
        # Key sayısı
        pattern = "gavatcore:*"
        keys = await redis_client.keys(pattern)
        stats["total_keys"] = len(keys)
        
        return stats
        
    except Exception as e:
        print(f"❌ Redis stats hatası: {e}")
        return {} 