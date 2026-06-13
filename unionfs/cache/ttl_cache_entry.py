"""The TTL cache entry module."""

import time

from typing import Optional


class TTLCacheEntry[T]:
    def __init__(self, ttl: float = 2.0, initial_value: Optional[T] = None):
        self.__ttl = ttl
        self.__time = 0.0
        self.__value: Optional[T] = None

        if not initial_value is None:
            self.set_value_if_dead(initial_value)

    @property
    def ttl(self) -> float:
        return self.__ttl

    @property
    def value(self) -> float:
        return self.__value

    @ttl.setter
    def ttl(self, value: float) -> float:
        if value < 0:
            raise ValueError("TTL value cannot be negative.")

        self.__ttl = value

    def get_value_if_alive(self) -> Optional[T]:
        if self.__value is None:
            raise ValueError("No value has been set.")

        if time.monotonic() - self.__time <= self.__ttl:
            return self.__value

        return None

    def set_value_if_dead(self, value: T) -> bool:
        now = time.monotonic()

        is_dead = now - self.__time > self.__ttl
        if is_dead:
            self.__value = value
            self.__time = now

        return is_dead

    def get_then_set_if_needed(self, callback, *args, **kwargs) -> T:
        now = time.monotonic()

        # print(now - self.__time > self.__ttl, self.__value)
        if now - self.__time > self.__ttl or self.__value is None:
            self.__value = callback(*args, **kwargs)
            self.__time = now

        return self.__value
