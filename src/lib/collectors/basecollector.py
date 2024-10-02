import typing

from lib.logging import setup_logging


class BaseCollector:
    def __init__(self):
        self.logger = setup_logging(self.__class__.__name__)

    def collect(self) -> typing.Optional[dict]:
        return None
