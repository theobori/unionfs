"""The TTL cache module."""

import threading

from typing import Dict, NoReturn, Optional

from unionfs.cache.ttl_cache_entry import TTLCacheEntry


class TTLCache[K, V]:
    def __init__(self, ttl: float = 2.0):
        if ttl < 0:
            raise ValueError("TTL value cannot be negative.")

        self.__ttl = ttl
        self.__entries: Dict[K, TTLCacheEntry[V]] = {}
        self.__lock = threading.Lock()

    def get_if_alive(self, key: K) -> Optional[V]:
        with self.__lock:
            entry = self.__entries.get(key)
            if entry is None:
                raise ValueError(f"The key '{key}' does not exist.")

            try:
                return entry.get_value_if_alive()
            except ValueError as e:
                raise e

        return None

    def set_if_dead(self, key: K, value: V, ttl: Optional[float] = None) -> bool:
        with self.__lock:
            entry = self.__entries.get(key)
            if entry is None:
                self.__entries[key] = TTLCacheEntry(
                    ttl=ttl or self.__ttl, initial_value=value
                )
                return True

            return self.__entries[key].set_value_if_dead(value)

    def get_and_set_if_needed(
        self, key: K, callback, *args, ttl: Optional[float] = None, **kwargs
    ) -> V:
        value: V
        with self.__lock:
            if key not in self.__entries:
                self.__entries[key] = TTLCacheEntry(ttl=ttl or self.__ttl)

            entry = self.__entries[key]
            value = entry.get_and_set_if_needed(callback, *args, **kwargs)

        return value

    def invalidate(self, key: K) -> NoReturn:
        with self.__lock:
            if key in self.__entries:
                del self.__entries[key]
