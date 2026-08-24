import time

_I2C_ADDRESS = 0x2C

# Registers
_REG_COMMAND = 0x01
_REG_COM_I_EN = 0x02
_REG_DIV_I_EN = 0x03
_REG_COM_IRQ = 0x04
_REG_DIV_IRQ = 0x05
_REG_ERROR = 0x06
_REG_STATUS_2 = 0x08
_REG_FIFO_DATA = 0x09
_REG_FIFO_LEVEL = 0x0A
_REG_CONTROL = 0x0C
_REG_BIT_FRAMING = 0x0D
_REG_MODE = 0x11
_REG_TX_CONTROL = 0x14
_REG_TX_ASK = 0x15
_REG_CRC_RESULT_MSB = 0x21
_REG_CRC_RESULT_LSB = 0x22
_REG_T_MODE = 0x2A
_REG_T_PRESCALER = 0x2B
_REG_T_RELOAD_HI = 0x2C
_REG_T_RELOAD_LO = 0x2D

_CMD_IDLE = 0x00
_CMD_CALC_CRC = 0x03
_CMD_TRANCEIVE = 0x0C
_CMD_MF_AUTHENT = 0x0E
_CMD_SOFT_RESET = 0x0F

_TAG_CMD_REQIDL = 0x26
_TAG_CMD_REQALL = 0x52

_TAG_CMD_ANTCOL1 = 0x93
_TAG_CMD_ANTCOL2 = 0x95
_TAG_CMD_ANTCOL3 = 0x97


class PiicoDev_RFID:

    OK = 1
    NOTAGERR = 2
    ERR = 3

    def __init__(
        self,
        i2c,
        address=_I2C_ADDRESS
    ):

        self.i2c = i2c
        self.address = address

        self._tag_present = False
        self._read_tag_id_success = False

        self.reset()

        time.sleep(0.05)

        self._wreg(_REG_T_MODE, 0x80)
        self._wreg(_REG_T_PRESCALER, 0xA9)
        self._wreg(_REG_T_RELOAD_HI, 0x03)
        self._wreg(_REG_T_RELOAD_LO, 0xE8)

        self._wreg(_REG_TX_ASK, 0x40)
        self._wreg(_REG_MODE, 0x3D)

        self._wreg(_REG_DIV_I_EN, 0x80)
        self._wreg(_REG_COM_I_EN, 0x20)

        self.antennaOn()

    # ---------------------------------------------------
    # Low-level I2C
    # ---------------------------------------------------

    def _wreg(self, reg, value):

        buffer = bytearray([
            reg,
            value
        ])

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(
                self.address,
                buffer
            )
        finally:
            self.i2c.unlock()

    def _wfifo(self, reg, values):

        buffer = bytearray(
            [reg] + list(values)
        )

        while not self.i2c.try_lock():
            pass

        try:
            self.i2c.writeto(
                self.address,
                buffer
            )
        finally:
            self.i2c.unlock()

    def _rreg(self, reg):

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

    # ---------------------------------------------------
    # Register helpers
    # ---------------------------------------------------

    def _sflags(self, reg, mask):

        current = self._rreg(reg)

        self._wreg(
            reg,
            current | mask
        )

    def _cflags(self, reg, mask):

        current = self._rreg(reg)

        self._wreg(
            reg,
            current & (~mask)
        )

    # ---------------------------------------------------
    # Core MFRC522 communications
    # ---------------------------------------------------

    def _tocard(self, cmd, send):

        recv = []

        bits = 0
        irq_en = 0
        wait_irq = 0

        stat = self.ERR

        if cmd == _CMD_MF_AUTHENT:
            irq_en = 0x12
            wait_irq = 0x10

        elif cmd == _CMD_TRANCEIVE:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(
            _REG_COMMAND,
            _CMD_IDLE
        )

        self._wreg(
            _REG_COM_IRQ,
            0x7F
        )

        self._sflags(
            _REG_FIFO_LEVEL,
            0x80
        )

        self._wfifo(
            _REG_FIFO_DATA,
            send
        )

        self._wreg(
            _REG_COMMAND,
            cmd
        )

        if cmd == _CMD_TRANCEIVE:
            self._sflags(
                _REG_BIT_FRAMING,
                0x80
            )

        timeout = 20000

        while timeout:

            irq = self._rreg(
                _REG_COM_IRQ
            )

            timeout -= 1

            if irq & wait_irq:
                break

            if irq & 0x01:
                break

        self._cflags(
            _REG_BIT_FRAMING,
            0x80
        )

        if timeout:

            if (
                self._rreg(_REG_ERROR)
                & 0x1B
            ) == 0:

                stat = self.OK

                if irq & irq_en & 0x01:

                    stat = self.NOTAGERR

                elif cmd == _CMD_TRANCEIVE:

                    count = self._rreg(
                        _REG_FIFO_LEVEL
                    )

                    lbits = (
                        self._rreg(
                            _REG_CONTROL
                        ) & 0x07
                    )

                    if lbits:
                        bits = (
                            (count - 1)
                            * 8
                            + lbits
                        )
                    else:
                        bits = count * 8

                    if count == 0:
                        count = 1
                    elif count > 16:
                        count = 16

                    for _ in range(count):

                        recv.append(
                            self._rreg(
                                _REG_FIFO_DATA
                            )
                        )

            else:

                stat = self.ERR

        return stat, recv, bits

    # ---------------------------------------------------
    # CRC engine
    # ---------------------------------------------------

    def _crc(self, data):

        self._wreg(
            _REG_COMMAND,
            _CMD_IDLE
        )

        self._cflags(
            _REG_DIV_IRQ,
            0x04
        )

        self._sflags(
            _REG_FIFO_LEVEL,
            0x80
        )

        for c in data:

            self._wreg(
                _REG_FIFO_DATA,
                c
            )

        self._wreg(
            _REG_COMMAND,
            _CMD_CALC_CRC
        )

        timeout = 0xFF

        while timeout:

            irq = self._rreg(
                _REG_DIV_IRQ
            )

            if irq & 0x04:
                break

            timeout -= 1

        self._wreg(
            _REG_COMMAND,
            _CMD_IDLE
        )

        return [
            self._rreg(
                _REG_CRC_RESULT_LSB
            ),
            self._rreg(
                _REG_CRC_RESULT_MSB
            ),
        ]

    # ---------------------------------------------------
    # RFID functions
    # ---------------------------------------------------

    def _request(self, mode):

        self._wreg(
            _REG_BIT_FRAMING,
            0x07
        )

        stat, recv, bits = self._tocard(
            _CMD_TRANCEIVE,
            [mode]
        )

        if (
            stat != self.OK
            or bits != 0x10
        ):
            stat = self.ERR

        return stat, bits

    def _anticoll(
        self,
        anticolN=_TAG_CMD_ANTCOL1
    ):

        ser_chk = 0

        ser = [
            anticolN,
            0x20
        ]

        self._wreg(
            _REG_BIT_FRAMING,
            0x00
        )

        stat, recv, bits = self._tocard(
            _CMD_TRANCEIVE,
            ser
        )

        if stat == self.OK:

            if len(recv) == 5:

                for i in range(4):
                    ser_chk ^= recv[i]

                if ser_chk != recv[4]:
                    stat = self.ERR

            else:

                stat = self.ERR

        return stat, recv

    def _selectTag(
        self,
        sernum,
        anticolN
    ):

        buf = [
            anticolN,
            0x70
        ]

        buf.extend(sernum)

        crc = self._crc(buf)

        buf.extend(crc)

        status, _, bits = self._tocard(
            _CMD_TRANCEIVE,
            buf
        )

        return (
            status == self.OK
            and bits == 0x18
        )

    # ---------------------------------------------------
    # Public API
    # ---------------------------------------------------

    def reset(self):

        self._wreg(
            _REG_COMMAND,
            _CMD_SOFT_RESET
        )

    def antennaOn(self):

        if not (
            self._rreg(
                _REG_TX_CONTROL
            ) & 0x03
        ):
            self._sflags(
                _REG_TX_CONTROL,
                0x83
            )

    def tagPresent(self):

        stat, _ = self._request(
            _TAG_CMD_REQIDL
        )

        return stat == self.OK

    def readID(self):

        stat, uid = self._anticoll()

        if stat != self.OK:
            return ""

        return ":".join(
            "{:02X}".format(x)
            for x in uid[:4]
        )