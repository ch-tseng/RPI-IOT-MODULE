# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

#Default colors for rooms
colorRoom = (203, 241, 249)
colorWall = (74, 35, 4)
colorDoor = (184, 84, 3)
#Positions for rooms ( y1, x1, y2, x2)
posRooms = [ (5, 5, 112, 152), (128, 5, 235, 152), (5, 160, 112, 307), (128, 160, 235, 307) ]
posDoors = [ (106, 20, 112, 80), (128, 20, 134, 80), (106, 175, 112, 235), (128, 175, 134, 235) ]

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

# Draw a purple rectangle with yellow outline.
# ( y1, x1, y2, x2)
draw.rectangle(posRooms[0], outline=colorWall, fill=colorRoom)
draw.rectangle(posRooms[1], outline=colorWall, fill=colorRoom)
draw.rectangle(posRooms[2], outline=colorWall, fill=colorRoom)
draw.rectangle(posRooms[3], outline=colorWall, fill=colorRoom)

#Doors
draw.rectangle(posDoors[0], outline=colorWall, fill=colorDoor)
draw.rectangle(posDoors[1], outline=colorWall, fill=colorDoor)
draw.rectangle(posDoors[2], outline=colorWall, fill=colorDoor)
draw.rectangle(posDoors[3], outline=colorWall, fill=colorDoor)

# Load default font.
#font = ImageFont.load_default()
font = ImageFont.truetype("fonts/font1.ttf", 18)

# Alternatively load a TTF font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
#font = ImageFont.truetype('Minecraftia.ttf', 16)

# Define a function to create rotated text.  Unfortunately PIL doesn't have good
# native support for rotated fonts, but this function can be used to make a
# text image and rotate it so it's easy to paste in the buffer.
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

# Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
#(y, x)
draw_rotated_text(disp.buffer, 'T:', (10, 60), 90, font, fill=(0,255,0))
draw_rotated_text(disp.buffer, 'H:', (10, 30), 90, font, fill=(0,0,255))

# Write buffer to display hardware, must be called to make things visible on the
# display!
disp.display()
