# ============================================================
# Tutorial 22 — Chorus
# ============================================================
#
# This tutorial teaches:
#
# - What a chorus effect is
# - How chorus creates a thicker sound
# - How delayed copies of a sound create richness
# - How a chorus differs from an echo
# - How to add chorus to a Synthio synthesizer
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
#     Audio effect processors
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
# Synth
#   ↓
# Chorus
#   ↓
# DAC
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
# CREATE THE CHORUS EFFECT
# ------------------------------------------------------------
#
# A chorus works by creating several delayed
# copies of the original sound.
#
# These copies are continuously shifted slightly
# forward and backward in time.
#
# The result sounds like:
#
# One instrument
#      ↓
# Several instruments playing together
#
#
# voices
#     Number of chorus voices.
#
# mix
#     Dry / wet balance.
#
# max_delay_ms
#     Maximum delay available to the chorus.
#
# ------------------------------------------------------------

chorus = audiodelays.Chorus(
    mix=0.6,

    voices=3,

    max_delay_ms=100,

    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------

chorus.play(synth)

audio.play(chorus)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A sawtooth waveform makes the chorus
# effect easier to hear.
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
    attack_time=0.05,
    decay_time=0.20,
    sustain_level=0.60,
    release_time=0.30,
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

NOTE_TIME = 0.5


# ------------------------------------------------------------
# STARTUP MESSAGE
# ------------------------------------------------------------

print()
print("Tutorial 22 - Chorus")
print("--------------------")
print("Voices     :", chorus.voices)
print("Mix        :", chorus.mix)
print()
print("Listen for a thicker, wider sound.")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen for:
#
# - A wider sound
# - More apparent depth
# - A richer texture
#
# The chorus does NOT create obvious echoes.
#
# Instead it creates multiple subtle copies
# that blend together.
#
#
# EXPERIMENTS
#
# Try changing:
#
# voices=2
# voices=4
# voices=6
#
# How many "virtual instruments"
# can you hear?
#
#
# Try changing:
#
# mix=0.2
#
# Mostly original sound
#
#
# Try changing:
#
# mix=0.8
#
# Strong chorus effect
#
#
# Compare:
#
# Chorus
# vs
# Echo
#
# Notice how chorus thickens the sound
# while echo creates distinct repeats.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        note.frequency = freq

        synth.press(note)

        print(
            f"Playing {freq} Hz with chorus"
        )

        time.sleep(NOTE_TIME)

        synth.release(note)

        time.sleep(0.05)