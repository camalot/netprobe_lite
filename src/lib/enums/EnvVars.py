import os
import typing
from enum import Enum


class EnvVars(Enum):
    DATASTORE_PROBE_TYPE = "NP_DATASTORE_PROBE_TYPE"
    DATASTORE_SPEEDTEST_TYPE = "NP_DATASTORE_SPEEDTEST_TYPE"
    DATASTORE_TOPIC_PROBE = "NP_DATASTORE_TOPIC_NETPROBE"
    DATASTORE_TOPIC_SPEEDTEST = "NP_DATASTORE_TOPIC_SPEEDTEST"

    FILE_DATASTORE_PATH = "NP_FILE_DATASTORE_PATH"

    HTTP_READ_URL = "NP_HTTP_READ_URL"
    HTTP_WRITE_URL = "NP_HTTP_WRITE_URL"
    HTTP_READ_METHOD = "NP_HTTP_READ_METHOD"
    HTTP_WRITE_METHOD = "NP_HTTP_WRITE_METHOD"
    HTTP_READ_HEADERS = "NP_HTTP_READ_HEADERS"
    HTTP_WRITE_HEADERS = "NP_HTTP_WRITE_HEADERS"
    HTTP_READ_TIMEOUT = "NP_HTTP_READ_TIMEOUT"
    HTTP_WRITE_TIMEOUT = "NP_HTTP_WRITE_TIMEOUT"
    HTTP_READ_AUTH = "NP_HTTP_READ_AUTH"
    HTTP_WRITE_AUTH = "NP_HTTP_WRITE_AUTH"
    HTTP_READ_COOKIES = "NP_HTTP_READ_COOKIES"
    HTTP_WRITE_COOKIES = "NP_HTTP_WRITE_COOKIES"
    HTTP_READ_PARAMS = "NP_HTTP_READ_PARAMS"
    HTTP_WRITE_PARAMS = "NP_HTTP_WRITE_PARAMS"
    HTTP_VERIFY_SSL = "NP_HTTP_VERIFY_SSL"

    LOG_LEVEL = "NP_LOG_LEVEL"
    LOG_FORMAT = "NP_LOG_FORMAT"

    MQTT_HOST = "NP_MQTT_HOST"
    MQTT_PORT = "NP_MQTT_PORT"
    MQTT_USERNAME = "NP_MQTT_USERNAME"
    MQTT_PASSWORD = "NP_MQTT_PASSWORD"

    MONGODB_URL = "NP_MONGODB_URL"
    MONGODB_DB = "NP_MONGODB_DB"
    MONGODB_COLLECTION = "NP_MONGODB_COLLECTION"

    PRESENTATION_PORT = "NP_PRESENTATION_PORT"
    PRESENTATION_INTERFACE = "NP_PRESENTATION_INTERFACE"

    PROBE_ENABLED = "NP_PROBE_ENABLED"
    PROBE_COUNT = "NP_PROBE_COUNT"
    PROBE_DEVICE_ID = "NP_DEVICE_ID"
    PROBE_DNS_TEST_SITE = "NP_PROBE_DNS_TEST_SITE"
    PROBE_INTERVAL = "NP_PROBE_INTERVAL"
    PROBE_SITES = "NP_SITES"
    PROBE_LOCAL_DNS = "NP_LOCAL_DNS"
    PROBE_LOCAL_DNS_IP = "NP_LOCAL_DNS_IP"

    REDIS_HOST = "NP_REDIS_HOST"
    REDIS_PORT = "NP_REDIS_PORT"
    REDIS_DB = "NP_REDIS_DB"
    REDIS_PASSWORD = "NP_REDIS_PASSWORD"

    SPEEDTEST_ENABLED = "NP_SPEEDTEST_ENABLED"
    SPEEDTEST_INTERVAL = "NP_SPEEDTEST_INTERVAL"
    SPEEDTEST_WEIGHT_REBALANCE = "NP_WEIGHT_SPEEDTEST_REBALANCE"
    SPEEDTEST_WEIGHT_ENFORCE = "NP_WEIGHT_SPEEDTEST_ENFORCE"

    THRESHOLD_EXTERNAL_DNS_LATENCY = "NP_THRESHOLD_EXTERNAL_DNS_LATENCY"
    THRESHOLD_INTERNAL_DNS_LATENCY = "NP_THRESHOLD_INTERNAL_DNS_LATENCY"
    THRESHOLD_JITTER = "NP_THRESHOLD_JITTER"
    THRESHOLD_LATENCY = "NP_THRESHOLD_LATENCY"
    THRESHOLD_LOSS = "NP_THRESHOLD_LOSS"
    THRESHOLD_SPEEDTEST_DOWNLOAD = "NP_THRESHOLD_SPEEDTEST_DOWNLOAD"
    THRESHOLD_SPEEDTEST_UPLOAD = "NP_THRESHOLD_SPEEDTEST_UPLOAD"

    WEIGHT_EXTERNAL_DNS_LATENCY = "NP_WEIGHT_EXTERNAL_DNS_LATENCY"
    WEIGHT_INTERNAL_DNS_LATENCY = "NP_WEIGHT_INTERNAL_DNS_LATENCY"
    WEIGHT_JITTER = "NP_WEIGHT_JITTER"
    WEIGHT_LATENCY = "NP_WEIGHT_LATENCY"
    WEIGHT_LOSS = "NP_WEIGHT_LOSS"
    WEIGHT_SPEEDTEST_DOWNLOAD = "NP_WEIGHT_SPEEDTEST_DOWNLOAD"
    WEIGHT_SPEEDTEST_UPLOAD = "NP_WEIGHT_SPEEDTEST_UPLOAD"

    def expand(self, default: typing.Any = None) -> str:
        result = EnvVars.unquote(os.getenv(self.value, default))
        return result

    def boolean(self, default: bool) -> bool:
        return bool(self.expand(str(default)).lower() in ('true', '1', 't', 'y', 'yes'))

    def nullable(self, default: typing.Any = None) -> typing.Optional[str]:
        return self.expand(default) or None

    def string(self, default: str = '') -> str:
        return str(self.expand(default))

    def integer(self, default: int = 0) -> int:
        return int(self.expand(str(default)))

    def float(self, default: float = 0.0) -> float:
        return float(self.expand(str(default)))

    def list(self, separator: str = ',', default: typing.List[str] = []) -> typing.List[str]:
        # split and trim the values
        return [x.strip() for x in self.expand(separator.join(default)).split(separator)]

    # take key=value pairs separated by a separator and return a dictionary
    def dict(self, separator: str = ";", default: typing.Dict[str, str] = {}) -> typing.Dict[str, str]:
        result = self.nullable_dict(separator, default)
        if result:
            return result
        return {}

    def nullable_dict(
        self, separator: str = ";", default: typing.Optional[typing.Dict[str, str]] = {}
    ) -> typing.Optional[typing.Dict[str, str]]:
        if default:
            # split and trim the values
            return {
                x.split("=")[0].strip(): x.split("=")[1].strip()
                for x in self.expand(separator.join(default)).split(separator)
            }
        return None

    @staticmethod
    def unquote(value: typing.Optional[str]) -> typing.Any:
        """This function removes quotes from a string if they exist. It is used to clean up environment variables.
        as they can be read with quotes if they are set in a docker-compose file or a .env file."""
        if not value:
            return None

        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        return value
