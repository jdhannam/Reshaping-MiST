# piicodev_ultrasonic.py
#
# CircuitPython driver for
# PiicoDev Ultrasonic Rangefinder

class PiicoDevUltrasonic:

    DEVICE_ID = 578
    DEFAULT_ADDRESS = 0x35

    REG_WHOAMI = 0x01
    REG_FIRM_MAJ = 0x02
    REG_FIRM_MIN = 0x03
    REG_I2C_ADDRESS = 0x04
    REG_RAW = 0x05
    REG_PERIOD = 0x06
    REG_LED = 0x07
    REG_STATUS = 0x08
    REG_SELF_TEST = 0x09

    def __init__(
        self,
        i2c,
        address=DEFAULT_ADDRESS,
        minimum=0.0,
        maximum=100.0,
    ):

        self.i2c = i2c
        self._address = address

        self.minimum = minimum
        self.maximum = maximum

        self.millimeters_per_microsecond = 0.343

        try:
            if self.whoami != self.DEVICE_ID:
                print(
                    "Warning: unexpected device ID:",
                    self.whoami
                )
        except Exception as e:
            print(
                "Couldn't find ultrasonic sensor:",
                e
            )

    # ---------------------------------------
    # low level helpers
    # ---------------------------------------

    def _read(self, reg, length=1):

        regbuf = bytearray([reg])
        data = bytearray(length)

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto_then_readfrom(
                self._address,
                regbuf,
                data
            )
        finally:
            self.i2c.unlock()

        return bytes(data)

    def _write(self, reg, data):

        buf = bytearray(1 + len(data))

        buf[0] = reg

        for i, v in enumerate(data):
            buf[i + 1] = v

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(
                self._address,
                buf
            )
        finally:
            self.i2c.unlock()

    def _read_int(self, reg, length=1):

        return int.from_bytes(
            self._read(reg, length),
            "big"
        )

    def _write_int(
        self,
        reg,
        value,
        length=1
    ):

        self._write(
            reg,
            value.to_bytes(length, "big")
        )

    def _set_bit(self, value, bit):
        return value | (1 << bit)

    # ---------------------------------------
    # status
    # ---------------------------------------

    @property
    def new_sample_available(self):

        status = self._read_int(
            self.REG_STATUS
        )

        return bool(status & 0x01)

    # ---------------------------------------
    # ranging
    # ---------------------------------------

    @property
    def round_trip_us(self):

        return self._read_int(
            self.REG_RAW,
            2
        )

    @property
    def distance_mm(self):

        return round(
            self.round_trip_us
            * self.millimeters_per_microsecond
            / 2
        )

    @property
    def distance_inch(self):

        return self.distance_mm / 25.4

    # ---------------------------------------
    # address
    # ---------------------------------------

    @property
    def address(self):

        return self._address

    def set_i2c_address(self, addr):

        if not (
            0x08 <= addr <= 0x77
        ):
            raise ValueError(
                "Address must be 0x08-0x77"
            )

        self._write_int(
            self.REG_I2C_ADDRESS,
            addr
        )

        self._address = addr

    # ---------------------------------------
    # LED
    # ---------------------------------------

    @property
    def led(self):

        return bool(
            self._read_int(
                self.REG_LED
            )
        )

    @led.setter
    def led(self, value):

        self._write_int(
            self._set_bit(
                self.REG_LED,
                7
            ),
            int(bool(value))
        )

    # ---------------------------------------
    # sample period
    # ---------------------------------------

    @property
    def period_ms(self):

        return self._read_int(
            self.REG_PERIOD,
            2
        )

    @period_ms.setter
    def period_ms(self, period):

        if not (
            0 <= period <= 65535
        ):
            raise ValueError(
                "period_ms must be 0-65535"
            )

        self._write_int(
            self._set_bit(
                self.REG_PERIOD,
                7
            ),
            period,
            2
        )

    # ---------------------------------------
    # info
    # ---------------------------------------

    @property
    def whoami(self):

        return self._read_int(
            self.REG_WHOAMI,
            2
        )

    @property
    def firmware(self):

        return (
            self._read_int(
                self.REG_FIRM_MAJ
            ),
            self._read_int(
                self.REG_FIRM_MIN
            ),
        )

    @property
    def self_test(self):

        return self._read_int(
            self.REG_SELF_TEST
        )