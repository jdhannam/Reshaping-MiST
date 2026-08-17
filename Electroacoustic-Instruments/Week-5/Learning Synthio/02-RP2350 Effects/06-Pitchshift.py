# ============================================================
# Tutorial 24 — Pitch Shift
# ============================================================
#
# This tutorial teaches:
#
# - What pitch shifting is
# - How pitch shifting differs from changing note frequency
# - How to transpose audio up and down
# - How semitones relate to musical intervals
# - How to add pitch shifting to a Synthio synthesizer
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
# Pitch Shift
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
# CREATE THE PITCH SHIFT EFFECT
# ------------------------------------------------------------
#
# Pitch shifting changes the pitch of the
# entire audio signal after it leaves
# the synthesizer.
#
# semitones
#     Number of semitones to shift.
#
# Positive values:
#     Shift upward.
#
# Negative values:
#     Shift downward.
#
# mix
#     Dry / wet balance.
#
# ------------------------------------------------------------
#
# Musical Examples
#
# +12 semitones
#     One octave higher
#
# -12 semitones
#     One octave lower
#
# +7 semitones
#     Perfect fifth
#
# ------------------------------------------------------------

pitch_shift = audiodelays.PitchShift(
    semitones=12,

    mix=1.0,

    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------

pitch_shift.play(synth)

audio.play(pitch_shift)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A simple sawtooth wave works well because
# it contains many harmonics.
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
print("Tutorial 24 - Pitch Shift")
print("-------------------------")
print("Semitones :", pitch_shift.semitones)
print("Mix       :", pitch_shift.mix)
print()
print("Listen for the entire synth")
print("being shifted in pitch.")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen for:
#
# - The original melody
# - The shifted pitch
# - How intervals remain the same
#
# Notice:
#
# The synthesizer still plays the same frequencies.
#
# The pitch shift effect changes the audio AFTER
# it leaves the synthesizer.
#
#
# EXPERIMENTS
#
# Try:
#
# semitones = 0
#
# No pitch shifting
#
#
# Try:
#
# semitones = 12
#
# One octave higher
#
#
# Try:
#
# semitones = -12
#
# One octave lower
#
#
# Try:
#
# semitones = 7
#
# Perfect fifth
#
#
# Try:
#
# mix = 0.5
#
# Blend original and shifted audio
#
#
# ADVANCED CHALLENGE
#
# Try using:
#
# semitones=synthio.LFO(
#     rate=0.25,
#     scale=12,
# )
#
# to create a continuously changing
# pitch shift effect.
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

        time.sleep(0.05)