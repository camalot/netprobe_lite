# Data presentation service (prometheus)
import json
import os
import time
import traceback

from config import PresentationConfiguration
from enums.SpeedTestCacheTypes import SpeedTestCacheTypes
from helpers.logging import setup_logging
from helpers.mqtt import MqttDataStore
from helpers.redis import RedisDataStore
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily, InfoMetricFamily



class CustomCollector(object):
    def __init__(self):
        # Namespace for the metrics
        self.logger = setup_logging()
        self.presentation = PresentationConfiguration()

        self.namespace = self.safe_name(self.presentation.device_id)
        pass

    def safe_name(self, name):
        return name.replace(' ', '_').replace('.', '_').replace('-', '_').lower()

    def metric_safe_name(self, name):
        safe_name = self.safe_name(name)
        return f'{self.namespace}_{safe_name}'

    def collect(self):

        data_store = None

        if self.presentation.speedtest.cache_type == SpeedTestCacheTypes.REDIS:
            try:
                data_store = RedisDataStore()
                data_store_topic = "speedtest"
            except Exception as e:
                self.logger.error('Could not connect to Redis')
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
        elif self.presentation.speedtest.cache_type == SpeedTestCacheTypes.MQTT:
            try:
                data_store = MqttDataStore()
            except Exception as e:
                self.logger.error('Could not connect to MQTT')
                self.logger.error(e)
                self.logger.error(traceback.format_exc())
        if not data_store:
            return

        # Retrieve Netprobe data
        results_netprobe = data_store.read(self.presentation.device_id)  # Get the latest results from Redis

        if results_netprobe:
            stats_netprobe = json.loads(json.loads(results_netprobe))
        else:
            return

        g = GaugeMetricFamily(
            self.metric_safe_name('network_stats'),
            'Network statistics for latency and loss from the probe to the destination',
            labels=['type', 'target'],
        )

        total_latency = 0  # Calculate these in presentation rather than prom to reduce cardinality
        total_loss = 0
        total_jitter = 0

        average_jitter = 0
        average_loss = 0
        average_latency = 0

        for item in stats_netprobe['stats']:  # Expose each individual latency / loss metric for each site tested
            g.add_metric(['latency', item['site']], item['latency'])
            g.add_metric(['loss', item['site']], item['loss'])
            g.add_metric(['jitter', item['site']], item['jitter'])

            total_latency += float(item['latency'])
            total_loss += float(item['loss'])
            total_jitter += float(item['jitter'])

        average_latency = total_latency / len(stats_netprobe['stats'])
        average_loss = total_loss / len(stats_netprobe['stats'])
        average_jitter = total_jitter / len(stats_netprobe['stats'])
        yield g

        h = GaugeMetricFamily(
            self.metric_safe_name('dns_stats'),
            'DNS performance statistics for various DNS servers',
            labels=['server', 'ip', 'type'],
        )

        local_dns_latency = 0
        ext_dns_latency = 0
        local_dns = []
        ext_dns = []
        for item in stats_netprobe['dns_stats']:
            labels = [item['nameserver'], item['nameserver_ip'], item['type']]
            h.add_metric(labels, item['latency'])

            # find them by type, and then get the average of the latency
            if item['type'].lower() == 'internal':
                local_dns.append(float(item['latency']))
            else:
                ext_dns.append(float(item['latency']))

        local_dns_latency = sum(local_dns) / len(local_dns)
        ext_dns_latency = sum(ext_dns) / len(ext_dns)
        yield h


        # Retrieve Speedtest data
        results_speedtest = data_store.read(data_store_topic)  # Get the latest results from Redis

        if results_speedtest:  # Speed test is optional
            stats_speedtest = json.loads(json.loads(results_speedtest))

            s = GaugeMetricFamily(
                self.metric_safe_name('speed_stats'),
                'Speedtest performance statistics from speedtest.net',
                labels=['direction'],
            )

            for key in stats_speedtest['speed_stats'].keys():
                if stats_speedtest['speed_stats'][key]:
                    s.add_metric([key], stats_speedtest['speed_stats'][key])

            yield s

        # Calculate overall health score
        weight_loss = self.presentation.weight_loss  # Loss is 60% of score
        weight_latency = self.presentation.weight_latency  # Latency is 15% of score
        weight_jitter = self.presentation.weight_jitter  # Jitter is 20% of score
        # weight_dns_latency = presentation.weight_dns_latency  # DNS latency is 5% of score
        weight_internal_dns_latency = self.presentation.weight_internal_dns_latency  # Internal DNS latency is 2.5% of score
        weight_external_dns_latency = self.presentation.weight_external_dns_latency  # External DNS latency is 2.5% of score

        weight_speedtest_download = self.presentation.weight_speedtest_download
        weight_speedtest_upload = self.presentation.weight_speedtest_upload

        g_score_weight = GaugeMetricFamily(
            self.metric_safe_name('weight'),
            'Network Score Weights',
            labels=['type'],
        )

        g_score_weight.add_metric(['loss'], weight_loss)
        g_score_weight.add_metric(['latency'], weight_latency)
        g_score_weight.add_metric(['jitter'], weight_jitter)
        g_score_weight.add_metric(['internal_dns_latency'], weight_internal_dns_latency)
        g_score_weight.add_metric(['external_dns_latency'], weight_external_dns_latency)
        g_score_weight.add_metric(['speedtest_download'], weight_speedtest_download)
        g_score_weight.add_metric(['speedtest_upload'], weight_speedtest_upload)
        yield g_score_weight

        threshold_loss = self.presentation.threshold_loss  # 5% loss threshold as max
        threshold_latency = self.presentation.threshold_latency  # 100ms latency threshold as max
        threshold_jitter = self.presentation.threshold_jitter  # 30ms jitter threshold as max
        # threshold_dns_latency = self.presentation.threshold_dns_latency  # 100ms dns latency threshold as max
        threshold_internal_dns_latency = self.presentation.threshold_internal_dns_latency  # 100ms internal dns latency threshold as max
        threshold_external_dns_latency = self.presentation.threshold_external_dns_latency  # 100ms external dns latency threshold as max

        threshold_speedtest_download = self.presentation.threshold_speedtest_download
        threshold_speedtest_upload = self.presentation.threshold_speedtest_upload

        g_score_thresholds = GaugeMetricFamily(
            self.metric_safe_name('threshold'),
            'Network Score Thresholds',
            labels=['type'],
        )

        g_score_thresholds.add_metric(['loss'], threshold_loss)
        g_score_thresholds.add_metric(['latency'], threshold_latency)
        g_score_thresholds.add_metric(['jitter'], threshold_jitter)
        g_score_thresholds.add_metric(['internal_dns_latency'], threshold_internal_dns_latency)
        g_score_thresholds.add_metric(['external_dns_latency'], threshold_external_dns_latency)
        g_score_thresholds.add_metric(['speedtest_download'], threshold_speedtest_download)
        g_score_thresholds.add_metric(['speedtest_upload'], threshold_speedtest_upload)

        yield g_score_thresholds

        eval_loss = 1 if average_loss / threshold_loss >= 1 else average_loss / threshold_loss
        eval_latency = 1 if average_latency / threshold_latency >= 1 else average_latency / threshold_latency
        eval_jitter = 1 if average_jitter / threshold_jitter >= 1 else average_jitter / threshold_jitter
        eval_external_dns_latency = (
            1 if ext_dns_latency / threshold_external_dns_latency >= 1
            else ext_dns_latency / threshold_external_dns_latency
        )
        eval_internal_dns_latency = (
            1 if local_dns_latency / threshold_internal_dns_latency >= 1
            else local_dns_latency / threshold_internal_dns_latency
        )

        # if average_loss / threshold_loss >= 1:
        #     eval_loss = 1
        # else:
        #     eval_loss = average_loss / threshold_loss

        # if average_latency / threshold_latency >= 1:
        #     eval_latency = 1
        # else:
        #     eval_latency = average_latency / threshold_latency

        # if average_jitter / threshold_jitter >= 1:
        #     eval_jitter = 1
        # else:
        #     eval_jitter = average_jitter / threshold_jitter

        # if ext_dns_latency / threshold_external_dns_latency >= 1:
        #     eval_external_dns_latency = 1
        # else:
        #     eval_external_dns_latency = ext_dns_latency / threshold_external_dns_latency

        # if local_dns_latency / threshold_internal_dns_latency >= 1:
        #     eval_internal_dns_latency = 1
        # else:
        #     eval_internal_dns_latency = local_dns_latency / threshold_internal_dns_latency

        g_cv = GaugeMetricFamily(
            self.metric_safe_name('coefficient'),
            'Network Score Coefficients',
            labels=['type'],
        )
        g_cv.add_metric(['loss'], eval_loss)
        g_cv.add_metric(['latency'], eval_latency)
        g_cv.add_metric(['jitter'], eval_jitter)
        g_cv.add_metric(['internal_dns_latency'], eval_internal_dns_latency)
        g_cv.add_metric(['external_dns_latency'], eval_external_dns_latency)

        yield g_cv

        # Master scoring function
        score = (
            (1 - weight_loss * eval_loss)
            - (weight_jitter * eval_jitter)
            - (weight_latency * eval_latency)
            - (weight_internal_dns_latency * eval_internal_dns_latency)
            - (weight_external_dns_latency * eval_external_dns_latency)
        )

        i = GaugeMetricFamily(self.metric_safe_name('health_score'), 'Overall internet health function')
        i.add_metric(['health'], score)

        yield i


class NetProbePresentation:
    def __init__(self):
        self.logger = setup_logging()
        self.presentation = PresentationConfiguration()

    def run(self):
        interface=self.presentation.interface
        port=self.presentation.port
        self.logger.debug('Starting presentation service')
        start_http_server(port, addr=interface)
        self.logger.info(
            f'Listening => {interface}:{port}'
        )
        REGISTRY.register(CustomCollector())
        while True:
            time.sleep(15)
