import time, sys
from SPIOT.spiotmodule import SPIOT

iot = SPIOT(baudrate=115200, portname='/dev/ttyAMA0', encrypt=False)

#iot.removeAllDevice()
iot.begin()

#time.sleep(1)

iot.flashDevice("DOOR", 0)

while True:
    try:
        #iot.printRawData()
        #iot.updateQueue()
        #print ("update")
        #iot.removeGroupDevices("PIR")
        print("DOOR --> {}, seconds: {}".format(iot.getDeviceData("DOOR", 0), iot.getDeviceTime("DOOR", 0)))
        print("TH_T --> {}, seconds: {}".format(iot.getDeviceData("TH_T", 0), iot.getDeviceTime("TH_T", 0)))
        print("TH_H --> {}, seconds: {}".format(iot.getDeviceData("TH_H", 0), iot.getDeviceTime("TH_H", 0)))

        time.sleep(0.5)

    except KeyboardInterrupt:
        print "Bye"
        sys.exit()
