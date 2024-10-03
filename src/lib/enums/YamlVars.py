import typing
from enum import Enum

import yaql


class YamlVars(Enum):
    DATASTORE_PROBE_TYPE = "$.datastore.probe.type"
    DATASTORE_SPEEDTEST_TYPE = "$.datastore.speedtest.type"
    DATASTORE_PROBE_TOPIC = "$.datastore.probe.topic"
    DATASTORE_SPEEDTEST_TOPIC = "$.datastore.speedtest.topic"

    FILE_DATASTORE_PATH = "$.datastore.file.path"

    HTTP_VERIFY_SSL = "$.datastore.http.verify_ssl"
    HTTP_READ_URL = "$.datastore.http.read.url"
    HTTP_READ_METHOD = "$.datastore.http.read.method"
    HTTP_READ_HEADERS = "$.datastore.http.read.headers"
    HTTP_READ_TIMEOUT = "$.datastore.http.read.timeout"
    HTTP_READ_AUTH = "$.datastore.http.read.auth"
    HTTP_READ_COOKIES = "$.datastore.http.read.cookies"
    HTTP_READ_PARAMS = "$.datastore.http.read.params"
    HTTP_WRITE_URL = "$.datastore.http.write.url"
    HTTP_WRITE_METHOD = "$.datastore.http.write.method"
    HTTP_WRITE_HEADERS = "$.datastore.http.write.headers"
    HTTP_WRITE_TIMEOUT = "$.datastore.http.write.timeout"
    HTTP_WRITE_AUTH = "$.datastore.http.write.auth"
    HTTP_WRITE_COOKIES = "$.datastore.http.write.cookies"
    HTTP_WRITE_PARAMS = "$.datastore.http.write.params"

    LOG_LEVEL = "$.logging.level"
    LOG_FORMAT = "$.logging.format"
    LOG_DATE_FORMAT = "$.logging.date_format"

    MQTT_HOST = "$.datastore.mqtt.host"
    MQTT_PORT = "$.datastore.mqtt.port"
    MQTT_USERNAME = "$.datastore.mqtt.username"
    MQTT_PASSWORD = "$.datastore.mqtt.password"

    MONGODB_URL = "$.datastore.mongodb.url"
    MONGODB_DB = "$.datastore.mongodb.db"
    MONGODB_COLLECTION = "$.datastore.mongodb.collection"

    PRESENTATION_PORT = "$.presentation.port"
    PRESENTATION_INTERFACE = "$.presentation.interface"

    PROBE_COUNT = "$.probe.count"
    PROBE_ENABLED = "$.probe.enabled"
    PROBE_INTERVAL = "$.probe.interval"
    PROBE_DEVICE_ID = "$.probe.device_id"
    PROBE_DNS_TEST_SITE = "$.probe.dns.test"
    PROBE_SITES = "$.probe.sites"
    PROBE_LOCAL_DNS = "$.probe.dns.local"
    PROBE_EXTERNAL_DNS = "$.probe.dns.nameservers"

    REDIS_HOST = "$.datastore.redis.host"
    REDIS_PORT = "$.datastore.redis.port"
    REDIS_DB = "$.datastore.redis.db"
    REDIS_PASSWORD = "$.datastore.redis.password"

    SPEEDTEST_ENABLED = "$.speedtest.enabled"
    SPEEDTEST_INTERVAL = "$.speedtest.interval"
    SPEEDTEST_WEIGHT_REBALANCE = "$.health.weights.speedtest_rebalance"
    SPEEDTEST_WEIGHT_ENFORCE = "$.health.weights.speedtest_enforce"

    THRESHOLD_EXTERNAL_DNS_LATENCY = "$.health.thresholds.external_dns_latency"
    THRESHOLD_INTERNAL_DNS_LATENCY = "$.health.thresholds.internal_dns_latency"
    THRESHOLD_JITTER = "$.health.thresholds.jitter"
    THRESHOLD_LATENCY = "$.health.thresholds.latency"
    THRESHOLD_LOSS = "$.health.thresholds.loss"
    THRESHOLD_SPEEDTEST_DOWNLOAD = "$.health.thresholds.speedtest_download"
    THRESHOLD_SPEEDTEST_UPLOAD = "$.health.thresholds.speedtest_upload"

    WEIGHT_EXTERNAL_DNS_LATENCY = "$.health.weights.external_dns_latency"
    WEIGHT_INTERNAL_DNS_LATENCY = "$.health.weights.internal_dns_latency"
    WEIGHT_JITTER = "$.health.weights.jitter"
    WEIGHT_LATENCY = "$.health.weights.latency"
    WEIGHT_LOSS = "$.health.weights.loss"
    WEIGHT_SPEEDTEST_DOWNLOAD = "$.health.weights.speedtest_download"
    WEIGHT_SPEEDTEST_UPLOAD = "$.health.weights.speedtest_upload"

    __engine__ = yaql.factory.YaqlFactory().create()
    def expand(self, data: dict, default: typing.Optional[typing.Any]) -> typing.Optional[typing.Any]:
        try:
            # from yaml use the value of the key to query to expand the data value
            expression = YamlVars.__engine__(self.value)
            result = expression.evaluate(data=data) # type: ignore
            if result is None:
                print(f"Could not find value for {self.value}, using default value {default}")
                return default
            return result
        except KeyError as ke:
            print(f"Could not find value for {self.value}, using default value {default}")
            return default

    def nullable(self, data: dict, default: typing.Optional[typing.Any]) -> typing.Optional[typing.Any]:
        return self.expand(data, default) or None

    def string(self, data: dict, default: str) -> str:
        return str(self.expand(data, default))

    def list(self, data: dict, default: typing.List[str]) -> typing.List[str]:
        result = self.expand(data, None) or default
        if result is None:
            return default
        return list(result)

    def boolean(self, data: dict, default: bool) -> bool:
        return bool(self.string(data, str(default)).lower() in ('true', '1', 't', 'y', 'yes'))

    def float(self, data: dict, default: float) -> float:
        return float(self.string(data, str(default)))

    def integer(self, data: dict, default: int) -> int:
        return int(self.string(data, str(default)))
