import logging
import os
import re
import typing

import yaml
from dotenv import find_dotenv, load_dotenv
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars

# Load configs from env
try:  # Try to load env vars from file, if fails pass
    load_dotenv(find_dotenv())
except:  # noqa: E722
    pass


class Configuration:
    def __init__(self, file_path: typing.Optional[str] = ConfigurationDefaults.CONFIG_FILE_PATH):
        self.reload(file_path)

    def reload(self, file_path: typing.Optional[str] = ConfigurationDefaults.CONFIG_FILE_PATH):
        try:
            file_path = EnvVars.CONFIG_FILE.file(ConfigurationDefaults.CONFIG_FILE_PATH)
        except FileNotFoundError:
            file_path = None

        if not file_path or not os.path.exists(file_path):
            file_path = ConfigurationDefaults.CONFIG_FILE_PATH

        base_config = {}
        # if file_path exists and is not none, load the file
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as file:
                base_config = yaml.safe_load(file)

        self.probe = NetProbeConfiguration(base_config)
        self.logging = LoggingConfiguration(base_config)
        self.speedtest = SpeedTestConfiguration(base_config)
        self.datastore = DataStoreConfiguration(base_config)
        self.presentation = PresentationConfiguration(base_config, probe=self.probe, speedtest=self.speedtest)


class MqttDataStoreConfiguration:
    def __init__(self, base: dict = {}, *args, **kwargs):
        self.host = EnvVars.MQTT_HOST.string(YamlVars.MQTT_HOST.string(base, ConfigurationDefaults.MQTT_HOST))
        self.port = EnvVars.MQTT_PORT.integer(YamlVars.MQTT_PORT.integer(base, ConfigurationDefaults.MQTT_PORT))
        self.username = EnvVars.MQTT_USERNAME.nullable(YamlVars.MQTT_USERNAME.nullable(base, None))
        self.password = EnvVars.MQTT_PASSWORD.nullable(YamlVars.MQTT_PASSWORD.nullable(base, None))

        st_topic = None
        np_topic = None
        if 'netprobe' in kwargs:
            np: dict = kwargs.get('netprobe')  # type: ignore
            np_type = np.get('type', None)
            np_topic = (
                np.get('topic', ConfigurationDefaults.DATASTORE_PROBE_TOPIC) if np_type == DataStoreTypes.MQTT else None
            )
        if 'speedtest' in kwargs:
            st: dict = kwargs.get('speedtest')  # type: ignore
            st_type = st.get('type', None)
            st_topic = (
                st.get('topic', ConfigurationDefaults.DATASTORE_SPEEDTEST_TOPIC)
                if st_type == DataStoreTypes.MQTT
                else None
            )

        self.topics = []
        if np_topic:
            self.topics.append(np_topic)
        if st_topic:
            self.topics.append(st_topic)

    def merge(self, config: dict):
        self.__dict__.update(config)


class MongoDBDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.url = EnvVars.MONGODB_URL.string(YamlVars.MONGODB_URL.string(base, ConfigurationDefaults.MONGODB_URL))
        self.db = EnvVars.MONGODB_DB.string(YamlVars.MONGODB_DB.string(base, ConfigurationDefaults.MONGODB_DB))
        self.collection = EnvVars.MONGODB_COLLECTION.string(
            YamlVars.MONGODB_COLLECTION.string(base, ConfigurationDefaults.MONGODB_COLLECTION)
        )

    def merge(self, config: dict):
        self.__dict__.update(config)


class LoggingConfiguration:
    def __init__(self, base: dict = {}):
        log_level = EnvVars.LOG_LEVEL.string(YamlVars.LOG_LEVEL.string(base, ConfigurationDefaults.LOG_LEVEL)).upper()
        self.level = getattr(logging, log_level, logging.INFO)
        self.format = EnvVars.LOG_FORMAT.string(YamlVars.LOG_FORMAT.string(base, ConfigurationDefaults.LOG_FORMAT))
        self.date_format = EnvVars.LOG_DATEFORMAT.string(
            YamlVars.LOG_DATE_FORMAT.string(base, ConfigurationDefaults.LOG_DATEFORMAT)
        )

    def merge(self, config: dict):
        self.__dict__.update(config)


class SpeedTestConfiguration:
    def __init__(self, base: dict = {}):
        self.enabled = EnvVars.SPEEDTEST_ENABLED.boolean(
            YamlVars.SPEEDTEST_ENABLED.boolean(base, ConfigurationDefaults.SPEEDTEST_ENABLED)
        )
        self.interval = EnvVars.SPEEDTEST_INTERVAL.integer(
            YamlVars.SPEEDTEST_INTERVAL.integer(base, ConfigurationDefaults.SPEEDTEST_INTERVAL)
        )
        self.weight_rebalance = EnvVars.SPEEDTEST_WEIGHT_REBALANCE.boolean(
            YamlVars.SPEEDTEST_WEIGHT_REBALANCE.boolean(base, ConfigurationDefaults.SPEEDTEST_WEIGHT_REBALANCE)
        )
        self.enforce_weight = EnvVars.SPEEDTEST_WEIGHT_ENFORCE.boolean(
            YamlVars.SPEEDTEST_WEIGHT_ENFORCE.boolean(base, ConfigurationDefaults.SPEEDTEST_WEIGHT_ENFORCE)
        )
        self.download_weight = EnvVars.WEIGHT_SPEEDTEST_DOWNLOAD.float(
            YamlVars.WEIGHT_SPEEDTEST_DOWNLOAD.float(base, ConfigurationDefaults.WEIGHT_SPEEDTEST_DOWNLOAD)
        )
        self.upload_weight = EnvVars.WEIGHT_SPEEDTEST_UPLOAD.float(
            YamlVars.WEIGHT_SPEEDTEST_UPLOAD.float(base, ConfigurationDefaults.WEIGHT_SPEEDTEST_UPLOAD)
        )
        self.threshold_download = EnvVars.THRESHOLD_SPEEDTEST_DOWNLOAD.float(
            YamlVars.THRESHOLD_SPEEDTEST_DOWNLOAD.float(base, ConfigurationDefaults.THRESHOLD_SPEEDTEST_DOWNLOAD)
        )
        self.threshold_upload = EnvVars.THRESHOLD_SPEEDTEST_UPLOAD.float(
            YamlVars.THRESHOLD_SPEEDTEST_UPLOAD.float(base, ConfigurationDefaults.THRESHOLD_SPEEDTEST_UPLOAD)
        )
        self.enforce_or_enabled = self.enforce_weight or self.enabled

    def merge(self, config: dict):
        self.__dict__.update(config)


class DataStoreConfiguration:
    def __init__(self, base: dict = {}):

        probe_type = EnvVars.DATASTORE_PROBE_TYPE.string(
            YamlVars.DATASTORE_PROBE_TYPE.string(base, ConfigurationDefaults.DATASTORE_PROBE_TYPE)
        ).upper()
        probe_topic = EnvVars.DATASTORE_PROBE_TOPIC.string(
            YamlVars.DATASTORE_PROBE_TOPIC.string(base, ConfigurationDefaults.DATASTORE_PROBE_TOPIC)
        )
        speed_type = EnvVars.DATASTORE_SPEEDTEST_TYPE.string(
            YamlVars.DATASTORE_SPEEDTEST_TYPE.string(base, ConfigurationDefaults.DATASTORE_SPEEDTEST_TYPE)
        ).upper()
        speed_topic = EnvVars.DATASTORE_SPEEDTEST_TOPIC.string(
            YamlVars.DATASTORE_SPEEDTEST_TOPIC.string(base, ConfigurationDefaults.DATASTORE_SPEEDTEST_TOPIC)
        )

        self.netprobe = {'type': DataStoreTypes.from_str(probe_type), 'topic': probe_topic}
        self.speedtest = {'type': DataStoreTypes.from_str(speed_type), 'topic': speed_topic}

        self.file = FileDataStoreConfiguration(base)
        self.redis = RedisDataStoreConfiguration(base)
        self.mongodb = MongoDBDataStoreConfiguration(base)
        self.http = HttpDataStoreConfiguration(base)
        self.mqtt = MqttDataStoreConfiguration(base, netprobe=self.netprobe, speedtest=self.speedtest)

    def merge(self, config: dict):
        self.__dict__.update(config)


class HttpRequestConfiguration:
    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', None)
        self.method = kwargs.get('method', 'GET')
        self.headers = kwargs.get('headers', {})
        self.timeout = kwargs.get('timeout', 10)
        self.cookies = kwargs.get('cookies', None)
        self.auth = kwargs.get('auth', None)
        self.params = kwargs.get('params', None)

    def merge(self, config: dict):
        self.__dict__.update(config)


class HttpDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.verify_ssl = EnvVars.HTTP_VERIFY_SSL.boolean(
            YamlVars.HTTP_VERIFY_SSL.boolean(base, ConfigurationDefaults.HTTP_VERIFY_SSL)
        )

        self.read = HttpRequestConfiguration(
            url=(
                EnvVars.HTTP_READ_URL.nullable(
                    YamlVars.HTTP_READ_URL.nullable(base, ConfigurationDefaults.HTTP_READ_URL)
                )
            ),
            method=(
                EnvVars.HTTP_READ_METHOD.string(
                    YamlVars.HTTP_READ_METHOD.string(base, ConfigurationDefaults.HTTP_READ_METHOD)
                )
            ),
            headers=(
                EnvVars.HTTP_READ_HEADERS.nullable_dict(
                    default=YamlVars.HTTP_READ_HEADERS.expand(base, ConfigurationDefaults.HTTP_READ_HEADERS)
                )
            ),
            timeout=(
                EnvVars.HTTP_READ_TIMEOUT.integer(
                    YamlVars.HTTP_READ_TIMEOUT.integer(base, ConfigurationDefaults.HTTP_READ_TIMEOUT)
                )
            ),
            auth=(
                EnvVars.HTTP_READ_AUTH.nullable_dict(
                    default=YamlVars.HTTP_READ_AUTH.expand(base, ConfigurationDefaults.HTTP_READ_AUTH)
                )
            ),
            cookies=(
                EnvVars.HTTP_READ_COOKIES.nullable_dict(
                    default=YamlVars.HTTP_READ_COOKIES.expand(base, ConfigurationDefaults.HTTP_READ_COOKIES)
                )
            ),
            params=(
                EnvVars.HTTP_READ_PARAMS.nullable_dict(
                    default=YamlVars.HTTP_READ_PARAMS.expand(base, ConfigurationDefaults.HTTP_READ_PARAMS)
                )
            ),
        )
        self.write = HttpRequestConfiguration(
            url=(
                EnvVars.HTTP_WRITE_URL.nullable(
                    YamlVars.HTTP_WRITE_URL.nullable(base, ConfigurationDefaults.HTTP_WRITE_URL)
                )
            ),
            method=(
                EnvVars.HTTP_WRITE_METHOD.string(
                    YamlVars.HTTP_WRITE_METHOD.string(base, ConfigurationDefaults.HTTP_WRITE_METHOD)
                )
            ),
            headers=(
                EnvVars.HTTP_WRITE_HEADERS.nullable_dict(
                    default=YamlVars.HTTP_WRITE_HEADERS.expand(base, ConfigurationDefaults.HTTP_WRITE_HEADERS)
                )
            ),
            timeout=(
                EnvVars.HTTP_WRITE_TIMEOUT.integer(
                    YamlVars.HTTP_WRITE_TIMEOUT.integer(base, ConfigurationDefaults.HTTP_WRITE_TIMEOUT)
                )
            ),
            auth=(
                EnvVars.HTTP_WRITE_AUTH.nullable_dict(
                    default=YamlVars.HTTP_WRITE_AUTH.expand(base, ConfigurationDefaults.HTTP_WRITE_AUTH)
                )
            ),
            cookies=(
                EnvVars.HTTP_WRITE_COOKIES.nullable_dict(
                    default=YamlVars.HTTP_WRITE_COOKIES.expand(base, ConfigurationDefaults.HTTP_WRITE_COOKIES)
                )
            ),
            params=(
                EnvVars.HTTP_WRITE_PARAMS.nullable_dict(
                    default=YamlVars.HTTP_WRITE_PARAMS.expand(base, ConfigurationDefaults.HTTP_WRITE_PARAMS)
                )
            ),
        )

    def merge(self, config: dict):
        self.__dict__.update(config)


class NetProbeConfiguration:
    def __init__(self, base: dict = {}):
        self.enabled = EnvVars.PROBE_ENABLED.boolean(
            YamlVars.PROBE_ENABLED.boolean(base, ConfigurationDefaults.PROBE_ENABLED)
        )
        self.interval = EnvVars.PROBE_INTERVAL.integer(
            YamlVars.PROBE_INTERVAL.integer(base, ConfigurationDefaults.PROBE_INTERVAL)
        )
        self.count = EnvVars.PROBE_COUNT.integer(YamlVars.PROBE_COUNT.integer(base, ConfigurationDefaults.PROBE_COUNT))

        sites = EnvVars.PROBE_SITES.list(',', list())
        if not sites or len(sites) == 0:
            sites = YamlVars.PROBE_SITES.list(base, ConfigurationDefaults.PROBE_SITES)

        self.sites = sites
        self.dns_test_site = EnvVars.PROBE_DNS_TEST_SITE.string(
            YamlVars.PROBE_DNS_TEST_SITE.string(base, ConfigurationDefaults.PROBE_DNS_TEST_SITE)
        )
        self.device_id = (
            str(
                EnvVars.PROBE_DEVICE_ID.string(
                    YamlVars.PROBE_DEVICE_ID.string(base, ConfigurationDefaults.PROBE_DEVICE_ID)
                )
            )
            .replace(' ', '_')
            .replace('.', '_')
            .replace('-', '_')
            .lower()
        )

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

        external_dns = YamlVars.PROBE_EXTERNAL_DNS.expand(base, [])
        internal_dns = YamlVars.PROBE_LOCAL_DNS.expand(base, [])

        if external_dns and isinstance(external_dns, list):
            for dns in external_dns:
                if "name" in dns and "ip" in dns:
                    # make sure its not already in the list
                    if not any(d[1] == dns['ip'] for d in self.nameservers):
                        self.nameservers.append((dns['name'], dns['ip'], "external"))

        if internal_dns and isinstance(internal_dns, list):
            for dns in internal_dns:
                if "name" in dns and "ip" in dns:
                    # make sure its not already in the list
                    if not any(d[1] == dns['ip'] for d in self.nameservers):
                        self.nameservers.append((dns['name'], dns['ip'], "internal"))

    def merge(self, config: dict):
        self.__dict__.update(config)


class RedisDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.host = EnvVars.REDIS_HOST.string(YamlVars.REDIS_HOST.string(base, ConfigurationDefaults.REDIS_HOST))
        self.port = EnvVars.REDIS_PORT.integer(YamlVars.REDIS_PORT.integer(base, ConfigurationDefaults.REDIS_PORT))
        self.password = EnvVars.REDIS_PASSWORD.nullable(YamlVars.REDIS_PASSWORD.nullable(base, None))
        self.db = EnvVars.REDIS_DB.string(YamlVars.REDIS_DB.string(base, ConfigurationDefaults.REDIS_DB))

    def merge(self, config: dict):
        self.__dict__.update(config)


class FileDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.path = EnvVars.FILE_DATASTORE_PATH.string(
            YamlVars.FILE_DATASTORE_PATH.string(base, ConfigurationDefaults.FILE_DATASTORE_PATH)
        )


class PresentationConfiguration:
    def __init__(self, base: dict = {}, probe: NetProbeConfiguration = None, speedtest: SpeedTestConfiguration = None):  # type: ignore
        if not probe:
            raise ValueError("Probe configuration is required")
        if not speedtest:
            raise ValueError("Speedtest configuration is required")

        self.speedtest = speedtest
        self.port = EnvVars.PRESENTATION_PORT.integer(
            YamlVars.PRESENTATION_PORT.integer(base, ConfigurationDefaults.PRESENTATION_PORT)
        )
        self.interface = EnvVars.PRESENTATION_INTERFACE.string(
            YamlVars.PRESENTATION_INTERFACE.string(base, ConfigurationDefaults.PRESENTATION_INTERFACE)
        )
        self.device_id = probe.device_id

        self.weight_loss = EnvVars.WEIGHT_LOSS.float(
            YamlVars.WEIGHT_LOSS.float(base, ConfigurationDefaults.WEIGHT_LOSS)
        )

        self.weight_latency = EnvVars.WEIGHT_LATENCY.float(
            YamlVars.WEIGHT_LATENCY.float(base, ConfigurationDefaults.WEIGHT_LATENCY)
        )

        self.weight_jitter = EnvVars.WEIGHT_JITTER.float(
            YamlVars.WEIGHT_JITTER.float(base, ConfigurationDefaults.WEIGHT_JITTER)
        )

        self.weight_internal_dns_latency = EnvVars.WEIGHT_INTERNAL_DNS_LATENCY.float(
            YamlVars.WEIGHT_INTERNAL_DNS_LATENCY.float(base, ConfigurationDefaults.WEIGHT_INTERNAL_DNS_LATENCY)
        )

        self.weight_external_dns_latency = EnvVars.WEIGHT_EXTERNAL_DNS_LATENCY.float(
            YamlVars.WEIGHT_EXTERNAL_DNS_LATENCY.float(base, ConfigurationDefaults.WEIGHT_EXTERNAL_DNS_LATENCY)
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

        self.threshold_loss = EnvVars.THRESHOLD_LOSS.integer(
            YamlVars.THRESHOLD_LOSS.integer(base, ConfigurationDefaults.THRESHOLD_LOSS)
        )
        self.threshold_latency = EnvVars.THRESHOLD_LATENCY.integer(
            YamlVars.THRESHOLD_LATENCY.integer(base, ConfigurationDefaults.THRESHOLD_LATENCY)
        )
        self.threshold_jitter = EnvVars.THRESHOLD_JITTER.integer(
            YamlVars.THRESHOLD_JITTER.integer(base, ConfigurationDefaults.THRESHOLD_JITTER)
        )
        self.threshold_internal_dns_latency = EnvVars.THRESHOLD_INTERNAL_DNS_LATENCY.integer(
            YamlVars.THRESHOLD_INTERNAL_DNS_LATENCY.integer(base, ConfigurationDefaults.THRESHOLD_INTERNAL_DNS_LATENCY)
        )
        self.threshold_external_dns_latency = EnvVars.THRESHOLD_EXTERNAL_DNS_LATENCY.integer(
            YamlVars.THRESHOLD_EXTERNAL_DNS_LATENCY.integer(base, ConfigurationDefaults.THRESHOLD_EXTERNAL_DNS_LATENCY)
        )

        self.threshold_speedtest_download = 0
        self.threshold_speedtest_upload = 0

        if self.speedtest.enforce_or_enabled:
            self.threshold_speedtest_download = self.speedtest.threshold_download
            self.threshold_speedtest_upload = self.speedtest.threshold_upload


ApplicationConfiguration = Configuration()
