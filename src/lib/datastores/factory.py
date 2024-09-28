from enums.DataStoreTypes import DataStoreTypes
from helpers.logging import setup_logging

class DatastoreFactory:
    def __init__(self):
        pass

    def create(self, type: DataStoreTypes):
        logger = setup_logging()
        if type == DataStoreTypes.REDIS:
            logger.debug("Creating Redis Datastore")
            from lib.datastores.redis import RedisDataStore
            return RedisDataStore()
        elif type == DataStoreTypes.FILE:
            logger.debug("Creating File Datastore")
            from lib.datastores.file import FileDataStore
            return FileDataStore()
        elif type == DataStoreTypes.MQTT:
            logger.debug("Creating MQTT Datastore")
            from lib.datastores.mqtt import MqttDataStore
            return MqttDataStore()
        elif type == DataStoreTypes.MONGODB:
            logger.debug("Creating MongoDB Datastore")
            from lib.datastores.mongodb import MongoDBDatastore
            return MongoDBDatastore()
        else:
            raise Exception("DataStore type not supported")
