import asyncio
import signal
from concurrent.futures import ProcessPoolExecutor

# from bot.lib.colors import Colors
from dotenv import find_dotenv, load_dotenv
from helpers.logging import setup_logging
from netprobe import NetProbe
from netprobe_speedtest import NetProbeSpeedTest
from presentation import NetProbePresentation
load_dotenv(find_dotenv())

logger = setup_logging()


def sighandler(signum, frame):
    logger.warning('<SIGTERM received>')
    exit(0)


def presentation():
    try:
        presentation = NetProbePresentation()
        logger.debug('Starting presentation')
        presentation.run()
    except KeyboardInterrupt:
        logger.warning('<KeyboardInterrupt received>')
        exit(0)


def speedtest():
    try:
        speedtest = NetProbeSpeedTest()
        logger.debug('Starting Speed Test')
        speedtest.run()
    except KeyboardInterrupt:
        logger.warning('<KeyboardInterrupt received>')
        exit(0)


def probe():
    try:
        probe = NetProbe()
        logger.debug('Starting probe')
        probe.run()
    except KeyboardInterrupt:
        logger.warning('<KeyboardInterrupt received>')
        exit(0)


if __name__ == '__main__':
    print('Starting main')
    try:
        loop = asyncio.new_event_loop()
        signal.signal(signal.SIGTERM, sighandler)
        try:
            executor = ProcessPoolExecutor()

            loop.run_in_executor(executor, presentation)
            loop.run_in_executor(executor, speedtest)
            loop.run_in_executor(executor, probe)

            loop.run_forever()
        except DeprecationWarning:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()
    except DeprecationWarning:
        pass
