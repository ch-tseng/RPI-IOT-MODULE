import time
from SPIOT.spiotmodule import SPIOT

iot = SPIOT(baudrate=115200, portname='/dev/ttyAMA0', encrypt=False)

#iot.removeAllDevice()
iot.begin()

#time.sleep(1)

while True:
    #iot.printRawData()
    #iot.updateQueue()
    #print ("update")
    #iot.removeGroupDevices("PIR")
    print("DOOR --> {}".format(iot.getDeviceData("DOOR", 0)))

    time.sleep(0.5)
