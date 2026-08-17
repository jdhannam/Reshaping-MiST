# ============================================================
# Tutorial 29 — Probability Music Synth
# ============================================================
#
# This tutorial teaches:
#
# - What probability-based music is
# - How randomness can generate melodies
# - How weighted probabilities work
# - How some notes can occur more often than others
# - How generative music systems are built
#
# ============================================================
#
# WHAT IS PROBABILITY MUSIC?
#
# Instead of writing a fixed melody,
# we allow the synthesizer to choose notes.
#
# However, not all notes are equally likely.
#
# Example:
#
# A appears 4 times
# C appears 2 times
# E appears 1 time
#
# Result:
#
# A is heard more often than E.
#
# This creates music that sounds more
# intentional than completely random notes.
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
import random
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
# We use a sawtooth waveform because
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
    attack_time=0.02,
    decay_time=0.15,
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
    amplitude=0.12,
)


# ------------------------------------------------------------
# PROBABILITY SCALE
# ------------------------------------------------------------
#
# Notes can appear multiple times.
#
# More appearances =
# Higher probability.
#
# ------------------------------------------------------------
#
# A appears 4 times
# C appears 3 times
# E appears 2 times
# G appears 1 time
#
# This creates a strong "A minor" feeling.
#
# ------------------------------------------------------------

probability_scale = [

    220, 220, 220, 220,   # A

    262, 262, 262,        # C

    330, 330,             # E

    392,                  # G
]


# ------------------------------------------------------------
# RHYTHM OPTIONS
# ------------------------------------------------------------
#
# The synthesizer will also choose
# random note lengths.
#
# ------------------------------------------------------------

durations = [
    0.15,
    0.25,
    0.50,
]


# ------------------------------------------------------------
# STARTUP MESSAGE
# ------------------------------------------------------------

print()
print("Tutorial 29 - Probability Music Synth")
print("-------------------------------------")
print()
print("The synthesizer will create")
print("an endless melody.")
print()
print("Some notes occur more often")
print("because of weighted probability.")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# For each note:
#
# 1. Choose a random note
# 2. Choose a random duration
# 3. Play the note
#
# Because some notes appear more often
# in the probability list, they will be
# selected more frequently.
#
#
# EXPERIMENTS
#
# Add more copies of:
#
# 220
#
# and notice that A becomes more common.
#
#
# Add:
#
# 494
#
# and hear how the harmony changes.
#
#
# Remove duplicate notes to create
# a completely random scale.
#
#
# ADVANCED CHALLENGE
#
# Create a major scale:
#
# C D E F G A B
#
# and assign different probabilities
# to each note.
#
# ------------------------------------------------------------

while True:

    # Select note using weighted probability

    frequency = random.choice(
        probability_scale
    )

    # Select note duration

    duration = random.choice(
        durations
    )

    note.frequency = frequency

    synth.press(note)

    print(
        f"Frequency: {frequency} Hz "
        f"Duration: {duration:.2f}s"
    )

    time.sleep(duration)

    synth.release(note)

    time.sleep(0.05)