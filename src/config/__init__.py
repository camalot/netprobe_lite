import json
import logging
import os
import re
import typing

from lib.enums.DataStoreTypes import DataStoreTypes
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars

import yaml
from dotenv import find_dotenv, load_dotenv

# Load configs from env
try:  # Try to load env vars from file, if fails pass
    load_dotenv(find_dotenv())
except:  # noqa: E722
    pass


class Configuration:
    def __init__(self, file_path: typing.Optional[str] = ConfigurationDefaults.CONFIG_FILE_PATH):

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
        self.host = EnvVars.MQTT_HOST.string(ConfigurationDefaults.MQTT_HOST)
        self.port = EnvVars.MQTT_PORT.integer(ConfigurationDefaults.MQTT_PORT)
        self.username = EnvVars.MQTT_USERNAME.nullable()
        self.password = EnvVars.MQTT_PASSWORD.nullable()

        dsc = DataStoreConfiguration()
        np_type = dsc.netprobe.get('type', None)
        np_topic = dsc.netprobe.get('topic', ConfigurationDefaults.DATASTORE_TOPIC_PROBE) if np_type == DataStoreTypes.MQTT else None

        st_type = dsc.speedtest.get('type', None)
        st_topic = dsc.speedtest.get('topic', ConfigurationDefaults.DATASTORE_TOPIC_SPEEDTEST) if st_type == DataStoreTypes.MQTT else None

        self.topics = []
        if np_topic:
            self.topics.append(np_topic)
        if st_topic:
            self.topics.append(st_topic)
        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")

    def merge(self, config: dict):
        self.__dict__.update(config)


class MongoDBDataStoreConfiguration:
    def __init__(self):
        self.url = EnvVars.MONGODB_URL.string(ConfigurationDefaults.MONGODB_URL)
        self.db = EnvVars.MONGODB_DB.string(ConfigurationDefaults.MONGODB_DB)
        self.collection = EnvVars.MONGODB_COLLECTION.string(ConfigurationDefaults.MONGODB_COLLECTION)
        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")

    def merge(self, config: dict):
        self.__dict__.update(config)


class LoggingConfiguration:
    def __init__(self):
        log_level = EnvVars.LOG_LEVEL.string(ConfigurationDefaults.LOG_LEVEL).upper()
        self.level = getattr(logging, log_level, logging.INFO)
        self.format = EnvVars.LOG_FORMAT.string(ConfigurationDefaults.LOG_FORMAT)
        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")

    def merge(self, config: dict):
        self.__dict__.update(config)


class SpeedTestConfiguration:
    def __init__(self):
        self.enabled = EnvVars.SPEEDTEST_ENABLED.boolean(ConfigurationDefaults.SPEEDTEST_ENABLED)
        self.interval = EnvVars.SPEEDTEST_INTERVAL.integer(ConfigurationDefaults.SPEEDTEST_INTERVAL)
        self.weight_rebalance = EnvVars.SPEEDTEST_WEIGHT_REBALANCE.boolean(ConfigurationDefaults.SPEEDTEST_WEIGHT_REBALANCE)
        self.enforce_weight = EnvVars.SPEEDTEST_WEIGHT_ENFORCE.boolean(ConfigurationDefaults.SPEEDTEST_WEIGHT_ENFORCE)
        self.download_weight = EnvVars.WEIGHT_SPEEDTEST_DOWNLOAD.float(ConfigurationDefaults.WEIGHT_SPEEDTEST_DOWNLOAD)
        self.upload_weight = EnvVars.WEIGHT_SPEEDTEST_UPLOAD.float(ConfigurationDefaults.WEIGHT_SPEEDTEST_UPLOAD)
        self.threshold_download = EnvVars.THRESHOLD_SPEEDTEST_DOWNLOAD.float(ConfigurationDefaults.THRESHOLD_SPEEDTEST_DOWNLOAD)
        self.threshold_upload = EnvVars.THRESHOLD_SPEEDTEST_UPLOAD.float(ConfigurationDefaults.THRESHOLD_SPEEDTEST_UPLOAD)

        self.enforce_or_enabled = self.enforce_weight or self.enabled

        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")

    def merge(self, config: dict):
        self.__dict__.update(config)


class DataStoreConfiguration:
    def __init__(self):
        self.netprobe = {
            'type': DataStoreTypes.from_str(
                EnvVars.DATASTORE_PROBE_TYPE.string(ConfigurationDefaults.DATASTORE_TYPE_PROBE).upper()
            ),
            'topic': EnvVars.DATASTORE_TOPIC_PROBE.string(ConfigurationDefaults.DATASTORE_TOPIC_PROBE),
        }
        self.speedtest = {
            'type': DataStoreTypes.from_str(
                EnvVars.DATASTORE_SPEEDTEST_TYPE.string(ConfigurationDefaults.DATASTORE_TYPE_SPEEDTEST).upper()
            ),
            'topic': EnvVars.DATASTORE_TOPIC_SPEEDTEST.string(ConfigurationDefaults.DATASTORE_TOPIC_SPEEDTEST),
        }
        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")

    def merge(self, config: dict):
        self.__dict__.update(config)


class NetProbeConfiguration:
    def __init__(self):
        self.enabled = EnvVars.PROBE_ENABLED.boolean(ConfigurationDefaults.PROBE_ENABLED)
        self.interval = EnvVars.PROBE_INTERVAL.integer(ConfigurationDefaults.PROBE_INTERVAL)
        self.count = EnvVars.PROBE_COUNT.integer(ConfigurationDefaults.PROBE_COUNT)
        self.sites = EnvVars.PROBE_SITES.list(',', ConfigurationDefaults.PROBE_SITES)
        self.dns_test_site = EnvVars.PROBE_DNS_TEST_SITE.string(ConfigurationDefaults.PROBE_DNS_TEST_SITE)
        self.device_id = EnvVars.PROBE_DEVICE_ID.string(
            ConfigurationDefaults.PROBE_DEVICE_ID
        ).replace(' ', '_').replace('.', '_').replace('-', '_').lower()

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
                ip = EnvVars.unquote(os.getenv(f'NP_DNS_NAMESERVER_{index}_IP', None))
                if ip and label:
                    self.nameservers.append((EnvVars.unquote(label), ip, 'external'))
            m = re.match(match_pattern_local, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if m:
                index = m.group(1)
                label = value if value else f"INTERNAL DNS NAMESERVER {index}"
                ip = EnvVars.unquote(os.getenv(f'NP_LOCAL_DNS_NAMESERVER_{index}_IP', None))
                if ip and label:
                    self.nameservers.append((EnvVars.unquote(label), ip, 'internal'))

        # singular local dns
        NP_LOCAL_DNS = EnvVars.unquote(os.getenv('NP_LOCAL_DNS', None))
        NP_LOCAL_DNS_IP = EnvVars.unquote(os.getenv('NP_LOCAL_DNS_IP', None))

        if NP_LOCAL_DNS and NP_LOCAL_DNS_IP:
            self.nameservers.append((NP_LOCAL_DNS, NP_LOCAL_DNS_IP, "internal"))

        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")

    def merge(self, config: dict):
        self.__dict__.update(config)


class RedisDataStoreConfiguration:
    def __init__(self):
        self.host = EnvVars.REDIS_HOST.string(ConfigurationDefaults.REDIS_HOST)
        self.port = EnvVars.REDIS_PORT.integer(ConfigurationDefaults.REDIS_PORT)
        self.password = EnvVars.REDIS_PASSWORD.nullable()
        self.db = EnvVars.REDIS_DB.string(ConfigurationDefaults.REDIS_DB)

        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")

    def merge(self, config: dict):
        self.__dict__.update(config)


class FileDataStoreConfiguration:
    def __init__(self):
        self.path = EnvVars.FILE_DATASTORE_PATH.string(ConfigurationDefaults.FILE_DATASTORE_PATH)

        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")


class PresentationConfiguration:
    def __init__(self):
        self.speedtest = SpeedTestConfiguration()
        probe = NetProbeConfiguration()
        self.port = EnvVars.PRESENTATION_PORT.integer(ConfigurationDefaults.PRESENTATION_PORT)
        self.interface = EnvVars.PRESENTATION_INTERFACE.string(ConfigurationDefaults.PRESENTATION_INTERFACE)
        self.device_id = probe.device_id

        self.weight_loss = EnvVars.WEIGHT_LOSS.float(ConfigurationDefaults.WEIGHT_LOSS)
        self.weight_latency = EnvVars.WEIGHT_LATENCY.float(ConfigurationDefaults.WEIGHT_LATENCY)
        self.weight_jitter = EnvVars.WEIGHT_JITTER.float(ConfigurationDefaults.WEIGHT_JITTER)
        self.weight_internal_dns_latency = EnvVars.WEIGHT_INTERNAL_DNS_LATENCY.float(
            ConfigurationDefaults.WEIGHT_INTERNAL_DNS_LATENCY
        )
        self.weight_external_dns_latency = EnvVars.WEIGHT_EXTERNAL_DNS_LATENCY.float(
            ConfigurationDefaults.WEIGHT_EXTERNAL_DNS_LATENCY
        )

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
            self.weight_speedtest_download = self.speedtest.download_weight
            self.weight_speedtest_upload = self.speedtest.upload_weight
        else:
            t_wstd = self.speedtest.download_weight
            t_wstu = self.speedtest.upload_weight
            if self.total_weight < 1 and (self.total_weight + t_wstd + t_wstu) <= 1 and self.speedtest.weight_rebalance:
                # add this weight to the "loss" weight
                self.weight_loss += t_wstd + t_wstu

        # Recalculate total weight after rebalance
        self.total_weight = sum(
            [
                self.weight_loss,
                self.weight_latency,
                self.weight_jitter,
                self.weight_external_dns_latency,
                self.weight_internal_dns_latency,
                self.weight_speedtest_download,
                self.weight_speedtest_upload,
            ]
        )

        self.threshold_loss = EnvVars.THRESHOLD_LOSS.integer(ConfigurationDefaults.THRESHOLD_LOSS)
        self.threshold_latency = EnvVars.THRESHOLD_LATENCY.integer(ConfigurationDefaults.THRESHOLD_LATENCY)
        self.threshold_jitter = EnvVars.THRESHOLD_JITTER.integer(ConfigurationDefaults.THRESHOLD_JITTER)
        self.threshold_internal_dns_latency = EnvVars.THRESHOLD_INTERNAL_DNS_LATENCY.integer(
            ConfigurationDefaults.THRESHOLD_INTERNAL_DNS_LATENCY
        )
        self.threshold_external_dns_latency = EnvVars.THRESHOLD_EXTERNAL_DNS_LATENCY.integer(
            ConfigurationDefaults.THRESHOLD_EXTERNAL_DNS_LATENCY
        )

        self.threshold_speedtest_download = 0
        self.threshold_speedtest_upload = 0

        if self.speedtest.enforce_or_enabled:
            self.threshold_speedtest_download = self.speedtest.threshold_download
            self.threshold_speedtest_upload = self.speedtest.threshold_upload

        # print(f"{self.__class__.__name__} => {json.dumps(self.__dict__)}")
