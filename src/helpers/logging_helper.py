# Logging helper
# - Sets up logging config

import logging
import sys
from logging.handlers import RotatingFileHandler

class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, validate=True):
        super().__init__(fmt=fmt, datefmt=datefmt, validate=validate)
        self.reset = "\033[0m"
        self.log_colors = {
            logging.CRITICAL: "\033[91m",
            logging.ERROR: "\033[91m",
            logging.WARNING: "\033[93m",
            logging.INFO: "\033[92m",
            logging.DEBUG: "\033[94m",
        }

    def format(self, record):
        log_color = self.log_colors.get(record.levelno, self.reset)
        record.msg = f"{log_color}{record.msg}{self.reset}"
        return super().format(record)


def setup_logging(filename):
    # Logging config
    # Create logger
    logger = logging.getLogger("netprobe")
    logger.setLevel(level=logging.DEBUG)

    # Set formatter
    logFileFormatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    logColorFormatter = ColorFormatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


    # Set the handler
    fileHandler = RotatingFileHandler(filename=filename, maxBytes=5_000_000, backupCount=3)

    stdoutHandler = logging.StreamHandler(sys.stdout)
    stderrHandler = logging.StreamHandler(sys.stderr)

    fileHandler.setFormatter(logFileFormatter)
    stdoutHandler.setFormatter(logColorFormatter)
    stderrHandler.setFormatter(logColorFormatter)

    fileHandler.setLevel(level=logging.INFO)
    stdoutHandler.setLevel(level=logging.DEBUG)
    stderrHandler.setLevel(level=logging.ERROR)

    # Set the logger
    logger.addHandler(fileHandler)
    logger.addHandler(stdoutHandler)
    logger.addHandler(stderrHandler)

    return logger
