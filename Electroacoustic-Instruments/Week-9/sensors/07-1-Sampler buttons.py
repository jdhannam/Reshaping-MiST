# ============================================================
# Tutorial — Sampler Synth Template
# ============================================================
#
# What this script demonstrates:
#
# 1. How to load WAV files from storage
# 2. How to trigger samples using buttons
# 3. How to play multiple samples at once
# 4. How an audio mixer combines sounds
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
#     Gives access to Pico pin names.
#
# audiobusio
#     Sends digital audio to an I2S DAC.
#
# audiomixer
#     Allows multiple sounds to play together.
#
# audiocore
#     Provides WAV file playback support.
#
# digitalio
#     Reads push-button inputs.
#
# os
#     Lets us scan folders and files.
#
# time
#     Used for timing.
#
# ------------------------------------------------------------

import board
import audiobusio
import audiomixer
import audiocore
import digitalio
import os
import time


# ------------------------------------------------------------
# AUDIO SETUP (I2S)
# ------------------------------------------------------------
#
# I2S sends digital audio data to an external DAC.
#
# These pins can be changed if your hardware
# requires different connections.
#
# Using GP16–GP18 leaves the ADC pins free
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
#
# voice_count
#     Number of sounds that can play
#     simultaneously.
#
# For example:
#
# Voice 0 → Kick
# Voice 1 → Snare
# Voice 2 → Clap
# Voice 3 → Hi-Hat
#
# All four sounds can play together.
#
# ------------------------------------------------------------

VOICE_COUNT = 4

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
# When multiple samples play at the same time,
# their volumes add together.
#
# Lowering each voice level helps prevent
# distortion and clipping.
#
# ------------------------------------------------------------

for i in range(VOICE_COUNT):

    mixer.voice[i].level = 0.5


# ------------------------------------------------------------
# LOAD SAMPLES
# ------------------------------------------------------------
#
# This section scans the /sounds folder.
#
# Any file ending in .wav will be loaded.
#
# Files are sorted alphabetically so that
# button assignments remain predictable.
#
# Example:
#
# Button 0 → sample-1.wav
# Button 1 → sample-2.wav
# Button 2 → sample-3.wav
# Button 3 → sample-4.wav
#
# ------------------------------------------------------------

SOUND_FOLDER = "/sounds"

sample_files = sorted(
    f for f in os.listdir(SOUND_FOLDER)
    if f.lower().endswith(".wav")
)

samples = []

# Store open file handles.
#
# WaveFile objects need the file to remain open
# while the sample is being played.

sample_handles = []


# ------------------------------------------------------------
# LOAD EACH WAV FILE
# ------------------------------------------------------------

for filename in sample_files:

    path = SOUND_FOLDER + "/" + filename

    try:

        # Open the WAV file
        file_handle = open(path, "rb")

        # Create a WaveFile object
        wav = audiocore.WaveFile(file_handle)

        # Store both
        sample_handles.append(file_handle)
        samples.append(wav)
        print("Loaded sample:", filename)

    except Exception as error:

        print("Error loading:", filename)
        print(error)


# ------------------------------------------------------------
# DISPLAY LOADED FILES
# ------------------------------------------------------------

print()

if len(samples) == 0:
    print("No WAV files found!")

else:
    print("Total samples loaded:", len(samples))
    print()
    print("Button Assignments")

    for i, filename in enumerate(
        sample_files[:VOICE_COUNT]
    ):

        print(
            "Button",
            i,
            "->",
            filename
        )

print()


# ------------------------------------------------------------
# BUTTON SETUP
# ------------------------------------------------------------
#
# Four push-buttons are connected:
#
# GP2
# GP3
# GP4
# GP5
#
# Each button triggers one sample.
#
# ------------------------------------------------------------

button_pins = [
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
]

buttons = []

for pin in button_pins:

    button = digitalio.DigitalInOut(pin)
    button.switch_to_input(pull=digitalio.Pull.DOWN)
    buttons.append(button)


# ------------------------------------------------------------
# BUTTON STATE MEMORY
# ------------------------------------------------------------
#
# We store the previous state of each button.
#
# This allows us to detect:
#
# NOT PRESSED → PRESSED
#
# which is called a rising edge.
#
# This prevents samples from being repeatedly
# retriggered while a button is held down.
#
# ------------------------------------------------------------

previous_states = [False] * len(buttons)


print("Sampler Ready")
print("Press a button to trigger a sample")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Continuously checks button states.
# When a new button press is detected:
#
# 1. Find the assigned sample
# 2. Play it on the matching mixer voice
#
# Example:
# Button 0 → Voice 0 → Sample 0
#
# ------------------------------------------------------------

while True:

    for i, button in enumerate(buttons):

        current_state = button.value

        # ------------------------------------
        # NEW BUTTON PRESS DETECTED
        # ------------------------------------
        #
        # Trigger only once when the button
        # first becomes pressed.
        #
        # ------------------------------------

        if current_state and not previous_statesif i < len(samples):

                print(
                    "Playing:",
                    sample_files[i]
                )

                mixer.voice[i].play(
                    samples[i],
                    loop=False,
                )

            else:

                print(
                    "No sample assigned to button",
                    i
                )

        # Remember state for next loop
        previous_states[i] = current_state
    time.sleep(0.01)