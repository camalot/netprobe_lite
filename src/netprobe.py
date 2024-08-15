import json
import time
import traceback

from config import Config_Netprobe
from helpers.logging_helper import setup_logging
from helpers.network_helper import NetworkCollector
from helpers.redis_helper import RedisConnect


class Netprobe:
    def __init__(self):
        pass

    def run(self):
        # Global Variables
        probe_interval = Config_Netprobe.probe_interval
        probe_count = Config_Netprobe.probe_count
        sites = Config_Netprobe.sites
        dns_test_site = Config_Netprobe.dns_test_site
        nameservers = Config_Netprobe.nameservers
        device_id = Config_Netprobe.device_id
        collector = NetworkCollector(sites, probe_count, dns_test_site, nameservers)

        # Logging Config
        log_path = Config_Netprobe.log_path
        logger = setup_logging(f"{log_path}/netprobe.log")

        # Logging each nameserver
        for nameserver, ip, type in Config_Netprobe.nameservers:
            logger.info(f"NAMESERVER: {nameserver} IP: {ip} TYPE: {type}")

        while True:
            try:
                stats = collector.collect()
            except Exception as e:
                print("Error testing network")
                logger.error("Error testing network")
                logger.error(e)
                logger.error(traceback.format_exc())
                continue
            # Connect to Redis
            try:
                cache = RedisConnect()
                # Save Data to Redis
                cache_interval = probe_interval + 15  # Set the redis cache TTL slightly longer than the probe interval
                cache.redis_write(device_id, json.dumps(stats), cache_interval)
            except Exception as e:
                logger.error("Could not connect to Redis")
                logger.error(e)
                logger.error(traceback.format_exc())
            time.sleep(probe_interval)


if __name__ == '__main__':
    netprobe = Netprobe()
    netprobe.run()
