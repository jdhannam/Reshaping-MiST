# ============================================================
# Tutorial 00 — Understanding the Main Loop
# ============================================================
#
# This tutorial teaches:
#
# - What a main loop is
# - Why microcontrollers run forever
# - How Synthio projects are structured
# - The "Input → Process → Output" pattern
#
# ============================================================
#
# Almost every project will use:
#
# while True:
#     ...
#
# This is called the MAIN LOOP.
#
# The main loop runs forever.
#
# It repeatedly:
#
# 1. Reads inputs
# 2. Processes inputs
# 3. Updates outputs
#
# This pattern is used everywhere:
#
# - Synthesizers
# - Robots
# - Game controllers
# - Industrial machines
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import audiobusio
import audiomixer
import synthio
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
# CREATE A SIMPLE SINE WAVE
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
# The oscillator will continue running.
# We will modify it inside the main loop.
#
# ------------------------------------------------------------

synth.press(note)


# ------------------------------------------------------------
# DATA FOR THE MAIN LOOP
# ------------------------------------------------------------
#
# Our "input" in this tutorial is simply
# a list of frequencies.
#
# Later tutorials replace this with:
#
# - Sensors
# - Knobs
# - Buttons
#
# ------------------------------------------------------------

pattern = [
    220,
    247,
    262,
    294,
    330,
    349,
    392,
    440,
]

index = 0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Almost ALL embedded systems follow:
#
# INPUT > PROCESS INPUT > EXECUTE
#
# ------------------------------------------------------------

while True:

    # ========================================================
    # STEP 1 - INPUT
    # ========================================================
    #
    # Read information from the world.
    #
    # In this tutorial:
    #
    # We read the next frequency
    # from our list.
    #
    # ========================================================

    current_frequency = pattern[index]


    # ========================================================
    # STEP 2 - PROCESS INPUT
    # ========================================================
    #
    # - Read sensors
    # - Process button presses
    # - Calculate new values
    #
    # ========================================================

    target_frequency = current_frequency


    # ========================================================
    # STEP 3 - EXECUTE
    # ========================================================
    #
    # Update hardware.
    #
    # Here we tell the synthesizer
    # to change pitch.
    #
    # ========================================================

    note.frequency = target_frequency


    # ========================================================
    # STATUS MESSAGE
    # ========================================================

    print(f"Frequency = {target_frequency} Hz")


    # ========================================================
    # TIMING
    # ========================================================
    #
    # Without this delay the loop
    # would run thousands of times
    # per second.
    #
    # We slow it down so we can
    # hear each note.
    #
    # ========================================================

    time.sleep(0.5)


    # ========================================================
    # PREPARE FOR NEXT LOOP
    # ========================================================
    #
    # Move to the next note.
    #
    # ========================================================

    index += 1


    # ========================================================
    # LOOP BACK TO START
    # ========================================================
    #
    # If we reach the end of the list,
    # start again from the beginning.
    #
    # ========================================================

    if index >= len(pattern):
        index = 0