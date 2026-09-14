# this code is for using the piicodev magnetometer sensor
# with circuitpython

# MMC5603.py
#
# CircuitPython MMC5603 driver
# Based on Core Electronics PiicoDev MMC5603 MicroPython driver


import math
import time
from adafruit_bus_device.i2c_device import I2CDevice

_I2C_ADDRESS = 0x30

_REG_XOUT0 = 0x00
_REG_XOUT1 = 0x01
_REG_YOUT0 = 0x02
_REG_YOUT1 = 0x03
_REG_ZOUT0 = 0x04
_REG_ZOUT1 = 0x05

_REG_STATUS = 0x18
_REG_ODR = 0x1A
_REG_CTRL0 = 0x1B
_REG_CTRL1 = 0x1C
_REG_CTRL2 = 0x1D

_REG_PRODUCT_ID = 0x39

_BIT_DO_SET = 0x08
_BIT_DO_RESET = 0x10


class MMC5603:

    def __init__(
        self,
        i2c,
        address=_I2C_ADDRESS,
        odr=255,
        sign_x=0,
        sign_y=0,
        sign_z=1,
        calibration_file="calibration.cal",
        suppress_warnings=False,
    ):

        self.address = address
        self.device = I2CDevice(i2c, address)

        self.calibration_file = calibration_file
        self.suppress_warnings = suppress_warnings

        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0

        self.sign_x = -1 if sign_x == 0 else 1
        self.sign_y = -1 if sign_y == 0 else 1
        self.sign_z = -1 if sign_z == 0 else 1

        self.sensitivity = 0.1
        self.declination = 0
        self._data_valid = False

        self.check_id()
        self.reset()
        self.set_output_data_rate(odr)
        self.enable_continuous_mode()

        if calibration_file:
            self.load_calibration()

    # -----------------------------
    # Low-level I2C
    # -----------------------------

    def _write_register(self, reg, value):

        with self.device:
            self.device.write(
                bytes([
                    reg,
                    value & 0xFF
                ])
            )

    def _read_register(self, reg, length=1):

        data = bytearray(length)

        with self.device:
            self.device.write(bytes([reg]))

        with self.device:
            self.device.readinto(data)

        return bytes(data)

    # -----------------------------
    # Configuration
    # -----------------------------

    def check_id(self):

        pid = self._read_register(
            _REG_PRODUCT_ID
        )[0]

        if pid != 0x10:
            print(
                "Warning: Unexpected Product ID:",
                hex(pid)
            )

    def reset(self):

        self._write_register(
            _REG_CTRL1,
            0x80
        )

        time.sleep(0.02)

        self.set_reset()

    def set_reset(self):

        self._write_register(
            _REG_CTRL0,
            _BIT_DO_SET
        )

        time.sleep(0.001)

        self._write_register(
            _REG_CTRL0,
            _BIT_DO_RESET
        )

        time.sleep(0.001)

    def set_output_data_rate(self, odr):

        if not (1 <= odr <= 255):
            raise ValueError(
                "ODR must be 1-255"
            )

        self._write_register(
            _REG_ODR,
            odr
        )

    def enable_continuous_mode(self):

        self._write_register(
            _REG_CTRL0,
            0x80
        )

        self._write_register(
            _REG_CTRL2,
            0x10
        )

    def set_declination(self, degrees):
        self.declination = degrees

    # -----------------------------
    # Reading
    # -----------------------------

    def data_valid(self):
        return self._data_valid

    def read(self, raw=False):

        self._data_valid = False

        try:
            data = self._read_register(
                _REG_XOUT0,
                9
            )

            x = (
                (data[0] << 8)
                | data[1]
            )

            y = (
                (data[2] << 8)
                | data[3]
            )

            z = (
                (data[4] << 8)
                | data[5]
            )

            self._data_valid = True

        except Exception:

            return {
                "x": float("nan"),
                "y": float("nan"),
                "z": float("nan"),
            }

        x -= (1 << 15)
        y -= (1 << 15)
        z -= (1 << 15)

        x -= self.x_offset
        y -= self.y_offset
        z -= self.z_offset

        if not raw:
            x *= self.sensitivity * self.sign_x
            y *= self.sensitivity * self.sign_y
            z *= self.sensitivity * self.sign_z

        return {
            "x": x,
            "y": y,
            "z": z,
        }

    def read_polar(self):

        d = self.read()

        angle = (
            math.atan2(
                d["x"],
                -d["y"]
            )
            / math.pi
            * 180
        )

        angle += self.declination

        while angle < 0:
            angle += 360

        while angle >= 360:
            angle -= 360

        mag = math.sqrt(
            d["x"] ** 2
            + d["y"] ** 2
            + d["z"] ** 2
        )

        return {
            "polar": angle,
            "Gauss": mag * 100,
            "uT": mag,
        }

    def read_heading(self):
        return self.read_polar()["polar"]

    def read_magnitude(self):
        return self.read_polar()["uT"]

    # -----------------------------
    # Calibration
    # -----------------------------

    def load_calibration(self):

        try:

            with open(
                self.calibration_