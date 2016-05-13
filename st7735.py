"""
The MIT License (MIT)

Copyright (c) 2016 Alex March (github.com/hosaka)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE
"""

# MicroPython ST7735 TFT display driver

class ST7735(object):

    # command definitions
    CMD_NOP     = const(0x00) # No Operation
    CMD_SWRESET = const(0x01) # Software reset
    CMD_RDDID   = const(0x04) # Read Display ID
    CMD_RDDST   = const(0x09) # Read Display Status

    CMD_SLPIN   = const(0x10) # Sleep in & booster off
    CMD_SLPOUT  = const(0x11) # Sleep out & booster on
    CMD_PTLON   = const(0x12) # Partial mode on
    CMD_NORON   = const(0x13) # Partial off (Normal)

    CMD_INVOFF  = const(0x20) # Display inversion off
    CMD_INVON   = const(0x21) # Display inversion on
    CMD_DISPOFF = const(0x28) # Display off
    CMD_DISPON  = const(0x29) # Display on
    CMD_CASET   = const(0x2A) # Column address set
    CMD_RASET   = const(0x2B) # Row address set
    CMD_RAMWR   = const(0x2C) # Memory write
    CMD_RAMRD   = const(0x2E) # Memory read

    CMD_PTLAR   = const(0x30) # Partial start/end address set
    CMD_COLMOD  = const(0x3A) # Interface pixel format
    CMD_MADCTL  = const(0x36) # Memory data access control

    CMD_RDID1   = const(0xDA) # Read ID1
    CMD_RDID2   = const(0xDB) # Read ID2
    CMD_RDID3   = const(0xDC) # Read ID3
    CMD_RDID4   = const(0xDD) # Read ID4

    # panel function commands
    CMD_FRMCTR1 = const(0xB1) # In normal mode (Full colors)
    CMD_FRMCTR2 = const(0xB2) # In Idle mode (8-colors)
    CMD_FRMCTR3 = const(0xB3) # In partial mode + Full colors
    CMD_INVCTR  = const(0xB4) # Display inversion control

    CMD_PWCTR1  = const(0xC0) # Power control settings
    CMD_PWCTR2  = const(0xC1) # Power control settings
    CMD_PWCTR3  = const(0xC2) # In normal mode (Full colors)
    CMD_PWCTR4  = const(0xC3) # In Idle mode (8-colors)
    CMD_PWCTR5  = const(0xC4) # In partial mode + Full colors
    CMD_VMCTR1  = const(0xC5) # VCOM control

    CMD_GMCTRP1 = const(0xE0)
    CMD_GMCTRN1 = const(0xE1)

    # colors
    COLOR_BLACK   = const(0x0000)
    COLOR_BLUE    = const(0x001F)
    COLOR_RED     = const(0xF800)
    COLOR_GREEN   = const(0x07E0)
    COLOR_CYAN    = const(0x07FF)
    COLOR_MAGENTA = const(0xF81F)
    COLOR_YELLOW  = const(0xFFE0)
    COLOR_WHITE   = const(0xFFFF)

    def __init__(self, width, height):
        # self.tab     = tab
        self.width     = width
        self.height    = height
        self.power     = True
        self.inverted  = False
        self.backlight = True

        # default margins, set yours in HAL init
        self.margin_row = 0
        self.margin_col = 0

    def _set_window(self, x0, y0, x1, y1):
        """
        Set window frame boundaries.

        Any pixels written to the display will start from this area.
        """
        # set row XSTART/XEND
        self.write_cmd(CMD_RASET)
        self.write_data(bytearray(
            [0x00, y0 + self.margin_row, 0x00, y1 + self.margin_row])
        )

        # set column XSTART/XEND
        self.write_cmd(CMD_CASET)
        self.write_data(bytearray(
            [0x00, x0 + self.margin_col, 0x00, x1 + self.margin_col])
        )

        # write addresses to RAM
        self.write_cmd(CMD_RAMWR)

    def power(self, state=None):
        """
        Get/set display power.
        """
        if state is None:
            return self.power
        self.write_cmd(CMD_DISPON if state else CMD_DISPOFF)
        self.power = state

    def clear(self, color=COLOR_WHITE):
        """
        Clear the display filling it with color.
        """
        self.rect(0, 0, self.width, self.height, color)

    def invert(self, state=None):
        """
        Get/set display color inversion.
        """
        if state is None:
            return self.inverted
        self.write_cmd(CMD_INVON if state else CMD_INVOFF)
        self.inverted = state

    def rgbcolor(self, r, g, b):
        """
        Pack 24-bit RGB into 16-bit value.
        """
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def pixel(self, x, y, color):
        """
        Draw a single pixel on the display with given color.
        """
        self._set_window(x, y, x + 1, y + 1)
        self.write_pixels(1, bytearray([color >> 8, color]))

    def rect(self, x, y, w, h, color):
        """
        Draw a rectangle with specified coordinates/size and fill with color.
        """
        # starting coordinate is within the screen
        if (x >= self.width) or (y >= self.height):
            return

        # trim the requested size if necessary
        if (x + w - 1) >= self.width:
            w = self.width - x
        if (y + h - 1) >= self.height:
            h = self.height - y

        # print("final coords:")
        # print(x, y, w, h)
        # print("set window:")
        # print(x, y, x + w - 1, y + h - 1)

        # set window
        self._set_window(x, y, x + w - 1, y + h - 1)

        # count pixels and write them
        pixels = (w * h)

        # print("write pixels:")
        # print(pixels)
        self.write_pixels(pixels, bytearray([color >> 8, color]))

    def hline(self, x, y, w, color):
        if (x >= self.width) or (y >= self.height):
            return
        if (x + w - 1) >= self.width:
            w = self.width - x

        self._set_window(x, y, x + w - 1, y)
        self.write_pixels(x+w-1, bytearray([color >> 8, color]))

    def vline(self, x, y, h, color):
        if (x >= self.width) or (y >= self.height):
            return
        if (y + h -1) >= self.height:
            h = self.height - y

        self._set_window(x, y, x, y + h - 1)
        self.write_pixels(y+h-1, bytearray([color >> 8, color]))

    def text(self, string, x, y):
        # font?
        pass

    """
    ST7735 HAL functions

    Implement these in your driver API to communicate with the display using
    defined Pins and SPI bus.
    """
    def init(self):
        """
        HAL: Init your "tab" version of the display.
        """
        raise NotImplementedError

    def reset(self):
        """
        HAL: Display reset command.
        """
        raise NotImplementedError

    def backlight(self, state):
        """
        HAL: Toggle display backlight depending on given state.
        """
        raise NotImplementedError

    def write_pixels(self, count, color):
        """
        HAL: Write individual pixels to the display.
        """
        raise NotImplementedError

    def write_cmd(self, cmd):
        """
        HAL: Write a command to the display.
        """
        raise NotImplementedError

    def write_data(self, data):
        """
        HAL: Write data to the display.
        """
        raise NotImplementedError
