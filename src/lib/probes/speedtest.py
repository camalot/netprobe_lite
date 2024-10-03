from config import ApplicationConfiguration
from lib.collectors.speedtestcollector import SpeedTestCollector
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.probes.baseprobe import BaseProbe, BaseProbeConfiguration


class SpeedTestProbe(BaseProbe):
    def __init__(self):
        self.app_config = ApplicationConfiguration
        probe_config = BaseProbeConfiguration(
            self.app_config.speedtest.enabled,
            self.app_config.speedtest.interval,
            self.app_config.datastore.speedtest.get('topic', ConfigurationDefaults.DATASTORE_SPEEDTEST_TOPIC),
            self.app_config.datastore.speedtest.get('type', ConfigurationDefaults.DATASTORE_SPEEDTEST_TYPE),
        )
        super().__init__(probe_config, SpeedTestCollector())

    def run(self) -> None:
        return super().run()
