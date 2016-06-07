# MicroPython ST7735 TFT display HAL

import time
from st7735 import ST7735

class TFT(ST7735):

    # command definitions
    # CMD_NOP     = const(0x00) # No Operation
    CMD_SWRESET = const(0x01) # Software reset
    # CMD_RDDID   = const(0x04) # Read Display ID
    # CMD_RDDST   = const(0x09) # Read Display Status

    # CMD_SLPIN   = const(0x10) # Sleep in & booster off
    CMD_SLPOUT  = const(0x11) # Sleep out & booster on
    # CMD_PTLON   = const(0x12) # Partial mode on
    CMD_NORON   = const(0x13) # Partial off (Normal)

    CMD_INVOFF  = const(0x20) # Display inversion off
    # CMD_INVON   = const(0x21) # Display inversion on
    # CMD_DISPOFF = const(0x28) # Display off
    CMD_DISPON  = const(0x29) # Display on
    CMD_CASET   = const(0x2A) # Column address set
    CMD_RASET   = const(0x2B) # Row address set
    # CMD_RAMWR   = const(0x2C) # Memory write
    # CMD_RAMRD   = const(0x2E) # Memory read

    # CMD_PTLAR   = const(0x30) # Partial start/end address set
    CMD_COLMOD  = const(0x3A) # Interface pixel format
    CMD_MADCTL  = const(0x36) # Memory data access control

    # CMD_RDID1   = const(0xDA) # Read ID1
    # CMD_RDID2   = const(0xDB) # Read ID2
    # CMD_RDID3   = const(0xDC) # Read ID3
    # CMD_RDID4   = const(0xDD) # Read ID4

    # panel function commands
    CMD_FRMCTR1 = const(0xB1) # In normal mode (Full colors)
    CMD_FRMCTR2 = const(0xB2) # In Idle mode (8-colors)
    # CMD_FRMCTR3 = const(0xB3) # In partial mode + Full colors
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

    def __init__(self, width, height, spi, dc, cs, rst, bl=None):
        """
        SPI      - SPI Bus (CLK/MOSI/MISO)
        DC       - RS/DC data/command flag
        CS       - Chip Select, enable communication
        RST/RES  - Reset
        BL/Lite  - Backlight control
        """

        # self.tab = tab
        self.spi = spi
        self.dc  = dc
        self.cs  = cs
        self.rst = rst
        self.bl  = bl

        # ST7735 init
        super().__init__(width, height)

    # ST7735 HAL
    def init(self):
        """
        Define your init for different display tab color versions.
        """
        raise NotImplementedError

        # self.clear()
        # self.power(True)

    def reset(self):
        """
        Hard reset the display.
        """
        self.dc.value(0)
        self.rst.value(1)
        time.sleep_ms(500)
        self.rst.value(0)
        time.sleep_ms(500)
        self.rst.value(1)
        time.sleep_ms(500)

    def backlight(self, state=None):
        """
        Get or set the backlight status if the pin is available.
        """
        if self.bl is None:
            return None
        else:
            if state is None:
                return self.backlight_on
            self.bl.value(1 if state else 0)
            self.backlight_on = state

    def write_pixels(self, count, color):
        """
        Write pixels to the display.

        count - total number of pixels
        color - 16-bit RGB value
        """
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(count):
            self.spi.write(color)
        self.cs.value(1)

    def write_cmd(self, cmd):
        """
        Display command write implementation using SPI.
        """
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(cmd)
        self.cs.value(1)

    def write_data(self, data):
        """
        Display data write implementation using SPI.
        """
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)

class TFT_GREEN(TFT):

    def __init__(self, width, height, spi, dc, cs, rst, bl=None):
        super().__init__(width, height, spi, dc, cs, rst, bl)

    def init(self):
        # set column and row margins
        self.margin_row = 1
        self.margin_col = 2

        # hard reset first
        self.reset()

        self.write_cmd(TFT.CMD_SWRESET)
        time.sleep_ms(150)
        self.write_cmd(TFT.CMD_SLPOUT)
        time.sleep_ms(255)

        # TODO: optimize data streams and delays
        self.write_cmd(TFT.CMD_FRMCTR1)
        self.write_data(bytearray([0x01, 0x2C, 0x2D]))
        self.write_cmd(TFT.CMD_FRMCTR2)
        self.write_data(bytearray([0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D]))
        time.sleep_ms(10)

        self.write_cmd(TFT.CMD_INVCTR)
        self.write_data(0x07)

        self.write_cmd(TFT.CMD_PWCTR1)
        self.write_data(bytearray([0xA2, 0x02, 0x84]))
        self.write_cmd(TFT.CMD_PWCTR2)
        self.write_data(0xC5)
        self.write_cmd(TFT.CMD_PWCTR3)
        self.write_data(bytearray([0x8A, 0x00]))
        self.write_cmd(TFT.CMD_PWCTR4)
        self.write_data(bytearray([0x8A, 0x2A]))
        self.write_cmd(TFT.CMD_PWCTR5)
        self.write_data(bytearray([0x8A, 0xEE]))

        self.write_cmd(TFT.CMD_VMCTR1)
        self.write_data(0x0E)

        self.write_cmd(TFT.CMD_INVOFF)
        self.write_cmd(TFT.CMD_MADCTL)
        self.write_data(0x00) # RGB

        self.write_cmd(TFT.CMD_COLMOD)
        self.write_data(0x05)

        self.write_cmd(TFT.CMD_CASET)
        self.write_data(bytearray([0x00, 0x01, 0x00, 127]))

        self.write_cmd(TFT.CMD_RASET)
        self.write_data(bytearray([0x00, 0x01, 0x00, 119]))

        self.write_cmd(TFT.CMD_GMCTRP1)
        self.write_data(bytearray([0x02, 0x1c, 0x07, 0x12, 0x37, 0x32,
            0x29, 0x2d, 0x29, 0x25, 0x2b, 0x39, 0x00, 0x01, 0x03, 0x10]))

        self.write_cmd(TFT.CMD_GMCTRN1)
        self.write_data(bytearray([0x03, 0x1d, 0x07, 0x06, 0x2e, 0x2c,
            0x29, 0x2d, 0x2e, 0x2e, 0x37, 0x3f, 0x00, 0x00, 0x02, 0x10]))

        self.write_cmd(TFT.CMD_NORON)
        time.sleep_ms(10)

        self.write_cmd(TFT.CMD_DISPON)
        time.sleep_ms(100)
