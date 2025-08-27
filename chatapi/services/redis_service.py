import json
import redis
from django.conf import settings
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class RedisService:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=getattr(settings, "REDIS_DB", 0),
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour
    
    def get_chat_context(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve chat context and filters"""
        key = f"chat:{chat_id}:context"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def set_chat_context(self, chat_id: str, context: Dict[str, Any], ttl: int = None):
        """Store chat context and filters"""
        key = f"chat:{chat_id}:context"
        self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(context)
        )
    
    def append_message(self, chat_id: str, message: str, response: Dict):
        """Store message history"""
        key = f"chat:{chat_id}:messages"
        data = {
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        self.client.lpush(key, json.dumps(data))
        self.client.ltrim(key, 0, 9)  # Keep last 10 messages
        self.client.expire(key, self.default_ttl)
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response"""
        data = self.client.get(f"cache:{cache_key}")
        return json.loads(data) if data else None
    
    def set_cached_response(self, cache_key: str, response: Dict, ttl: int = 300):
        """Cache response for 5 minutes by default"""
        self.client.setex(
            f"cache:{cache_key}",
            ttl,
            json.dumps(response)
        )