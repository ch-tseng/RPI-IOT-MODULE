#!/usr/bin/env python
  
  
import time
import serial
  
  
ser = serial.Serial(
  
    port='/dev/ttyAMA0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

counter=0
  
ser.write(serial.to_bytes([0x99, 0x00, 0x00, 0x00, 0x00, 0x00]))
time.sleep(1)

ser.write(serial.to_bytes([0x10, 0x00, 0x00, 0x00, 0x00, 0x00]))
time.sleep(1)

def pushDevice():
    ser.write(serial.to_bytes([0x08, 0x00, 0x00, 0x00, 0x00, 0x00]))

def ByteToHex( byteStr ):
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

#-------------------------------------------------------------------------------

def HexToByte( hexStr ):
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

count=1  
while 1:
    #x=ser.readline()
    #print hex(x)

    for line in ser.read():

        print(str(count) + str(': ') + ByteToHex(line) )
        count = count+1

    pushDevice()
    time.sleep(1)

