import time
import serial

class SPIOT:

    def query(self):
        count = 1
        Serial = self.serial

        for line in Serial.read():
            print(str(count) + str(': ') + self.ByteToHex(line) )
            count = count+1

        self.pushDevice()

    def noEncrypt(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x99, 0x00, 0x00, 0x00, 0x00, 0x00]))

    def queryDevices(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x10, 0x00, 0x00, 0x00, 0x00, 0x00]))

    def pushDevice(self):
        Serial = self.serial
        Serial.write(serial.to_bytes([0x08, 0x00, 0x00, 0x00, 0x00, 0x00]))

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

        return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()

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

        return ''.join( bytes )

    def __init__(self, baudrate=115200, portname='/dev/ttyAMA0', encrypt=False):
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

