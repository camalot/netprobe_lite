# Netprobe

Simple and effective tool for measuring ISP performance at home. The tool measures several performance metrics
including packet loss, latency, jitter, and DNS performance. It also has an optional speed test to measure bandwidth.
Netprobe aggregates these metrics into a common score, which you can use to monitor overall health of your internet
connection.

> [!NOTE]
> This is a [fork of Netprobe_lite](https://github.com/plaintextpackets/netprobe_lite). I did some refactoring of how the
> container is built, how the variables are set, the names of the variables, a lot of refactoring to pass lint tests, and
> other things.

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

### Environment Variables

| NAME | DESCRIPTION | DEFAULT |
| ---- | ----------- | ------- |
| `NP_MODULE` | Sets the entry point of the python application. | `FULL` |
| `NP_SITES` | Comma-separated list of domains to test | `google.com,facebook.com,twitter.com,youtube.com` |
| `NP_DNS_TEST_SITE` | A single site to test DNS | `google.com` |
| `NP_DNS_NAMESERVER_<N>` | A DNS nameserver name to test with. `<N>` is an index/number of the entry. | `Google` |
| `NP_DNS_NAMESERVER_<N>_IP` | The IP Address of the DNS nameserver that matches up with the prior value. | `8.8.8.8` |
| `NP_LOCAL_DNS_NAMESERVER_<N>` | A local/internal DNS nameserver name. `<N>` is an index/number of the entry | `Local DNS` |
| `NP_LOCAL_DNS_NAMESERVER_<N>_IP` | The IP Address of the the local DNS. | `192.168.2.1` |
| `NP_WEIGHT_DNS_LATENCY` | DNS latency weight for the score. | `0.05` |
| `NP_WEIGHT_JITTER` | Jitter weight for the score. | `0.2` |
| `NP_WEIGHT_LATENCY` | Latency weight for the score. | `0.15` |
| `NP_WEIGHT_LOSS` | Packet loss weight for the score. | `0.6` |
| `NP_THRESHOLD_DNS_LATENCY` | DNS latency threshold for score, in milliseconds. | `100` |
| `NP_THRESHOLD_JITTER` | Jitter threshold for score, in milliseconds. | `30` |
| `NP_THRESHOLD_LATENCY` | Latency threshold for score, in milliseconds. | `100` |
| `NP_THRESHOLD_LOSS` | Packet loss threshold for score, in percentage. | `5` |
| `NP_SPEEDTEST_ENABLED` | Enable/Disable speedtest runs | `false` |
| `NP_SPEEDTEST_INTERVAL` | Interval on which the speedtest will run, in seconds. | `937` |
| `NP_PRESENTATION_INTERFACE` | What interface is the prometheus metrics presented. | `0.0.0.0` |
| `NP_PRESENTATION_PORT` |  This is the port on which the presentation layer will run | `5000` |
| `NP_REDIS_PASSWORD` | The password to connect to redis. | `password` |
| `NP_REDIS_PORT` | The port to connect to redis. | `6379` |
| `NP_REDIS_URL` | The hostname/port to connect to redis. | `netprobe-redis` |
| `NP_PROBE_COUNT` | The number of checks to run against the tests | `50` |
| `NP_PROBE_INTERVAL` | The interval at which the system probes | `30` |
| `NP_DEVICE_ID` | This is used as the "namespace" in prometheus | `netprobe` |

### Configuration via file

TODO

## Installation

### First-time Install

1. Clone the repository locally to the probe machine:

``` shell
git clone https://github.com/plaintextpackets/netprobe_lite.git
```

1. From the cloned folder, use docker compose to launch the app:

```shell
source build.env && docker-compose -f docker-compose.yml -f example.docker-compose.override.yml up --build
```

1. To shut down the app, use docker compose again:

``` shell
docker compose down
```

### Upgrading Between Versions

When upgrading between versions, it is best to delete the deployment altogether and restart with the new code.
The process is described below.

1. Stop Netprobe in Docker and use the -v flag to delete all volumes (warning this deletes old data):

``` shell
docker compose down -v
```

1. Clone the latest code (or download manually from GitHub and replace the current files):

``` shell
git clone https://github.com/plaintextpackets/netprobe_lite.git
```

1. Re-start Netprobe:

``` shell
docker compose up
```

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

### Change Netprobe port

To change the port that Netprobe Lite is running on, edit the 'compose.yml' file, under the 'grafana' section:

``` yaml
ports:
    - '3001:3000'
```

Change the port on the left to the port you want to access Netprobe Lite on

### Customize DNS test

If the DNS server your network uses is not already monitored, you can add your DNS server IP for testing.

To do so, modify this line in .env:

``` shell
NP_DNS_NAMESERVER_4_IP="8.8.8.8" # Replace this IP with the DNS server you use at home
```

Change 8.8.8.8 to the IP of the DNS server you use, then restart the application
(docker compose down / docker compose up)

### Use external Grafana

Some users have their own Grafana instance running and would like to ingest Netprobe statistics there
rather than running Grafana in Docker. To do this:

1. In the compose.yaml file, add a port mapping to the Prometheus deployment config:

``` shell
  prometheus:
    ...
    ports:
      - 'XXXX:9090'
```

... where XXXX is the port you wish to expose Prometheus on your host machine

1. Remove all of the Grafana configuration from the compose.yaml file

1. Run Netprobe and then add a datasource to your existing Grafana as `http://x.x.x.x:XXXX`
where x.x.x.x = IP of the probe machine running Docker

### Data storage - default method

By default, Docker will store the data collected in several Docker volumes, which will persist between restarts.

They are:

``` shell
netprobe_grafana_data (used to store Grafana user / pw)
netprobe_prometheus_data (used to store time series data)
```

To clear out old data, you need to stop the app and remove these volumes:

``` shell
docker compose down
docker volume rm netprobe_grafana_data
docker volume rm netprobe_prometheus_data
```

When started again the old data should be wiped out.

### Data storage - bind mount method

Using the default method, the data is stored within Docker volumes which you cannot easily access from the
host itself. If you'd prefer storing data in mapped folders from the host, follow these instructions
(thank you @Jeppedy):

1. Clone the repository

1. Inside the folder create two directories:

``` shell
mkdir -p data/grafana data/prometheus
```

1. Modify the compose.yml as follows (volume path as well as adding user ID):

``` yaml
  prometheus:
    restart: always
    container_name: netprobe-prometheus
    image: "prom/prometheus"
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data/prometheus:/prometheus # modify this to map to the folder you created

    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - custom_network  # Attach to the custom network
    user: "1000" # set this to the desired user with correct permissions to the bind mount

  grafana:
    restart: always
    image: grafana/grafana-enterprise
    container_name: netprobe-grafana
    volumes:
      - ./config/grafana/datasources/automatic.yml:/etc/grafana/provisioning/datasources/automatic.yml
      - ./config/grafana/dashboards/main.yml:/etc/grafana/provisioning/dashboards/main.yml
      - ./config/grafana/dashboards/netprobe.json:/var/lib/grafana/dashboards/netprobe.json
      - ./data/grafana:/var/lib/grafana  # modify this to map to the folder you created
    ports:
      - '3001:3000'
    networks:
      - custom_network  # Attach to the custom network
    user: "1000" # set this to the desired user with correct permissions to the bind mount
```

1. Remove the volumes section from compose.yml

### Run on startup

Netprobe will automatically restart itself after the host system is rebooted, provided that Docker
is also launched on startup. If you want to disable this behavior, modify the 'restart' variables in
the compose.yaml file to this:

``` yaml
restart: never
```

### Wipe all stored data

To wipe all stored data and remove the Docker volumes, use this command:

``` shell
docker compose down -v
```

This will delete all containers and volumes related to Netprobe.

## FAQ & Troubleshooting

Q. How do I reset my Grafana password?

A. Delete the docker volume for grafana. This will reset your password but will leave your data:

``` shell
docker volume rm netprobe_grafana_data
```

Q. I am running Pihole and when I enter my host IP under `NP_DNS_NAMESERVER_4_IP=` I receive this error:

``` text
The resolution lifetime expired after 5.138 seconds: Server Do53:192.168.0.91@53 answered got a response from
('172.21.0.1', 53) instead of ('192.168.0.91', 53)
```

A. This is a limitation of Docker. If you are running another DNS server in Docker and want to test it in
Netprobe, you need to specify the Docker network gateway IP:

1. Stop netprobe but don't wipe it (docker compose down)
1. Find the gateway IP of your netprobe-probe container:

``` shell
$ docker inspect netprobe-probe | grep Gateway
  "Gateway": "",
  "IPv6Gateway": "",
  "Gateway": "192.168.208.1",
  "IPv6Gateway": "",
```

1. Enter that IP (e.g. 182.168.208.1) into your .env file for `NP_DNS_NAMESERVER_4_IP=`

Q. I constantly see one of my DNS servers at 5s latency, is this normal?

A. 5s is the timeout for DNS queries in Netprobe Lite. If you see this happening for one specific IP,
likely your machine is having issues using that DNS server (and so you shouldn't use it for home use).

## License

This project is released under a custom license that restricts commercial use. You are free to use, modify,
and distribute the software for non-commercial purposes. Commercial use of this software is strictly prohibited
without prior permission. If you have any questions or wish to use this software commercially, please contact
[plaintextpackets@gmail.com](mailto:plaintextpackets@gmail.com).
