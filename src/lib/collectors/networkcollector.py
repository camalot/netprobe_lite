import json
import os
import re
import subprocess
import traceback
import typing
from threading import Thread

import dns.resolver
from lib.collectors.basecollector import BaseCollector


class NetworkCollector(BaseCollector):  # Main network collection class
    def __init__(self, sites: list[str], count: int, dns_test_site: str, nameservers: list[tuple[str, str, str]]):
        super().__init__()
        self.sites = sites  # List of sites to ping
        self.count = str(count)  # Number of pings
        self.stats = []  # List of stat dicts
        self.dnsstats = []  # List of stat dicts
        self.dns_test_site = dns_test_site  # Site used to test DNS response times
        self.nameservers = nameservers

    def pingtest(self, count, site) -> bool:
        ping = None
        if os.name == "nt":
            # This is only for testing purposes locally.
            self.logger.warning("Windows detected, using fake ping")
            try:
                ping = """10 packets transmitted, 10 received, 0% packet loss, time 9011ms
rtt min/avg/max/mdev = 11.487/12.915/14.475/1.095 ms"""
            except Exception as e:
                self.logger.error(f"Error pinging {site}")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
                return False
        else:
            try:
                ping = subprocess.getoutput(f"ping -n -i 0.1 -c {count} {site} | grep 'rtt\\|loss'")
                # 10 packets transmitted, 10 received, 0% packet loss, time 9011ms
                # rtt min/avg/max/mdev = 11.487/12.915/14.475/1.095 ms

                # logger.debug(ping)
                # loss = ping.split(' ')[5].strip('%')
                # latency = ping.split('/')[4]
                # jitter = ping.split('/')[6].split(' ')[0]

            except Exception as e:
                self.logger.error(f"Error pinging {site}")
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
                return False

        if ping is None:
            self.logger.error(f"Error pinging {site}. No output from ping command")
            return False

        try:
            self.logger.debug(ping)
            loss_regex = re.compile(r"(\d+)% packet loss", re.MULTILINE | re.DOTALL | re.IGNORECASE)
            latency_regex = re.compile(
                r"^rtt\s.*?(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)\sms", re.MULTILINE | re.DOTALL | re.IGNORECASE
            )

            loss_match = loss_regex.search(ping)
            latency_match = latency_regex.search(ping)
            loss = 0
            latency = 0
            jitter = 0

            if loss_match:
                loss = float(loss_match.group(1))
            else:
                loss = -1
                self.logger.critical("Ping output did not match expected format")
            if latency_match:
                latency = float(latency_match.group(2))
                jitter = float(latency_match.group(4))
            else:
                self.logger.critical("Ping output did not match expected format")
                latency = -1
                jitter = -1

            # check that the values are valid
            if loss >= 0 or latency == 0 or jitter == 0:
                netdata = {"site": site, "latency": latency, "loss": loss, "jitter": jitter}
                self.logger.debug(json.dumps(netdata, indent=4))
                self.stats.append(netdata)
            else:
                self.logger.warning(f"Invalid ping results for {site}")

        except Exception as e:
            self.logger.error(f"Error parsing ping output for {site}")
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            return False

        return True

    def dnstest(self, site, nameserver) -> bool:
        resolver = dns.resolver.Resolver()
        server = []  # Resolver needs a list
        server.append(nameserver[1])

        try:
            resolver.nameservers = server
            resolver.timeout = 10
            answers = resolver.query(site, 'A')

            dns_latency = round(answers.response.time * 1000, 2)

            dnsdata = {
                "nameserver": nameserver[0],
                "nameserver_ip": nameserver[1],
                "type": nameserver[2] if len(nameserver) == 3 else "external",
                "latency": dns_latency,
            }

            self.dnsstats.append(dnsdata)

        except Exception as e:
            self.logger.error(f"Error performing DNS resolution on {nameserver}")
            self.logger.error(e)
            self.logger.error(traceback.format_exc())

            # dnsdata = {
            #     "nameserver": nameserver[0],
            #     "nameserver_ip": nameserver[1],
            #     "type": nameserver[2] if len(nameserver) == 3 else "external",
            #     "latency": 5000,
            # }

            # self.dnsstats.append(dnsdata)

        return True

    def collect(self) -> typing.Optional[dict]:
        try:
            # Empty preveious results
            self.stats = []
            self.dnsstats = []

            # Create threads, start them
            threads = []

            for item in self.sites:
                t = Thread(target=self.pingtest, args=(self.count, item))
                threads.append(t)
                t.start()

            # Wait for threads to complete
            for t in threads:
                t.join()

            # Create threads, start them
            threads = []

            for item in self.nameservers:
                s = Thread(target=self.dnstest, args=(self.dns_test_site, item))
                threads.append(s)
                s.start()

            # Wait for threads to complete
            for s in threads:
                s.join()

            results = {"stats": self.stats, "dns_stats": self.dnsstats}

            return results
        except Exception as e:
            self.logger.error("Error collecting network stats")
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            return None
