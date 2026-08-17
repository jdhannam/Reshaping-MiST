# ============================================================
# Tutorial 5 — LFO Modulating Filter Cutoff
# ============================================================
#
# What this script demonstrates:
# - What an LFO is (Low Frequency Oscillator)
# - How to create an LFO
# - How to attach an LFO to a filter
# - How to make the filter cutoff move automatically
# - How to combine ADSR + Filter + LFO + Pattern
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
# We use a SAWTOOTH waveform instead of a sine wave.
#
# Why?
#
# Filters remove harmonics.
# A sawtooth contains many harmonics.
# A sine wave contains only one main frequency.
#
# This makes the effect of the filter much easier to hear.
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
# CREATE AN LFO
# ------------------------------------------------------------
#
# LFO = Low Frequency Oscillator
#
# An LFO is usually too slow to hear directly.
#
# Instead it is used to automatically control
# another parameter.
#
# Common uses:
#
# - Vibrato (pitch modulation)
# - Tremolo (volume modulation)
# - Filter sweeps
#
# ------------------------------------------------------------

LFO_RATE = 2.0

lfo = synthio.LFO(
    rate=LFO_RATE,
    scale=600,
    offset=1200,
)

# ------------------------------------------------------------
# FILTER TYPES
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=lfo,
    Q=1.2,
)


filter_hpf = synthio.Biquad(
    synthio.FilterMode.HIGH_PASS,
    frequency=lfo,
    Q=1.0
)


filter_bpf = synthio.Biquad(
    synthio.FilterMode.BAND_PASS,
    frequency=lfo,
    Q=1.0,
)


filter_notch = synthio.Biquad(
    synthio.FilterMode.NOTCH,
    frequency=lfo,
    Q=1.0,
)


# ------------------------------------------------------------
# CHOOSE WHICH FILTER TO TEST
# ------------------------------------------------------------
#
# Change this line to:
# filter_lpf
# filter_hpf
# filter_bpf
# filter_notch
#
# ------------------------------------------------------------

selected_filter = filter_lpf



# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    filter=selected_filter,
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
# Listen for:
#
# "Wah... Wah... Wah..."
#
# This is the low‑pass filter moving up and down
# under control of the LFO.
#
# Experiment:
#
# Change:
#
# LFO_RATE = 2.0
#
# To:
#
# 0.5   (very slow sweep)
# 1.0
# 4.0
# 8.0   (fast sweep)
#
# Also try changing:
#
# scale=600
#
# To:
#
# scale=200
# scale=1000
# scale=2000
#
# and listen to how the sweep changes.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:
        note.frequency = freq
        synth.press(note)
        print(
            f"Playing {freq} Hz "
            f"with LFO-controlled LPF")

        time.sleep(NOTE_TIME)
        synth.release(note)
        time.sleep(0.05)
