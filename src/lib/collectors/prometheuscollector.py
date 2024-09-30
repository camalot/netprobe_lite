import traceback

from config import Configuration
from helpers.logging import setup_logging
from lib.datastores.factory import DatastoreFactory
from lib.enums.DataStoreTypes import DataStoreTypes
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector



class PrometheusCollector(Collector):
    def __init__(self):
        # Namespace for the metrics
        self.logger = setup_logging(self.__class__.__name__)
        self.config = Configuration()

        self.namespace = self.safe_name(self.config.presentation.device_id)
        pass

    def safe_name(self, name):
        return name.replace(' ', '_').replace('.', '_').replace('-', '_').lower()

    def metric_safe_name(self, name):
        safe_name = self.safe_name(name)
        return f'{self.namespace}_{safe_name}'

    def collect(self):
        probe_data_store = None
        speedtest_data_store = None
        try:
            probe_data_store = DatastoreFactory().create(self.config.datastore.netprobe.get('type', DataStoreTypes.FILE))
        except Exception as e:
            self.logger.error('Could not connect to data store')
            self.logger.error(e)
            self.logger.error(traceback.format_exc())

        try:
            speedtest_data_store = DatastoreFactory().create(self.config.datastore.speedtest.get('type', DataStoreTypes.FILE))
        except Exception as e:
            self.logger.error('Could not connect to data store')
            self.logger.error(e)
            self.logger.error(traceback.format_exc())


        if not probe_data_store:
            self.logger.error('Could not connect to data store')
            return

        # Retrieve Netprobe data
        results_netprobe = probe_data_store.read(self.config.datastore.netprobe.get('topic', 'netprobe/probe'))

        stats_speedtest = None
        if speedtest_data_store:
            stats_speedtest = speedtest_data_store.read(self.config.datastore.speedtest.get('topic', 'netprobe/speedtest'))  # Get the latest results from Redis

        if results_netprobe:
            stats_netprobe = results_netprobe
        else:
            self.logger.debug(f"No data found in data store. Skipping.")
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

        latency_item_count = len(stats_netprobe['stats'])
        loss_item_count = len(stats_netprobe['stats'])
        jitter_item_count = len(stats_netprobe['stats'])

        for item in stats_netprobe['stats']:  # Expose each individual latency / loss metric for each site tested
            g.add_metric(['latency', item['site']], item['latency'])
            g.add_metric(['loss', item['site']], item['loss'])
            g.add_metric(['jitter', item['site']], item['jitter'])

            total_latency += float(item['latency'])
            total_loss += float(item['loss'])
            total_jitter += float(item['jitter'])

        if stats_speedtest:
            for key in stats_speedtest.keys():
                if key == 'latency' or key == 'jitter':
                    g.add_metric([key, 'speedtest'], stats_speedtest[key])
                # add speedtest jitter and latency to the total
                if key == 'latency':
                    total_latency += float(stats_speedtest[key])
                    latency_item_count += 1
                elif key == 'jitter':
                    total_jitter += float(stats_speedtest[key])
                    jitter_item_count += 1

        average_latency = total_latency / latency_item_count
        average_loss = total_loss / loss_item_count
        average_jitter = total_jitter / jitter_item_count
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

        average_local_dns_latency = sum(local_dns) / len(local_dns)
        average_ext_dns_latency = sum(ext_dns) / len(ext_dns)
        yield h

        if stats_speedtest:  # Speed test is optional
            s = GaugeMetricFamily(
                self.metric_safe_name('speed_stats'),
                'Speedtest performance statistics from speedtest.net',
                labels=['type'],
            )

            for key in stats_speedtest.keys():
                if stats_speedtest[key]:
                    s.add_metric([key], stats_speedtest[key])

            yield s

        # Calculate overall health score
        weight_loss = self.config.presentation.weight_loss  # Loss is 60% of score
        weight_latency = self.config.presentation.weight_latency  # Latency is 15% of score
        weight_jitter = self.config.presentation.weight_jitter  # Jitter is 20% of score

        weight_internal_dns_latency = self.config.presentation.weight_internal_dns_latency  # Internal DNS latency is 2.5% of score
        weight_external_dns_latency = self.config.presentation.weight_external_dns_latency  # External DNS latency is 2.5% of score

        weight_speedtest_download = self.config.presentation.weight_speedtest_download
        weight_speedtest_upload = self.config.presentation.weight_speedtest_upload

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

        threshold_loss = self.config.presentation.threshold_loss  # 5% loss threshold as max
        threshold_latency = self.config.presentation.threshold_latency  # 100ms latency threshold as max
        threshold_jitter = self.config.presentation.threshold_jitter  # 30ms jitter threshold as max

        threshold_internal_dns_latency = self.config.presentation.threshold_internal_dns_latency  # 100ms internal dns latency threshold as max
        threshold_external_dns_latency = self.config.presentation.threshold_external_dns_latency  # 100ms external dns latency threshold as max

        threshold_speedtest_download = self.config.presentation.threshold_speedtest_download
        threshold_speedtest_upload = self.config.presentation.threshold_speedtest_upload

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

        self.logger.info(f"Loss Threshold: {threshold_loss}")
        self.logger.info(f"Latency Threshold: {threshold_latency}")
        self.logger.info(f"Jitter Threshold: {threshold_jitter}")
        self.logger.info(f"Internal DNS Latency Threshold: {threshold_internal_dns_latency}")
        self.logger.info(f"External DNS Latency Threshold: {threshold_external_dns_latency}")
        self.logger.info(f"Speedtest Download Threshold: {threshold_speedtest_download}")
        self.logger.info(f"Speedtest Upload Threshold: {threshold_speedtest_upload}")

        yield g_score_thresholds
        if threshold_loss == 0:
            cv_loss = 0
        else:
            cv_loss = 1 if average_loss / threshold_loss >= 1 else average_loss / threshold_loss
        if threshold_latency == 0:
            cv_latency = 0
        else:
            cv_latency = 1 if average_latency / threshold_latency >= 1 else average_latency / threshold_latency
        if threshold_jitter == 0:
            cv_jitter = 0
        else:
            cv_jitter = 1 if average_jitter / threshold_jitter >= 1 else average_jitter / threshold_jitter
        if threshold_external_dns_latency == 0:
            cv_external_dns_latency = 0
        else:
            cv_external_dns_latency = (
                1 if average_ext_dns_latency / threshold_external_dns_latency >= 1
                else average_ext_dns_latency / threshold_external_dns_latency
            )
        if threshold_internal_dns_latency == 0:
            cv_internal_dns_latency = 0
        else:
            cv_internal_dns_latency = (
                1 if average_local_dns_latency / threshold_internal_dns_latency >= 1
                else average_local_dns_latency / threshold_internal_dns_latency
            )

        self.logger.info(f"Loss Coefficient: {cv_loss}")
        self.logger.info(f"Latency Coefficient: {cv_latency}")
        self.logger.info(f"Jitter Coefficient: {cv_jitter}")
        self.logger.info(f"External DNS Latency Coefficient: {cv_external_dns_latency}")
        self.logger.info(f"Internal DNS Latency Coefficient: {cv_internal_dns_latency}")

        # assume 0 if no speedtest data
        cv_download = 0
        cv_upload = 0
        if stats_speedtest:
            self.logger.debug(f"Speedtest Data: {stats_speedtest}")

            download = stats_speedtest['download'] if stats_speedtest['download'] else 0
            if download >= 0:
                cv_download = 1 - (
                    1 if download / threshold_speedtest_download >= 1
                    else (download / threshold_speedtest_download)
                )

            upload = stats_speedtest['upload'] if stats_speedtest['upload'] else 0
            if upload >= 0:
                cv_upload = 1 - (
                    1 if upload / threshold_speedtest_upload >= 1
                    else (upload / threshold_speedtest_upload)
                )

            self.logger.debug(f"{download} / {threshold_speedtest_download} = {cv_download}")
            self.logger.debug(f"{upload} / {threshold_speedtest_upload} = {cv_upload}")

            self.logger.info(f"Speedtest Download Coefficient: {cv_download}")
            self.logger.info(f"Speedtest Upload Coefficient: {cv_upload}")

        g_cv = GaugeMetricFamily(
            self.metric_safe_name('coefficient'),
            'Network Score Coefficients',
            labels=['type'],
        )
        g_cv.add_metric(['loss'], cv_loss)
        g_cv.add_metric(['latency'], cv_latency)
        g_cv.add_metric(['jitter'], cv_jitter)
        g_cv.add_metric(['internal_dns_latency'], cv_internal_dns_latency)
        g_cv.add_metric(['external_dns_latency'], cv_external_dns_latency)
        g_cv.add_metric(['speedtest_download'], cv_download)
        g_cv.add_metric(['speedtest_upload'], cv_upload)

        yield g_cv

        # Master scoring function
        score = (
            (1 - weight_loss * cv_loss)
            - (weight_jitter * cv_jitter)
            - (weight_latency * cv_latency)
            - (weight_internal_dns_latency * cv_internal_dns_latency)
            - (weight_external_dns_latency * cv_external_dns_latency)
            - (weight_speedtest_download * cv_download)
            - (weight_speedtest_upload * cv_upload)
        )
        self.logger.info(f"Loss Score: {(1 - (weight_loss * cv_loss))*100}%")
        self.logger.info(f"Latency Score: {(1 - (weight_latency * cv_latency)) * 100}%")
        self.logger.info(f"Jitter Score: {(1 - (weight_jitter * cv_jitter)) * 100}%")
        self.logger.info(f"Internal DNS Latency Score: {(1 - (weight_internal_dns_latency * cv_internal_dns_latency)) * 100}%")
        self.logger.info(f"External DNS Latency Score: {(1 - (weight_external_dns_latency * cv_external_dns_latency)) * 100}%")
        self.logger.info(f"Speedtest Download Score: {(1 - (weight_speedtest_download * cv_download)) * 100}%")
        self.logger.info(f"Speedtest Upload Score: {(1 - (weight_speedtest_upload * cv_upload)) * 100}%")

        self.logger.info(f"Total Network Health Score: {score * 100}%")

        i = GaugeMetricFamily(self.metric_safe_name('health_score'), 'Overall internet health function')
        i.add_metric(['health'], score)

        yield i
