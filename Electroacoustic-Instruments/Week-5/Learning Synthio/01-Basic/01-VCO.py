# ============================================================
# Tutorial 1 — Constant Tone (220 Hz)
# ============================================================
#
# What this script demonstrates:
# 1. How to set up audio output on a Raspberry Pi Pico
# 2. How to create a simple sine wave wavetable
# 3. How to play a constant tone at 220 Hz
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
#
# These modules give us access to:
#
# - Hardware pins
# - Digital audio output
# - Audio mixing
# - The Synthio synthesizer engine
# - Numerical functions for generating waveforms
#
# ------------------------------------------------------------

import board                 # Access to Pico pin names
import audiobusio            # I2S digital audio output
import audiomixer            # Audio mixer
import synthio               # Synthesizer engine
import ulab.numpy as np      # Fast numerical library
import time                  # Timing and delays


# ------------------------------------------------------------
# AUDIO SETUP
# ------------------------------------------------------------
#
# I2S is a digital audio protocol used to send 
# audio to an external DAC (Digital to Analog Converter).
#
# Change these pins if your hardware uses different wiring.
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
# The mixer combines one or more audio sources before sending
# them to the DAC.
#
# voice_count
#     Number of audio inputs connected to the mixer.
#
# sample_rate
#     Number of audio samples generated each second.
#
# ------------------------------------------------------------

mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)


# Send mixer output to the DAC.

audio.play(mixer)


# ------------------------------------------------------------
# CREATE THE SYNTHESIZER
# ------------------------------------------------------------
#
# The Synthesizer generates audio from Notes.
#
# ------------------------------------------------------------

synth = synthio.Synthesizer(
    sample_rate=22050
)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A wavetable contains one cycle of a waveform.
#
# Synthio repeatedly loops over this table to create a
# continuous sound.
#
# In this example we generate a sine wave.
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000


# Generate one cycle of a sine wave.
#
# np.linspace(...)
#     Creates evenly spaced values from 0 to 2π.
#
# np.sin(...)
#     Calculates the sine of each value.
#
# Multiplying by AMPLITUDE scales the waveform into the
# 16-bit audio range expected by Synthio.

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
# CREATE A NOTE
# ------------------------------------------------------------
#
# A Synthio Note contains:
#
# - Frequency (pitch)
# - Waveform (tone colour)
# - Amplitude (volume)
#
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,       # A3 = 220 Hz
    waveform=wave_sine,
    amplitude=0.1,       # Keep volume modest
)


# ------------------------------------------------------------
# CONNECT THE SYNTH TO THE MIXER
# ------------------------------------------------------------
#
# The mixer must be told to play the synthesizer before
# any notes can be heard.
#
# ------------------------------------------------------------

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# START THE NOTE
# ------------------------------------------------------------
#
# Pressing a note starts it playing.
# Since we never release the note, it will continue forever.
#
# ------------------------------------------------------------

synth.press(note)

print("Playing constant 220 Hz tone...")


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Nothing else happens in this tutorial.
# The note will continue playing until the board is reset.
#
# Later tutorials will add:
#
# - Multiple notes
# - ADSR envelopes
# - Filters
# - LFOs
# - Sensors
#
# ------------------------------------------------------------

while True:
    time.sleep(1)