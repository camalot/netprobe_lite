import json
import time
import traceback

from config import NetprobeConifguration
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

        # Logging each nameserver
        for nameserver, ip, type in NetprobeConifguration.nameservers:
            self.logger.info(f"NAMESERVER: {nameserver} IP: {ip} TYPE: {type}")

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
