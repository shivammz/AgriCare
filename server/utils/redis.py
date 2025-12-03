# AgriCare/server/redis.py

import redis.asyncio as redis_asyncio
from config import Config
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Wrapper class to handle Redis connection failures gracefully
class RedisWrapper:
    """Wraps Redis client to auto-fallback on connection errors"""
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.fallback = InMemoryRedis()
        self.use_fallback = False
    
    async def _try_operation(self, operation, *args, **kwargs):
        """Try operation on Redis, fallback to in-memory if it fails"""
        if self.use_fallback:
            return await operation(self.fallback, *args, **kwargs)
        
        try:
            # Test if redis_client is InMemoryRedis
            if isinstance(self.redis_client, InMemoryRedis):
                return await operation(self.redis_client, *args, **kwargs)
            
            # Try real Redis
            result = await operation(self.redis_client, *args, **kwargs)
            return result
        except Exception as e:
            logger.warning(f"⚠️ Redis operation failed, switching to in-memory fallback: {e}")
            self.use_fallback = True
            return await operation(self.fallback, *args, **kwargs)
    
    async def get(self, key: str) -> Optional[str]:
        return await self._try_operation(lambda client, k: client.get(k), key)
    
    async def setex(self, key: str, seconds: int, value: str):
        return await self._try_operation(lambda client, k, s, v: client.setex(k, s, v), key, seconds, value)
    
    async def incr(self, key: str) -> int:
        return await self._try_operation(lambda client, k: client.incr(k), key)
    
    async def expire(self, key: str, seconds: int):
        return await self._try_operation(lambda client, k, s: client.expire(k, s), key, seconds)
    
    async def ttl(self, key: str) -> int:
        return await self._try_operation(lambda client, k: client.ttl(k), key)
    
    async def delete(self, key: str):
        return await self._try_operation(lambda client, k: client.delete(k), key)

# In-memory fallback storage
class InMemoryRedis:
    """Fallback in-memory storage when Redis is unavailable"""
    def __init__(self):
        self._store = {}
        self._expiry = {}
        logger.warning("🔴 Redis unavailable - using in-memory storage (OTPs won't persist across server restarts)")
    
    async def get(self, key: str) -> Optional[str]:
        if key in self._expiry and datetime.now() > self._expiry[key]:
            del self._store[key]
            del self._expiry[key]
            return None
        return self._store.get(key)
    
    async def setex(self, key: str, seconds: int, value: str):
        self._store[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=seconds)
    
    async def incr(self, key: str) -> int:
        current = await self.get(key)
        new_value = (int(current) if current else 0) + 1
        self._store[key] = str(new_value)
        return new_value
    
    async def expire(self, key: str, seconds: int):
        if key in self._store:
            self._expiry[key] = datetime.now() + timedelta(seconds=seconds)
    
    async def ttl(self, key: str) -> int:
        if key in self._expiry:
            remaining = (self._expiry[key] - datetime.now()).total_seconds()
            return int(max(0, remaining))
        return -1
    
    async def delete(self, key: str):
        self._store.pop(key, None)
        self._expiry.pop(key, None)

# Try to use real Redis, but be ready to fall back
try:
    if Config.REDIS_URL:
        redis_client = redis_asyncio.from_url(
            Config.REDIS_URL, 
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1
        )
        redis = RedisWrapper(redis_client)
        logger.info("✅ Redis client initialized (connection will be tested on first use)")
    else:
        logger.info("ℹ️  No REDIS_URL configured, using in-memory storage")
        redis = RedisWrapper(InMemoryRedis())
except Exception as e:
    logger.warning(f"⚠️  Failed to initialize Redis: {e}")
    redis = RedisWrapper(InMemoryRedis())

