# ============================================================
# Tutorial 4 — Introduction to Polyphony
# ============================================================
#
# This tutorial teaches:
#
# - What polyphony means
# - How to play multiple notes at the same time
# - How chords are constructed
# - How Synthio handles multiple active notes
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

synth = synthio.Synthesizer(
    sample_rate=22050
)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE A SINE WAVETABLE
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
    attack_time=0.05,
    decay_time=0.2,
    sustain_level=0.6,
    release_time=0.3,
)


# ------------------------------------------------------------
# WHAT IS POLYPHONY?
# ------------------------------------------------------------
#
# Monophonic:
#     One note at a time.
#
# Polyphonic:
#     Multiple notes at the same time.
#
# We will build simple 3-note chords.
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# CREATE THREE NOTES
# ------------------------------------------------------------
#
# These notes share:
#
# - the same waveform
# - the same envelope
#
# But each note will have its own frequency.
#
# ------------------------------------------------------------

note1 = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    envelope=envelope,
    amplitude=0.08,
)

note2 = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    envelope=envelope,
    amplitude=0.08,
)

note3 = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    envelope=envelope,
    amplitude=0.08,
)


# ------------------------------------------------------------
# CHORDS
# ------------------------------------------------------------
#
# Each tuple contains:
#
# Root
# Third
# Fifth
#
# These are simple major chords.
#
# ------------------------------------------------------------

chords = [

    # A Major
    (220, 277, 330),

    # C Major
    (262, 330, 392),

    # D Major
    (294, 370, 440),

    # F Major
    (349, 440, 523),

]


# ------------------------------------------------------------
# NOTE LENGTH
# ------------------------------------------------------------

CHORD_TIME = 1.0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# For each chord:
#
# 1. Assign frequencies
# 2. Press all notes together
# 3. Hold the chord
# 4. Release all notes together
#
# ------------------------------------------------------------

while True:

    for root, third, fifth in chords:

        note1.frequency = root
        note2.frequency = third
        note3.frequency = fifth

        synth.press(
            (note1, note2, note3)
        )

        print(
            f"Chord: "
            f"{root} Hz, "
            f"{third} Hz, "
            f"{fifth} Hz"
        )

        time.sleep(CHORD_TIME)

        synth.release(
            (note1, note2, note3)
        )

        time.sleep(0.1)