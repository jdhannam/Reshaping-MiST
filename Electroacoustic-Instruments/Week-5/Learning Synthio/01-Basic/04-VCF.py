# ============================================================
# Tutorial 4 — Adding a Low‑Pass Filter to a Tone Pattern
# ============================================================
#
# This tutorial teaches:
#
# - What a filter is in synthesis
# - How a low‑pass filter (LPF) changes timbre
# - How to attach a filter to a Synthio note
# - How to play a pattern with filtered tones
# - How to test other filter types
#
# IMPORTANT:
# We use a SAWTOOTH waveform instead of a sine wave.
#
# Why?
# A sine wave contains only one frequency component,
# so a filter has very little to remove.
#
# A sawtooth wave contains many harmonics which makes
# the effect of the filter much easier to hear.
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
#
# board
#     Access to Pico GPIO pins
#
# audiobusio
#     Sends digital audio using I2S
#
# audiomixer
#     Mixes one or more sounds together
#
# synthio
#     Synthesizer engine built into CircuitPython
#
# ulab.numpy
#     Used to create custom waveforms
#
# time
#     Used for delays between notes
#
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
#
# Configure the I2S audio output.
#
# Change these pins if your DAC requires different connections.
#
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,
    word_select=board.GP28,
    data=board.GP26,
)


# ------------------------------------------------------------
# CREATE AN AUDIO MIXER
# ------------------------------------------------------------
#
# The mixer combines sounds before sending them
# to the I2S audio output.
#
# voice_count
#     Number of simultaneous sound sources.
#
# sample_rate
#     Audio quality and frequency range.
#
# ------------------------------------------------------------

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

synth = synthio.Synthesizer(sample_rate=22050)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# For this filter demonstration we use a SAWTOOTH waveform.
# A saw wave contains many harmonics.
# Harmonics are higher frequencies above the fundamental tone.
#
# Since filters work by removing or emphasizing frequencies,
# a waveform with many harmonics makes the filter effect
# much easier to hear.
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
# ADSR stands for:
#
# A = Attack
# D = Decay
# S = Sustain
# R = Release
#
# The envelope controls how the volume changes over time.
#
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.2,
    sustain_level=0.6,
    release_time=0.3,
)


# ------------------------------------------------------------
# FILTER SECTION
# ------------------------------------------------------------
#
# Filters change TIMBRE.
# Timbre is the character or colour of a sound.
#
# A filter does NOT primarily change pitch.
# Instead it controls which frequencies are allowed through.
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# LOWPASS FILTER (LPF)
# ------------------------------------------------------------
#
# A lowpass filter:
#
# Allows LOW frequencies through
# Reduces HIGH frequencies
#
#
# frequency: Cutoff frequency in Hz
# Q: Resonance
#
# Higher Q creates a small boost around the cutoff frequency.
#
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=800,
    Q=1.2,
)


# ------------------------------------------------------------
# OTHER AVAILABLE FILTER TYPES
# ------------------------------------------------------------
#
# Uncomment ONE filter at a time and replace
# filter_lpf in the note definition below.
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# HIGH‑PASS FILTER (HPF)
# ------------------------------------------------------------
#
# Allows HIGH frequencies through
# Reduces LOW frequencies
#
# ------------------------------------------------------------

# filter_hpf = synthio.Biquad(
#     synthio.FilterMode.HIGH_PASS,
#     frequency=500,
#     Q=1.0,
# )


# ------------------------------------------------------------
# BAND‑PASS FILTER (BPF)
# ------------------------------------------------------------
#
# Allows a narrow band of frequencies through
# Reduces frequencies above and below
#
# ------------------------------------------------------------

# filter_bpf = synthio.Biquad(
#     synthio.FilterMode.BAND_PASS,
#     frequency=1200,
#     Q=1.5,
# )


# ------------------------------------------------------------
# NOTCH FILTER
# ------------------------------------------------------------
#
# Removes a narrow band of frequencies
# Allows frequencies above and below
#
# ------------------------------------------------------------

# filter_notch = synthio.Biquad(
#     synthio.FilterMode.NOTCH,
#     frequency=900,
#     Q=1.0,
# )


# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------
#
# A Note combines:
#
# - Frequency (pitch)
# - Waveform
# - Envelope
# - Filter
# - Amplitude
#
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    amplitude=0.15,
)


# ------------------------------------------------------------
# DEFINE A SIMPLE SCALE
# ------------------------------------------------------------
# These frequencies roughly form an A minor scale.

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
# Play each note in sequence.
# Listen carefully to how the filter changes the character
# of the sound compared to an unfiltered saw wave.
#
# Try changing:
#
# frequency=800
#
# to:
#
# frequency=200
# frequency=500
# frequency=2000
# frequency=5000
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        note.frequency = freq
        synth.press(note)

        print(
            f"Playing {freq} Hz "
            f"with LPF cutoff {filter_lpf.frequency} Hz"
        )

        time.sleep(NOTE_TIME)
        synth.release(note)
        time.sleep(0.05)