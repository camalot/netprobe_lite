import logging
import sys
import typing

from config import LoggingConfiguration
from lib.logging.ColorFormatter import ColorFormatter


def setup_logging(name: typing.Optional[str] = None, config: LoggingConfiguration = None) -> logging.Logger:  # type: ignore
    logger = logging.getLogger("netprobe" if name is None else name)

    if config is None:
        raise ValueError("Logging configuration is required")

    logger.setLevel(level=config.level)

    # Set formatter
    logColorFormatter = ColorFormatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    stdoutHandler = logging.StreamHandler(sys.stdout)
    stdoutHandler.name = "stdout"
    stdoutHandler.setFormatter(logColorFormatter)
    stdoutHandler.setLevel(level=config.level)

    active_handlers = [stdoutHandler]

    if not logger.handlers:
        # check if stdoutHandler is already added
        # check if a handler with the name is already added
        for handler in active_handlers:
            if not logger.hasHandlers():
                logger.addHandler(handler)
            elif not any([handler.name == h.name for h in logger.handlers]):
                logger.addHandler(handler)

    return logger
