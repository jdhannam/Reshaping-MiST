# ============================================================
# Tutorial 2 — Playing a Pattern of Constant Tones
# ============================================================
#
# This tutorial teaches:
#
# - How to create a simple wavetable synthesizer
# - How to play a sequence (pattern) of pitches
# - How to change the frequency of a note while it is playing
# - How frequency controls musical pitch
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
#
# board
#     Access to Raspberry Pi Pico pins
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
#     Fast numerical library used to create waveforms
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
# I2S is a digital audio protocol used to send audio
# data to an external DAC.
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


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A wavetable contains one complete cycle
# of a waveform.
#
# This example generates a sine wave.
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
# CREATE A NOTE
# ------------------------------------------------------------
#
# We create ONE note object.
#
# Instead of creating a new note for every pitch,
# we will simply change the frequency property.
#
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,       # Starting frequency (A3)
    waveform=wave_sine,
    amplitude=0.1,
)


# ------------------------------------------------------------
# CONNECT SYNTH TO THE MIXER
# ------------------------------------------------------------

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# START THE NOTE
# ------------------------------------------------------------
#
# The note will remain active continuously.
#
# Later we will change its frequency while it
# is already playing.
#
# ------------------------------------------------------------

synth.press(note)


# ------------------------------------------------------------
# DEFINE A PATTERN OF TONES
# ------------------------------------------------------------
#
# Frequencies are measured in Hertz (Hz).
#
# Higher frequency = higher pitch
# Lower frequency  = lower pitch
#
# Students can edit these values to create
# their own melodies.
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
# 1. Change the note frequency
# 2. Wait a short time
# 3. Move to the next frequency
#
# Notice that we never release the note.
#
# The oscillator continues running while
# only the pitch changes.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        # Change the pitch

        note.frequency = freq

        print(
            f"Playing {freq} Hz"
        )

        # Wait before changing pitch again

        time.sleep(NOTE_TIME)