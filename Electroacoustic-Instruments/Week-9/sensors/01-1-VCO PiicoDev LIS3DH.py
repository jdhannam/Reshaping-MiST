# ============================================================
# Tutorial — VCO Control with PiicoDev LIS3DH
# ============================================================
#
# What this script demonstrates:
#
# 1. Reading data from a 3-axis accelerometer
# 2. Mapping tilt into synthesizer controls
# 3. Using motion to control pitch and amplitude
# 4. Smoothing accelerometer readings
#
#
# X Axis = Pitch
# Y Axis = Amplitude
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
import adafruit_lis3dh


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
# CREATE ACCELEROMETER
# ------------------------------------------------------------
#
# PiicoDev LIS3DH
#
# Reads:
#
# X axis
# Y axis
# Z axis
#
# ------------------------------------------------------------

i2c = busio.I2C(board.GP9, board.GP8)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)


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
print("Tilt X = Pitch")
print("Tilt Y = Amplitude")


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
#
# Accelerometer values are approximately:
#
# -1.0 g to +1.0 g
#
# We convert this range into useful
# synthesizer values.
#
# ------------------------------------------------------------

def scale_axis(value,in_min,in_max,out_min,out_max,):
    return out_min + ((value - in_min)/(in_max - in_min)) * (out_max - out_min)


def exponential_pitch(value):
    """
    Convert tilt into musical pitch.

    Human hearing responds
    logarithmically to frequency.
    """

    position = (value + 1.0) / 2.0

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
    # READ ACCELEROMETER
    # ----------------------------------------

    x, y, z = lis3dh.acceleration()

    # ----------------------------------------
    # MAP SENSOR TO SYNTH
    # ----------------------------------------

    target_freq = exponential_pitch(x)

    target_amp = scale_axis(
        y,
        -1.0,
        1.0,
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

    if (
        time.monotonic()
        - last_print
        > 0.25
    ):

        print(
            "X:",
            round(x, 2),
            "| Y:",
            round(y, 2),
            "| Freq:",
            int(smooth_freq),
            "Hz | Amp:",
            round(smooth_amp, 2),
        )

        last_print = time.monotonic()

    time.sleep(0.01)