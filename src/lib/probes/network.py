import json
import time
import traceback

from config import Configuration
from lib.collectors.networkcollector import NetworkCollector
from lib.datastores.factory import DatastoreFactory
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.probes.baseprobe import BaseProbe
from lib.probes.baseprobe import BaseProbeConfiguration


class NetworkProbe(BaseProbe):
    def __init__(self):
        self.app_config = Configuration()
        probe_count = self.app_config.probe.count
        sites = self.app_config.probe.sites
        dns_test_site = self.app_config.probe.dns_test_site
        nameservers = self.app_config.probe.nameservers
        self.device_id = self.app_config.probe.device_id

        super().__init__(
            BaseProbeConfiguration(
                enabled=self.app_config.probe.enabled,
                interval=self.app_config.probe.interval,
                topic=self.app_config.datastore.netprobe.get('topic', ConfigurationDefaults.DATASTORE_TOPIC_PROBE),
                datastore=self.app_config.datastore.netprobe.get('type', ConfigurationDefaults.DATASTORE_TYPE_PROBE),
            ),
            NetworkCollector(sites, probe_count, dns_test_site, nameservers),
        )

        self.logger.info(f"PROBE COUNT: {probe_count}")
        self.logger.info(f"SITES: {sites}")
        self.logger.info(f"DNS TEST SITE: {dns_test_site}")
        self.logger.info(f"DEVICE ID: {self.device_id}")

        # Logging each nameserver
        self.logger.info("NAMESERVERS:")
        for nameserver, ip, type in self.app_config.probe.nameservers:
            self.logger.info(f"NAMESERVER: {nameserver} IP: {ip} TYPE: {type}")

        # log weight information
        self.logger.info("NETWORK SCORE:")
        self.logger.info("WEIGHTS:")
        self.logger.info(f"JITTER WEIGHT: {self.app_config.presentation.weight_jitter * 100}%")
        self.logger.info(f"LOSS WEIGHT: {self.app_config.presentation.weight_loss * 100}%")
        self.logger.info(f"LATENCY WEIGHT: {self.app_config.presentation.weight_latency * 100}%")
        self.logger.info(
            f"EXTERNAL DNS LATENCY WEIGHT: {self.app_config.presentation.weight_external_dns_latency * 100}%"
        )
        self.logger.info(
            f"INTERNAL DNS LATENCY WEIGHT: {self.app_config.presentation.weight_internal_dns_latency * 100}%"
        )
        self.logger.info(f"SPEEDTEST DOWNLOAD WEIGHT: {self.app_config.presentation.weight_speedtest_download * 100}%")
        self.logger.info(f"SPEEDTEST UPLOAD WEIGHT: {self.app_config.presentation.weight_speedtest_upload * 100}%")

        total_weight = sum(
            [
                self.app_config.presentation.weight_jitter,
                self.app_config.presentation.weight_loss,
                self.app_config.presentation.weight_latency,
                self.app_config.presentation.weight_external_dns_latency,
                self.app_config.presentation.weight_internal_dns_latency,
                self.app_config.presentation.weight_speedtest_download,
                self.app_config.presentation.weight_speedtest_upload,
            ]
        )
        self.logger.info(f"TOTAL WEIGHT: {total_weight * 100}%")

        self.logger.info("THRESHOLDS:")
        self.logger.info(f"JITTER THRESHOLD: {self.app_config.presentation.threshold_jitter}ms")
        self.logger.info(f"LOSS THRESHOLD: {self.app_config.presentation.threshold_loss}%")
        self.logger.info(f"LATENCY THRESHOLD: {self.app_config.presentation.threshold_latency}ms")
        self.logger.info(
            f"EXTERNAL DNS LATENCY THRESHOLD: {self.app_config.presentation.threshold_external_dns_latency}ms"
        )
        self.logger.info(
            f"INTERNAL DNS LATENCY THRESHOLD: {self.app_config.presentation.threshold_internal_dns_latency}ms"
        )
        self.logger.info(f"SPEEDTEST DOWNLOAD THRESHOLD: {self.app_config.presentation.threshold_speedtest_download}Mbp/s")
        self.logger.info(f"SPEEDTEST UPLOAD THRESHOLD: {self.app_config.presentation.threshold_speedtest_upload}Mbp/s")

    # def run(self):
    #     while True:
    #         try:
    #             self.logger.debug("Testing network")
    #             stats = self.collector.collect()
    #         except Exception as e:
    #             self.logger.error("Error testing network")
    #             self.logger.error(e)
    #             self.logger.error(traceback.format_exc())
    #             continue
    #         # Connect to Datastore
    #         try:
    #             data_store = DatastoreFactory().create(self.config.datastore.netprobe.get('type', DataStoreTypes.NONE))
    #             cache_interval = self.interval + 15  # Set the cache TTL slightly longer than the probe interval
    #             topic = self.config.datastore.netprobe.get('topic', ConfigurationDefaults.DATASTORE_TOPIC_PROBE)
    #             data_store.write(topic, stats, cache_interval)
    #             self.logger.debug("Stats successfully written to data store")
    #         except Exception as e:
    #             self.logger.error("Could not connect to data store")
    #             self.logger.error(e)
    #             self.logger.error(traceback.format_exc())
    #         self.logger.debug(f'Probe sleeping for {self.interval} seconds')
    #         time.sleep(self.interval)
