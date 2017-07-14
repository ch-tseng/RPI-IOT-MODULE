import urllib2
import time, sys
from SPIOT.spiotmodule import SPIOT

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

ThingSpeakEnabled = False
ThingSpeakUpdatePeriod = 30  #seconds
ThingSpeakURL = "https://api.thingspeak.com/update?api_key="
CHkey = [ "S5P44WKNJN7FWSJT", "41OVS979P9ONI7MM", "7HI4406LTFC7JN0B", "XXQIPDBM6TTHC7I9" ]
debug = False

#Default colors for rooms
colorRoom = (203, 241, 249)
colorWall = (66, 65, 63)
colorDoor = (184, 84, 3)

#Positions for rooms ( y1, x1, y2, x2)
posRooms = [ (5, 5, 112, 152), (128, 5, 235, 152), (5, 160, 112, 307), (128, 160, 235, 307) ]
posDoorClose = [ (109, 20 , 109, 80), (128, 50, 128, 110), (109, 175, 109, 235), (128, 225, 128, 285) ]
posDoorOpen = [ (106, 20, 84, 73), (132, 123, 156, 70), (106, 175, 86, 228), (132, 277, 152, 225) ]
posThief = [ (56, 122), (160, 122), (56, 277), (160, 277)  ]
posPlug = [ (56, 42), (160, 42), (56, 197), (160, 197) ]
post_T = [ (10, 80), (200, 80), (10, 235), (200, 235) ]
post_H = [ (10, 30), (200, 30), (10, 185), (200, 185) ]
posClearTH = [(10, 120, 32, 10), (200, 120, 222, 10), (10, 275, 32, 165), (200, 275, 222, 165) ]

#font = ImageFont.load_default()
font = ImageFont.truetype("fonts/font1.ttf", 18)

PIR = [0, 0, 0, 0]
TH_T = [0, 0, 0, 0]
TH_H = [0, 0, 0, 0]
DOOR = [0, 0, 0, 0]
PLUG = [0, 0, 0, 0]

# Raspberry Pi configuration.
DC = 18
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

# Initialize display.
disp.begin()

# Clear the display to a red background.
# Can pass any tuple of red, green, blue values (from 0 to 255 each).
disp.clear((0, 0, 0))

# Alternatively can clear to a black screen by calling:
# disp.clear()

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

def drawRoom(ID):
    global posRooms, colorWall, colorRoom
    draw.rectangle(posRooms[ID], outline=colorWall, fill=colorRoom)

def drawDOOR(ID, status = 0):
    global colorRoom, colorWall, posDoorClose, posDoorOpen

    #clear
    draw.line(posDoorClose[ID], fill=colorRoom, width=6)
    draw.line(posDoorOpen[ID], fill=colorRoom, width=6)
    #draw.rectangle((posRooms[ID][0], posRooms[ID][1], posDoorOpen[ID][2], posDoorOpen[ID][3]), outline=colorWall, fill=colorRoom)

    #draw
    if status==0:
        draw.line(posDoorClose[ID], fill=colorDoor, width=6)
    else:
        draw.line(posDoorOpen[ID], fill=colorDoor, width=6)

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

def draw_thief(ID, image, angle, status=0):
    global posThief, colorRoom, colorDoor
    thiefImg = Image.open('thief.jpg')
    #clear
    draw.rectangle((posThief[ID][0], posThief[ID][1], posThief[ID][0]+28, posThief[ID][1]+30), fill=colorRoom)

    if(status>0):
        thiefRotated = thiefImg.rotate(angle, expand=1)
        image.paste(thiefRotated, posThief[ID])

def draw_plug(ID, image, angle, status=0):
    global posPlug, colorRoom, colorDoor
    #clear
    draw.rectangle((posPlug[ID][0], posPlug[ID][1], posPlug[ID][0]+30, posPlug[ID][1]+30), fill=colorRoom)

    if(status>0):
        plugImg = Image.open('plug1.jpg')

    else:
        if(iot.getDeviceTime("PLUG", ID)>120):
            plugImg = Image.open('plug-no.jpg')

        else:
            plugImg = Image.open('plug0.jpg')

    plugRotated = plugImg.rotate(angle, expand=1)
    image.paste(plugImg, posPlug[ID])

def printTH(ID, T, H):
    global colorRoom, posClearTH
    draw.rectangle(posClearTH[ID], fill=colorRoom)

    draw_rotated_text(disp.buffer, str(T)+'C', post_T[ID], 90, font, fill=(3,141,3))
    draw_rotated_text(disp.buffer, str(H)+'%', post_H[ID], 90, font, fill=(0,0,255))

def updateThingSpeak(T, H, PIR, DOOR, PLUG, CH):
    global lastThingsSpeakTime, ThingSpeakURL, CHkey

    if(PIR>1):
        PIR = 1
    else:
        PIR = 0

    if(DOOR>1):
        DOOR = 1
    else:
        DOOR = 0

    if(PLUG>1):
        PLUG = 1
    else:
        PLUG = 0

    URL = ThingSpeakURL + CHkey[CH-1] + "&field1=" + str(T) + "&field2=" + str(H) + "&field3=" + str(DOOR) + "&field4=" + str(PIR) + "&field5=" + str(PLUG)
    if(debug==True): print(URL)
    lastThingsSpeakTime = time.time()

    urllib2.urlopen(URL)

#--------------------------------------------------------------
iot = SPIOT(baudrate=115200, portname='/dev/ttyS0', encrypt=False)

iot.begin()
#time.sleep(1)
#iot.removeAllDevices()
#iot.flashDevice("DOOR", 0)
#iot.removeGroupDevices("PLUG")


drawRoom(0)
drawRoom(1)
drawRoom(2)
drawRoom(3)
drawDOOR(0, 0)
drawDOOR(1, 0)
drawDOOR(2, 0)
drawDOOR(3, 0)
draw_plug(0, disp.buffer, 90, 0)
draw_plug(1, disp.buffer, 90, 0)
draw_plug(2, disp.buffer, 90, 0)
draw_plug(3, disp.buffer, 90, 0)

lastTH = [(0, 0), (0, 0), (0, 0), (0, 0)]
lastPIR = [0, 0, 0, 0]
lastDOOR = [0, 0, 0, 0]
lastPLUG = [0, 0, 0, 0]

lastThingsSpeakTime = 0

while True:
    if( (time.time() - lastThingsSpeakTime)>ThingSpeakUpdatePeriod):
        updateThingSpeakNow = True
    else:
        updateThingSpeakNow = False

    for i in (0,1,2,3):
        DOOR[i] = iot.getDeviceData("DOOR", i)
        PIR[i] = iot.getDeviceData("PIR", i)    
        TH_T[i] = iot.getDeviceData("TH_T", i)
        TH_H[i] = iot.getDeviceData("TH_H", i)
        PLUG[i] = iot.getDeviceData("PLUG", i)
        if(debug==True): print("#{} --> DOOR:{}, PIR:{}, PLUG:{}, TH_T:{}, TH_H:{}".format(i, DOOR[i], PIR[i], PLUG[i], TH_T[i], TH_H[i]))

        if(lastTH[i] != (TH_T[i], TH_H[i])):
            #(y, x)
            printTH(i, TH_T[i], TH_H[i])
            lastTH[i] = (TH_T[i], TH_H[i])

        if(lastPIR[i] != PIR[i]):
            draw_thief(i, disp.buffer, 90, PIR[i])
            lastPIR[i] = PIR[i]

            if( i==1 or i==2 ):
                   iot.setSmartPlug(i-1, PIR[i])

        if(lastDOOR[i] != DOOR[i]):
            drawDOOR(i, DOOR[i])
            lastDOOR[i] = DOOR[i]

            if(i==3):
                iot.setSmartPlug(i-1, DOOR[i])

        #for special case.....
        if(i==1 or i==2):
            if(lastPLUG[i-1] != PLUG[i-1]):
                draw_plug(i, disp.buffer, 90, PLUG[i-1])
                lastPLUG[i-1] = PLUG[i-1]
       
        #Original
        #if(lastPLUG[i] != PLUG[i]):
        #    draw_plug(i, disp.buffer, 90, PLUG[i])
        #    lastPLUG[i] = PLUG[i]

        if( updateThingSpeakNow==True ):
            if(ThingSpeakEnabled==True):
                updateThingSpeak(TH_T[i], TH_H[i], PIR[i], DOOR[i], PLUG[i], i+1)

    disp.display()
    time.sleep(0.1)
