#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import threading
import serial

#You can adjust the parameters below -------------------------------------------------------------------
debug = False
UPDATERATE = 0.25  # the time period  to request for new data from RX (seconds)
MAXDEVICE_NUM = 16

#Don't update the parameters below ---------------------------------------------------------------------
DEVICE_INFO = {"PIR": {"ID":1, "HEX":0x20}, "DOOR": {"ID":2, "HEX":0x30}, \
               "TH_T": {"ID":3, "HEX":0x40}, "TH_H": {"ID":4, "HEX":0x40}, "PLUG": {"ID":5,"HEX":0x10} }
DEVICE_GROUP_HEX = {1: 0x20, 2: 0x30, 3: 0x40, 4: 0x40, 5:0x10 }

class SPIOT:

    def printRawData(self):
        count = 1
        Serial = self.serial

        for line in Serial.read():
            #print(str(count) + str(': ') + self.ByteToHex(line) )
            count = count+1

        self.pushDevice()

    def noEncrypt(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x99, 0x00, 0x00, 0x00, 0x00, 0x00]))
        time.sleep(0.3)
        self.queryDevices()

    def queryDevices(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x10, 0x00, 0x00, 0x00, 0x00, 0x00]))
        time.sleep(0.3)

    def pushDevice(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x08, 0x00, 0x00, 0x00, 0x00, 0x00]))
        #time.sleep(0.3)

    def removeAllDevices(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x0F, 0xF0, 0x5A, 0xA5, 0x00, 0x00]))
        #time.sleep(0.3)

    def removeGroupDevices(self, typeName):
        Serial = self.serial
        tNameList = self.dTypeName
        hex = tNameList[typeName]["HEX"]
        #hex = '0x{0:02x}'.format(intValue) 
        Serial.write(serial.to_bytes([0x0E, hex, 0x5A, 0xA5, 0x00, 0x00]))
        if(self.debug==True): print("RETURN --->{}".format(hex))
        #time.sleep(0.3)

    def removeTheDevice(self, typeName, idDevice):
        Serial = self.serial
        tNameList = self.dTypeName
        hex = tNameList[typeName]["HEX"] + idDevice
        #hex = '0x{0:02x}'.format(intValue+idDevice)
        Serial.write(serial.to_bytes([0x0E, hex, 0x5A, 0xA5, 0x00, 0x00]))

    def getDeviceData(self, typeName, idDevice):
        dData = self.dValue
        tNameList = self.dTypeName

        idType = tNameList[typeName]["ID"]

        try:
            intValue = dData[idType][idDevice]

        except:
            intValue = 0

        return intValue

    def getDeviceTime(self, typeName, idDevice):
        dAccessTime = self.lastAccess
        tNameList = self.dTypeName

        idType = tNameList[typeName]["ID"]

        try:
            lastAccessTime = dAccessTime[idType][idDevice]
            seconds = int(time.time()) - lastAccessTime

        except:
            seconds = 999999999

        return seconds


    def flashDevice(self, typeName, idDevice):
        Serial = self.serial

        tNameList = self.dTypeName
        hex = tNameList[typeName]["HEX"] + idDevice
        #hex = '0x{0:02x}'.format(intValue)
        sData = [0x17, hex, 0x00, 0x00, 0x00, 0x00]
        if(self.debug==True): print("SEND FLASH CMD: {}".format(sData))
        Serial.write(serial.to_bytes(sData))

    def setSmartPlug(self, idDevice, onoff):
        Serial = self.serial

        tNameList = self.dTypeName
        hex = tNameList["PLUG"]["HEX"] + idDevice
        if(onoff==1):
            action = 0x01;
        else:
            action = 0x00;

        sData = [0x0A, hex, action, 0x00, 0x00, 0x00]
        if(self.debug==True): print("SEND PLUG CMD: {}".format(sData))
        Serial.write(serial.to_bytes(sData))

    def ByteToHex( self, byteStr ):
        """
        Convert a byte string to it's hex string representation e.g. for output.
        """

        # Uses list comprehension which is a fractionally faster implementation than
        # the alternative, more readable, implementation below
        #
        #    hex = []
        #    for aChar in byteStr:
        #        hex.append( "%02X " % ord( aChar ) )
        #
        #    return ''.join( hex ).strip()

        rtnValue = ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()
        if(self.debug==True): print("Original:{} --> HEX:{}".format(byteStr, rtnValue))

        return rtnValue

    def HexToByte( self, hexStr ):
        """
        Convert a string hex byte values into a byte string. The Hex Byte values may
        or may not be space separated.
        """
        # The list comprehension implementation is fractionally slower in this case
        #
        #    hexStr = ''.join( hexStr.split(" ") )
        #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
        #                                   for i in range(0, len( hexStr ), 2) ] )

        bytes = []

        hexStr = ''.join( hexStr.split(" ") )

        for i in range(0, len(hexStr), 2):
            bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

        rtnValue = ''.join( bytes )
        #print("Original:{} --> Byte:{}".format(hexStr, int(hexStr, 16)-64))

        return rtnValue

    def updateQueue(self):
        queueRX = ['','','','','','']
        stringRX = ""
        Serial = self.serial
      
        for line in Serial.read():
            dataRX = self.ByteToHex(line)
            stringRX = stringRX + dataRX
            deviceData = self.dValue
            accessData = self.lastAccess
            
            if(dataRX=='06'):
                queueRX[0] = dataRX
 
                if(Serial.in_waiting):   #讀取第二個byte
                    for line in Serial.read():
                        dataRX = self.ByteToHex(line)
                        stringRX = stringRX + "-" + dataRX

                        if(dataRX[:1]=="1"):    #Smart PLUG device
                            deviceID = int(dataRX, 16)-16

                            if(Serial.in_waiting):   #讀取第三個byte
                                for line in Serial.read():
                                    dataRX = self.ByteToHex(line)
                                    stringRX = stringRX + "-" + dataRX
                                    #print(stringRX)
                                    #print("deviceData={}, PLUG typeID={} , deviceID={}, value={}".format(deviceData, self.dTypeName["PLUG"], deviceID, int(dataRX, 16)))

                                    if self.dTypeName["PLUG"]["ID"] in deviceData:
                                        deviceData[self.dTypeName["PLUG"]["ID"]][deviceID] = int(dataRX, 16)

                                    else:
                                        deviceData[self.dTypeName["PLUG"]["ID"]] = { deviceID: int(dataRX, 16) }

                                    if self.dTypeName["PLUG"]["ID"] in accessData:
                                        accessData[self.dTypeName["PLUG"]["ID"]][deviceID] = int(time.time())

                                    else:
                                        accessData[self.dTypeName["PLUG"]["ID"]] = { deviceID: int(time.time()) }

           
                        elif(dataRX[:1]=="2"):    #PIR device
                            deviceID = int(dataRX, 16)-32

                            if(Serial.in_waiting):   #讀取第三個byte
                                for line in Serial.read():
                                    dataRX = self.ByteToHex(line)
                                    stringRX = stringRX + "-" + dataRX
                                    #print("deviceData={}, PIR typeID={} , deviceID={}, value={}".format(deviceData, self.dTypeName["PIR"], deviceID, int(dataRX, 16)))

                                    if self.dTypeName["PIR"]["ID"] in deviceData:
                                        deviceData[self.dTypeName["PIR"]["ID"]][deviceID] = int(dataRX, 16)
                                        
                                    else:
                                        deviceData[self.dTypeName["PIR"]["ID"]] = { deviceID: int(dataRX, 16) }  

                                    if self.dTypeName["PIR"]["ID"] in accessData:
                                        accessData[self.dTypeName["PIR"]["ID"]][deviceID] = int(time.time())

                                    else:
                                        accessData[self.dTypeName["PIR"]["ID"]] = { deviceID: int(time.time()) }

                        elif(dataRX[:1]=="3"):    #DOOR device
                            deviceID = int(dataRX, 16)-48

                            if(Serial.in_waiting):   #讀取第三個byte
                                for line in Serial.read():
                                    dataRX = self.ByteToHex(line)
                                    stringRX = stringRX + "-" + dataRX
                                    #print("deviceData={}, DOOR typeID={} , deviceID={}, value={}".format(deviceData, self.dTypeName["DOOR"], deviceID, int(dataRX, 16)))

                                    if self.dTypeName["DOOR"]["ID"] in deviceData:
                                        deviceData[self.dTypeName["DOOR"]["ID"]][deviceID] = int(dataRX, 16)

                                    else:
                                        deviceData[self.dTypeName["DOOR"]["ID"]] = { deviceID: int(dataRX, 16) }

                                    if self.dTypeName["DOOR"]["ID"] in accessData:
                                        accessData[self.dTypeName["DOOR"]["ID"]][deviceID] = int(time.time())

                                    else:
                                        accessData[self.dTypeName["DOOR"]["ID"]] = { deviceID: int(time.time()) }
 
                        elif(dataRX[:1]=="4"):    #TH device
                            deviceID = int(dataRX, 16)-64

                            if(Serial.in_waiting):   #讀取第三個byte
                                for line in Serial.read():
                                    dataRX = self.ByteToHex(line)
                                    stringRX = stringRX + "-" + dataRX

                                    #print("deviceData={}, TH_T typeID={} , deviceID={}, value={}".format(deviceData, self.dTypeName["TH_T"], deviceID, int(dataRX, 16)))
                                    if self.dTypeName["TH_T"]["ID"] in deviceData:
                                        deviceData[self.dTypeName["TH_T"]["ID"]][deviceID] = int(dataRX, 16)
                                    else:
                                        deviceData[self.dTypeName["TH_T"]["ID"]] = { deviceID: int(dataRX, 16) }

                                    if self.dTypeName["TH_T"]["ID"] in accessData:
                                        accessData[self.dTypeName["TH_T"]["ID"]][deviceID] = int(time.time())
                                    else:
                                        accessData[self.dTypeName["TH_T"]["ID"]] = { deviceID: int(time.time()) }
                    


                                    if(Serial.in_waiting):   #讀取第四個byte
                                        for line in Serial.read():
                                            dataRX = self.ByteToHex(line)
                                            stringRX = stringRX + "-" + dataRX
                                           
                                            if self.dTypeName["TH_H"]["ID"] in deviceData:
                                                deviceData[self.dTypeName["TH_H"]["ID"]][deviceID] = int(dataRX, 16)
                                            else:
                                                deviceData[self.dTypeName["TH_H"]["ID"]] = { deviceID: int(dataRX, 16) }

                                            if self.dTypeName["TH_H"]["ID"] in accessData:
                                                accessData[self.dTypeName["TH_H"]["ID"]][deviceID] = int(time.time())
                                            else:
                                                accessData[self.dTypeName["TH_H"]["ID"]] = { deviceID: int(time.time()) }

                    #print (stringRX)
                    self.dValue = deviceData
                    self.lastAccess = accessData
                    if(self.debug==True): print("self.dValue = {}".format(deviceData))
                    if(self.debug==True): print("self.lastAccess = {}".format(accessData))


    def bgUpdate(self):
        Serial = self.serial
            
        while True:
            if(Serial.in_waiting):
                self.updateQueue()

            else:
                Serial.flushInput()
                self.pushDevice()
                time.sleep(0.35)

    def id2DeviceGroupName(self, typeID=2):
        typeList = self.dTypeName
        #dTypeName = (key for key, value in typeList.items() if value == typeID).next()
        tName = ""
        for key, value in dTypeName.items():
            if(typeID== value["ID"]):
                tName = key
                break

        return tName

    def id2DeviceGroupHEX(self, typeID=2):
        typeList = self.dTypeName
        #dTypeName = (key for key, value in typeList.items() if value == typeID).next()
        dHEX = ""
        for key, value in dTypeName.items():
            if(typeID== value["ID"]):
                dHEX = value["HEX"]
                break

        return dHEX

    def __init__(self, baudrate=115200, portname='/dev/ttyAMA0', encrypt=False):
        self.debug = debug
        self.process = False
        self.maxDeviceNum = MAXDEVICE_NUM
        self.dTypeName = DEVICE_INFO
        #self.dGroup = DEVICE_GROUP_HEX
        self.dValue = {}
        self.lastAccess = {}

        self.encrypt = encrypt
        self.baudrate = baudrate
        self.serial = serial.Serial(
            port=portname,
            baudrate = baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )

        if(encrypt==False):
            self.noEncrypt()

    def begin(self):
        self.process = True
        self.t = threading.Timer(UPDATERATE, self.bgUpdate)
        self.t.daemon = True
        self.t.start()

