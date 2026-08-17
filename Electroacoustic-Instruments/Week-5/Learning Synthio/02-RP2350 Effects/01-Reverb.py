# ============================================================
# Tutorial 19 — Reverb Basics
# ============================================================
#
# This tutorial teaches:
#
# - the implementation of Reverb
# - "dry" and "wet" signals
# - How to add reverb to a Synthio synthesizer
# - How room size affects the sound
#
# ============================================================
#
# IMPORTANT
#
# This tutorial requires:
#
# - A controller that uses a RP2350 chip, not RP2040
# - CircuitPython 10+
# - audiofreeverb module
# - A board that includes audiofreeverb support
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
#
# board
#     Access to GPIO pin names
#
# audiobusio
#     I2S digital audio output
#
# synthio
#     Synthesizer engine
#
# audiofreeverb
#     Reverb effect processor
#
# ulab.numpy
#     Used to generate waveforms
#
# time
#     Timing between notes
#
# ------------------------------------------------------------

import board
import audiobusio
import synthio
import audiofreeverb
import ulab.numpy as np
import time


# ------------------------------------------------------------
# AUDIO SETUP
# ------------------------------------------------------------
#
# We will build this signal chain:
#
# Synth > Reverb > DAC
#
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,
    word_select=board.GP28,
    data=board.GP26,
)


# ------------------------------------------------------------
# CREATE THE SYNTHESIZER
# ------------------------------------------------------------

SAMPLE_RATE = 22050

synth = synthio.Synthesizer(
    sample_rate=SAMPLE_RATE,
    channel_count=1,
)


# ------------------------------------------------------------
# CREATE THE REVERB EFFECT
# ------------------------------------------------------------
#
# roomsize
#     Size of the virtual room.
#
#     0.0 = very small room
#     1.0 = huge hall
#
#
# damp
#     Amount of high frequency absorption.
#
#     Lower values:
#         brighter reflections
#
#     Higher values:
#         darker reflections
#
#
# mix
#     Dry / wet balance.
#
#     0.0 = original sound only
#     1.0 = reverb only
#
# ------------------------------------------------------------

reverb = audiofreeverb.Freeverb(
    roomsize=0.7,
    damp=0.3,
    mix=0.5,

    buffer_size=1024,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------
#
# Instead of:
#
# audio → synth
#
# we use:
#
# audio → reverb → synth
#
# ------------------------------------------------------------

reverb.play(synth)

audio.play(reverb)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# We use a sawtooth wave because Reverb is easier 
# to hear when the sound contains harmonics.
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000

wave_saw = np.array(
    np.linspace(
        -AMPLITUDE,
        AMPLITUDE,
        SAMPLE_SIZE,
        endpoint=False,
    ),
    dtype=np.int16,
)


# ------------------------------------------------------------
# CREATE AN ADSR ENVELOPE
# ------------------------------------------------------------
#
# A slightly longer release helps us hear
# the reverb tail.
#
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.20,
    sustain_level=0.60,
    release_time=0.50,
)


# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    amplitude=0.15,
)


# ------------------------------------------------------------
# DEFINE A PATTERN OF NOTES
# ------------------------------------------------------------
#
# A simple ascending scale.
#
# ------------------------------------------------------------

pattern = [
    220,   # A3
    247,   # B3
    262,   # C4
    294,   # D4
    330,   # E4
    349,   # F4
    392,   # G4
    440,   # A4
]


# ------------------------------------------------------------
# NOTE TIMING
# ------------------------------------------------------------

NOTE_TIME = 0.5


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

while True:

    for freq in pattern:

        note.frequency = freq
        synth.press(note)
        print(f"Playing {freq} Hz")
        time.sleep(NOTE_TIME)
        synth.release(note)

        #
        # Allow time to hear
        # the reverb tail.
        #

        time.sleep(0.30)