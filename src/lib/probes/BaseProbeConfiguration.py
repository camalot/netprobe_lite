from lib.enums.DataStoreTypes import DataStoreTypes

class BaseProbeConfiguration:
    def __init__(self, enabled: bool, interval: int, topic: str, datastore: DataStoreTypes):
        self.enabled = enabled
        self.interval = interval
        self.topic = topic
        self.datastore = datastore
