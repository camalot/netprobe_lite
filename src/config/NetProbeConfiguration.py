import os
import re

from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class NetProbeConfiguration:
    def __init__(self, base: dict = {}):
        self.enabled = EnvVars.PROBE_ENABLED.boolean(
            YamlVars.PROBE_ENABLED.boolean(base, ConfigurationDefaults.PROBE_ENABLED)
        )
        self.interval = EnvVars.PROBE_INTERVAL.integer(
            YamlVars.PROBE_INTERVAL.integer(base, ConfigurationDefaults.PROBE_INTERVAL)
        )
        self.count = EnvVars.PROBE_COUNT.integer(YamlVars.PROBE_COUNT.integer(base, ConfigurationDefaults.PROBE_COUNT))

        sites = EnvVars.PROBE_SITES.list(',', list())
        if not sites or len(sites) == 0:
            sites = YamlVars.PROBE_SITES.list(base, ConfigurationDefaults.PROBE_SITES)

        self.sites = sites
        self.dns_test_site = EnvVars.PROBE_DNS_TEST_SITE.string(
            YamlVars.PROBE_DNS_TEST_SITE.string(base, ConfigurationDefaults.PROBE_DNS_TEST_SITE)
        )
        self.device_id = (
            str(
                EnvVars.PROBE_DEVICE_ID.string(
                    YamlVars.PROBE_DEVICE_ID.string(base, ConfigurationDefaults.PROBE_DEVICE_ID)
                )
            )
            .replace(' ', '_')
            .replace('.', '_')
            .replace('-', '_')
            .lower()
        )

        # get all environment variables that match the pattern DNS_NAMESERVER_\d{1,}
        # and create a list of tuples with the nameserver and the IP
        self.nameservers = []
        match_pattern_external = r'^NP_DNS_NAMESERVER_(\d{1,})$'
        match_pattern_local = r'^NP_LOCAL_DNS_NAMESERVER_(\d{1,})$'
        for key, value in os.environ.items():
            m = re.match(match_pattern_external, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if m:
                # get the nameserver number from the match
                index = m.group(1)
                label = value if value else f"EXTERNAL DNS NAMESERVER {index}"
                ip = EnvVars.unquote(os.getenv(f'NP_DNS_NAMESERVER_{index}_IP', None))
                if ip and label:
                    self.nameservers.append((EnvVars.unquote(label), ip, 'external'))
            m = re.match(match_pattern_local, key, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if m:
                index = m.group(1)
                label = value if value else f"INTERNAL DNS NAMESERVER {index}"
                ip = EnvVars.unquote(os.getenv(f'NP_LOCAL_DNS_NAMESERVER_{index}_IP', None))
                if ip and label:
                    self.nameservers.append((EnvVars.unquote(label), ip, 'internal'))

        # singular local dns
        NP_LOCAL_DNS = EnvVars.unquote(os.getenv('NP_LOCAL_DNS', None))
        NP_LOCAL_DNS_IP = EnvVars.unquote(os.getenv('NP_LOCAL_DNS_IP', None))

        if NP_LOCAL_DNS and NP_LOCAL_DNS_IP:
            self.nameservers.append((NP_LOCAL_DNS, NP_LOCAL_DNS_IP, "internal"))

        external_dns = YamlVars.PROBE_EXTERNAL_DNS.expand(base, [])
        internal_dns = YamlVars.PROBE_LOCAL_DNS.expand(base, [])

        if external_dns and isinstance(external_dns, list):
            for dns in external_dns:
                if "name" in dns and "ip" in dns:
                    # make sure its not already in the list
                    if not any(d[1] == dns['ip'] for d in self.nameservers):
                        self.nameservers.append((dns['name'], dns['ip'], "external"))

        if internal_dns and isinstance(internal_dns, list):
            for dns in internal_dns:
                if "name" in dns and "ip" in dns:
                    # make sure its not already in the list
                    if not any(d[1] == dns['ip'] for d in self.nameservers):
                        self.nameservers.append((dns['name'], dns['ip'], "internal"))

    def merge(self, config: dict):
        self.__dict__.update(config)
