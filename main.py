# MicroPython ST7735 TFT display driver example usage

from machine import Pin, SPI
from tft import TFT_GREEN

# DC       - RS/DC data/command flag
# CS       - Chip Select, enable communication
# RST/RES  - Reset
dc  = Pin('GP3', Pin.OUT, Pin.PULL_DOWN)
cs  = Pin('GP7', Pin.OUT, Pin.PULL_DOWN)
rst = Pin('GP4', Pin.OUT, Pin.PULL_DOWN)

# SPI Bus (CLK/MOSI/MISO)
# check your port docs to see which Pins you can use
spi = SPI(0, mode=SPI.MASTER, baudrate=8000000, polarity=1, phase=0)

# TFT object, this is ST7735R green tab version
tft = TFT_GREEN(128, 160, spi, dc, cs, rst)

# init TFT
tft.init()

# start using the driver
tft.clear(tft.rgbcolor(255, 0, 0))
