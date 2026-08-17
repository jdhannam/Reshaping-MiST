# ============================================================
# Tutorial 11 — Sample & Hold (Random Pitch)
# ============================================================
#
# This tutorial teaches:
#
# - What Sample & Hold means
# - How to generate random values
# - How to hold a value for a period of time
# - How random modulation changes pitch
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

synth = synthio.Synthesizer(
    sample_rate=22050
)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE A SAWTOOTH WAVEFORM
# ------------------------------------------------------------
#
# A sawtooth wave makes pitch changes easier to hear.
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
    decay_time=0.2,
    sustain_level=0.7,
    release_time=0.3,
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
# SAMPLE & HOLD SETTINGS
# ------------------------------------------------------------
#
# MIN_FREQ
#     Lowest possible pitch
#
# MAX_FREQ
#     Highest possible pitch
#
# HOLD_TIME
#     How long each random value is held
#
# ------------------------------------------------------------

MIN_FREQ = 150
MAX_FREQ = 800

HOLD_TIME = 0.25


# ------------------------------------------------------------
# START THE NOTE
# ------------------------------------------------------------
#
# The note stays pressed continuously.
#
# We only change its frequency.
#
# ------------------------------------------------------------

synth.press(note)


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Sample:
#     Pick a random frequency
#
# Hold:
#     Keep it for a short time
#
# Repeat forever.
#
# Listen for:
#
# Random stepped pitch changes.
#
# Experiment:
#
# HOLD_TIME = 0.05
# HOLD_TIME = 0.50
# HOLD_TIME = 1.00
#
# ------------------------------------------------------------

while True:

    random_frequency = random.uniform(
        MIN_FREQ,
        MAX_FREQ
    )

    note.frequency = random_frequency

    print(
        f"Sampled: {random_frequency:.1f} Hz"
    )

    time.sleep(HOLD_TIME)