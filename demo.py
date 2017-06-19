import time, sys
from SPIOT.spiotmodule import SPIOT

iot = SPIOT(baudrate=115200, portname='/dev/ttyAMA0', encrypt=False)

iot.begin()

#time.sleep(1)
#iot.removeAllDevices()
#iot.flashDevice("DOOR", 0)

while True:
    try:
        #iot.printRawData()
        #iot.updateQueue()
        #print ("update")
        #iot.removeGroupDevices("PIR")

        for i in (0,1,2,3):
            print("#{} PIR  --> {}, seconds: {}".format(i, iot.getDeviceData("PIR", i), iot.getDeviceTime("PIR", i)))
            print("#{} DOOR --> {}, seconds: {}".format(i, iot.getDeviceData("DOOR", i), iot.getDeviceTime("DOOR", i)))
            print("#{} TH_T --> {}, seconds: {}".format(i, iot.getDeviceData("TH_T", i), iot.getDeviceTime("TH_T", i)))
            print("#{} TH_H --> {}, seconds: {}".format(i, iot.getDeviceData("TH_H", i), iot.getDeviceTime("TH_H", i)))
            print(" --------------------------------------------------------------------------------- ")

        time.sleep(1)

    except KeyboardInterrupt:
        print "Bye"
        sys.exit()
