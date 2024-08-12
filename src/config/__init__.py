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
    probe_interval = int(os.getenv('NP_PROBE_INTERVAL', '30'))
    probe_count = int(os.getenv('NP_PROBE_COUNT', '50'))
    sites = os.getenv('NP_SITES', 'google.com,facebook.com,twitter.com,youtube.com').split(',')
    dns_test_site = os.getenv('NP_DNS_TEST_SITE', 'google.com')
    speedtest_enabled = bool(os.getenv("NP_SPEEDTEST_ENABLED", 'FALSE').lower() in ('true', '1', 't', 'y', 'yes'))
    speedtest_interval = int(os.getenv('NP_SPEEDTEST_INTERVAL', '937'))
    device_id = os.getenv('NP_DEVICE_ID', 'netprobe').replace(' ', '_').replace('.', '_').replace('-', '_').lower()

    log_path = os.getenv('NP_LOGS_PATH', './logs')

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


class Config_Redis():
    redis_url = os.getenv('NP_REDIS_URL', 'localhost')
    redis_port = os.getenv('NP_REDIS_PORT', '6379')
    redis_password = os.getenv('NP_REDIS_PASSWORD', 'password')
    log_path = os.getenv('NP_LOGS_PATH', './logs')

class Config_Presentation():
    presentation_port = int(os.getenv('NP_PRESENTATION_PORT', '5000'))
    presentation_interface = os.getenv('NP_PRESENTATION_INTERFACE', '0.0.0.0')
    device_id = os.getenv('NP_DEVICE_ID', 'netprobe')
    log_path = os.getenv('NP_LOGS_PATH', './logs')

    local_dns_name = os.getenv('NP_LOCAL_DNS', None)

    weight_loss = float(os.getenv('NP_WEIGHT_LOSS', '.6'))
    weight_latency = float(os.getenv('NP_WEIGHT_LATENCY', '.15'))
    weight_jitter = float(os.getenv('NP_WEIGHT_JITTER', '.2'))
    weight_dns_latency = float(os.getenv('NP_WEIGHT_DNS_LATENCY', '.05'))

    threshold_loss = int(os.getenv('NP_THRESHOLD_LOSS', '5'))
    threshold_latency = int(os.getenv('NP_THRESHOLD_LATENCY', '100'))
    threshold_jitter = int(os.getenv('NP_THRESHOLD_JITTER', '30'))
    threshold_dns_latency = int(os.getenv('NP_THRESHOLD_DNS_LATENCY', '100'))