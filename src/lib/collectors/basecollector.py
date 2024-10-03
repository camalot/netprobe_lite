import typing

from config import ApplicationConfiguration
from lib.logging import setup_logging


class BaseCollector:
    def __init__(self):
        config = ApplicationConfiguration
        self.logger = setup_logging(self.__class__.__name__, config.logging)

    def collect(self) -> typing.Optional[dict]:
        return None
