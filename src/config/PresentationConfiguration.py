from config.NetProbeConfiguration import NetProbeConfiguration
from config.SpeedTestConfiguration import SpeedTestConfiguration
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class PresentationConfiguration:
    def __init__(
        self,
        base: dict = {},
        probe: NetProbeConfiguration = None,  # type: ignore
        speedtest: SpeedTestConfiguration = None,  # type: ignore
    ):
        if not probe:
            raise ValueError("Probe configuration is required")
        if not speedtest:
            raise ValueError("Speedtest configuration is required")

        self.speedtest = speedtest
        self.port = EnvVars.PRESENTATION_PORT.integer(
            YamlVars.PRESENTATION_PORT.integer(base, ConfigurationDefaults.PRESENTATION_PORT)
        )
        self.interface = EnvVars.PRESENTATION_INTERFACE.string(
            YamlVars.PRESENTATION_INTERFACE.string(base, ConfigurationDefaults.PRESENTATION_INTERFACE)
        )
        self.device_id = probe.device_id

        self.weight_loss = EnvVars.WEIGHT_LOSS.float(
            YamlVars.WEIGHT_LOSS.float(base, ConfigurationDefaults.WEIGHT_LOSS)
        )

        self.weight_latency = EnvVars.WEIGHT_LATENCY.float(
            YamlVars.WEIGHT_LATENCY.float(base, ConfigurationDefaults.WEIGHT_LATENCY)
        )

        self.weight_jitter = EnvVars.WEIGHT_JITTER.float(
            YamlVars.WEIGHT_JITTER.float(base, ConfigurationDefaults.WEIGHT_JITTER)
        )

        self.weight_internal_dns_latency = EnvVars.WEIGHT_INTERNAL_DNS_LATENCY.float(
            YamlVars.WEIGHT_INTERNAL_DNS_LATENCY.float(base, ConfigurationDefaults.WEIGHT_INTERNAL_DNS_LATENCY)
        )

        self.weight_external_dns_latency = EnvVars.WEIGHT_EXTERNAL_DNS_LATENCY.float(
            YamlVars.WEIGHT_EXTERNAL_DNS_LATENCY.float(base, ConfigurationDefaults.WEIGHT_EXTERNAL_DNS_LATENCY)
        )

        self.total_weight = sum(
            [
                self.weight_loss,
                self.weight_latency,
                self.weight_jitter,
                self.weight_external_dns_latency,
                self.weight_internal_dns_latency,
            ]
        )

        self.weight_speedtest_download = 0
        self.weight_speedtest_upload = 0

        if self.speedtest.enforce_or_enabled:
            self.weight_speedtest_download = self.speedtest.download_weight
            self.weight_speedtest_upload = self.speedtest.upload_weight
        else:
            t_wstd = self.speedtest.download_weight
            t_wstu = self.speedtest.upload_weight
            if self.total_weight < 1 and (self.total_weight + t_wstd + t_wstu) <= 1 and self.speedtest.weight_rebalance:
                # add this weight to the "loss" weight
                self.weight_loss += t_wstd + t_wstu

        # Recalculate total weight after rebalance
        self.total_weight = sum(
            [
                self.weight_loss,
                self.weight_latency,
                self.weight_jitter,
                self.weight_external_dns_latency,
                self.weight_internal_dns_latency,
                self.weight_speedtest_download,
                self.weight_speedtest_upload,
            ]
        )

        self.threshold_loss = EnvVars.THRESHOLD_LOSS.integer(
            YamlVars.THRESHOLD_LOSS.integer(base, ConfigurationDefaults.THRESHOLD_LOSS)
        )
        self.threshold_latency = EnvVars.THRESHOLD_LATENCY.integer(
            YamlVars.THRESHOLD_LATENCY.integer(base, ConfigurationDefaults.THRESHOLD_LATENCY)
        )
        self.threshold_jitter = EnvVars.THRESHOLD_JITTER.integer(
            YamlVars.THRESHOLD_JITTER.integer(base, ConfigurationDefaults.THRESHOLD_JITTER)
        )
        self.threshold_internal_dns_latency = EnvVars.THRESHOLD_INTERNAL_DNS_LATENCY.integer(
            YamlVars.THRESHOLD_INTERNAL_DNS_LATENCY.integer(base, ConfigurationDefaults.THRESHOLD_INTERNAL_DNS_LATENCY)
        )
        self.threshold_external_dns_latency = EnvVars.THRESHOLD_EXTERNAL_DNS_LATENCY.integer(
            YamlVars.THRESHOLD_EXTERNAL_DNS_LATENCY.integer(base, ConfigurationDefaults.THRESHOLD_EXTERNAL_DNS_LATENCY)
        )

        self.threshold_speedtest_download = 0
        self.threshold_speedtest_upload = 0

        if self.speedtest.enforce_or_enabled:
            self.threshold_speedtest_download = self.speedtest.threshold_download
            self.threshold_speedtest_upload = self.speedtest.threshold_upload
