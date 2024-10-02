
class ConfigurationDefaults:
    CONFIG_FILE_PATH = "/app/config/netprobe.yaml"

    DATASTORE_TOPIC_SPEEDTEST = "netprobe/speedtest"
    DATASTORE_TOPIC_PROBE = "netprobe/probe"
    DATASTORE_TYPE_SPEEDTEST = "FILE"
    DATASTORE_TYPE_PROBE = "FILE"

    FILE_DATASTORE_PATH = "/data"

    HTTP_READ_URL = None
    HTTP_WRITE_URL = None
    HTTP_READ_METHOD = "GET"
    HTTP_WRITE_METHOD = "POST"
    HTTP_READ_HEADERS = {}
    HTTP_WRITE_HEADERS = {}
    HTTP_READ_TIMEOUT = 5
    HTTP_WRITE_TIMEOUT = 5
    HTTP_READ_AUTH = None
    HTTP_WRITE_AUTH = None
    HTTP_READ_COOKIES = None
    HTTP_WRITE_COOKIES = None
    HTTP_READ_PARAMS = None
    HTTP_WRITE_PARAMS = None
    HTTP_VERIFY_SSL = True

    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    MONGODB_URL = "mongodb://localhost:27017/admin"
    MONGODB_DB = "netprobe"
    MONGODB_COLLECTION = "netprobe"

    MQTT_HOST = "localhost"
    MQTT_PORT = 1883

    PRESENTATION_PORT = 5000
    PRESENTATION_INTERFACE = "0.0.0.0"

    PROBE_ENABLED = True
    PROBE_COUNT = 50
    PROBE_INTERVAL = 120
    PROBE_SITES = ["google.com", "facebook.com", "twitter.com", "youtube.com"]
    PROBE_DNS_TEST_SITE = "google.com"
    PROBE_DEVICE_ID = "netprobe"

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = "0"

    SPEEDTEST_INTERVAL = 937
    SPEEDTEST_ENABLED = False
    SPEEDTEST_WEIGHT_REBALANCE = True
    SPEEDTEST_WEIGHT_ENFORCE = False

    THRESHOLD_EXTERNAL_DNS_LATENCY = 100
    THRESHOLD_INTERNAL_DNS_LATENCY = 50
    THRESHOLD_JITTER = 40
    THRESHOLD_LATENCY = 100
    THRESHOLD_LOSS = 5
    THRESHOLD_SPEEDTEST_DOWNLOAD = 200
    THRESHOLD_SPEEDTEST_UPLOAD = 200

    WEIGHT_EXTERNAL_DNS_LATENCY = 0.025
    WEIGHT_INTERNAL_DNS_LATENCY = 0.025
    WEIGHT_JITTER = 0.2
    WEIGHT_LATENCY = 0.15
    WEIGHT_LOSS = 0.4
    WEIGHT_SPEEDTEST_DOWNLOAD = 0.1
    WEIGHT_SPEEDTEST_UPLOAD = 0.1
