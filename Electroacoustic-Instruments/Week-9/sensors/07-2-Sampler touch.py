# ============================================================
# Tutorial — Sampler Synth with MPR121 Touch Sensor
# ============================================================
#
# What this script demonstrates:
#
# 1. How to load WAV files from storage
# 2. How to trigger samples using capacitive touch pads
# 3. How an audio mixer works
# 4. How multiple samples can play simultaneously
#
#
# Folder Structure:
#
# CIRCUITPY/
# │
# ├── code.py
# └── sounds/
#       ├── sample-1.wav
#       ├── sample-2.wav
#       ├── sample-3.wav
#       └── sample-4.wav
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
#
# board
#     Access to Pico pin names.
#
# busio
#     Provides I2C communication.
#
# audiobusio
#     Sends digital audio to an I2S DAC.
#
# audiomixer
#     Mixes multiple sounds together.
#
# audiocore
#     Provides WAV file playback.
#
# adafruit_mpr121
#     Capacitive touch sensor library.
#
# os
#     Allows access to files and folders.
#
# time
#     Used for timing.
#
# ------------------------------------------------------------

import board
import busio
import audiobusio
import audiomixer
import audiocore
import adafruit_mpr121
import os
import time


# ------------------------------------------------------------
# AUDIO SETUP (I2S)
# ------------------------------------------------------------
#
# I2S sends digital audio to an external DAC.
#
# Using GP16–GP18 leaves ADC pins free
# for future sensors and potentiometers.
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
#
# A mixer combines multiple sounds together.
# The MPR121 provides 12 touch pads,
# so we create 12 mixer voices.
# Each voice can play one sample.
#
# ------------------------------------------------------------

VOICE_COUNT = 12

mixer = audiomixer.Mixer(
    voice_count=VOICE_COUNT,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)

audio.play(mixer)


# ------------------------------------------------------------
# MIXER LEVELS
# ------------------------------------------------------------
#
# If several samples play together,
# their volume adds together.
# Reducing individual voice levels helps
# avoid clipping and distortion.
#
# ------------------------------------------------------------

for i in range(VOICE_COUNT):

    mixer.voice[i].level = 0.5


# ------------------------------------------------------------
# LOAD SAMPLES
# ------------------------------------------------------------
#
# Scan the /sounds folder.
# Any file ending in .wav is loaded.
# Files are sorted alphabetically so that
# sample assignments remain predictable.
#
# ------------------------------------------------------------

SOUND_FOLDER = "/sounds"

sample_files = sorted(
    f for f in os.listdir(SOUND_FOLDER)
    if f.lower().endswith(".wav")
)


# ------------------------------------------------------------
# SAMPLE STORAGE
# ------------------------------------------------------------
#
# samples
#     Stores WaveFile objects.
#
# sample_handles
#     Stores open file handles.
#
# Why keep files open?
#
# WaveFile objects may need access to the
# original file during playback.
#
# ------------------------------------------------------------

samples = []
sample_handles = []


# ------------------------------------------------------------
# LOAD EACH SAMPLE
# ------------------------------------------------------------
#
# Up to 12 samples can be loaded because
# the MPR121 has 12 touch pads.
#
# ------------------------------------------------------------

for filename in sample_files[:VOICE_COUNT]:

    path = SOUND_FOLDER + "/" + filename

    try:

        file_handle = open(path, "rb")
        wav = audiocore.WaveFile(file_handle)
        sample_handles.append(file_handle)
        samples.append(wav)

        print(
            "Loaded sample:",
            filename
        )

    except Exception as error:

        print(
            "Error loading:",
            filename
        )

        print(error)


# ------------------------------------------------------------
# DISPLAY SAMPLE ASSIGNMENTS
# ------------------------------------------------------------

print()

print(
    "Total samples loaded:",
    len(samples)
)

print()

print("Pad Assignments")

for i, filename in enumerate(sample_files[:VOICE_COUNT]):

    print(
        "Pad",
        i,
        "->",
        filename
    )

print()


# ------------------------------------------------------------
# MPR121 SETUP
# ------------------------------------------------------------
#
# MPR121 provides 12 capacitive touch pads.
#
# Touch Pad 0 → Sample 0
# Touch Pad 1 → Sample 1
# Touch Pad 2 → Sample 2
#
# etc...
#
# ------------------------------------------------------------

i2c = busio.I2C(
    scl=board.GP9,
    sda=board.GP8,
)

mpr121 = adafruit_mpr121.MPR121(i2c)

print("MPR121 Ready")
print("Touch a pad to trigger a sample")
print()


# ------------------------------------------------------------
# TOUCH STATE MEMORY
# ------------------------------------------------------------
#
# Stores previous touch states.
# This allows us to detect a NEW touch:
#
# Not Touched → Touched
#
# which is called a rising edge.
# Without this, a sample would continuously
# retrigger while a finger remained on a pad.
#
# ------------------------------------------------------------

previous_states = [False] * 12


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Continuously scans all 12 touch pads.
#
# When a new touch is detected:
#
# Pad 0 → Voice 0 → Sample 0
# Pad 1 → Voice 1 → Sample 1
# Pad 2 → Voice 2 → Sample 2
#
# etc.
#
# Different samples can play together.
#
# ------------------------------------------------------------

while True:

    for pad in range(12):

        current_state = mpr121[pad].value

        # ------------------------------------
        # NEW TOUCH DETECTED
        # ------------------------------------
        #
        # Trigger only when a touch begins.
        #
        # ------------------------------------

        if current_state and not previous_statesif pad < len(samples):

                print(
                    "Playing:",
                    sample_files[pad]
                )

                mixer.voice[pad].play(
                    samples[pad],
                    loop=False,
                )

            else:

                print("Pad", pad, "has no sample assigned.")

        # Remember state for next scan
        previous_states[pad] = current_state

    time.sleep(0.01)