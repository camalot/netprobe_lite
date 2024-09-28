# Netprobe Service
import json
import time
import traceback

from config import Configuration
from helpers.logging import setup_logging
from helpers.network import SpeedTestCollector
from lib.datastores.factory import DatastoreFactory


class NetProbeSpeedTest:
    def __init__(self):
        self.config = Configuration()
        self.enabled = self.config.speedtest.enabled
        self.interval = self.config.speedtest.interval
        self.collector = SpeedTestCollector()
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
                    data_store = DatastoreFactory().create(self.config.datastore.type)
                    # Save Data to Datastore
                    cache_interval = self.interval * 2  # Set the redis cache 2x longer than the speedtest interval
                    topic = self.config.datastore.topics.get('speedtest', 'speedtest')
                    data_store.write(topic, stats, cache_interval)
                    self.logger.info('Stats successfully written to Datastore for Speed Test')
                except Exception as e:
                    self.logger.error('Could not connect to Datastore')
                    self.logger.error(e)
                    self.logger.error(traceback.format_exc())

                self.logger.info(f'Speed Test sleeping for {self.interval} seconds')
                time.sleep(self.interval)
