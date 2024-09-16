import redis


class RedisTool:
    def __init__(self, host='localhost', port=6379, db=5):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

    def delete(self, key):
        self.redis.delete(key)

    def keys(self, pattern='*'):
        return self.redis.keys(pattern)
