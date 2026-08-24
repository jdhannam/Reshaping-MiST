import time

_BASE_ADDR = 0x08

_REG_DEVID = 0x00
_REG_FIRMVER = 0x01

_REG_CTRL = 0x03
_REG_CLEAR = 0x04
_REG_I2CADDR = 0x05

_REG_BRIGHT = 0x06
_REG_LEDVALS = 0x07


def wheel(h, s=1.0, v=1.0):

    if s == 0:
        x = int(v * 255)
        return (x, x, x)

    i = int(h * 6)
    f = h * 6 - i

    p = int(255 * (v * (1 - s)))
    q = int(255 * (v * (1 - s * f)))
    t = int(255 * (v * (1 - s * (1 - f))))

    v = int(v * 255)

    i %= 6

    if i == 0:
        return (v, t, p)

    if i == 1:
        return (q, v, p)

    if i == 2:
        return (p, v, t)

    if i == 3:
        return (p, q, v)

    if i == 4:
        return (t, p, v)

    return (v, p, q)


class PiicoDevRGB:

    def __init__(
        self,
        i2c,
        address=0x08,
        brightness=50,
    ):

        self.i2c = i2c
        self.addr = address

        self.led = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        self.brightness = brightness

        self.set_brightness(brightness)
        self.show()

    # ---------------------
    # I2C helpers
    # ---------------------

    def _write(self, reg, data):

        buf = bytearray(1 + len(data))

        buf[0] = reg

        for i, b in enumerate(data):
            buf[i + 1] = b

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(
                self.addr,
                buf
            )
        finally:
            self.i2c.unlock()

    def _read(self, reg, length=1):

        regbuf = bytearray([reg])
        data = bytearray(length)

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto_then_readfrom(
                self.addr,
                regbuf,
                data
            )
        finally:
            self.i2c.unlock()

        return bytes(data)

    # ---------------------
    # LED control
    # ---------------------

    def set_pixel(self, index, colour):

        self.led[index] = [
            round(colour[0]),
            round(colour[1]),
            round(colour[2]),
        ]

    def fill(self, colour):

        for i in range(3):
            self.led[i] = list(colour)

        self.show()

    def show(self):

        buffer = (
            bytes(self.led[0]) +
            bytes(self.led[1]) +
            bytes(self.led[2])
        )

        self._write(
            _REG_LEDVALS,
            buffer
        )

    def clear(self):

        self._write(
            _REG_CLEAR,
            b"\x01"
        )

        self.led = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        time.sleep(0.001)

    # ---------------------
    # Brightness
    # ---------------------

    def set_brightness(self, value):

        value = max(
            0,
            min(255, int(value))
        )

        self.brightness = value

        self._write(
            _REG_BRIGHT,
            bytes([value])
        )

        time.sleep(0.001)

    # ---------------------
    # Power LED
    # ---------------------

    def pwr_led(self, state):

        self._write(
            _REG_CTRL,
            bytes([
                1 if state else 0
            ])
        )

        time.sleep(0.001)

    # ---------------------
    # Device info
    # ---------------------

    def read_firmware(self):

        fw = self._read(
            _REG_FIRMVER,
            2
        )

        return (
            fw[1],
            fw[0]
        )

    def read_id(self):

        return self._read(
            _REG_DEVID,
            1
        )[0]

    # ---------------------
    # Address
    # ---------------------

    def set_i2c_address(
        self,
        new_addr
    ):

        if not (
            0x08 <= new_addr <= 0x77
        ):
            raise ValueError(
                "Address must be 0x08-0x77"
            )

        self._write(
            _REG_I2CADDR,
            bytes([new_addr])
        )

        self.addr = new_addr

        time.sleep(0.005)