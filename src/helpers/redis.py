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
        # this isn't even used. It's just set to a value that is never used
        # need to identify in the redis configuration where this is used
        # when it should be used to auth to the redis server
        # default should be "". If it is set to a value, it should be used
        self.password = RedisConfiguration.redis_password
        self.db = RedisConfiguration.redis_db

        # Connect to Redis
        if self.password:
            self.r = redis.Redis(host=self.host, port=int(self.port), db=int(self.db), password=self.password)
        else:
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
