from config import Configuration
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.probes.baseprobe import BaseProbe
from lib.probes.baseprobe import BaseProbeConfiguration
from lib.collectors.speedtestcollector import SpeedTestCollector
from lib.enums.DataStoreTypes import DataStoreTypes


class SpeedTestProbe(BaseProbe):
    def __init__(self):
        self.config = Configuration()
        probe_config = BaseProbeConfiguration(
            self.config.speedtest.enabled,
            self.config.speedtest.interval,
            self.config.datastore.speedtest.get('topic', ConfigurationDefaults.DATASTORE_TOPIC_SPEEDTEST),
            self.config.datastore.speedtest.get('type', DataStoreTypes.NONE)
        )
        super().__init__(probe_config, SpeedTestCollector())

    def run(self) -> None:
        return super().run()
