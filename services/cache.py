import time

class Cache:
    def __init__(self, ttl):
        self.ttl = ttl
        self.cache = {}

    def set(self, key, value):
        self.cache[key] = {'value': value, 'time': time.time()}

    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['time'] < self.ttl:
                return entry['value']
            else:
                del self.cache[key]
        return None
    
kc_user_cache = Cache(60*10) # 10 minute cache