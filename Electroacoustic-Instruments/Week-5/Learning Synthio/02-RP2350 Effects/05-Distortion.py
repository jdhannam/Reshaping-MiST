# ============================================================
# Tutorial 23 — Distortion
# ============================================================
#
# This tutorial teaches:
#
# - What distortion is
# - How distortion changes a waveform
# - How clipping creates additional harmonics
# - How drive affects the sound
# - How to add distortion to a Synthio synthesizer
#
# ============================================================
#
# IMPORTANT
#
# This tutorial requires:
#
# - A controller that uses a RP2350 chip, not RP2040
# - CircuitPython 10+
# - audiofilters module
# - A board that includes audiofilters support
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
# audiofilters
#     Distortion and filter effects
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
import audiofilters
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
# Distortion
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
# CREATE THE DISTORTION EFFECT
# ------------------------------------------------------------
#
# Distortion works by increasing the gain
# of a signal until the waveform begins to
# clip.
#
# Clipping creates new harmonics and changes
# the character of the sound.
#
#
# pre_gain
#     Amount of boost before distortion.
#
# post_gain
#     Output level compensation.
#
# mix
#     Dry / wet balance.
#
# ------------------------------------------------------------

distortion = audiofilters.Distortion(
    mix=1.0,

    mode=audiofilters.DistortionMode.OVERDRIVE,

    soft_clip=True,

    pre_gain=20,

    post_gain=-10,

    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------

distortion.play(synth)

audio.play(distortion)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A sine wave clearly demonstrates how
# distortion creates additional harmonics.
#
# Compare this to a clean sine wave.
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

envelope = synthio.Envelope(
    attack_time=0.02,
    decay_time=0.10,
    sustain_level=0.70,
    release_time=0.20,
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
print("Tutorial 23 - Distortion")
print("------------------------")
print("Pre Gain  :", distortion.pre_gain)
print("Post Gain :", distortion.post_gain)
print("Mix       :", distortion.mix)
print()
print("Listen for added harmonics and grit.")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen for:
#
# - More harmonics
# - A brighter sound
# - Increased aggressiveness
#
# Compare:
#
# Clean oscillator
#
# vs
#
# Distorted oscillator
#
#
# EXPERIMENTS
#
# Try changing:
#
# pre_gain=5
#
# Very light distortion
#
#
# Try changing:
#
# pre_gain=20
#
# Moderate overdrive
#
#
# Try changing:
#
# pre_gain=40
#
# Heavy distortion
#
#
# Try changing:
#
# mix=0.5
#
# Blend clean and distorted audio
#
#
# Try changing:
#
# soft_clip=False
#
# Compare hard clipping against
# soft clipping.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        note.frequency = freq

        synth.press(note)

        print(
            f"Playing {freq} Hz with distortion"
        )

        time.sleep(NOTE_TIME)

        synth.release(note)

        time.sleep(0.05)