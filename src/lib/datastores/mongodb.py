import typing

from lib.datastores.datastore import DataStore
from config import MongoDBDataStoreConfiguration
from pymongo import MongoClient

class MongoDBDatastore(DataStore):
    def __init__(self):
        super().__init__()
        self.config = MongoDBDataStoreConfiguration()
        self.client = MongoClient(self.config.url)
        self.db = self.client[self.config.db]
        self.collection = self.db[self.config.collection]
        self.logger.debug(f"Initializing MongoDB Data Store with database {self.config.db}")

    def write(self, key, data, ttl) -> bool:
        try:
            result = self.collection.update_one({ "id": key }, { "$set": { "data": data, "ttl": ttl } }, upsert=True)
            return True if result else False
        except Exception as e:
            self.logger.error(f"Error writing to MongoDB: {e}")
            return False

    def read(self, key) -> typing.Any:
        result = self.collection.find_one({ "id": key })
        if result:
            return result["data"]
        else:
            return None
