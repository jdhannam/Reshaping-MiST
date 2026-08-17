# ============================================================
# Tutorial 28 — Theremin (Distance Controls Pitch)
# ============================================================
#
# This tutorial teaches:
#
# - How to read distance from a VL53L1X sensor
# - How to convert distance into pitch
# - How a Theremin works
# - How to control a synthesizer using hand movement
# - How sensor data can become music
#
# ============================================================
#
# WHAT IS A THEREMIN?
#
# A Theremin is one of the world's earliest
# electronic musical instruments.
#
# Traditional Theremins use antennas.
#
# In this tutorial we use a distance sensor.
#
# Hand close
#      ↓
# Higher pitch
#
# Hand far away
#      ↓
# Lower pitch
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
import adafruit_vl53l1x
import ulab.numpy as np
import time


# ------------------------------------------------------------
# AUDIO SETUP
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,
    word_select=board.GP28,
    data=board.GP26,
)

mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)

audio.play(mixer)


# ------------------------------------------------------------
# CREATE THE SYNTHESIZER
# ------------------------------------------------------------

synth = synthio.Synthesizer(
    sample_rate=22050
)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A sine wave provides a classic
# theremin-like sound.
#
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
# CREATE A NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    amplitude=0.12,
)


# ------------------------------------------------------------
# START THE NOTE
# ------------------------------------------------------------
#
# The note remains active continuously.
#
# Only the frequency changes.
#
# ------------------------------------------------------------

synth.press(note)


# ------------------------------------------------------------
# VL53L1X SETUP
# ------------------------------------------------------------
#
# GP9 = SCL
# GP8 = SDA
#
# Change if your wiring differs.
#
# ------------------------------------------------------------

i2c = busio.I2C(
    board.GP9,
    board.GP8,
)

tof = adafruit_vl53l1x.VL53L1X(i2c)

tof.start_ranging()


# ------------------------------------------------------------
# DISTANCE RANGE
# ------------------------------------------------------------
#
# These values define the active
# playing area of the theremin.
#
# ------------------------------------------------------------

MIN_DISTANCE = 5
MAX_DISTANCE = 150


# ------------------------------------------------------------
# FREQUENCY RANGE
# ------------------------------------------------------------
#
# Lowest and highest playable notes.
#
# ------------------------------------------------------------

MIN_FREQUENCY = 80
MAX_FREQUENCY = 1000


# ------------------------------------------------------------
# DISTANCE FILTERING
# ------------------------------------------------------------
#
# Sensors are never perfectly stable.
#
# We smooth readings to reduce
# pitch jitter.
#
# ------------------------------------------------------------

DISTANCE_ALPHA = 0.20

filtered_distance = 50.0


# ------------------------------------------------------------
# LAST VALID FREQUENCY
# ------------------------------------------------------------
#
# Used if the sensor temporarily
# loses the target.
#
# ------------------------------------------------------------

current_frequency = 220.0


# ------------------------------------------------------------
# DISTANCE TO FREQUENCY
# ------------------------------------------------------------
#
# Convert:
#
# Distance
#     →
# Frequency
#
# Close hand
#     →
# High note
#
# Far hand
#     →
# Low note
#
# ------------------------------------------------------------

def distance_to_frequency(cm):

    cm = max(
        MIN_DISTANCE,
        min(cm, MAX_DISTANCE)
    )

    position = (
        (cm - MIN_DISTANCE)
        /
        (MAX_DISTANCE - MIN_DISTANCE)
    )

    return MAX_FREQUENCY * (
        (MIN_FREQUENCY / MAX_FREQUENCY)
        ** position
    )


# ------------------------------------------------------------
# STARTUP MESSAGE
# ------------------------------------------------------------

print()
print("Tutorial 28 - Theremin")
print("----------------------")
print()
print("Move your hand")
print("toward and away")
print("from the sensor.")
print()
print("Closer  = Higher pitch")
print("Farther = Lower pitch")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# 1. Read distance
# 2. Smooth measurement
# 3. Convert to frequency
# 4. Update synthesizer pitch
#
#
# EXPERIMENTS
#
# Change:
#
# MAX_FREQUENCY
#
# 800
# 1200
# 2000
#
#
# Change:
#
# MIN_FREQUENCY
#
# 40
# 80
# 120
#
#
# Change:
#
# DISTANCE_ALPHA
#
# 0.05
# 0.20
# 0.50
#
# Larger values:
#
# Faster response
#
# Smaller values:
#
# Smoother movement
#
# ------------------------------------------------------------

while True:

    if tof.data_ready:

        distance = tof.distance

        tof.clear_interrupt()

        if distance is not None:

            filtered_distance += (
                distance - filtered_distance
            ) * DISTANCE_ALPHA

            current_frequency = (
                distance_to_frequency(
                    filtered_distance
                )
            )

            note.frequency = current_frequency

            print(
                f"Distance: {filtered_distance:.1f} cm  "
                f"Frequency: {current_frequency:.1f} Hz"
            )

    time.sleep(0.01)