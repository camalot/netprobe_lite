import asyncio
import signal
from concurrent.futures import ProcessPoolExecutor

from config import ApplicationConfiguration
from dotenv import find_dotenv, load_dotenv
from lib.logging import setup_logging
from lib.presentations.prometheus import PrometheusPresentation
from lib.probes.network import NetworkProbe
from lib.probes.speedtest import SpeedTestProbe

load_dotenv(find_dotenv())


class Netprobe:
    def __init__(self):
        self.config = ApplicationConfiguration
        self.logger = setup_logging(config=self.config.logging)

    def sighandler(self, signum, frame):
        self.logger.warning('<SIGTERM received>')
        exit(0)

    def presentation(self):
        try:
            presentation = PrometheusPresentation()
            self.logger.debug('Starting presentation')
            presentation.run()
        except KeyboardInterrupt:
            self.logger.warning('<KeyboardInterrupt received>')
            exit(0)

    def speedtest(self):
        try:
            speedtest = SpeedTestProbe()
            self.logger.debug('Starting Speed Test')
            speedtest.run()
        except KeyboardInterrupt:
            self.logger.warning('<KeyboardInterrupt received>')
            exit(0)

    def probe(self):
        try:
            probe = NetworkProbe()
            self.logger.debug('Starting probe')
            probe.run()
        except KeyboardInterrupt:
            self.logger.warning('<KeyboardInterrupt received>')
            exit(0)


if __name__ == '__main__':
    netprobe = Netprobe()
    print('Starting main')
    try:
        loop = asyncio.new_event_loop()
        signal.signal(signal.SIGTERM, netprobe.sighandler)
        try:
            executor = ProcessPoolExecutor()

            loop.run_in_executor(executor, netprobe.presentation)
            loop.run_in_executor(executor, netprobe.speedtest)
            loop.run_in_executor(executor, netprobe.probe)

            loop.run_forever()
        except DeprecationWarning:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()
    except DeprecationWarning:
        pass
