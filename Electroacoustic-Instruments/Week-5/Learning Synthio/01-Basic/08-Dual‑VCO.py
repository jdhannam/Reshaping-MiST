# ============================================================
# Tutorial 8 — Adding a Second Oscillator (Dual‑Oscillator Synth)
# ============================================================
#
# This tutorial teaches:
#
# - How to use TWO oscillators at the same time
# - How to layer multiple notes together
# - How detuning creates a chorus-like effect
# - How ADSR + pattern + dual oscillators work together
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
# CREATE TWO WAVEFORMS
# ------------------------------------------------------------
#
# Oscillator 1 will use a SINE wave.
#
# Oscillator 2 will use a SAWTOOTH wave.
#
# Combining different waveforms gives a richer sound.
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000


# ------------------------------------------------------------
# OSCILLATOR 1 — SINE WAVE
# ------------------------------------------------------------

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
# OSCILLATOR 2 — SAWTOOTH WAVE
# ------------------------------------------------------------

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
#
# Both oscillators will share the same envelope.
#
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.2,
    sustain_level=0.6,
    release_time=0.3,
)


# ------------------------------------------------------------
# DETUNE SETTINGS
# ------------------------------------------------------------
#
# Detuning means one oscillator is slightly higher
# or lower in pitch than another.
#
# When two very similar frequencies play together,
# they create a slow beating effect.
#
# This makes the sound feel:
#
# - Wider
# - Richer
# - More chorused
#
# ------------------------------------------------------------

DETUNE_HZ = 3


# ------------------------------------------------------------
# OSCILLATOR 1 NOTE
# ------------------------------------------------------------
#
# Main pitch.
#
# ------------------------------------------------------------

note1 = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    envelope=envelope,
    amplitude=0.10,
)


# ------------------------------------------------------------
# OSCILLATOR 2 NOTE
# ------------------------------------------------------------
#
# Slightly detuned version.
#
# ------------------------------------------------------------

note2 = synthio.Note(
    frequency=223,
    waveform=wave_saw,
    envelope=envelope,
    amplitude=0.10,
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
# We update BOTH oscillators.
#
# Oscillator 2 remains slightly detuned.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        # Oscillator 1
        note1.frequency = freq

        # Oscillator 2
        note2.frequency = freq + DETUNE_HZ

        # Play both oscillators together
        synth.press((note1, note2))

        print(
            f"Playing {freq} Hz "
            f"with dual oscillators "
            f"(sine + saw, detuned by {DETUNE_HZ} Hz)"
        )

        time.sleep(NOTE_TIME)

        synth.release((note1, note2))

        time.sleep(0.05)