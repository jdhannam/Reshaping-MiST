# ============================================================
# Tutorial — VCO Control with PiicoDev VL53L1X
# ============================================================
#
# What this script demonstrates:
#
# 1. Reading distance measurements
# 2. Mapping distance into synthesizer controls
# 3. Controlling oscillator pitch and amplitude
# 4. Smoothing sensor values
#
#
# Distance = Pitch
# Distance = Volume
#
# Move your hand towards and away from the sensor
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

import adafruit_vl53l1x


# ------------------------------------------------------------
# AUDIO SETUP (I2S)
# ------------------------------------------------------------
#
# GP17 = BCLK
# GP18 = LRCLK / WS
# GP16 = DATA
#
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
# CREATE DISTANCE SENSOR
# ------------------------------------------------------------
#
# PiicoDev VL53L1X
#
# Measures distance in millimetres.
#
# ------------------------------------------------------------

i2c = busio.I2C(board.GP9, board.GP8)
distance_sensor = adafruit_vl53l1x.VL53L1X(i2c)
distance_sensor.start_ranging()

# ------------------------------------------------------------
# CREATE SINE WAVE WAVETABLE
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
# DISTANCE RANGE
# ------------------------------------------------------------
#
# Classroom-friendly range.
#
# Values outside this range
# will be clamped.
#
# ------------------------------------------------------------

MIN_DISTANCE = 50      # mm
MAX_DISTANCE = 500     # mm


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
print("Move your hand above the sensor.")


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def clamp(value, minimum, maximum):
    return max(minimum,min(maximum, value))


def scale_value(value,in_min,in_max,out_min,out_max,):
    return out_min + ((value - in_min)/(in_max - in_min)) * (out_max - out_min)


def exponential_pitch(distance):
    """
    Convert distance into pitch.

    Human hearing perceives pitch
    approximately logarithmically.
    """

    distance = clamp(
        distance,
        MIN_DISTANCE,
        MAX_DISTANCE
    )

    position = (distance - MIN_DISTANCE) / (MAX_DISTANCE - MIN_DISTANCE)

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
    # READ DISTANCE
    # ----------------------------------------

    distance = distance_sensor.distance()

    # ----------------------------------------
    # CLAMP RANGE
    # ----------------------------------------

    distance = clamp(
        distance,
        MIN_DISTANCE,
        MAX_DISTANCE
    )

    # ----------------------------------------
    # MAP TO SYNTH VALUES
    # ----------------------------------------

    target_freq = exponential_pitch(
        distance
    )

    target_amp = scale_value(
        distance,
        MIN_DISTANCE,
        MAX_DISTANCE,
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
            "Distance:",
            int(distance),
            "mm",
            "| Freq:",
            int(smooth_freq),
            "Hz",
            "| Amp:",
            round(smooth_amp, 2),
        )

        last_print = time.monotonic()

    time.sleep(0.01)