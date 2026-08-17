# ============================================================
# Tutorial 6 — Adding a Second LFO to Modulate Pitch
# ============================================================
#
# This tutorial teaches:
# - How to use TWO LFOs at the same time
# - LFO #1 modulates FILTER cutoff (wah‑wah effect)
# - LFO #2 modulates PITCH (vibrato effect)
# - How multiple modulation sources interact
# - How to combine ADSR + Filter + LFOs + Pattern
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
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# We use a sawtooth wave because it contains many harmonics.
#
# Filters are much easier to hear when a waveform contains
# lots of harmonic content.
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256

wave_saw = np.linspace(
    -32000,
    32000,
    SAMPLE_SIZE,
    dtype=np.int16,
)


# ------------------------------------------------------------
# CREATE AN ADSR ENVELOPE
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.2,
    sustain_level=0.6,
    release_time=0.3,
)


# ------------------------------------------------------------
# LFO #1 — FILTER MODULATION
# ------------------------------------------------------------
#
# This LFO automatically moves the filter cutoff.
#
# rate
#     Speed of sweep
#
# scale
#     Sweep amount
#
# offset
#     Centre position
#
# ------------------------------------------------------------

lfo_filter = synthio.LFO(
    rate=2.0,
    scale=600,
    offset=1200,
)


# ------------------------------------------------------------
# FILTER SECTION
# ------------------------------------------------------------
#
# The filter frequency is controlled by LFO #1.
# The cutoff will continuously sweep between
# approximately 600 Hz and 1800 Hz.
#
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=lfo_filter,
    Q=1.2,
)


# ------------------------------------------------------------
# LFO #2 — VIBRATO (PITCH MODULATION)
# ------------------------------------------------------------
#
# Vibrato is a small up‑and‑down change in pitch.
#
# Musicians use vibrato to make notes sound
# more expressive and alive.
#
# Unlike the filter LFO, this LFO affects pitch.
#
# ------------------------------------------------------------

lfo_pitch = synthio.LFO(
    rate=5.0,
    scale=0.02,
    offset=0,
)


# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------
#
# bend adds pitch modulation.
# The pitch LFO creates a gentle vibrato effect
# while the filter LFO creates the wah‑wah effect.
#
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    bend=lfo_pitch,
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

NOTE_TIME = 0.5


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen for TWO effects happening simultaneously:
#
# 1. Filter sweep (wah‑wah)
#      caused by LFO #1
#
# 2. Vibrato (pitch wobble)
#      caused by LFO #2
#
# Try changing:
#
# lfo_filter rate
#
# from:
#     2.0
#
# to:
#     0.5
#     1.0
#     4.0
#
#
# Try changing:
#
# lfo_pitch rate
#
# from:
#     5.0
#
# to:
#     3.0
#     8.0
#
#
# Try changing:
#
# lfo_pitch scale
#
# from:
#     0.02
#
# to:
#     0.01
#     0.05
#     0.10
#
# and listen carefully to the difference.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:
        note.frequency = freq
        synth.press(note)

        print(
            f"Playing {freq} Hz "
            f"with Filter LFO and Pitch LFO"
        )

        time.sleep(NOTE_TIME)
        synth.release(note)
        time.sleep(0.05)

