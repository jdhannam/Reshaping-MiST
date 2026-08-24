# piicodev_buzzer.py

import time

_BASE_ADDR = 0x5C

_DEV_ID = 0x51

_REG_STATUS = 0x01
_REG_FIRM_MAJ = 0x02
_REG_FIRM_MIN = 0x03
_REG_I2C_ADDR = 0x04
_REG_TONE = 0x05
_REG_VOLUME = 0x06
_REG_LED = 0x07
_REG_SELFTEST = 0x09
_REG_DEVICE_ID = 0x11


class PiicoDevBuzzer:

    def __init__(
        self,
        i2c,
        address=0x5C,
        volume=2,
    ):

        self.i2c = i2c
        self.addr = address

        # Turn power LED on
        self.pwr_led(True)

        fw = self.firmware

        if fw[0] < 2:
            self.volume(volume)

    # --------------------------------------------------
    # Low level
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Sound
    # --------------------------------------------------

    def tone(self, frequency, duration=0):

        freq = int(frequency)
        dur = int(duration)

        data = (
            freq.to_bytes(2, "big") +
            dur.to_bytes(2, "big")
        )

        self._write(
            _REG_TONE,
            data
        )

    def no_tone(self):

        self.tone(0)

    # --------------------------------------------------
    # Volume
    # --------------------------------------------------

    def volume(self, level):

        if level not in (0, 1, 2):
            raise ValueError(
                "volume must be 0, 1 or 2"
            )

        self._write(
            _REG_VOLUME,
            bytes([level])
        )

        time.sleep(0.005)

    # --------------------------------------------------
    # Power LED
    # --------------------------------------------------

    def pwr_led(self, enable=True):

        self._write(
            _REG_LED,
            bytes([1 if enable else 0])
        )

    # --------------------------------------------------
    # Device Information
    # --------------------------------------------------

    @property
    def firmware(self):

        major = int.from_bytes(
            self._read(_REG_FIRM_MAJ),
            "big"
        )

        minor = int.from_bytes(
            self._read(_REG_FIRM_MIN),
            "big"
        )

        return (major, minor)

    @property
    def whoami(self):

        return self.firmware

    @property
    def self_test(self):

        return int.from_bytes(
            self._read(_REG_SELFTEST),
            "big"
        )

    def read_status(self):

        return int.from_bytes(
            self._read(_REG_STATUS),
            "big"
        )

    def read_id(self):

        return int.from_bytes(
            self._read(_REG_DEVICE_ID),
            "big"
        )

    # --------------------------------------------------
    # I2C Address
    # --------------------------------------------------

    def set_i2c_address(self, new_addr):

        if not (0x08 <= new_addr <= 0x77):
            raise ValueError(
                "Address must be 0x08-0x77"
            )

        self._write(
            _REG_I2C_ADDR,
            bytes([new_addr])
        )

        self.addr = new_addr

        time.sleep(0.005)