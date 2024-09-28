# Redis helper
# Functions to help read and write from Redis
import json
import typing

import redis
from config import RedisDataStoreConfiguration
from lib.datastores.datastore import DataStore


class RedisDataStore(DataStore):
    def __init__(self):
        super().__init__()
        self.config = RedisDataStoreConfiguration()
        # Load global variables
        self.host = self.config.host
        self.port = self.config.port
        # this isn't even used. It's just set to a value that is never used
        # need to identify in the redis configuration where this is used
        # when it should be used to auth to the redis server
        # default should be "". If it is set to a value, it should be used
        self.password = self.config.password
        self.db = self.config.db
        # Connect to Redis
        if self.password:
            self.r = redis.Redis(host=self.host, port=int(self.port), db=int(self.db), password=self.password)
        else:
            self.r = redis.Redis(host=self.host, port=int(self.port), db=int(self.db))
        self.logger.info(f"Initializing Redis Data Store with host {self.host} and port {self.port}")

    def read(self, key) -> typing.Any:  # Read data from Redis
        results = self.r.get(key)  # Get the latest results from Redis for a given key
        if results:
            data = json.loads(results)
        else:
            data = ""
        return data

    def write(self, key, data, ttl) -> bool:  # Write data to Redis
        self.logger.debug(f"Writing to Redis: {key} - {ttl}")
        write = self.r.set(key, json.dumps(data), ttl)  # Store data with a given TTL
        return True if write else False
