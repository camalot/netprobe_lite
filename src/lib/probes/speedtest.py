from config import Configuration
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.probes.baseprobe import BaseProbe
from lib.probes.baseprobe import BaseProbeConfiguration
from lib.collectors.speedtestcollector import SpeedTestCollector


class SpeedTestProbe(BaseProbe):
    def __init__(self):
        self.app_config = Configuration()
        probe_config = BaseProbeConfiguration(
            self.app_config.speedtest.enabled,
            self.app_config.speedtest.interval,
            self.app_config.datastore.speedtest.get('topic', ConfigurationDefaults.DATASTORE_TOPIC_SPEEDTEST),
            self.app_config.datastore.speedtest.get('type', ConfigurationDefaults.DATASTORE_TYPE_SPEEDTEST),
        )
        super().__init__(probe_config, SpeedTestCollector())

    def run(self) -> None:
        return super().run()
