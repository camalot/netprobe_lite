import typing
from helpers.logging import setup_logging
class DataStore:
    def __init__(self):
        self.logger = setup_logging()

    def read(self, key) -> typing.Any:
        return None

    def write(self, key, data, ttl) -> bool:
        return False
