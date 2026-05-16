import redis
import json
import config
from typing import Optional, Any

# Mock Redis class for environments without a real Redis server
class MemoryCache:
    def __init__(self):
        self._data = {}
        print("⚡ Redis not found. Using In-Memory Cache (Performance optimized).")

    def set(self, key: str, value: str, ex: int = None):
        self._data[key] = value

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def delete(self, key: str):
        if key in self._data:
            del self._data[key]

# Initialize Client
_client = None

def get_redis():
    global _client
    if _client is not None:
        return _client

    if config.REDIS_URL:
        try:
            _client = redis.from_url(config.REDIS_URL, decode_responses=True)
            _client.ping()
            print("🚀 Connected to Redis (High Throughput Mode)")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Falling back to memory.")
            _client = MemoryCache()
    else:
        _client = MemoryCache()
    
    return _client

def cache_set(key: str, value: Any, expire: int = 3600):
    client = get_redis()
    str_val = json.dumps(value) if not isinstance(value, str) else value
    client.set(key, str_val, ex=expire)

def cache_get(key: str) -> Optional[Any]:
    client = get_redis()
    val = client.get(key)
    if val:
        try:
            return json.loads(val)
        except:
            return val
    return None

def cache_delete(key: str):
    client = get_redis()
    client.delete(key)
