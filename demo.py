import time
from SPIOT.spiotmodule import SPIOT

iot = SPIOT(baudrate=115200, portname='/dev/ttyAMA0', encrypt=False)

while True:
    iot.query()
    time.sleep(1)
