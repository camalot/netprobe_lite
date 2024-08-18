import json
import time
import traceback

from config import Config_Netprobe
from helpers.logging_helper import setup_logging
from helpers.network_helper import NetworkCollector
from helpers.redis_helper import RedisConnect


class Netprobe:
    def __init__(self):
        self.probe_interval = Config_Netprobe.probe_interval
        probe_count = Config_Netprobe.probe_count
        sites = Config_Netprobe.sites
        dns_test_site = Config_Netprobe.dns_test_site
        nameservers = Config_Netprobe.nameservers
        self.device_id = Config_Netprobe.device_id
        self.collector = NetworkCollector(sites, probe_count, dns_test_site, nameservers)

        # Logging Config
        self.logger = setup_logging()

        # Logging each nameserver
        for nameserver, ip, type in Config_Netprobe.nameservers:
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
            self.logger.info(f'Probe sleeping for {self.probe_interval} seconds')
            time.sleep(self.probe_interval)
