from enum import Enum

class SpeedTestCacheTypes(Enum):
    NONE = "NONE"
    FILE = "FILE"
    REDIS = "REDIS"
    MQTT = "MQTT"
    PROMETHEUS = "PROMETHEUS"
    # MONGODB = 5

    @staticmethod
    def from_str(label: str):
        try:
            return SpeedTestCacheTypes[label.upper()]
        except KeyError:
            return SpeedTestCacheTypes.NONE
