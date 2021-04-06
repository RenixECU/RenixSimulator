from paho.mqtt.publish import single
from time import sleep
import json
import logging

logger = logging.getLogger()


def send_tpms(index):

    info = {
        "time": "2021-04-03 20:12:07",
        "model": "Ford",
        "type": "TPMS",
        "id": "340a250e",
        "pressure_PSI": 45 * (index/100),
        "temperature_F": 90 * (index/100),
        "code": "284c05",
        "mic": "CHECKSUM"
    }

    try:
        single("tpms", json.dumps(info))
    except ConnectionRefusedError:
        logger.error("could not connect to mqtt")


if __name__ == "__main__":
    count = 0
    while True:
        send_tpms(count)
        count = (count + 1) % 100
        sleep(1)
