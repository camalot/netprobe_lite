import asyncio
import signal
from concurrent.futures import ProcessPoolExecutor

# from bot.lib.colors import Colors
from dotenv import find_dotenv, load_dotenv
from helpers.logging import setup_logging
from netprobe import Netprobe
from netprobe_speedtest import NetprobeSpeedTest
from presentation import NetprobePresenation
load_dotenv(find_dotenv())

logger = setup_logging()


def sighandler(signum, frame):
    logger.warn('<SIGTERM received>')
    exit(0)


def presentation():
    try:
        presentation = NetprobePresenation()
        logger.debug('Starting presentation')
        presentation.run()
    except KeyboardInterrupt:
        logger.warn('<KeyboardInterrupt received>')
        exit(0)


def speedtest():
    try:
        speedtest = NetprobeSpeedTest()
        logger.debug('Starting speedtest')
        speedtest.run()
    except KeyboardInterrupt:
        logger.warn('<KeyboardInterrupt received>')
        exit(0)


def probe():
    try:
        probe = Netprobe()
        logger.debug('Starting probe')
        probe.run()
    except KeyboardInterrupt:
        logger.warn('<KeyboardInterrupt received>')
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
