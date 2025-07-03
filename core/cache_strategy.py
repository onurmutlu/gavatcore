"""
🗄️ Cache Strategy - Önbellek stratejileri
"""
from enum import Enum

class CacheStrategy(Enum):
    """Önbellek stratejileri"""
    LRU = "lru"  # Least Recently Used
    FIFO = "fifo"  # First In First Out
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Akıllı/uyarlanabilir 