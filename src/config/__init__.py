import logging
import os
import re
import typing

import yaml
from dotenv import find_dotenv, load_dotenv

# Load configs from env
try:  # Try to load env vars from file, if fails pass
    load_dotenv(find_dotenv())
except:  # noqa: E722
    pass


class Configuration:
    def __init__(self, file_path: typing.Optional[str] = '/app/config/netprobe.yaml'):

        self.netprobe = NetprobeConifguration()
        self.redis = RedisConfiguration()
        self.presentation = PresentationConfiguration()
        self.logging = LoggingConfiguration()


        # if file_path exists and is not none, load the file
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.__dict__.update(yaml.safe_load(file))


class LoggingConfiguration:
    def __init__(self):
        log_level = os.getenv('NP_LOG_LEVEL', 'INFO').upper()
        self.level = getattr(logging, log_level, logging.INFO)
        self.format = os.getenv('NP_LOG_FORMAT', '%(asctime)s %(levelname)s %(message)s')

    def merge(self, config: dict):
        self.__dict__.update(config)

# Create class for each
class NetprobeConifguration:
    probe_interval = int(os.getenv('NP_PROBE_INTERVAL', '30'))
    probe_count = int(os.getenv('NP_PROBE_COUNT', '50'))
    sites = os.getenv('NP_SITES', 'google.com,facebook.com,twitter.com,youtube.com').split(',')
    dns_test_site = os.getenv('NP_DNS_TEST_SITE', 'google.com')
    speedtest_enabled = bool(os.getenv("NP_SPEEDTEST_ENABLED", 'FALSE').lower() in ('true', '1', 't', 'y', 'yes'))
    speedtest_interval = int(os.getenv('NP_SPEEDTEST_INTERVAL', '937'))
    device_id = os.getenv('NP_DEVICE_ID', 'netprobe').replace(' ', '_').replace('.', '_').replace('-', '_').lower()

    # get all environment variables that match the pattern DNS_NAMESERVER_\d{1,}
    # and create a list of tuples with the nameserver and the IP
    nameservers = []
    match_pattern_external = r'^NP_DNS_NAMESERVER_(\d{1,})$'
    match_pattern_local = r'^NP_LOCAL_DNS_NAMESERVER_(\d{1,})$'
    for key, value in os.environ.items():
        m = re.match(match_pattern_external, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if m:
            # get the nameserver number from the match
            index = m.group(1)
            label = value if value else f"EXTERNAL DNS NAMESERVER {index}"
            ip = os.getenv(f'NP_DNS_NAMESERVER_{index}_IP', None)
            if ip and label:
                nameservers.append((label, ip, 'external'))
        m = re.match(match_pattern_local, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if m:
            index = m.group(1)
            label = value if value else f"INTERNAL DNS NAMESERVER {index}"
            ip = os.getenv(f'NP_LOCAL_DNS_NAMESERVER_{index}_IP', None)
            if ip and label:
                nameservers.append((label, ip, 'internal'))

    # singular local dns
    NP_LOCAL_DNS = os.getenv('NP_LOCAL_DNS', None)
    NP_LOCAL_DNS_IP = os.getenv('NP_LOCAL_DNS_IP', None)

    if NP_LOCAL_DNS and NP_LOCAL_DNS_IP:
        nameservers.append((NP_LOCAL_DNS, NP_LOCAL_DNS_IP, "internal"))


class RedisConfiguration:
    redis_host = os.getenv('NP_REDIS_URL', os.getenv('NP_REDIS_HOST', 'localhost'))
    redis_port = os.getenv('NP_REDIS_PORT', '6379')
    redis_password = os.getenv('NP_REDIS_PASSWORD', '')
    redis_db = os.getenv('NP_REDIS_DB', '0')


class PresentationConfiguration:
    presentation_port = int(os.getenv('NP_PRESENTATION_PORT', '5000'))
    presentation_interface = os.getenv('NP_PRESENTATION_INTERFACE', '0.0.0.0')
    device_id = os.getenv('NP_DEVICE_ID', 'netprobe')

    local_dns_name = os.getenv('NP_LOCAL_DNS', None)

    weight_loss = float(os.getenv('NP_WEIGHT_LOSS', '.6'))
    weight_latency = float(os.getenv('NP_WEIGHT_LATENCY', '.15'))
    weight_jitter = float(os.getenv('NP_WEIGHT_JITTER', '.2'))
    weight_external_dns_latency = float(os.getenv('NP_WEIGHT_INTERNAL_DNS_LATENCY', '.025'))
    weight_internal_dns_latency = float(os.getenv('NP_WEIGHT_EXTERNAL_DNS_LATENCY', '.025'))

    total_weight = sum([weight_loss, weight_latency, weight_jitter, weight_external_dns_latency, weight_internal_dns_latency])

    speedtest_weight_rebalance = os.getenv('NP_WEIGHT_SPEEDTEST_REBALANCE', 'TRUE').lower() in ('true', '1', 't', 'y', 'yes')

    if NetprobeConifguration.speedtest_enabled:
        weight_speedtest_download = float(os.getenv('NP_WEIGHT_SPEEDTEST_DOWNLOAD', '.5'))
        weight_speedtest_upload = float(os.getenv('NP_WEIGHT_SPEEDTEST_UPLOAD', '.5'))
    else:
        t_wstd = float(os.getenv('NP_WEIGHT_SPEEDTEST_DOWNLOAD', '.5'))
        t_wstu = float(os.getenv('NP_WEIGHT_SPEEDTEST_UPLOAD', '.5'))
        if total_weight < 1 and (total_weight + t_wstd + t_wstu) <= 1 and speedtest_weight_rebalance:
            # add this weight to the "loss" weight
            weight_loss += t_wstd + t_wstu

        weight_speedtest_download = 0
        weight_speedtest_upload = 0

    threshold_loss = int(os.getenv('NP_THRESHOLD_LOSS', '5'))
    threshold_latency = int(os.getenv('NP_THRESHOLD_LATENCY', '100'))
    threshold_jitter = int(os.getenv('NP_THRESHOLD_JITTER', '30'))
    # threshold_dns_latency = int(os.getenv('NP_THRESHOLD_DNS_LATENCY', '100'))
    threshold_internal_dns_latency = int(os.getenv('NP_THRESHOLD_INTERNAL_DNS_LATENCY', '100'))
    threshold_external_dns_latency = int(os.getenv('NP_THRESHOLD_EXTERNAL_DNS_LATENCY', '100'))

    if NetprobeConifguration.speedtest_enabled:
        threshold_speedtest_download = int(os.getenv('NP_THRESHOLD_SPEEDTEST_DOWNLOAD', '200'))
        threshold_speedtest_upload = int(os.getenv('NP_THRESHOLD_SPEEDTEST_UPLOAD', '200'))
    else:
        threshold_speedtest_download = 0
        threshold_speedtest_upload = 0
