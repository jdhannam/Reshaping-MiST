# ============================================================
# Tutorial 7 — Glissandi (Smooth Pitch Slides) with ADSR
# ============================================================
#
# This tutorial teaches:
#
# - How to play a pattern of tones
# - How to use ADSR envelopes
# - How to create a glissando (smooth pitch slide)
# - How to interpolate between frequencies
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

synth = synthio.Synthesizer(sample_rate=22050)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE A SINE WAVE
# ------------------------------------------------------------
#
# A sine wave is ideal for demonstrating pitch.
#
# It has a pure, clean tone with very few distractions,
# making the glissando easy to hear.
#
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
# CREATE AN ADSR ENVELOPE
# ------------------------------------------------------------
#
# ADSR =
#
# Attack
# Decay
# Sustain
# Release
#
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.2,
    sustain_level=0.6,
    release_time=0.3,
)


# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    envelope=envelope,
    amplitude=0.15,
)


# ------------------------------------------------------------
# DEFINE A SCALE
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
# GLISSANDO SETTINGS
# ------------------------------------------------------------
#
# More steps:
#     smoother slide
#
# Fewer steps:
#     more noticeable stepping
#
# ------------------------------------------------------------

NOTE_TIME = 0.5

GLISS_STEPS = 50

GLISS_DELAY = 0.005


# ------------------------------------------------------------
# GLISSANDO FUNCTION
# ------------------------------------------------------------
#
# Interpolation means calculating values between
# two points.
#
# Example:
#
# Start = 220 Hz
# End   = 440 Hz
#
# We calculate many small frequencies between them.
#
# The more intermediate frequencies we generate,
# the smoother the slide sounds.
#
# ------------------------------------------------------------

def glissando(start_freq, end_freq):

    for step in range(GLISS_STEPS + 1):

        position = step / GLISS_STEPS

        current_freq = (
            start_freq +
            (end_freq - start_freq) * position
        )

        note.frequency = current_freq

        time.sleep(GLISS_DELAY)


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# We keep the note pressed while sliding.
#
# This creates one continuous sound moving from
# pitch to pitch.
#
# Listen for:
#
# A smooth movement between notes rather than
# individual jumps.
#
# Experiment:
#
# GLISS_STEPS = 10
# GLISS_STEPS = 25
# GLISS_STEPS = 100
#
# and compare the smoothness.
#
# ------------------------------------------------------------

while True:

    # Start at first note in pattern
    note.frequency = pattern[0]

    # Trigger ADSR envelope once
    synth.press(note)

    for i in range(len(pattern) - 1):

        start_freq = pattern[i]
        end_freq = pattern[i + 1]

        print(
            f"Glissando: "
            f"{start_freq} Hz → {end_freq} Hz"
        )

        glissando(
            start_freq,
            end_freq,
        )

        time.sleep(NOTE_TIME)

    # Release ADSR envelope
    synth.release(note)

    # Allow release stage to be heard
    time.sleep(0.5)