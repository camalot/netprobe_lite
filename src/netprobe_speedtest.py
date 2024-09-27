# Netprobe Service
import json
import time
import traceback

from config import SpeedTestConfiguration
from helpers.logging import setup_logging
from helpers.network import NetProbe_SpeedTest
from helpers.redis import RedisDataStore


class NetProbeSpeedTest:
    def __init__(self):
        speedtest_config = SpeedTestConfiguration()
        self.enabled = speedtest_config.enabled
        self.interval = speedtest_config.interval
        self.collector = NetProbe_SpeedTest()
        # Logging Config
        self.logger = setup_logging()

    def run(self):
        if self.enabled:
            self.logger.info('Speed Test Enabled')
            while True:
                try:
                    stats = self.collector.collect()
                except Exception as e:
                    self.logger.error('Error running Speed Test')
                    self.logger.error(e)
                    self.logger.error(traceback.format_exc())
                    time.sleep(self.interval)  # Pause before retrying
                    continue
                # Connect to Redis
                try:
                    cache = RedisDataStore()
                    # Save Data to Redis
                    cache_interval = self.interval * 2  # Set the redis cache 2x longer than the speedtest interval
                    cache.write('speedtest', json.dumps(stats), cache_interval)
                    self.logger.info('Stats successfully written to Redis for Speed Test')
                except Exception as e:
                    self.logger.error('Could not connect to Redis')
                    self.logger.error(e)
                    self.logger.error(traceback.format_exc())

                self.logger.info(f'Speed Test sleeping for {self.interval} seconds')
                time.sleep(self.interval)
