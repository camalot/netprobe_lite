import logging
import os
import re
import typing

from enums.DataStoreTypes import DataStoreTypes
import yaml
from dotenv import find_dotenv, load_dotenv

# Load configs from env
try:  # Try to load env vars from file, if fails pass
    load_dotenv(find_dotenv())
except:  # noqa: E722
    pass


@staticmethod
def unquote(value: typing.Optional[str]) -> str:
    """This function removes quotes from a string if they exist. It is used to clean up environment variables.
    as they can be read with quotes if they are set in a docker-compose file or a .env file."""
    if not value:
        return ''

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value

class Configuration:
    def __init__(self, file_path: typing.Optional[str] = '/app/config/netprobe.yaml'):

        self.probe = NetProbeConfiguration()
        self.redis = RedisDataStoreConfiguration()
        self.presentation = PresentationConfiguration()
        self.logging = LoggingConfiguration()
        self.mqtt = MqttDataStoreConfiguration()
        self.mongodb = MongoDBDataStoreConfiguration()
        self.speedtest = SpeedTestConfiguration()
        self.datastore = DataStoreConfiguration()

        # if file_path exists and is not none, load the file
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.__dict__.update(yaml.safe_load(file))


class MqttDataStoreConfiguration:
    def __init__(self):
        self.host = unquote(os.getenv('NP_MQTT_HOST', 'localhost'))
        self.port = int(unquote(os.getenv('NP_MQTT_PORT', '1883')))
        self.username = unquote(os.getenv('NP_MQTT_USERNAME', None))
        self.password = unquote(os.getenv('NP_MQTT_PASSWORD', None))
        # split and remove any whitespace from the topics
        # self.topics = [topic.strip() for topic in unquote(os.getenv('MQTT_TOPICS', 'netprobe,speedtest')).split(',')]
        self.topics = [
            unquote(os.getenv('NP_DATASTORE_TOPIC_SPEEDTEST', 'netprobe')),
            unquote(os.getenv('NP_DATASTORE_TOPIC_SPEEDTEST', 'speedtest')),
        ]

    def merge(self, config: dict):
        self.__dict__.update(config)

class MongoDBDataStoreConfiguration:
    def __init__(self):
        self.url = unquote(os.getenv('NP_MONGODB_URL', 'mongodb://localhost:27017?authSource=admin'))
        self.db = unquote(os.getenv('NP_MONGODB_DB', 'netprobe'))
        self.collection = unquote(os.getenv('NP_MONGODB_COLLECTION', 'netprobe'))

    def merge(self, config: dict):
        self.__dict__.update(config)

class LoggingConfiguration:
    def __init__(self):
        log_level = unquote(os.getenv('NP_LOG_LEVEL', 'INFO')).upper()
        self.level = getattr(logging, log_level, logging.INFO)
        self.format = unquote(os.getenv('NP_LOG_FORMAT', '%(asctime)s %(levelname)s %(message)s'))

    def merge(self, config: dict):
        self.__dict__.update(config)


class SpeedTestConfiguration:
    def __init__(self):
        self.enabled = bool(unquote(os.getenv("NP_SPEEDTEST_ENABLED", 'FALSE')).lower() in ('true', '1', 't', 'y', 'yes'))
        self.interval = int(unquote(os.getenv('NP_SPEEDTEST_INTERVAL', '937')))
        self.weight_rebalance = unquote(os.getenv('NP_WEIGHT_SPEEDTEST_REBALANCE', 'TRUE')).lower() in ('true', '1', 't', 'y', 'yes')
        self.enforce_weight = unquote(os.getenv('NP_WEIGHT_SPEEDTEST_ENFORCE', 'FALSE')).lower() in ('true', '1', 't', 'y', 'yes')
        self.download_weight = float(unquote(os.getenv('NP_WEIGHT_SPEEDTEST_DOWNLOAD', '.5')))
        self.upload_weight = float(unquote(os.getenv('NP_WEIGHT_SPEEDTEST_UPLOAD', '.5')))
        self.threshold_download = int(unquote(os.getenv('NP_THRESHOLD_SPEEDTEST_DOWNLOAD', '200')))
        self.threshold_upload = int(unquote(os.getenv('NP_THRESHOLD_SPEEDTEST_UPLOAD', '200')))
        self.enforce_or_enabled = self.enforce_weight or self.enabled


    def merge(self, config: dict):
        self.__dict__.update(config)

class DataStoreConfiguration:
    def __init__(self):
        self.type = DataStoreTypes.from_str(unquote(os.getenv('NP_DATASTORE_TYPE', 'FILE')).upper())
        self.topics = {
            'netprobe': unquote(os.getenv('NP_DATASTORE_TOPIC_NETPROBE', 'netprobe')),
            'speedtest': unquote(os.getenv('NP_DATASTORE_TOPIC_SPEEDTEST', 'speedtest')),
        }

    def merge(self, config: dict):
        self.__dict__.update(config)

class NetProbeConfiguration:
    def __init__(self):
        self.interval = int(unquote(os.getenv('NP_PROBE_INTERVAL', '30')))
        self.count = int(unquote(os.getenv('NP_PROBE_COUNT', '50')))
        self.sites = unquote(os.getenv('NP_SITES', 'google.com,facebook.com,twitter.com,youtube.com')).split(',')
        self.dns_test_site = unquote(os.getenv('NP_DNS_TEST_SITE', 'google.com'))
        self.device_id = unquote(os.getenv('NP_DEVICE_ID', 'netprobe')).replace(' ', '_').replace('.', '_').replace('-', '_').lower()

        # get all environment variables that match the pattern DNS_NAMESERVER_\d{1,}
        # and create a list of tuples with the nameserver and the IP
        self.nameservers = []
        match_pattern_external = r'^NP_DNS_NAMESERVER_(\d{1,})$'
        match_pattern_local = r'^NP_LOCAL_DNS_NAMESERVER_(\d{1,})$'
        for key, value in os.environ.items():
            m = re.match(match_pattern_external, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if m:
                # get the nameserver number from the match
                index = m.group(1)
                label = value if value else f"EXTERNAL DNS NAMESERVER {index}"
                ip = unquote(os.getenv(f'NP_DNS_NAMESERVER_{index}_IP', None))
                if ip and label:
                    self.nameservers.append((unquote(label), ip, 'external'))
            m = re.match(match_pattern_local, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if m:
                index = m.group(1)
                label = value if value else f"INTERNAL DNS NAMESERVER {index}"
                ip = unquote(os.getenv(f'NP_LOCAL_DNS_NAMESERVER_{index}_IP', None))
                if ip and label:
                    self.nameservers.append((unquote(label), ip, 'internal'))

        # singular local dns
        NP_LOCAL_DNS = unquote(os.getenv('NP_LOCAL_DNS', None))
        NP_LOCAL_DNS_IP = unquote(os.getenv('NP_LOCAL_DNS_IP', None))

        if NP_LOCAL_DNS and NP_LOCAL_DNS_IP:
            self.nameservers.append((NP_LOCAL_DNS, NP_LOCAL_DNS_IP, "internal"))


class RedisDataStoreConfiguration:
    def __init__(self):
        self.host = unquote(os.getenv('NP_REDIS_URL', os.getenv('NP_REDIS_HOST', 'localhost')))
        self.port = unquote(os.getenv('NP_REDIS_PORT', '6379'))
        self.password = unquote(os.getenv('NP_REDIS_PASSWORD', ''))
        self.db = unquote(os.getenv('NP_REDIS_DB', '0'))
        self.enabled = bool(unquote(os.getenv('NP_REDIS_ENABLED', 'TRUE')).lower() in ('true', '1', 't', 'y', 'yes'))

    def merge(self, config: dict):
        self.__dict__.update(config)

class FileDataStoreConfiguration:
    def __init__(self):
        self.path = unquote(os.getenv('NP_FILE_DATASTORE_PATH', '/data'))

class PresentationConfiguration:
    def __init__(self):
        self.speedtest = SpeedTestConfiguration()
        self.port = int(unquote(os.getenv('NP_PRESENTATION_PORT', '5000')))
        self.interface = unquote(os.getenv('NP_PRESENTATION_INTERFACE', '0.0.0.0'))
        self.device_id = unquote(os.getenv('NP_DEVICE_ID', 'netprobe'))

        self.local_dns_name = unquote(os.getenv('NP_LOCAL_DNS', None))

        self.weight_loss = float(unquote(os.getenv('NP_WEIGHT_LOSS', '.6')))
        self.weight_latency = float(unquote(os.getenv('NP_WEIGHT_LATENCY', '.15')))
        self.weight_jitter = float(unquote(os.getenv('NP_WEIGHT_JITTER', '.2')))
        self.weight_internal_dns_latency = float(unquote(os.getenv('NP_WEIGHT_INTERNAL_DNS_LATENCY', '.025')))
        self.weight_external_dns_latency = float(unquote(os.getenv('NP_WEIGHT_EXTERNAL_DNS_LATENCY', '.025')))

        self.total_weight = sum(
            [
                self.weight_loss,
                self.weight_latency,
                self.weight_jitter,
                self.weight_external_dns_latency,
                self.weight_internal_dns_latency,
            ]
        )

        self.weight_speedtest_download = 0
        self.weight_speedtest_upload = 0

        if self.speedtest.enforce_or_enabled:
            self.weight_speedtest_download = self.speedtest.download_weight # float(os.getenv('NP_WEIGHT_SPEEDTEST_DOWNLOAD', '.5'))
            self.weight_speedtest_upload = self.speedtest.upload_weight # float(os.getenv('NP_WEIGHT_SPEEDTEST_UPLOAD', '.5'))
        else:
            t_wstd = self.speedtest.download_weight #float(os.getenv('NP_WEIGHT_SPEEDTEST_DOWNLOAD', '.5'))
            t_wstu = self.speedtest.upload_weight # float(os.getenv('NP_WEIGHT_SPEEDTEST_UPLOAD', '.5'))
            if self.total_weight < 1 and (self.total_weight + t_wstd + t_wstu) <= 1 and self.speedtest.weight_rebalance:
                # add this weight to the "loss" weight
                self.weight_loss += t_wstd + t_wstu

        self.threshold_loss = int(unquote(os.getenv('NP_THRESHOLD_LOSS', '5')))
        self.threshold_latency = int(unquote(os.getenv('NP_THRESHOLD_LATENCY', '100')))
        self.threshold_jitter = int(unquote(os.getenv('NP_THRESHOLD_JITTER', '30')))
        self.threshold_internal_dns_latency = int(unquote(os.getenv('NP_THRESHOLD_INTERNAL_DNS_LATENCY', '100')))
        self.threshold_external_dns_latency = int(unquote(os.getenv('NP_THRESHOLD_EXTERNAL_DNS_LATENCY', '100')))

        self.threshold_speedtest_download = 0
        self.threshold_speedtest_upload = 0

        if self.speedtest.enforce_or_enabled:
            self.threshold_speedtest_download = self.speedtest.threshold_download # int(os.getenv('NP_THRESHOLD_SPEEDTEST_DOWNLOAD', '200'))
            self.threshold_speedtest_upload = self.speedtest.threshold_upload # int(os.getenv('NP_THRESHOLD_SPEEDTEST_UPLOAD', '200'))
