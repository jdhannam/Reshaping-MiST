# ============================================================
# Tutorial 3 — Playing a Pattern Using ADSR Envelopes
# ============================================================
#
# This tutorial teaches:
#
# - What ADSR envelopes are
# - How to attach an envelope to a Synthio note
# - How to trigger Attack, Decay, Sustain and Release
# - How to play a pattern where each note has its own shape
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
#
# board
#     Access to Raspberry Pi Pico pin names
#
# audiobusio
#     I2S digital audio output
#
# audiomixer
#     Audio mixer
#
# synthio
#     CircuitPython synthesizer engine
#
# ulab.numpy
#     Used to generate custom waveforms
#
# time
#     Used for note timing
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
# Configure digital audio output.
#
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,
    word_select=board.GP28,
    data=board.GP26,
)


# ------------------------------------------------------------
# AUDIO MIXER
# ------------------------------------------------------------
#
# The mixer combines audio sources before sending
# them to the DAC.
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

synth = synthio.Synthesizer(
    sample_rate=22050
)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A wavetable contains one cycle of a waveform.
#
# We use a sine wave because it produces a clean,
# simple tone that makes the envelope easier to hear.
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
# ADSR describes how the volume changes over time.
#
# A = Attack
#     How long it takes to reach full volume.
#
# D = Decay
#     How long it takes to fall from full volume
#     to the sustain level.
#
# S = Sustain
#     The volume held while the note remains pressed.
#
# R = Release
#     How long it takes to fade out after the note
#     is released.
#
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,      # 50 milliseconds
    decay_time=0.20,       # 200 milliseconds
    sustain_level=0.60,    # 60% volume
    release_time=0.30,     # 300 milliseconds
)


# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------
#
# The envelope becomes part of the note.
#
# Every time we press the note:
#
# Attack -> Decay -> Sustain
#
# Every time we release the note:
#
# Release
#
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
#
# A simple ascending scale.
#
# Students can change these values to
# create their own melodies.
#
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
#
# For each frequency:
#
# 1. Set the pitch
# 2. Press the note
# 3. Hold it briefly
# 4. Release the note
#
# Because we press and release every note,
# the ADSR envelope is triggered each time.
#
# Listen carefully to:
#
# - The quick attack
# - The slight drop during decay
# - The sustain level
# - The smooth release
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        # Set the pitch

        note.frequency = freq

        # Start the note
        # Triggers:
        # Attack -> Decay -> Sustain

        synth.press(note)

        print(
            f"Playing {freq} Hz"
        )

        # Hold the note

        time.sleep(NOTE_TIME)

        # Release the note
        # Triggers:
        # Release

        synth.release(note)

        # Small gap between notes

        time.sleep(0.05)