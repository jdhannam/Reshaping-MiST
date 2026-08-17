# ============================================================
# Tutorial 21 — Delay / Echo
# ============================================================
#
# This tutorial teaches:
#
# - What delay (echo) is
# - How echoes are created
# - How delay time affects the sound
# - How repeat level affects the sound
# - How to add an echo effect to a Synthio synthesizer
#
# ============================================================
#
# IMPORTANT
#
# This tutorial requires:
#
# - A controller that uses a RP2350 chip, not RP2040
# - CircuitPython 10+
# - audiodelays module
# - A board that includes audiodelays support
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
# audiodelays
#     Echo, Chorus and Pitch Shift effects
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
import audiodelays
import ulab.numpy as np
import time


# ------------------------------------------------------------
# AUDIO SETUP
# ------------------------------------------------------------
#
# Signal Chain
#
# Synth > Echo > DAC
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
# CREATE THE ECHO EFFECT
# ------------------------------------------------------------
#
# delay_ms
#     Time before the echo repeats.
#
# decay
#     How loud each repeat becomes.
#
# mix
#     Dry / wet balance.
#
# ------------------------------------------------------------
#
# Example:
#
# Original note
#      ↓
# 250 ms later
#      ↓
# First echo
#      ↓
# Second echo (quieter)
#      ↓
# Third echo (quieter still)
#
# ------------------------------------------------------------

echo = audiodelays.Echo(
    mix=0.5,
    delay_ms=250,
    decay=0.6,
    max_delay_ms=500,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------

echo.play(synth)

audio.play(echo)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A sawtooth wave makes the echoes easier to hear.
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

envelope = synthio.Envelope(
    attack_time=0.02,
    decay_time=0.10,
    sustain_level=0.70,
    release_time=0.20,
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
# DEFINE A PATTERN OF TONES
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

NOTE_TIME = 0.25


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen for:
#
# - The original note
# - The first repeat
# - The second repeat
# - The third repeat
#
#
# EXPERIMENTS
#
# Change:
#
# delay_ms=100
#
# Short slapback echo
#
#
# Change:
#
# delay_ms=250
#
# Medium echo
#
#
# Change:
#
# delay_ms=500
#
# Long echo
#
#
# Change:
#
# decay=0.3
#
# Echo fades quickly
#
#
# Change:
#
# decay=0.8
#
# Echo lasts much longer
#
#
# Change:
#
# mix=0.2
#
# Mostly original sound
#
#
# Change:
#
# mix=0.8
#
# Mostly echoes
#
# ------------------------------------------------------------

while True:

    for freq in pattern:
        note.frequency = freq
        synth.press(note)

        print(
            f"Playing {freq} Hz"
        )

        time.sleep(NOTE_TIME)
        synth.release(note)

        # Give the echoes time
        # to be heard.

        time.sleep(0.40)