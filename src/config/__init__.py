import os
import re
import typing
import yaml
from dotenv import find_dotenv, load_dotenv


# Load configs from env
try: # Try to load env vars from file, if fails pass
    load_dotenv(find_dotenv())
except:
    pass

class Configuration():
    def __init__(self, file_path: typing.Optional[str] = None):

        # if file_path exists and is not none, load the file
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.config = yaml.safe_load(file)
            

        self.netprobe = Config_Netprobe()
        self.redis = Config_Redis()
        self.presentation = Config_Presentation()

# Create class for each

class Config_Netprobe():
    probe_interval = int(os.getenv('PROBE_INTERVAL', '30'))
    probe_count = int(os.getenv('PROBE_COUNT', '50'))
    sites = os.getenv('SITES', 'google.com,facebook.com,twitter.com,youtube.com,amazon.com').split(',')
    dns_test_site = os.getenv('DNS_TEST_SITE', 'google.com')
    speedtest_enabled = bool(os.getenv("SPEEDTEST_ENABLED", 'FALSE').lower() in ('true', '1', 't', 'y', 'yes'))
    speedtest_interval = int(os.getenv('SPEEDTEST_INTERVAL', '937'))

    log_path = os.getenv('LOG_PATH', './logs')

    # get all environment variables that match the pattern DNS_NAMESERVER_\d{1,}
    # and create a list of tuples with the nameserver and the IP
    nameservers = []
    match_pattern = r'^DNS_NAMESERVER_(\d{1,})$'
    for key, value in os.environ.items():
        print(f'key: {key}, value: {value}')
        m = re.match(match_pattern, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if m:
            # get the nameserver number from the match
            nameserver = m.group(1)
            nameservers.append((value, os.getenv(f'DNS_NAMESERVER_{nameserver}_IP', f'DNS NAMESERVER {nameserver}')))

    NP_LOCAL_DNS = os.getenv('NP_LOCAL_DNS', None)
    NP_LOCAL_DNS_IP = os.getenv('NP_LOCAL_DNS_IP', None)

    if NP_LOCAL_DNS and NP_LOCAL_DNS_IP:
        nameservers.append((NP_LOCAL_DNS, NP_LOCAL_DNS_IP))


class Config_Redis():
    redis_url = os.getenv('REDIS_URL', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    redis_password = os.getenv('REDIS_PASSWORD', 'password')
    log_path = os.getenv('LOG_PATH', './logs')

class Config_Presentation():
    presentation_port = int(os.getenv('PRESENTATION_PORT', '5000'))
    presentation_interface = os.getenv('PRESENTATION_INTERFACE', '0.0.0.0')
    device_id = os.getenv('DEVICE_ID', 'netprobe')
    log_path = os.getenv('LOG_PATH', './logs')

    local_dns_name = os.getenv('NP_LOCAL_DNS', None)

    weight_loss = float(os.getenv('weight_loss', '.6'))
    weight_latency = float(os.getenv('weight_latency', '.15'))
    weight_jitter = float(os.getenv('weight_jitter', '.2'))
    weight_dns_latency = float(os.getenv('weight_dns_latency', '.05'))

    threshold_loss = int(os.getenv('threshold_loss', '5'))
    threshold_latency = int(os.getenv('threshold_latency', '100'))
    threshold_jitter = int(os.getenv('threshold_jitter', '30'))
    threshold_dns_latency = int(os.getenv('threshold_dns_latency', '100'))