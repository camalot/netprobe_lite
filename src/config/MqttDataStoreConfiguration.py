from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.DataStoreTypes import DataStoreTypes
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


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
