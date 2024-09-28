import json
import os
import typing
from lib.datastores.datastore import DataStore
from config import FileDataStoreConfiguration

class FileDataStore(DataStore):
    def __init__(self):
        super().__init__()
        self.config = FileDataStoreConfiguration()
        data_path = self.config.path
        # if data_path is empty, set it to the current directory
        if not data_path:
            data_path = os.getcwd()
        # if data_path ends with a /, remove it
        if data_path.endswith("/"):
            data_path = data_path[:-1]
        self.data_path = data_path

        # check that the path exists. If it doesn't, create it
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        self.logger.info(f"Initializing File Data Store with path {data_path}")

    def __normalize_topic(self, topic) -> str:
        # check if topic is a relative path. If it is, make it an absolute path
        if not topic.startswith("/"):
            topic = f"{self.data_path}/{topic}"
        return topic

    def read(self, topic) -> typing.Any:
        topic = self.__normalize_topic(topic)
        data = None
        try:
            self.logger.debug(f"Reading file {topic}")
            with open(topic, "r") as file:
                data = file.read()
        except FileNotFoundError:
            self.logger.warning(f"File {topic} not found")
            data = None
        return json.loads(data) if data else None

    def write(self, topic, data, ttl) -> bool:
        topic = self.__normalize_topic(topic)

        # remove the file from the topic and create the folder structure
        folder = os.path.dirname(topic)
        if not os.path.exists(folder):
            os.makedirs(folder)

        self.logger.debug(f"Writing to file {topic}")
        with open(topic, "w") as file:
            file.write(json.dumps(data))
        return True
