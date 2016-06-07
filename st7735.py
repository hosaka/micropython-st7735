# MicroPython ST7735 TFT display driver

class ST7735(object):

    def __init__(self, width, height):
        # self.tab        = tab
        self.width        = width
        self.height       = height
        self.power_on     = True
        self.inverted     = False
        self.backlight_on = True

        # default margins, set yours in HAL init
        self.margin_row = 0
        self.margin_col = 0

    def _set_window(self, x0, y0, x1, y1):
        """
        Set window frame boundaries.

        Any pixels written to the display will start from this area.
        """
        # set row: CMD_RASET
        self.write_cmd(0x2B)
        self.write_data(bytearray(
            [0x00, y0 + self.margin_row, 0x00, y1 + self.margin_row])
        )

        # set column: CMD_CASET
        self.write_cmd(0x2A)
        self.write_data(bytearray(
            [0x00, x0 + self.margin_col, 0x00, x1 + self.margin_col])
        )

        # write addresses to RAM: CMD_RAMWR
        self.write_cmd(0x2C)

    def power(self, state=None):
        """
        Get/set display power.
        """
        if state is None:
            return self.power_on
        # CMD_DISPON or CMD_DISPOFF
        self.write_cmd(0x29 if state else 0x28)
        self.power_on = state

    def clear(self, color=0xFFFF):
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

        # CMD_INVON or CMD_INVOFF
        self.write_cmd(0x21 if state else 0x20)
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
        # check the coordinates and trim if necessary
        if (x >= self.width) or (y >= self.height):
            return
        if (x + w - 1) >= self.width:
            w = self.width - x
        if (y + h - 1) >= self.height:
            h = self.height - y

        self._set_window(x, y, x + w - 1, y + h - 1)
        self.write_pixels((w*h), bytearray([color >> 8, color]))

    def line(self, x0, y0, x1, y1, color):
        # line is vertical
        if x0 == x1:
            # use the smallest y
            start, end = (x1, y1) if y1 < y0 else (x0, y0)
            self.vline(start, end, abs(y1 - y0) + 1, color)

        # line is horizontal
        elif y0 == y1:
            # use the smallest x
            start, end = (x1, y1) if x1 < x0 else (x0, y0)
            self.hline(start, end, abs(x1 - x0) + 1, color)

        else:
            # Bresenham's algorithm
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            inx = 1 if x1 - x0 > 0 else -1
            iny = 1 if y1 - y0 > 0 else -1

            # steep line
            if (dx >= dy):
                dy <<= 1
                e = dy - dx
                dx <<= 1
                while (x0 != x1):
                    # draw pixels
                    self.pixel(x0, y0, color)
                    if (e >= 0):
                        y0 += iny
                        e -= dx
                    e += dy
                    x0 += inx

            # not steep line
            else:
                dx <<= 1
                e = dx - dy
                dy <<= 1
                while(y0 != y1):
                    # draw pixels
                    self.pixel(x0, y0, color)
                    if (e >= 0):
                        x0 += inx
                        e -= dy
                    e += dx
                    y0 += iny

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

    def text(self, x, y, string, font, color, size=1):
        """
        Draw text at a given position using the user font.
        Font can be scaled with the size parameter.
        """
        if font is None:
            return

        width = size * font['width'] + 1

        px = x
        for c in string:
            self.char(px, y, c, font, color, size, size)
            px += width

            # wrap the text to the next line if it reaches the end
            if px + width > self.width:
                y += font['height'] * size + 1
                px = x

    def char(self, x, y, char, font, color, sizex=1, sizey=1):
        """
        Draw a character at a given position using the user font.

        Font is a data dictionary, can be scaled with sizex and sizey.
        """
        if font is None:
            return

        startchar = font['start']
        endchar = font['end']
        ci = ord(char)

        if (startchar <= ci <= endchar):
            width = font['width']
            height = font['height']
            ci = (ci - startchar) * width

            ch = font['data'][ci:ci + width]

            # no font scaling
            px = x
            if (sizex <= 1 and sizey <= 1):
                for c in ch:
                    py = y
                    for _ in range(height):
                        if c & 0x01:
                            self.pixel(px, py, color)
                        py += 1
                        c >>= 1
                    px += 1

            # scale to given sizes
            else:
                for c in ch:
                    py = y
                    for _ in range(height):
                        if c & 0x01:
                            self.rect(px, py, sizex, sizey, color)
                        py += sizey
                        c >>= 1
                    px += sizex
        else:
            # character not found in this font
            return

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
