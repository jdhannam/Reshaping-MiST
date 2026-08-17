# ============================================================
# Tutorial 20 — Reverb Parameter Sweep
# ============================================================
#
# This tutorial teaches:
#
# - How to change effect parameters while audio is playing
# - How room size affects reverb
# - How reverb can be controlled in real time
# - How a single effect can create many different sounds
#
# ============================================================
#
# IMPORTANT
#
# This tutorial requires:
#
# - A controller that uses a RP2350 chip, not RP2040
# - CircuitPython 10+
# - audiofreeverb module
# - A board that includes audiofreeverb support
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import audiobusio
import synthio
import audiofreeverb
import ulab.numpy as np
import time


# ------------------------------------------------------------
# AUDIO SETUP
# ------------------------------------------------------------
#
# Signal chain:
#
# Synth
#   ↓
# Reverb
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
# CREATE THE REVERB EFFECT
# ------------------------------------------------------------
#
# We start with a medium-sized room.
#
# During the tutorial we will gradually change
# the roomsize parameter while notes are playing.
#
# ------------------------------------------------------------

reverb = audiofreeverb.Freeverb(
    roomsize=0.1,
    damp=0.3,
    mix=0.5,

    buffer_size=1024,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------

reverb.play(synth)

audio.play(reverb)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# We use a sawtooth waveform because it contains
# many harmonics and makes the reverb easier to hear.
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
# CREATE AN ADSR ENVELOPE
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.20,
    sustain_level=0.60,
    release_time=0.50,
)


# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
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

NOTE_TIME = 0.4


# ------------------------------------------------------------
# ROOM SIZE VALUES
# ------------------------------------------------------------
#
# We gradually move from:
#
# Small Room
#        ↓
# Large Hall
#
# ------------------------------------------------------------

room_sizes = [
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
]


# ------------------------------------------------------------
# STARTUP MESSAGE
# ------------------------------------------------------------

print()
print("Tutorial 20 - Reverb Parameter Sweep")
print("------------------------------------")
print("Listen for the room gradually")
print("growing larger.")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# For each room size:
#
# 1. Update the reverb
# 2. Play the scale
# 3. Listen for the difference
#
# Small values:
#
#     Small room
#     Short reflections
#
# Large values:
#
#     Concert hall
#     Large reflections
#
#
# EXPERIMENTS
#
# Try changing:
#
# reverb.mix
#
# between:
#
# 0.2
# 0.5
# 0.8
#
#
# Try changing:
#
# reverb.damp
#
# between:
#
# 0.1
# 0.5
# 0.9
#
# ------------------------------------------------------------

while True:

    for room_size in room_sizes:

        reverb.roomsize = room_size

        print()
        print(
            f"Room Size = {room_size:.1f}"
        )

        for freq in pattern:

            note.frequency = freq

            synth.press(note)

            print(
                f"Playing {freq} Hz"
            )

            time.sleep(NOTE_TIME)

            synth.release(note)

            time.sleep(0.15)

        #
        # Pause before the next room size.
        #

        time.sleep(0.5)