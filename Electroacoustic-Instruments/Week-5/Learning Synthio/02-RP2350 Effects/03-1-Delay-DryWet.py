# ============================================================
# Tutorial — Delay with Dry/Wet Mix Demonstration
# ============================================================
#
# This tutorial teaches:
#
# - What delay (echo) is
# - What "dry" and "wet" mean in audio
# - How dry/wet mix changes the sound
# - How to switch between dry-only, wet-only, and blended echo
#
# ============================================================
#
# IMPORTANT
#
# Requires:
# - RP2350-based board
# - CircuitPython 10+
# - audiodelays module
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import audiobusio
import synthio
import audiodelays
import ulab.numpy as np
import time


# ------------------------------------------------------------
# AUDIO SETUP
# ------------------------------------------------------------
#
# Signal Chain:
#
# Synth  →  Echo  →  DAC
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
# DRY/WET MIX DEMONSTRATION
# ------------------------------------------------------------
#
# mix = 0.0   → 100% DRY (no echo)
# mix = 1.0   → 100% WET (only echoes)
# mix = 0.5   → 50/50 blend
#
# Students should uncomment ONE of the mix settings below
# to hear the difference.
#
# ------------------------------------------------------------

mix_setting = 0.5


# ------------------------------------------------------------
# CREATE THE ECHO EFFECT
# ------------------------------------------------------------

echo = audiodelays.Echo(
    mix=mix_setting,     # ← DRY/WET MIX HERE
    delay_ms=250,        # time between repeats
    decay=0.6,           # how quickly echoes fade
    max_delay_ms=500,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------

echo.play(synth)
audio.play(echo)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# Sawtooth wave makes echoes easier to hear.
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000

wave_saw = np.array(
    np.linspace(-AMPLITUDE, AMPLITUDE, SAMPLE_SIZE, endpoint=False),
    dtype=np.int16,
)


# ------------------------------------------------------------
# ADSR ENVELOPE
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
    waveform=wave_saw,
    envelope=envelope,
    amplitude=0.15,
)


# ------------------------------------------------------------
# PATTERN OF TONES
# ------------------------------------------------------------

pattern = [
    220, 247, 262, 294,
    330, 349, 392, 440,
]

NOTE_TIME = 0.25


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen for:
#
# DRY ONLY:
#     Only the original note, no echo.
#
# WET ONLY:
#     Only the echoes, original note removed.
#
# BLEND:
#     Original note + echoes together.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:
        note.frequency = freq
        synth.press(note)

        print(
            f"Playing {freq} Hz — mix={mix_setting}"
        )

        time.sleep(NOTE_TIME)
        synth.release(note)

        # Allow echoes to be heard
        time.sleep(0.40)
