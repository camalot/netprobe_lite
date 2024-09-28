import json
import time
import traceback

from config import Configuration
from enums.DataStoreTypes import DataStoreTypes
from helpers.logging import setup_logging
from helpers.network import NetworkCollector

from lib.datastores.factory import DatastoreFactory


class NetProbe:
    def __init__(self):
        self.config = Configuration()
        presentation_config = self.config.presentation
        probe_config = self.config.probe
        self.probe_interval = probe_config.interval
        probe_count = probe_config.count
        sites = probe_config.sites
        dns_test_site = probe_config.dns_test_site
        nameservers = probe_config.nameservers
        self.device_id = probe_config.device_id
        self.collector = NetworkCollector(sites, probe_count, dns_test_site, nameservers)

        # Logging Config
        self.logger = setup_logging()

        self.logger.info(f"PROBE DATASTORE TYPE: {self.config.datastore.netprobe.get('type', DataStoreTypes.FILE)}")
        self.logger.info(f"PROBE DATASTORE TOPIC: {self.config.datastore.netprobe.get('topic', 'netprobe/probe')}")

        self.logger.info(f"PROBE INTERVAL: {self.probe_interval}s")
        self.logger.info(f"PROBE COUNT: {probe_count}")
        self.logger.info(f"SITES: {sites}")
        self.logger.info(f"DNS TEST SITE: {dns_test_site}")
        self.logger.info(f"DEVICE ID: {self.device_id}")

        # Logging each nameserver
        self.logger.info("NAMESERVERS:")
        for nameserver, ip, type in probe_config.nameservers:
            self.logger.info(f"NAMESERVER: {nameserver} IP: {ip} TYPE: {type}")

        # log weight information
        self.logger.info("NETWORK SCORE:")
        self.logger.info("WEIGHTS:")
        self.logger.info(f"JITTER WEIGHT: {presentation_config.weight_jitter * 100}%")
        self.logger.info(f"LOSS WEIGHT: {presentation_config.weight_loss * 100}%")
        self.logger.info(f"LATENCY WEIGHT: {presentation_config.weight_latency * 100}%")
        self.logger.info(f"EXTERNAL DNS LATENCY WEIGHT: {presentation_config.weight_external_dns_latency * 100}%")
        self.logger.info(f"INTERNAL DNS LATENCY WEIGHT: {presentation_config.weight_internal_dns_latency * 100}%")
        total_weight = sum(
            [
                presentation_config.weight_jitter,
                presentation_config.weight_loss,
                presentation_config.weight_latency,
                presentation_config.weight_external_dns_latency,
                presentation_config.weight_internal_dns_latency
            ]
        )
        self.logger.info(f"TOTAL WEIGHT: {total_weight * 100}%")

        self.logger.info("THRESHOLDS:")
        self.logger.info(f"JITTER THRESHOLD: {presentation_config.threshold_jitter}ms")
        self.logger.info(f"LOSS THRESHOLD: {presentation_config.threshold_loss}%")
        self.logger.info(f"LATENCY THRESHOLD: {presentation_config.threshold_latency}ms")
        self.logger.info(f"EXTERNAL DNS LATENCY THRESHOLD: {presentation_config.threshold_external_dns_latency}ms")
        self.logger.info(f"INTERNAL DNS LATENCY THRESHOLD: {presentation_config.threshold_internal_dns_latency}ms")

    def run(self):
        while True:
            try:
                self.logger.debug("Testing network")
                stats = self.collector.collect()
            except Exception as e:
                self.logger.error("Error testing network")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
                continue
            # Connect to Datastore
            try:
                data_store = DatastoreFactory().create(self.config.datastore.netprobe.get('type', DataStoreTypes.FILE))
                cache_interval = self.probe_interval + 15  # Set the cache TTL slightly longer than the probe interval
                topic = self.config.datastore.netprobe.get('topic', 'netprobe/probe')
                data_store.write(topic, stats, cache_interval)
                self.logger.debug("Stats successfully written to data store")
            except Exception as e:
                self.logger.error("Could not connect to data store")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
            self.logger.debug(f'Probe sleeping for {self.probe_interval} seconds')
            time.sleep(self.probe_interval)
