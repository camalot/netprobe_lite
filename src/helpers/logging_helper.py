# Logging helper
# - Sets up logging config

import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(filename):
    # Logging config
    # Create logger
    logger = logging.getLogger("netprobe")
    logger.setLevel(level=logging.DEBUG)

    # Set formatter
    logFileFormatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Set the handler
    fileHandler = RotatingFileHandler(filename=filename, maxBytes=5_000_000, backupCount=3)

    stdoutHandler = logging.StreamHandler(sys.stdout)
    stderrHandler = logging.StreamHandler(sys.stderr)

    fileHandler.setFormatter(logFileFormatter)
    stdoutHandler.setFormatter(logFileFormatter)
    stderrHandler.setFormatter(logFileFormatter)

    fileHandler.setLevel(level=logging.DEBUG)
    stdoutHandler.setLevel(level=logging.DEBUG)
    stderrHandler.setLevel(level=logging.ERROR)

    # Set the logger
    logger.addHandler(fileHandler)
    logger.addHandler(stdoutHandler)
    logger.addHandler(stderrHandler)

    return logger
