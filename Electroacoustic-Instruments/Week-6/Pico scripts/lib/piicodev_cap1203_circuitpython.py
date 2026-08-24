# this code is for using the piicodev touch sensor
# with circuitpython

# cap1203.py
#
# CircuitPython CAP1203 driver
# Based on Core Electronics PiicoDev CAP1203 MicroPython driver

# cap1203.py

class CAP1203:

    ADDRESS = 0x28

    MAIN_CONTROL = 0x00
    GENERAL_STATUS = 0x02
    SENSOR_INPUT_STATUS = 0x03

    SENSOR_INPUT_1_DELTA = 0x10
    SENSOR_INPUT_2_DELTA = 0x11
    SENSOR_INPUT_3_DELTA = 0x12

    SENSITIVITY_CONTROL = 0x1F

    MULTIPLE_TOUCH_CONFIG = 0x2A

    PRODUCT_ID = 0xFD
    PRODUCT_ID_VALUE = 0x6D

    def __init__(
        self,
        i2c,
        address=0x28,
        touchmode="multi",
        sensitivity=3
    ):
        self.i2c = i2c
        self.address = address

        try:
            pid = self._read8(self.PRODUCT_ID)

            if pid != self.PRODUCT_ID_VALUE:
                print(
                    "Warning: Unexpected Product ID:",
                    hex(pid)
                )
        except Exception as e:
            print("CAP1203 init failed:", e)

        self.touchmode = touchmode
        self.sensitivity = sensitivity

        # Clear any pending interrupt flags
        self.clear_interrupt()

    # ---------------------------------------------------------
    # LOW LEVEL I2C
    # ---------------------------------------------------------

    def _read8(self, reg):

        regbuf = bytearray([reg])
        data = bytearray(1)

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto_then_readfrom(
                self.address,
                regbuf,
                data
            )
        finally:
            self.i2c.unlock()

        return data[0]

    def _write8(self, reg, value):

        data = bytearray([
            reg,
            value & 0xFF
        ])

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(
                self.address,
                data
            )
        finally:
            self.i2c.unlock()

    def _set_bits(self, reg, value, mask):

        current = self._read8(reg)

        current &= ~mask
        current |= (value & mask)

        self._write8(
            reg,
            current
        )

    # ---------------------------------------------------------
    # TOUCH MODE
    # ---------------------------------------------------------

    @property
    def touchmode(self):

        reg = self._read8(
            self.MULTIPLE_TOUCH_CONFIG
        )

        if reg & 0x80:
            return "single"

        return "multi"

    @touchmode.setter
    def touchmode(self, mode):

        if mode == "single":

            self._set_bits(
                self.MULTIPLE_TOUCH_CONFIG,
                0x80,
                0x80
            )

        elif mode == "multi":

            self._set_bits(
                self.MULTIPLE_TOUCH_CONFIG,
                0x00,
                0x80
            )

        else:

            raise ValueError(
                "touchmode must be 'single' or 'multi'"
            )

    # ---------------------------------------------------------
    # SENSITIVITY
    # ---------------------------------------------------------

    @property
    def sensitivity(self):

        reg = self._read8(
            self.SENSITIVITY_CONTROL
        )

        return (reg >> 4) & 0x07

    @sensitivity.setter
    def sensitivity(self, value):

        if not 0 <= value <= 7:
            raise ValueError(
                "sensitivity must be 0-7"
            )

        self._set_bits(
            self.SENSITIVITY_CONTROL,
            value << 4,
            0x70
        )

    # ---------------------------------------------------------
    # INTERRUPTS
    # ---------------------------------------------------------

    def clear_interrupt(self):

        self._write8(
            self.MAIN_CONTROL,
            0x00
        )

    @property
    def interrupt(self):

        return bool(
            self._read8(
                self.MAIN_CONTROL
            ) & 0x01
        )

    # ---------------------------------------------------------
    # TOUCH STATUS
    # ---------------------------------------------------------

    def read(self):

        status = self._read8(
            self.SENSOR_INPUT_STATUS
        )

        result = {
            1: 1 if status & 0x01 else 0,
            2: 1 if status & 0x02 else 0,
            3: 1 if status & 0x04 else 0,
        }

        self.clear_interrupt()

        return result

    # ---------------------------------------------------------
    # RAW DELTA COUNTS
    # ---------------------------------------------------------

    def _signed8(self, value):

        if value > 127:
            return value - 256

        return value

    def read_delta_counts(self):

        return {
            1: self._signed8(
                self._read8(
                    self.SENSOR_INPUT_1_DELTA
                )
            ),
            2: self._signed8(
                self._read8(
                    self.SENSOR_INPUT_2_DELTA
                )
            ),
            3: self._signed8(
                self._read8(
                    self.SENSOR_INPUT_3_DELTA
                )
            ),
        }