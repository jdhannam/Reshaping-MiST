# ============================================================
# Tutorial 25 — Effect Chains
# ============================================================
#
# This tutorial teaches:
#
# - What an effect chain is
# - Why effect order matters
# - How multiple effects can work together
# - How to connect several effects in series
# - How professional synthesizer signal paths work
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
# - audiodelays module
# - audiofilters module
# - A board that includes these modules
#
# ============================================================
#
# SIGNAL CHAIN
#
# Synth > Distortion > Chorus > Reverb > out
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import audiobusio
import synthio
import audiofilters
import audiodelays
import audiofreeverb
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


# ------------------------------------------------------------
# CREATE THE SYNTHESIZER
# ------------------------------------------------------------

SAMPLE_RATE = 22050

synth = synthio.Synthesizer(
    sample_rate=SAMPLE_RATE,
    channel_count=1,
)


# ------------------------------------------------------------
# CREATE EFFECT #1 - DISTORTION
# ------------------------------------------------------------
#
# Distortion adds harmonics
#
# ------------------------------------------------------------

distortion = audiofilters.Distortion(
    mode=audiofilters.DistortionMode.OVERDRIVE,

    pre_gain=15,
    post_gain=-8,
    soft_clip=True,
    mix=1.0,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CREATE EFFECT #2 - CHORUS
# ------------------------------------------------------------
#
# Chorus creates additional delayed copies.
#
# ------------------------------------------------------------

chorus = audiodelays.Chorus(
    mix=0.5,
    voices=3,
    max_delay_ms=100,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CREATE EFFECT #3 - REVERB
# ------------------------------------------------------------
#
# Reverb creates room reflections.
#
# ------------------------------------------------------------

reverb = audiofreeverb.Freeverb(
    roomsize=0.8,
    damp=0.3,
    mix=0.4,
    buffer_size=1024,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE EFFECT CHAIN
# ------------------------------------------------------------
#
# Here we connect the output of each effect
# into the next effect.
#
# Synth > Distortion > Chorus > Reverb > out
#
# ------------------------------------------------------------

distortion.play(synth)
chorus.play(distortion)
reverb.play(chorus)
audio.play(reverb)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A sawtooth waveform contains many harmonics.
#
# This makes all three effects easier to hear.
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
    release_time=0.50,
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
# MAIN LOOP
# ------------------------------------------------------------

while True:

    for freq in pattern:
        note.frequency = freq
        synth.press(note)

        print(
            f"Playing {freq} Hz through "
            f"Distortion → Chorus → Reverb"
        )

        time.sleep(NOTE_TIME)
        synth.release(note)

        # Allow the reverb tail
        # to be heard.

        time.sleep(0.30)

        