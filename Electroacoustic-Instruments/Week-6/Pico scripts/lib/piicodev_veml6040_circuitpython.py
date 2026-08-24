# this code is for using the piicodev Colour sensor
# with circuitpython

import math

_VEML6040_ADDRESS = 0x10

_CONF = 0x00
_REG_RED = 0x08
_REG_GREEN = 0x09
_REG_BLUE = 0x0A
_REG_WHITE = 0x0B

_G_SENSITIVITY = 0.25168


def rgb2hsv(r, g, b):
    r = float(r / 65535)
    g = float(g / 65535)
    b = float(b / 65535)

    high = max(r, g, b)
    low = min(r, g, b)

    h = high
    s = high
    v = high

    d = high - low
    s = 0 if high == 0 else d / high

    if high == low:
        h = 0.0
    else:
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return {
        "hue": h * 360,
        "sat": s,
        "val": v,
    }


class VEML6040:

    def __init__(self, i2c, address=0x10):
        self.i2c = i2c
        self.address = address

        # Wake sensor
        self._write16(_CONF, 0x0000)

    def _write16(self, reg, value):
        buf = bytearray(3)
        buf[0] = reg
        buf[1] = value & 0xFF
        buf[2] = (value >> 8) & 0xFF

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(self.address, buf)
        finally:
            self.i2c.unlock()

    def _read16(self, reg):
        regbuf = bytearray([reg])
        databuf = bytearray(2)

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto_then_readfrom(
                self.address,
                regbuf,
                databuf
            )
        finally:
            self.i2c.unlock()

        return databuf[0] | (databuf[1] << 8)

    def read_rgb(self):

        red = self._read16(_REG_RED)
        green = self._read16(_REG_GREEN)
        blue = self._read16(_REG_BLUE)
        white = self._read16(_REG_WHITE)

        colour_x = (
            (-0.023249 * red)
            + (0.291014 * green)
            + (-0.364880 * blue)
        )

        colour_y = (
            (-0.042799 * red)
            + (0.272148 * green)
            + (-0.279591 * blue)
        )

        colour_z = (
            (-0.155901 * red)
            + (0.251534 * green)
            + (-0.076240 * blue)
        )

        total = colour_x + colour_y + colour_z

        if total == 0:
            cct = float("nan")
        else:
            x = colour_x / total
            y = colour_y / total

            n = (x - 0.3320) / (0.1858 - y)

            cct = (
                449.0 * n**3
                + 3525.0 * n**2
                + 6823.3 * n
                + 5520.33
            )

        als = green * _G_SENSITIVITY

        return {
            "red": red,
            "green": green,
            "blue": blue,
            "white": white,
            "als": als,
            "cct": cct,
        }

    def read_hsv(self):
        d = self.read_rgb()
        return rgb2hsv(
            d["red"],
            d["green"],
            d["blue"]
        )

    def classify_hue(
        self,
        hues={
            "red": 0,
            "yellow": 60,
            "green": 120,
            "cyan": 180,
            "blue": 240,
            "magenta": 300,
        },
        min_brightness=0,
    ):
        d = self.read_hsv()

        if d["val"] <= min_brightness:
            return "None"

        return min(
            hues.items(),
            key=lambda x: min(
                360 - abs(d["hue"] - x[1]),
                abs(d["hue"] - x[1]),
            ),
        )[0]
