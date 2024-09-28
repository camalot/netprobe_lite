import json
import time
import typing
from config import MqttDataStoreConfiguration
from lib.datastores.datastore import DataStore
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

class MqttDataStore(DataStore):
    def __init__(self):
        super().__init__()
        self.messages = {}

        self.config = MqttDataStoreConfiguration()
        self.logger.info(f"Initializing MQTT Data Store with broker {self.config.host}:{self.config.port}")
        self.client = self.create()
        self.client.loop_start()
        count = 0
        found = 0
        # Wait for all topics to be subscribed to and received or timeout after 3 seconds
        while count < 3:
            for topic in self.config.topics:
                if topic in self.messages:
                    found += 1
            if found == len(self.config.topics):
                break

            count += 1
            found = 0
            time.sleep(1)
        self.client.loop_stop()

    def create(self) -> mqtt.Client:
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect
        # client.tls_set()
        client.username_pw_set(self.config.username, self.config.password)
        client.connect(self.config.host, self.config.port, 60)
        return client

    def on_connect(self, client, userdata, flags, rc):
        for topic in self.config.topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        self.logger.debug(f"Message received on topic {msg.topic}")
        self.logger.debug(msg.payload)
        self.messages[msg.topic] = msg.payload

    def on_disconnect(self, client, userdata, rc):
        self.logger.debug(f"Disconnected with result code {rc}")
        pass

    def read(self, topic) -> typing.Any:
        if topic in self.messages:
            return json.loads(self.messages[topic])
        return None

    def write(self, topic, data, ttl) -> bool:
        try:
            self.logger.debug(f"Publishing to topic {topic}")
            if isinstance(data, dict):
                data = json.dumps(data)

            self.client.publish(topic, data, qos=1, retain=True)
            return True
        except Exception as e:
            self.logger.error(f"Error publishing to topic {topic}")
            self.logger.error(e)
            return False
