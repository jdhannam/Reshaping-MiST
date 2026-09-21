# ============================================================
# Tutorial — VCO Control with PiicoDev Colour Sensor
# ============================================================
#
# What this script demonstrates:
#
# 1. Reading colour data from a VEML6040
# 2. Mapping colour values to synthesizer controls
# 3. Controlling oscillator pitch and amplitude
# 4. Smoothing sensor data for stable operation
#
#
# RED Channel  = Pitch
# BLUE Channel = Amplitude
#
# Try placing different coloured objects
# in front of the sensor.
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

from piicodev_veml6040_circuitpython import VEML6040


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
# CREATE COLOUR SENSOR
# ------------------------------------------------------------
#
# PiicoDev VEML6040
#
# Returns:
#
# Red
# Green
# Blue
# White
#
# ------------------------------------------------------------

i2c = busio.I2C(board.GP9, board.GP8)
colour = VEML6040(i2c)

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
# COLOUR VALUE RANGE
# ------------------------------------------------------------
#
# Classroom-friendly range.
#
# You may need to adjust these values
# depending on lighting conditions.
#
# ------------------------------------------------------------

MIN_COLOUR = 0
MAX_COLOUR = 10000


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
print("Red = Pitch")
print("Blue = Amplitude")


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def clamp(value, minimum, maximum):
    return max(minimum,min(maximum, value))


def scale_value(value,in_min,in_max,out_min,out_max,):
    return out_min + ((value - in_min)/(in_max - in_min)) * (out_max - out_min)


def exponential_pitch(value):
    """
    Convert red colour intensity
    into musical pitch.
    """

    value = clamp(
        value,
        MIN_COLOUR,
        MAX_COLOUR
    )

    position = (value - MIN_COLOUR) / (MAX_COLOUR - MIN_COLOUR)

    return MIN_FREQ * ((MAX_FREQ / MIN_FREQ)** position)


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
    # READ COLOUR SENSOR
    # ----------------------------------------

    red, green, blue, white = (colour.read_rgb())

    # ----------------------------------------
    # MAP COLOUR TO SYNTH
    # ----------------------------------------

    target_freq = exponential_pitch(red)

    target_amp = scale_value(
        clamp(
            blue,
            MIN_COLOUR,
            MAX_COLOUR,
        ),
        MIN_COLOUR,
        MAX_COLOUR,
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
            "R:",
            int(red),
            "| G:",
            int(green),
            "| B:",
            int(blue),
            "| Freq:",
            int(smooth_freq),
            "Hz",
            "| Amp:",
            round(smooth_amp, 2),
        )

        last_print = time.monotonic()

    time.sleep(0.01)