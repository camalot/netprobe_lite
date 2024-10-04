from config.FileDataStoreConfiguration import FileDataStoreConfiguration
from config.HttpDataStoreConfiguration import HttpDataStoreConfiguration
from config.MongoDBDataStoreConfiguration import MongoDBDataStoreConfiguration
from config.MqttDataStoreConfiguration import MqttDataStoreConfiguration
from config.RedisDataStoreConfiguration import RedisDataStoreConfiguration
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class DataStoreConfiguration:
    def __init__(self, base: dict = {}):

        probe_type = EnvVars.DATASTORE_PROBE_TYPE.string(
            YamlVars.DATASTORE_PROBE_TYPE.string(base, ConfigurationDefaults.DATASTORE_PROBE_TYPE)
        ).upper()
        probe_topic = EnvVars.DATASTORE_PROBE_TOPIC.string(
            YamlVars.DATASTORE_PROBE_TOPIC.string(base, ConfigurationDefaults.DATASTORE_PROBE_TOPIC)
        )
        speed_type = EnvVars.DATASTORE_SPEEDTEST_TYPE.string(
            YamlVars.DATASTORE_SPEEDTEST_TYPE.string(base, ConfigurationDefaults.DATASTORE_SPEEDTEST_TYPE)
        ).upper()
        speed_topic = EnvVars.DATASTORE_SPEEDTEST_TOPIC.string(
            YamlVars.DATASTORE_SPEEDTEST_TOPIC.string(base, ConfigurationDefaults.DATASTORE_SPEEDTEST_TOPIC)
        )

        self.netprobe = {'type': DataStoreTypes.from_str(probe_type), 'topic': probe_topic}
        self.speedtest = {'type': DataStoreTypes.from_str(speed_type), 'topic': speed_topic}

        self.file = FileDataStoreConfiguration(base)
        self.redis = RedisDataStoreConfiguration(base)
        self.mongodb = MongoDBDataStoreConfiguration(base)
        self.http = HttpDataStoreConfiguration(base)
        self.mqtt = MqttDataStoreConfiguration(base, netprobe=self.netprobe, speedtest=self.speedtest)

    def merge(self, config: dict):
        self.__dict__.update(config)
