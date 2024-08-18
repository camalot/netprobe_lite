# Netprobe Service
import json
import time
import traceback

from config import Config_Netprobe
from helpers.logging_helper import setup_logging
from helpers.network_helper import Netprobe_Speedtest
from helpers.redis_helper import RedisConnect


class NetprobeSpeedTest:
    def __init__(self):
        self.speedtest_enabled = Config_Netprobe.speedtest_enabled
        self.speedtest_interval = Config_Netprobe.speedtest_interval
        self.collector = Netprobe_Speedtest()
        # Logging Config
        self.logger = setup_logging()

    def run(self):
        if self.speedtest_enabled:
            self.logger.info('Speedtest enabled')
            while True:
                try:
                    stats = self.collector.collect()
                except Exception as e:
                    self.logger.error('Error running speedtest')
                    self.logger.error(e)
                    self.logger.error(traceback.format_exc())
                    time.sleep(self.speedtest_interval)  # Pause before retrying
                    continue
                # Connect to Redis
                try:
                    cache = RedisConnect()
                    # Save Data to Redis
                    cache_interval = self.speedtest_interval * 2  # Set the redis cache 2x longer than the speedtest interval
                    cache.write('speedtest', json.dumps(stats), cache_interval)
                    self.logger.info('Stats successfully written to Redis for Speed Test')
                except Exception as e:
                    self.logger.error('Could not connect to Redis')
                    self.logger.error(e)
                    self.logger.error(traceback.format_exc())

                self.logger.info(f'Speedtest sleeping for {self.speedtest_interval} seconds')
                time.sleep(self.speedtest_interval)
