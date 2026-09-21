# ============================================================
# Tutorial — VCO Control with PiicoDev MMC5603
# ============================================================
#
# What this script demonstrates:
#
# 1. Reading magnetic field values
# 2. Mapping sensor values to synthesizer controls
# 3. Controlling oscillator pitch and amplitude
# 4. Smoothing sensor data for stable operation
#
#
# X Axis = Pitch
# Y Axis = Amplitude
#
# Bring a magnet close to the sensor
# and listen to how the sound changes.
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import busio
import audiobusio
import audiomixer
import synthio
import ulab.numpy as np
import time

from piicodev_mmc5603_circuitpython import MMC5603

# ------------------------------------------------------------
# AUDIO SETUP (I2S)
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP17,
    word_select=board.GP18,
    data=board.GP16,
)


# ------------------------------------------------------------
# MIXER SETUP
# ------------------------------------------------------------

mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)

audio.play(mixer)


# ------------------------------------------------------------
# CREATE SYNTHESIZER
# ------------------------------------------------------------

synth = synthio.Synthesizer(
    sample_rate=22050
)


# ------------------------------------------------------------
# CREATE MAGNETOMETER
# ------------------------------------------------------------
#
# PiicoDev MMC5603
#
# Measures magnetic field strength
# on three axes:
#
# X
# Y
# Z
#
# ------------------------------------------------------------

i2c = busio.I2C(board.GP9, board.GP8)
mag = MMC5603(i2c)

# ------------------------------------------------------------
# WAVETABLE SETTINGS
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000

wave_sine = np.array(
    np.sin(
        np.linspace(
            0,
            2 * np.pi,
            SAMPLE_SIZE,
            endpoint=False,
        )
    ) * AMPLITUDE,
    dtype=np.int16,
)


# ------------------------------------------------------------
# SYNTH CONTROL RANGES
# ------------------------------------------------------------

MIN_FREQ = 50
MAX_FREQ = 2000

MIN_AMP = 0.0
MAX_AMP = 0.5


# ------------------------------------------------------------
# MAGNETIC FIELD RANGE
# ------------------------------------------------------------
#
# These values are estimates that work
# well for classroom demonstrations.
#
# Bringing a magnet closer increases
# the field strength.
#
# ------------------------------------------------------------

MIN_FIELD = -2000
MAX_FIELD = 2000


# ------------------------------------------------------------
# CREATE NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    amplitude=0.1,
)

mixer.voice[0].play(synth)

synth.press(note)

print("VCO running.")
print("Move a magnet near the sensor.")
print("X Axis = Pitch")
print("Y Axis = Amplitude")


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def clamp(value, minimum, maximum):
    return max(minimum,min(maximum, value))


def scale_value(value,in_min,in_max,out_min,out_max,):
    return out_min + ((value - in_min)/(in_max - in_min)) * (out_max - out_min)


def exponential_pitch(value):
    """
    Convert magnetic field strength
    into musical pitch.

    Human hearing is logarithmic.
    """

    value = clamp(
        value,
        MIN_FIELD,
        MAX_FIELD
    )

    position = (value - MIN_FIELD) / (MAX_FIELD - MIN_FIELD)

    return MIN_FREQ * ((MAX_FREQ / MIN_FREQ) ** position)


# ------------------------------------------------------------
# SMOOTHING VARIABLES
# ------------------------------------------------------------

smooth_freq = 220
smooth_amp = 0.1
SMOOTHING = 0.1
last_print = 0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

while True:

    # ----------------------------------------
    # READ MAGNETOMETER
    # ----------------------------------------

    x, y, z = mag.read()

    # ----------------------------------------
    # CONVERT TO SYNTH VALUES
    # ----------------------------------------

    target_freq = exponential_pitch(x)

    target_amp = scale_value(
        clamp(
            y,
            MIN_FIELD,
            MAX_FIELD
        ),
        MIN_FIELD,
        MAX_FIELD,
        MIN_AMP,
        MAX_AMP,
    )

    # ----------------------------------------
    # SMOOTH VALUES
    # ----------------------------------------

    smooth_freq += (target_freq - smooth_freq) * SMOOTHING
    smooth_amp += (target_amp - smooth_amp) * SMOOTHING

    # ----------------------------------------
    # UPDATE SYNTH
    # ----------------------------------------

    note.frequency = smooth_freq
    note.amplitude = smooth_amp

    # ----------------------------------------
    # SERIAL OUTPUT
    # ----------------------------------------

    if time.monotonic() - last_print > 0.25:

        print(
            "X:",
            int(x),
            "| Y:",
            int(y),
            "| Freq:",
            int(smooth_freq),
            "Hz | Amp:",
            round(smooth_amp, 2),
        )

        last_print = time.monotonic()

    time.sleep(0.01)