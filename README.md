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
| `NP_REDIS_HOST` | The hostname/port to connect to redis. | `netprobe-redis` |
| `NP_REDIS_PORT` | The port to connect to redis. | `6379` |
| `NP_REDIS_PASSWORD` | The password to connect to redis. | `password` |
| `NP_REDIS_DB` | The redis DB index | `0` |
| `NP_PROBE_COUNT` | The number of checks to run against the tests | `50` |
| `NP_PROBE_INTERVAL` | The interval at which the system probes | `30` |
| `NP_DEVICE_ID` | This is used as the "namespace" in prometheus | `netprobe` |

### Configuration via file

TODO

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

## License

This project is released under a custom license that restricts commercial use. You are free to use, modify,
and distribute the software for non-commercial purposes. Commercial use of this software is strictly prohibited
without prior permission. If you have any questions or wish to use this software commercially, please contact
[plaintextpackets@gmail.com](mailto:plaintextpackets@gmail.com).
