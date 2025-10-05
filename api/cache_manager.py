"""
Cache Manager for Performance Optimization
Caches frequently accessed memories and API responses
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import json


class CacheManager:
    """
    In-memory cache for memories and API responses
    Significantly reduces Snowflake queries and API calls
    """

    def __init__(self, ttl_minutes: int = 30):
        self.ttl_minutes = ttl_minutes
        # Cache structure: {cache_key: {data, timestamp}}
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.llm_response_cache: Dict[str, Dict[str, Any]] = {}

    def _generate_key(self, *args) -> str:
        """Generate cache key from arguments"""
        key_string = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cache entry is expired"""
        age = datetime.now() - timestamp
        return age > timedelta(minutes=self.ttl_minutes)

    def get_memories(self, topic: str, patient_id: str = None) -> Optional[List]:
        """Get cached memories for a topic"""
        cache_key = self._generate_key("memories", topic, patient_id or "default")

        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]

            if not self._is_expired(entry["timestamp"]):
                print(f"✅ Cache HIT: memories for '{topic}'")
                return entry["data"]
            else:
                # Expired, remove
                del self.memory_cache[cache_key]

        print(f"❌ Cache MISS: memories for '{topic}'")
        return None

    def set_memories(self, topic: str, memories: List, patient_id: str = None):
        """Cache memories for a topic"""
        cache_key = self._generate_key("memories", topic, patient_id or "default")

        self.memory_cache[cache_key] = {
            "data": memories,
            "timestamp": datetime.now()
        }

        print(f"💾 Cached {len(memories)} memories for '{topic}'")

    def get_llm_response(self, prompt: str, temperature: float = 0.8) -> Optional[str]:
        """Get cached LLM response for a prompt"""
        cache_key = self._generate_key("llm", prompt, temperature)

        if cache_key in self.llm_response_cache:
            entry = self.llm_response_cache[cache_key]

            if not self._is_expired(entry["timestamp"]):
                print(f"✅ Cache HIT: LLM response")
                return entry["data"]
            else:
                del self.llm_response_cache[cache_key]

        print(f"❌ Cache MISS: LLM response")
        return None

    def set_llm_response(self, prompt: str, response: str, temperature: float = 0.8):
        """Cache LLM response"""
        cache_key = self._generate_key("llm", prompt, temperature)

        self.llm_response_cache[cache_key] = {
            "data": response,
            "timestamp": datetime.now()
        }

        print(f"💾 Cached LLM response")

    def invalidate_memories(self, topic: str = None, patient_id: str = None):
        """Invalidate memory cache"""
        if topic:
            cache_key = self._generate_key("memories", topic, patient_id or "default")
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                print(f"🗑️  Invalidated cache for '{topic}'")
        else:
            # Clear all memory cache
            self.memory_cache.clear()
            print(f"🗑️  Cleared all memory cache")

    def invalidate_llm_responses(self):
        """Clear all LLM response cache"""
        self.llm_response_cache.clear()
        print(f"🗑️  Cleared all LLM cache")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        memory_count = len(self.memory_cache)
        llm_count = len(self.llm_response_cache)

        # Count expired entries
        memory_expired = sum(
            1 for entry in self.memory_cache.values()
            if self._is_expired(entry["timestamp"])
        )
        llm_expired = sum(
            1 for entry in self.llm_response_cache.values()
            if self._is_expired(entry["timestamp"])
        )

        return {
            "memory_cache": {
                "total": memory_count,
                "active": memory_count - memory_expired,
                "expired": memory_expired
            },
            "llm_cache": {
                "total": llm_count,
                "active": llm_count - llm_expired,
                "expired": llm_expired
            },
            "ttl_minutes": self.ttl_minutes
        }

    def cleanup_expired(self):
        """Remove expired cache entries"""
        # Clean memory cache
        expired_memory_keys = [
            key for key, entry in self.memory_cache.items()
            if self._is_expired(entry["timestamp"])
        ]
        for key in expired_memory_keys:
            del self.memory_cache[key]

        # Clean LLM cache
        expired_llm_keys = [
            key for key, entry in self.llm_response_cache.items()
            if self._is_expired(entry["timestamp"])
        ]
        for key in expired_llm_keys:
            del self.llm_response_cache[key]

        total_cleaned = len(expired_memory_keys) + len(expired_llm_keys)
        if total_cleaned > 0:
            print(f"🧹 Cleaned {total_cleaned} expired cache entries")


# Global cache manager instance
cache_manager = CacheManager(ttl_minutes=30)
