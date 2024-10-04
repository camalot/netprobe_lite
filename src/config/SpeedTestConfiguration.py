from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class SpeedTestConfiguration:
    def __init__(self, base: dict = {}):
        self.enabled = EnvVars.SPEEDTEST_ENABLED.boolean(
            YamlVars.SPEEDTEST_ENABLED.boolean(base, ConfigurationDefaults.SPEEDTEST_ENABLED)
        )
        self.interval = EnvVars.SPEEDTEST_INTERVAL.integer(
            YamlVars.SPEEDTEST_INTERVAL.integer(base, ConfigurationDefaults.SPEEDTEST_INTERVAL)
        )
        self.weight_rebalance = EnvVars.SPEEDTEST_WEIGHT_REBALANCE.boolean(
            YamlVars.SPEEDTEST_WEIGHT_REBALANCE.boolean(base, ConfigurationDefaults.SPEEDTEST_WEIGHT_REBALANCE)
        )
        self.enforce_weight = EnvVars.SPEEDTEST_WEIGHT_ENFORCE.boolean(
            YamlVars.SPEEDTEST_WEIGHT_ENFORCE.boolean(base, ConfigurationDefaults.SPEEDTEST_WEIGHT_ENFORCE)
        )
        self.download_weight = EnvVars.WEIGHT_SPEEDTEST_DOWNLOAD.float(
            YamlVars.WEIGHT_SPEEDTEST_DOWNLOAD.float(base, ConfigurationDefaults.WEIGHT_SPEEDTEST_DOWNLOAD)
        )
        self.upload_weight = EnvVars.WEIGHT_SPEEDTEST_UPLOAD.float(
            YamlVars.WEIGHT_SPEEDTEST_UPLOAD.float(base, ConfigurationDefaults.WEIGHT_SPEEDTEST_UPLOAD)
        )
        self.threshold_download = EnvVars.THRESHOLD_SPEEDTEST_DOWNLOAD.float(
            YamlVars.THRESHOLD_SPEEDTEST_DOWNLOAD.float(base, ConfigurationDefaults.THRESHOLD_SPEEDTEST_DOWNLOAD)
        )
        self.threshold_upload = EnvVars.THRESHOLD_SPEEDTEST_UPLOAD.float(
            YamlVars.THRESHOLD_SPEEDTEST_UPLOAD.float(base, ConfigurationDefaults.THRESHOLD_SPEEDTEST_UPLOAD)
        )
        self.enforce_or_enabled = self.enforce_weight or self.enabled

    def merge(self, config: dict):
        self.__dict__.update(config)
