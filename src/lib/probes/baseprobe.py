import signal
import time
import traceback

from helpers.logging import setup_logging
from lib.datastores.factory import DatastoreFactory
from lib.probes.BaseProbeConfiguration import BaseProbeConfiguration
from lib.collectors.basecollector import BaseCollector

class BaseProbe:
    def __init__(self, configuration: BaseProbeConfiguration, collector: BaseCollector):
        self.logger = setup_logging(self.__class__.__name__)
        self.config = configuration
        self.enabled = self.config.enabled
        self.interval = self.config.interval
        self.collector = collector

        signal.signal(signal.SIGTERM, self.sighandler)
        self._exit_loop = False

        if self.collector is None:
            self.logger.error('No collector specified')
            raise ValueError('No collector specified')

    def sighandler(self, signum, frame):
        self.logger.warning(f'<SIGTERM received: {self.__class__.__name__}>')
        self._exit_loop = True

    def run(self):
        while not self._exit_loop:
            try:
                self.logger.debug(f"Running probe: {self.__class__.__name__}")
                stats = self.collector.collect()
            except Exception as e:
                self.logger.error(f"Error executing probe: {self.__class__.__name__}")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
                continue
            # Connect to Datastore
            try:
                data_store = DatastoreFactory().create(self.config.datastore)
                cache_interval = self.interval + 15  # Set the cache TTL slightly longer than the probe interval
                topic = self.config.topic
                data_store.write(topic, stats, cache_interval)
                self.logger.debug("Stats successfully written to data store")
            except Exception as e:
                self.logger.error("Could not connect to data store")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
            self.logger.debug(f'Probe sleeping for {self.interval} seconds')
            time.sleep(self.interval)
        self.logger.debug(f"Exiting probe: {self.__class__.__name__}")
