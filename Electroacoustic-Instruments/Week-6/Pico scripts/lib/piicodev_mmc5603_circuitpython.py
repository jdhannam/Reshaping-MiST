# piicodev_mmc5603_circuitpython.py
#
# CircuitPython MMC5603 driver
# Based on PiicoDev MMC5603 MicroPython driver

import math
import time

_I2C_ADDRESS = 0x30

# Registers
_REG_XOUT0 = 0x00
_REG_YOUT0 = 0x02
_REG_ZOUT0 = 0x04

_REG_STATUS = 0x18
_REG_ODR = 0x1A
_REG_CTRL0 = 0x1B
_REG_CTRL1 = 0x1C
_REG_CTRL2 = 0x1D

_REG_PRODUCT_ID = 0x39

_BIT_DO_SET = 0x08
_BIT_DO_RESET = 0x10
_BIT_TAKE_MEASUREMENT = 0x01


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
        self.i2c = i2c
        self.addr = address

        self.calibration_file = calibration_file
        self.suppress_warnings = suppress_warnings

        self.x_offset = 0.0
        self.y_offset = 0.0
        self.z_offset = 0.0

        # sign_x/y/z: 0 = -1, 1 = +1 (PiicoDev convention)
        self.sign_x = -1 if sign_x == 0 else 1
        self.sign_y = -1 if sign_y == 0 else 1
        self.sign_z = -1 if sign_z == 0 else 1

        # 0.1 µT per LSB (from PiicoDev docs)
        self.sensitivity = 0.1
        self.declination = 0.0

        self._data_valid = False

        # Check product ID
        try:
            pid = self._read_register(_REG_PRODUCT_ID)[0]
            if pid != 0x10 and not suppress_warnings:
                print("Warning: Unexpected Product ID:", hex(pid))
        except Exception as e:
            if not suppress_warnings:
                print("MMC5603 init failed:", e)

        # Basic setup: reset, ODR, simple mode
        self.reset()
        self.set_output_data_rate(odr)
        self._configure_basic_mode()

        # Load calibration if available
        if calibration_file:
            self.load_calibration()

        time.sleep(0.02)

    # -----------------------------------
    # Low-level I2C
    # -----------------------------------

    def _read_register(self, reg, length=1):
        regbuf = bytearray([reg])
        data = bytearray(length)

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto_then_readfrom(self.addr, regbuf, data)
        finally:
            self.i2c.unlock()

        return bytes(data)

    def _write_register(self, reg, value):
        buf = bytearray([reg, value & 0xFF])

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(self.addr, buf)
        finally:
            self.i2c.unlock()

    # -----------------------------------
    # Configuration
    # -----------------------------------

    def reset(self):
        # Soft reset
        self._write_register(_REG_CTRL1, 0x80)
        time.sleep(0.02)

        # Set/reset sequence
        self._write_register(_REG_CTRL0, _BIT_DO_SET)
        time.sleep(0.002)
        self._write_register(_REG_CTRL0, _BIT_DO_RESET)
        time.sleep(0.002)

    def set_output_data_rate(self, odr):
        if not (1 <= odr <= 255):
            raise ValueError("ODR must be 1–255")
        self._write_register(_REG_ODR, odr)

    def _configure_basic_mode(self):
        # Keep it simple: no continuous mode, just triggered measurements
        # CTRL2: enable auto-set (optional but helpful)
        self._write_register(_REG_CTRL2, 0x10)

    def set_declination(self, degrees):
        self.declination = float(degrees)

    # -----------------------------------
    # Reading data
    # -----------------------------------

    def _take_measurement(self):
        # Trigger a single measurement
        self._write_register(_REG_CTRL0, _BIT_TAKE_MEASUREMENT)
        time.sleep(0.02)  # give it time; MMC5603 is slow

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
            self._take_measurement()
            data = self._read_register(_REG_XOUT0, 6)
        except Exception:
            return nan

        x = (data[0] << 8) | data[1]
        y = (data[2] << 8) | data[3]
        z = (data[4] << 8) | data[5]

        # Convert unsigned → signed (centered at 32768)
        x = self._signed16(x)
        y = self._signed16(y)
        z = self._signed16(z)

        # Apply offsets
        x = x - self.x_offset
        y = y - self.y_offset
        z = z - self.z_offset

        if not raw:
            x = x * self.sensitivity * self.sign_x
            y = y * self.sensitivity * self.sign_y
            z = z * self.sensitivity * self.sign_z

        self._data_valid = True

        return {
            "x": x,
            "y": y,
            "z": z,
        }

    def data_valid(self):
        return self._data_valid

    # -----------------------------------
    # Heading / magnitude
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
            math.atan2(d["x"], -d["y"]) / math.pi * 180.0
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

    # -----------------------------------
    # Calibration
    # -----------------------------------

    def calibrate(self, samples=1000):
        print("Rotate sensor through all axes...")

        self.x_offset = 0.0
        self.y_offset = 0.0
        self.z_offset = 0.0

        xmin = 1e9
        xmax = -1e9
        ymin = 1e9
        ymax = -1e9
        zmin = 1e9
        zmax = -1e9

        for _ in range(samples):
            time.sleep(0.01)
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

        self.x_offset = (xmax + xmin) / 2.0
        self.y_offset = (ymax + ymin) / 2.0
        self.z_offset = (zmax + zmin) / 2.0

        with open(self.calibration_file, "w") as f:
            f.write(f"{self.x_offset}\n")
            f.write(f"{self.y_offset}\n")
            f.write(f"{self.z_offset}\n")

        print("Calibration saved.")

    def load_calibration(self):
        try:
            with open(self.calibration_file, "r") as f:
                self.x_offset = float(f.readline())
                self.y_offset = float(f.readline())
                self.z_offset = float(f.readline())
        except Exception:
            if not self.suppress_warnings:
                print("No calibration file found.")
                
    # -----------------------------------
    # Magnet detection (robust version)
    # -----------------------------------

    def detect_magnet(self, baseline, threshold=20):
        """
        Returns:
            present: True/False
            strength_uT: magnitude of magnetic field
            delta_uT: change from baseline
            score: 0–100 scaled strength
            valid: True if sensor returned real data
        """

        d = self.read()

        # If any axis is NaN, return safe result
        if math.isnan(d["x"]) or math.isnan(d["y"]) or math.isnan(d["z"]):
            return {
                "present": False,
                "strength_uT": float("nan"),
                "delta_uT": float("nan"),
                "score": 0,
                "valid": False,
            }

        # Current magnitude
        mag = math.sqrt(d["x"]**2 + d["y"]**2 + d["z"]**2)

        # Baseline magnitude
        base_mag = math.sqrt(
            baseline["x"]**2 + baseline["y"]**2 + baseline["z"]**2
        )

        delta = abs(mag - base_mag)

        present = delta > threshold

        # Score: clamp to 0–100
        score = int(min((delta / threshold) * 50, 100))

        return {
            "present": present,
            "strength_uT": mag,
            "delta_uT": delta,
            "score": score,
            "valid": True,
        }
