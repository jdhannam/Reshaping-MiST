# ============================================================
# Tutorial 27 — Ambient Drone Synth
# ============================================================
#
# This tutorial teaches:
#
# - What a drone is
# - How multiple oscillators create rich textures
# - How slow LFOs create movement
# - How filters shape a sound over time
# - How to build an evolving ambient synthesizer patch
#
# ============================================================
#
# A drone is a continuously sustained sound.
#
# Unlike a melody, a drone changes very slowly.
#
# Ambient synthesizers often use:
#
# - Multiple oscillators
# - Slight detuning
# - Long envelopes
# - Slow LFOs
# - Filter movement
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
# A sawtooth waveform contains many harmonics.
#
# These harmonics give the filter plenty
# of frequencies to work with.
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
# CREATE A DRONE ENVELOPE
# ------------------------------------------------------------
#
# Slow attack
# Long release
#
# This creates smooth transitions.
#
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=2.0,
    decay_time=1.0,
    sustain_level=0.7,
    release_time=3.0,
)


# ------------------------------------------------------------
# FILTER LFO
# ------------------------------------------------------------
#
# Slowly moves the filter cutoff.
#
# One complete cycle every 20 seconds.
#
# ------------------------------------------------------------

filter_lfo = synthio.LFO(
    rate=0.05,
    scale=1200,
    offset=1800,
)


# ------------------------------------------------------------
# LOW PASS FILTER
# ------------------------------------------------------------
#
# The LFO slowly opens and closes
# the filter.
#
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=filter_lfo,
    Q=1.2,
)


# ------------------------------------------------------------
# VIBRATO LFO
# ------------------------------------------------------------
#
# Very slow vibrato.
#
# Creates gentle movement.
#
# ------------------------------------------------------------

vibrato_lfo = synthio.LFO(
    rate=0.15,
    scale=0.005,
    offset=0,
)


# ------------------------------------------------------------
# CREATE THREE OSCILLATORS
# ------------------------------------------------------------
#
# All oscillators play nearly the same note.
#
# Small differences in frequency create
# slow beating patterns.
#
# ------------------------------------------------------------

osc1 = synthio.Note(
    frequency=220.0,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    bend=vibrato_lfo,
    amplitude=0.06,
)

osc2 = synthio.Note(
    frequency=220.8,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    bend=vibrato_lfo,
    amplitude=0.06,
)

osc3 = synthio.Note(
    frequency=219.2,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    bend=vibrato_lfo,
    amplitude=0.06,
)


# ------------------------------------------------------------
# DRONE NOTES
# ------------------------------------------------------------
#
# These frequencies roughly correspond to:
#
# A2
# D3
# E3
# F3
#
# ------------------------------------------------------------

drone_notes = [
    110,
    147,
    165,
    175,
]


# ------------------------------------------------------------
# DRONE TIMING
# ------------------------------------------------------------
#
# Each drone lasts a long time.
#
# ------------------------------------------------------------

DRONE_TIME = 12


# ------------------------------------------------------------
# STARTUP MESSAGE
# ------------------------------------------------------------

print()
print("Tutorial 27 - Ambient Drone Synth")
print("---------------------------------")
print()
print("Listen for:")
print()
print("- Slow movement")
print("- Detuned oscillators")
print("- Filter sweeps")
print("- Long evolving textures")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Unlike previous tutorials,
# this patch changes very slowly.
#
# Relax and listen for:
#
# - Beating between oscillators
# - Filter movement
# - Harmonic changes
#
#
# EXPERIMENTS
#
# Try changing:
#
# osc2.frequency
# osc3.frequency
#
# for more or less detuning.
#
#
# Try changing:
#
# filter_lfo.rate
#
# 0.02
# 0.05
# 0.10
#
#
# Try changing:
#
# attack_time
#
# 1.0
# 3.0
# 5.0
#
#
# ADVANCED CHALLENGE
#
# Add a fourth oscillator:
#
# frequency = root * 2
#
# to create an octave drone.
#
# ------------------------------------------------------------

while True:

    for root in drone_notes:

        osc1.frequency = root
        osc2.frequency = root + 0.8
        osc3.frequency = root - 0.8

        print(
            f"Drone Root: {root} Hz"
        )

        synth.press(
            (
                osc1,
                osc2,
                osc3,
            )
        )

        time.sleep(DRONE_TIME)

        synth.release(
            (
                osc1,
                osc2,
                osc3,
            )
        )

        #
        # Allow the long release
        # to fade naturally.
        #

        time.sleep(2)