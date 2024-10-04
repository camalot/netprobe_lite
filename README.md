# Netprobe

Simple and effective tool for measuring ISP performance at home. The tool measures several performance metrics
including packet loss, latency, jitter, and DNS performance. It also has an optional speed test to measure bandwidth.
Netprobe aggregates these metrics into a common score, which you can use to monitor overall health of your internet
connection.

> [!NOTE]
> This is a [fork of Netprobe_lite](https://github.com/plaintextpackets/netprobe_lite). I did some refactoring of
> how the container is built, how the variables are set, the names of the variables, a lot of refactoring
> to pass lint tests, and other things.

## Support the Project

If you'd like to support the development of this project, feel free to
[buy me a coffee](https://buymeacoffee.com/plaintextpm)!

## Full Tutorial

Visit [YouTube](https://youtu.be/Wn31husi6tc) for a full tutorial on how to install and use Netprobe:

## Requirements and Setup

To run Netprobe, you'll need a PC running Docker connected directly to your ISP router. Specifically:

1. Netprobe requires the latest version of Docker. For instructions on installing Docker, see YouTube, it's super easy.

1. Netprobe should be installed on a machine (the 'probe') which has a wired Ethernet connection to your primary ISP
router. This ensures the tests are accurately measuring your ISP performance and excluding and interference from your
home network. An old PC with Linux installed is a great option for this.

### Datastore

The collection of the metrics is stored in a Datastore to cache for use. There are multiple datastores available:

- `NONE`: No cache
- `FILE`: Stores cache in a local (or mounted) volume.
- `REDIS`: Stores cache in Redis
- `MONGODB`: Stores cache in MongoDB database collection.
- `MQTT`: Stores cache in MQTT Broker.
- `HTTP`: Performs a `GET` to retrieve, and a `POST` to save the data

### Environment Variables

> [!NOTE]
> The order of importance for configuration values is as follows:
>
> 1. Environment Variable Value
> 1. Configuration File Value
> 1. Default Value

<!-- markdownlint-disable MD013 -->
| NAME | DESCRIPTION | YAML PATH | TYPE | DEFAULT |
|----------|----------|----------|------|---------|
| `NP_CONFIG_FILE`               | The path to the yaml config file        |                                  | `string`    | `/config/netprobe.yaml` |
| `NP_DATASTORE_PROBE_TYPE`      | The PROBE datastore type                | `$.datastore.probe.type`         | `string`    | `FILE`                  |
| `NP_DATASTORE_SPEEDTEST_TYPE`  | The SPEEDTEST datastore type            | `$.datastore.speedtest.type`     | `string`    | `FILE`                  |
| `NP_DATASTORE_NETPROBE_TOPIC`  | Datastore PROBE topic name              | `$.datastore.probe.topic`        | `string`    | `netprobe/probe`        |
| `NP_DATASTORE_SPEEDTEST_TOPIC` | Datastore SPEEDTEST topic name          | `$.datastore.speedtest.topic`    | `string`    | `netprobe/speedtest`    |
| `NP_FILE_DATASTORE_PATH`       | Root path for the file datastore        | `$.datastore.file.path`          | `string`    | `/data/cache`           |
| `NP_HTTP_READ_URL`             | read URL                                | `$.datastore.http.read.url`      | `string`    | `''`                    |
| `NP_HTTP_WRITE_URL`            | write URL                               | `$.datastore.http.write.url`     | `string`    | `''`                    |
| `NP_HTTP_READ_METHOD`          | read method                             | `$.datastore.http.read.method`   | `string`    | `GET`                   |
| `NP_HTTP_WRITE_METHOD`         | write method                            | `$.datastore.http.write.method`  | `string`    | `POST`                  |
| `NP_HTTP_READ_HEADERS`         | headers                                 | `$.datastore.http.read.headers`  | `dict`      | `{}`                    |
| `NP_HTTP_WRITE_HEADERS`        | headers                                 | `$.datastore.http.write.headers` | `dict`      | `{}`                    |
| `NP_HTTP_READ_TIMEOUT`         | timeout                                 | `$.datastore.http.read.timeout`  | `int`       | `5`                     |
| `NP_HTTP_WRITE_TIMEOUT`        | timeout                                 | `$.datastore.http.write.timeout` | `int`       | `5`                     |
| `NP_HTTP_READ_AUTH`            | auth object                             | `$.datastore.http.read.auth`     | `dict`      | `{}`                    |
| `NP_HTTP_WRITE_AUTH`           | auth object                             | `$.datastore.http.write.auth`    | `dict`      | `{}`                    |
| `NP_HTTP_READ_COOKIES`         | cookies object                          | `$.datastore.http.read.cookies`  | `dict`      | `{}`                    |
| `NP_HTTP_WRITE_COOKIES`        | cookies object                          | `$.datastore.http.write.cookies` | `dict`      | `{}`                    |
| `NP_HTTP_READ_PARAMS`          | params                                  | `$.datastore.http.read.params`   | `dict`      | `{}`                    |
| `NP_HTTP_WRITE_PARAMS`         | params                                  | `$.datastore.http.write.params`  | `dict`      | `{}`                    |
| `NP_HTTP_VERIFY_SSL`           | flag for validating ssl                 | `$.datastore.http.verify_ssl`    | `bool`      | `true`                  |
| `NP_LOG_LEVEL`                 | Minimum output log level                | `$.logging.level`                | `string`    | `INFO`                  |
| `NP_LOG_FORMAT`                | Log output format                       | `$.logging.format`               | `string`    | `%(asctime)s [%(levelname)s] [%(name)s] %(message)s` |
| `NP_LOG_DATE_FORMAT`           | Log date format                         | `$.logging.date_format`          | `string`    | `%Y-%m-%d %H:%M:%S`     |
| `NP_MQTT_HOST`                 | MQTT hostname                           | `$.datastore.mqtt.host`          | `string`    | `localhost`             |
| `NP_MQTT_PORT`                 | MQTT port                               | `$.datastore.mqtt.port`          | `int`       | `1833`                  |
| `NP_MQTT_USERNAME`             | MQTT auth username                      | `$.datastore.mqtt.username`      | `string`    | `''`                    |
| `NP_MQTT_PASSWORD`             | MQTT auth password                      | `$.datastore.mqtt.password`      | `string`    | `''`                    |
| `NP_MONGODB_URL`               | Mongodb URL                             | `$.datastore.mongodb.url`        | `string`    | `mongodb://localhost:27017/admin` |
| `NP_MONGODB_DB`                | Mongodb database name                   | `$.datastore.mongodb.db`         | `string`    | `netprobe`              |
| `NP_MONGODB_COLLECTION`        | Mongodb database collection             | `$.datastore.mongodb.collection` | `string`    | `netprobe`              |
| `NP_PRESENTATION_PORT`         | Listen port for metrics server          | `$.presentation.port`            | `int`       | `5000`                  |
| `NP_PRESENTATION_INTERFACE`    | Interface to bind for listening         | `$.presentation.interface`       | `string`    | `0.0.0.0`               |
| `NP_PROBE_ENABLED`             | Enable the network probe                | `$.probe.enabled`                | `bool`      | `true`                  |
| `NP_PROBE_COUNT`               | Number of probes to execute             | `$.probe.count`                  | `int`       | `50`                    |
| `NP_DEVICE_ID`                 | Name used as namespace for metrics      | `$.probe.device_id`              | `string`    | `netprobe`              |
| `NP_PROBE_DNS_TEST_SITE`       | Domain to perform DNS resolve           | `$.probe.dns.test`               | `string`    | `google.com`            |
| `NP_PROBE_INTERVAL`            | How often to execute probe (seconds)    | `$.probe.interval`               | `int`       | `30`                    |
| `NP_SITES`                     | Comma separated list of domains to test | `$.probe.sites`                  | `list[str]` |                         |
| `NP_REDIS_HOST`                | Redis hostname                          | `$.datastore.redis.host`         | `string`    | `localhost`             |
| `NP_SPEEDTEST_ENABLED`         | Enable or disable speed test            | `$.speedtest.enabled`            | `bool`      | `False`                 |
| `NP_SPEEDTEST_INTERVAL`        | Interval between speed tests            | `$.speedtest.interval`           | `int`       | `3600`                  |
| `NP_DNS_NAMESERVER_4_IP`       | IPv4 address of DNS server              | `$.dns.nameserver_4_ip`          | `string`    | `8.8.8.8`               |
| `NP_DNS_NAMESERVER_6_IP`       | IPv6 address of DNS server              | `$.dns.nameserver_6_ip`          | `string`    | `2001:4860:4860::8888`  |
<!-- markdownlint-enable MD013 -->
### Configuration via file

A configuration file can be used. The default location is `/config/netprobe.yaml`.

See [sample.netprobe.yaml](sample.netprobe.yaml) file for example configuration.

`NP_CONFIG_FILE` environment variable can be set to change the path of the configuration file.

> [!NOTE]
> The order of importance for configuration values is as follows:
>
> 1. Environment Variable Value
> 1. Configuration File Value
> 1. Default Value

## Installation

## How to use

1. Navigate to: `http://x.x.x.x:3001/d/app/netprobe` where x.x.x.x = IP of the probe machine running Docker.

1. Default user / pass is 'admin/admin'. Login to Grafana and set a custom password.

## How to customize

### Enable Speedtest

By default the speed test feature is disabled as many users pay for bandwidth usage (e.g. cellular connections). To
enable it, edit the .env file to set the option to 'True':

``` shell
NP_SPEEDTEST_ENABLED="True"
```

Note: speedtest.net has a limit on how frequently you can connection and run the test. If you set the test to run too
frequently, you will receive errors. Recommend leaving the `NP_SPEEEDTEST_INTERVAL` unchanged.

### Customize DNS test

If the DNS server your network uses is not already monitored, you can add your DNS server IP for testing.

To do so, modify this line in .env:

``` shell
NP_DNS_NAMESERVER_4_IP="8.8.8.8" # Replace this IP with the DNS server you use at home
```

Change 8.8.8.8 to the IP of the DNS server you use, then restart the application
(docker compose down / docker compose up)

## CALCULATIONS

> [!NOTE]
> The coefficient of variation (CV) is a statistic that compares the standard deviation of a data set
> to its mean. It's calculated by dividing the standard deviation by the mean, and is often expressed
> as a percentage. The CV is used to compare data sets that have different units or means.

``` math
  cv\_loss=\frac{\langle loss \rangle}{loss\_threshold}
```

``` math
  cv\_jitter=\frac{\langle jitter \rangle}{jitter\_threshold}
```

``` math
  cv\_latency=\frac{\langle latency \rangle}{latency\_threshold}
```

``` math
  cv\_internal\_dns\_latency=\frac{\langle internal\_dns\_latency \rangle}{internal\_dns\_latency\_threshold}
```

``` math
  cv\_external\_dns\_latency=\frac{\langle external\_dns\_latency \rangle}{external\_dns\_latency\_threshold}
```

``` math
  cv\_download=\frac{download}{download\_threshold}
```

``` math
  cv\_upload=\frac{upload}{upload\_threshold}

```

---

Final Score:

``` math
overall\_score=\left(1-weight\_loss \ast cv\_loss\right)-\left(weight\_jitter \ast cv\_jitter\right)
```

``` math
-\left(weight\_latency \ast cv\_latency\right)
```

``` math
-\left(weight\_internal_dns\_latency \ast cv\_internal\_dns\_latency\right)
```

``` math
-\left(weight\_external_dns\_latency \ast cv\_external\_dns\_latency\right)
```

``` math
-\left(weight\_speedtest\_download \ast cv\_download\right)
```

``` math
-\left(weight\_speedtest\_upload \ast cv\_upload\right)
```

## DASHBOARD

The [dashboards](dashboards) path contains both a dashboard that makes use of the speed test in
netprobe_lite and using speedtest exporter.

![Dashboard 1](assets/dashboard1.png)
![Dashboard 2](assets/dashboard2.png)
![Dashboard 3](assets/dashboard3.png)
![Dashboard 4](assets/dashboard4.png)
![Dashboard 5](assets/dashboard5.png)

## License

This project is released under a custom license that restricts commercial use. You are free to use, modify,
and distribute the software for non-commercial purposes. Commercial use of this software is strictly prohibited
without prior permission. If you have any questions or wish to use this software commercially, please contact
[plaintextpackets@gmail.com](mailto:plaintextpackets@gmail.com).
