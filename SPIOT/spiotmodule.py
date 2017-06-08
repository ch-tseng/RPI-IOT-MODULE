#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from threading import Thread
import serial

class SPIOT:

    def printRawData(self):
        count = 1
        Serial = self.serial

        for line in Serial.read():
            print(str(count) + str(': ') + self.ByteToHex(line) )
            count = count+1

        self.pushDevice()

    def noEncrypt(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x99, 0x00, 0x00, 0x00, 0x00, 0x00]))
        time.sleep(0.3)

    def queryDevices(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x10, 0x00, 0x00, 0x00, 0x00, 0x00]))
        time.sleep(0.3)

    def pushDevice(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x08, 0x00, 0x00, 0x00, 0x00, 0x00]))
        #time.sleep(0.3)

    def removeAllDevice(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x0F, 0xF0, 0x5A, 0xA5, 0x00, 0x00]))
        time.sleep(0.3)

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
        #print("Original:{} --> HEX:{}".format(byteStr, rtnValue))

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
      
        if(Serial.in_waiting):   #讀取第一個byte
            for line in Serial.read():
                dataRX = self.ByteToHex(line)
                stringRX = stringRX + dataRX
                deviceData = self.dValue
            
                if(dataRX=='06'):
                    queueRX[0] = dataRX
 
                    if(Serial.in_waiting):   #讀取第二個byte
                        for line in Serial.read():
                            dataRX = self.ByteToHex(line)
                            stringRX = stringRX + "-" + dataRX
           
                            if(dataRX[:1]=="3"):    #DOOR device
                                deviceID = int(dataRX, 16)-48

                                if(Serial.in_waiting):   #讀取第三個byte
                                    for line in Serial.read():
                                        dataRX = self.ByteToHex(line)
                                        stringRX = stringRX + "-" + dataRX
                                        print("deviceData={}, DOOR typeID={} , deviceID={}, value={}".format(deviceData, self.dType["DOOR"], deviceID, int(dataRX, 16)))

                                        if self.dType["DOOR"] in deviceData:
                                            deviceData[self.dType["DOOR"]][deviceID] = int(dataRX, 16)
                                        else:
                                            deviceData[self.dType["DOOR"]] = { deviceID: int(dataRX, 16) }  


                            elif(dataRX[:1]=="4"):    #TH device
                                deviceID = int(dataRX, 16)-64

                                if(Serial.in_waiting):   #讀取第三個byte
                                    for line in Serial.read():
                                        dataRX = self.ByteToHex(line)
                                        stringRX = stringRX + "-" + dataRX

                                        print("deviceData={}, TH_T typeID={} , deviceID={}, value={}".format(deviceData, self.dType["TH_T"], deviceID, int(dataRX, 16)))

                                        if self.dType["TH_T"] in deviceData:
                                            deviceData[self.dType["TH_T"]][deviceID] = int(dataRX, 16)
                                        else:
                                            deviceData[self.dType["TH_T"]] = { deviceID: int(dataRX, 16) }


                                        if(Serial.in_waiting):   #讀取第四個byte
                                            for line in Serial.read():
                                                dataRX = self.ByteToHex(line)
                                                stringRX = stringRX + "-" + dataRX
                                            
                                                if self.dType["TH_H"] in deviceData:
                                                    deviceData[self.dType["TH_H"]][deviceID] = int(dataRX, 16)
                                                else:
                                                    deviceData[self.dType["TH_H"]] = { deviceID: int(dataRX, 16) }

                        self.dValue = deviceData
                        print ("Received and coverted: {}".format(stringRX))
                        print("self.dValue = {}".format(deviceData))

                #elif(dataRX=='09'):


        else:
            self.pushDevice()
            time.sleep(0.35)

    def deviceTypeID(typeID=2):
        typeList = self.dType
        dTypeName = (key for key, value in typeList.items() if value == typeID).next()
        return dTypeName

    #def getData(self, tDevice, dID):
        

    def __init__(self, baudrate=115200, portname='/dev/ttyAMA0', encrypt=False):
        self.maxDeviceNum = 16
        self.dType = {"PIR": 1, "DOOR": 2, "TH_T": 3, "TH_H": 4, "PLUG": 5 }
        self.dValue = {}

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
            time.sleep(0.5)
            self.queryDevices()

    def begin(self):
        background_thread = Thread(target=self.updateQueue())
        background_thread.start()
