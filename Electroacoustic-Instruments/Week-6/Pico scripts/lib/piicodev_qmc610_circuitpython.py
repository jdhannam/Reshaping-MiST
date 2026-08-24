import math
import time

_I2C_ADDRESS = 0x1C

# Registers
_ADDRESS_XOUT = 0x01
_ADDRESS_YOUT = 0x03
_ADDRESS_ZOUT = 0x05

_ADDRESS_STATUS = 0x09

_ADDRESS_CONTROL1 = 0x0A
_ADDRESS_CONTROL2 = 0x0B

_ADDRESS_SIGN = 0x29

_BIT_MODE = 0
_BIT_ODR = 2
_BIT_OSR1 = 4
_BIT_OSR2 = 6

_BIT_RANGE = 2


def _read_bit(x, n):
    return (x & (1 << n)) != 0


def _set_bit(x, n):
    return x | (1 << n)


def _clear_bit(x, n):
    return x & ~(1 << n)


def _write_bit(x, n, b):
    if b:
        return _set_bit(x, n)
    return _clear_bit(x, n)


def _write_crumb(x, n, c):
    x = _write_bit(x, n, _read_bit(c, 0))
    x = _write_bit(x, n + 1, _read_bit(c, 1))
    return x


class QMC6310:

    range_gauss = {
        3000: 1e-3,
        1200: 4e-4,
        800: 2.6666667e-4,
        200: 6.6666667e-5,
    }

    range_microtesla = {
        3000: 1e-1,
        1200: 4e-2,
        800: 2.6666667e-2,
        200: 6.6666667e-3,
    }

    def __init__(
        self,
        i2c,
        address=0x1C,
        odr=3,
        osr1=0,
        osr2=3,
        range=3000,
        sign_x=0,
        sign_y=1,
        sign_z=1,
        calibration_file="calibration.cal",
        suppress_warnings=False,
    ):

        self.i2c = i2c
        self.addr = address

        self.odr = odr

        self._CR1 = 0
        self._CR2 = 0

        self.calibration_file = calibration_file
        self.suppress_warnings = suppress_warnings

        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0

        self.declination = 0

        self._data_valid = False

        sign = sign_x + sign_y * 2 + sign_z * 4

        self._set_mode(1)
        self.set_output_data_rate(odr)
        self.set_oversampling_ratio(osr1)
        self.set_oversampling_rate(osr2)
        self.set_range(range)
        self._set_sign(sign)

        if calibration_file:
            self.load_calibration()

        time.sleep(0.005)

    # -----------------------------------
    # Low-level I2C
    # -----------------------------------

    def _read_register(self, reg, length=1):

        regbuf = bytearray([reg])
        data = bytearray(length)

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto_then_readfrom(
                self.addr,
                regbuf,
                data,
            )
        finally:
            self.i2c.unlock()

        return bytes(data)

    def _write_register(self, reg, value):

        buf = bytearray([
            reg,
            value
        ])

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(
                self.addr,
                buf
            )
        finally:
            self.i2c.unlock()

    # -----------------------------------
    # Configuration
    # -----------------------------------

    def _set_mode(self, mode):

        self._CR1 = _write_crumb(
            self._CR1,
            _BIT_MODE,
            mode
        )

        self._write_register(
            _ADDRESS_CONTROL1,
            self._CR1
        )

    def set_output_data_rate(self, odr):

        self._CR1 = _write_crumb(
            self._CR1,
            _BIT_ODR,
            odr
        )

        self._write_register(
            _ADDRESS_CONTROL1,
            self._CR1
        )

    def set_oversampling_ratio(self, osr1):

        self._CR1 = _write_crumb(
            self._CR1,
            _BIT_OSR1,
            osr1
        )

        self._write_register(
            _ADDRESS_CONTROL1,
            self._CR1
        )

    def set_oversampling_rate(self, osr2):

        self._CR1 = _write_crumb(
            self._CR1,
            _BIT_OSR2,
            osr2
        )

        self._write_register(
            _ADDRESS_CONTROL1,
            self._CR1
        )

    def set_range(self, range_ut):

        if range_ut not in [3000, 1200, 800, 200]:
            raise ValueError(
                "range must be 200, 800, 1200 or 3000"
            )

        ranges = {
            3000: 0,
            1200: 1,
            800: 2,
            200: 3,
        }

        self.sensitivity = (
            self.range_microtesla[range_ut]
        )

        self._CR2 = _write_crumb(
            self._CR2,
            _BIT_RANGE,
            ranges[range_ut]
        )

        self._write_register(
            _ADDRESS_CONTROL2,
            self._CR2
        )

    def _set_sign(self, sign):

        self._write_register(
            _ADDRESS_SIGN,
            sign
        )

    # -----------------------------------
    # Reading data
    # -----------------------------------

    def _status_ready(self, status):
        return _read_bit(status, 0)

    def _status_overflow(self, status):
        return _read_bit(status, 1)

    def _signed16(self, value):

        if value >= 0x8000:
            value -= 65536

        return value

    def read(self, raw=False):

        self._data_valid = False

        nan = {
            "x": float("nan"),
            "y": float("nan"),
            "z": float("nan"),
        }

        try:
            status = int.from_bytes(
                self._read_register(
                    _ADDRESS_STATUS
                ),
                "big",
            )
        except:
            return nan

        if not self._status_ready(status):
            return nan

        if self._status_overflow(status):
            return nan

        x = int.from_bytes(
            self._read_register(
                _ADDRESS_XOUT, 2
            ),
            "little",
        )

        y = int.from_bytes(
            self._read_register(
                _ADDRESS_YOUT, 2
            ),
            "little",
        )

        z = int.from_bytes(
            self._read_register(
                _ADDRESS_ZOUT, 2
            ),
            "little",
        )

        x = self._signed16(x) - self.x_offset
        y = self._signed16(y) - self.y_offset
        z = self._signed16(z) - self.z_offset

        if not raw:
            x *= self.sensitivity
            y *= self.sensitivity
            z *= self.sensitivity

        self._data_valid = True

        return {
            "x": x,
            "y": y,
            "z": z,
        }

    def data_valid(self):
        return self._data_valid

    # -----------------------------------
    # Heading
    # -----------------------------------

    def _wrap_angle(self, angle):

        while angle < 0:
            angle += 360

        while angle >= 360:
            angle -= 360

        return angle

    def read_polar(self):

        d = self.read()

        angle = (
            math.atan2(
                d["x"],
                -d["y"]
            )
            / math.pi
            * 180.0
        )

        angle += self.declination

        angle = self._wrap_angle(angle)

        magnitude = math.sqrt(
            d["x"] ** 2 +
            d["y"] ** 2 +
            d["z"] ** 2
        )

        return {
            "polar": angle,
            "Gauss": magnitude * 100,
            "uT": magnitude,
        }

    def read_heading(self):
        return self.read_polar()["polar"]

    def read_magnitude(self):
        return self.read_polar()["uT"]

    def set_declination(self, degrees):
        self.declination = degrees

    # -----------------------------------
    # Calibration
    # -----------------------------------

    def calibrate(self):

        print(
            "Rotate sensor through all axes..."
        )

        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0

        xmin = 65535
        xmax = -65535

        ymin = 65535
        ymax = -65535

        zmin = 65535
        zmax = -65535

        for _ in range(1000):

            time.sleep(0.005)

            d = self.read(raw=True)

            x = d["x"]
            y = d["y"]
            z = d["z"]

            xmin = min(xmin, x)
            xmax = max(xmax, x)

            ymin = min(ymin, y)
            ymax = max(ymax, y)

            zmin = min(zmin, z)
            zmax = max(zmax, z)

        self.x_offset = (xmax + xmin) / 2
        self.y_offset = (ymax + ymin) / 2
        self.z_offset = (zmax + zmin) / 2

        with open(
            self.calibration_file,
            "w"
        ) as f:

            f.write(
                f"{self.x_offset}\n"
            )
            f.write(
                f"{self.y_offset}\n"
            )
            f.write(
                f"{self.z_offset}\n"
            )

    def load_calibration(self):

        try:

            with open(
                self.calibration_file,
                "r"
            ) as f:

                self.x_offset = float(
                    f.readline()
                )

                self.y_offset = float(
                    f.readline()
                )

                self.z_offset = float(
                    f.readline()
                )

        except:

            if not self.suppress_warnings:
                print(
                    "No calibration file found."
                )