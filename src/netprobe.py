import json
import time
import traceback

from config import NetprobeConifguration, PresentationConfiguration
from helpers.logging import setup_logging
from helpers.network import NetworkCollector
from helpers.redis import RedisConnect


class Netprobe:
    def __init__(self):
        self.probe_interval = NetprobeConifguration.probe_interval
        probe_count = NetprobeConifguration.probe_count
        sites = NetprobeConifguration.sites
        dns_test_site = NetprobeConifguration.dns_test_site
        nameservers = NetprobeConifguration.nameservers
        self.device_id = NetprobeConifguration.device_id
        self.collector = NetworkCollector(sites, probe_count, dns_test_site, nameservers)

        # Logging Config
        self.logger = setup_logging()

        self.logger.info(f"PROBE INTERVAL: {self.probe_interval}")
        self.logger.info(f"PROBE COUNT: {probe_count}")
        self.logger.info(f"SITES: {sites}")
        self.logger.info(f"DNS TEST SITE: {dns_test_site}")
        self.logger.info(f"DEVICE ID: {self.device_id}")

        # Logging each nameserver
        self.logger.info("NAMESERVERS:")
        for nameserver, ip, type in NetprobeConifguration.nameservers:
            self.logger.info(f"NAMESERVER: {nameserver} IP: {ip} TYPE: {type}")

        # log weight information
        self.logger.info("NETWORK SCORE:")
        self.logger.info("WEIGHTS:")
        self.logger.info(f"JITTER WEIGHT: {PresentationConfiguration.weight_jitter * 100}%")
        self.logger.info(f"LOSS WEIGHT: {PresentationConfiguration.weight_loss * 100}%")
        self.logger.info(f"LATENCY WEIGHT: {PresentationConfiguration.weight_latency * 100}%")
        self.logger.info(f"EXTERNAL DNS LATENCY WEIGHT: {PresentationConfiguration.weight_external_dns_latency * 100}%")
        self.logger.info(f"INTERNAL DNS LATENCY WEIGHT: {PresentationConfiguration.weight_internal_dns_latency * 100}%")
        total_weight = sum(
            [
                PresentationConfiguration.weight_jitter,
                PresentationConfiguration.weight_loss,
                PresentationConfiguration.weight_latency,
                PresentationConfiguration.weight_external_dns_latency,
                PresentationConfiguration.weight_internal_dns_latency
            ]
        )
        self.logger.info(f"TOTAL WEIGHT: {total_weight * 100}%")

        self.logger.info("THRESHOLDS:")
        self.logger.info(f"JITTER THRESHOLD: {PresentationConfiguration.threshold_jitter}ms")
        self.logger.info(f"LOSS THRESHOLD: {PresentationConfiguration.threshold_loss}%")
        self.logger.info(f"LATENCY THRESHOLD: {PresentationConfiguration.threshold_latency}ms")
        self.logger.info(f"EXTERNAL DNS LATENCY THRESHOLD: {PresentationConfiguration.threshold_external_dns_latency}ms")
        self.logger.info(f"INTERNAL DNS LATENCY THRESHOLD: {PresentationConfiguration.threshold_internal_dns_latency}ms")

    def run(self):
        while True:
            try:
                stats = self.collector.collect()
            except Exception as e:
                self.logger.error("Error testing network")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
                continue
            # Connect to Redis
            try:
                cache = RedisConnect()
                # Save Data to Redis
                cache_interval = self.probe_interval + 15  # Set the redis cache TTL slightly longer than the probe interval
                cache.write(self.device_id, json.dumps(stats), cache_interval)
            except Exception as e:
                self.logger.error("Could not connect to Redis")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
            self.logger.debug(f'Probe sleeping for {self.probe_interval} seconds')
            time.sleep(self.probe_interval)
