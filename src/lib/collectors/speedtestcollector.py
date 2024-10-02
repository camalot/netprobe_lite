import typing

from lib.collectors.basecollector import BaseCollector
import speedtest


class SpeedTestCollector(BaseCollector):  # Speed test class
    def __init__(self):
        super().__init__()

    def _fetch(self) -> typing.Optional[dict]:
        try:
            s = speedtest.Speedtest()
            s.get_closest_servers()
            s.get_best_server()
            download = s.download()
            upload = s.upload()
            # get the jitter and latency
            latency = s.results.ping

            return {"download": download, "upload": upload, "latency": latency}
        except Exception as e:
            self.logger.error("Error fetching speedtest results")
            self.logger.error(e)
            return
        None

    def collect(self) -> typing.Optional[dict]:
        results = self._fetch()
        return results
