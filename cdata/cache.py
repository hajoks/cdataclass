import collections
from functools import wraps


class _LRUCache:
    def __init__(self, capacity: int):
        self.d = collections.OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.d:
            return -1

        value = self.d.pop(key)
        self.d[key] = value
        return value

    def put(self, key: int, value: int) -> None:
        if key in self.d:
            self.d.pop(key)
        self.d[key] = value
        if len(self.d) > self.capacity:
            self.d.popitem(last=False)


def simple_lru_cache(*, maxsize: int):
    def _cache(f):
        c = _LRUCache(maxsize)

        @wraps(f)
        def _wrap(*args):
            if c.get(args) == -1:
                c.put(args, f(*args))
            return c.get(args)

        return _wrap

    return _cache


try:
    from functools import lru_cache

    cache = lru_cache
except ImportError:
    cache = simple_lru_cache
