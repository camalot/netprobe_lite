# Redis helper
# Functions to help read and write from Redis
import json

import redis
from config import RedisConfiguration


class RedisConnect:
    def __init__(self):
        # Load global variables
        self.host = RedisConfiguration.redis_host
        self.port = RedisConfiguration.redis_port
        self.password = RedisConfiguration.redis_password
        self.db = RedisConfiguration.redis_db

        # Connect to Redis
        self.r = redis.Redis(host=self.host, port=int(self.port), db=int(self.db))

    def read(self, key):  # Read data from Redis
        results = self.r.get(key)  # Get the latest results from Redis for a given key
        if results:
            data = json.loads(results)
        else:
            data = ""
        return data

    def write(self, key, data, ttl):  # Write data to Redis
        write = self.r.set(key, json.dumps(data), ttl)  # Store data with a given TTL
        return write
