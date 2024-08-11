# Netprobe Service

import time
from helpers.network_helper import Netprobe_Speedtest
from helpers.http_helper import *
from helpers.redis_helper import *
from config import Config_Netprobe
from datetime import datetime
from helpers.logging_helper import *

class NetprobeSpeedTest():
    def __init__(self):
        pass

    def run(self):
        # Global Variables
        speedtest_enabled = Config_Netprobe.speedtest_enabled
        speedtest_interval = Config_Netprobe.speedtest_interval
        collector = Netprobe_Speedtest()
        # Logging Config
        log_path = Config_Netprobe.log_path
        logger = setup_logging(f"{log_path}/speedtest.log")
        
        if speedtest_enabled == True:
            while True:
                try:
                    stats = collector.collect()
                    current_time = datetime.now()

                except Exception as e:
                    print("Error running speedtest")
                    logger.error("Error running speedtest")
                    logger.error(e)
                    time.sleep(speedtest_interval)  # Pause before retrying
                    continue

                # Connect to Redis
                try:
                    cache = RedisConnect()
                    # Save Data to Redis
                    cache_interval = speedtest_interval*2 # Set the redis cache 2x longer than the speedtest interval
                    cache.redis_write('speedtest',json.dumps(stats),cache_interval)
                    logger.info(f"Stats successfully written to Redis for Speed Test")

                except Exception as e:
                    logger.error("Could not connect to Redis")
                    logger.error(e)
                
                time.sleep(speedtest_interval)

        else:
            pass

if __name__ == '__main__':
    speedtest = NetprobeSpeedTest()
    speedtest.run()