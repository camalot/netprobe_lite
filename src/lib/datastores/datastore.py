import typing

from lib.logging import setup_logging


class DataStore:
    def __init__(self):
        self.logger = setup_logging(self.__class__.__name__)

    def read(self, topic: str) -> typing.Any:
        return None

    def write(self, topic: str, data: dict, ttl: int) -> bool:
        return False
