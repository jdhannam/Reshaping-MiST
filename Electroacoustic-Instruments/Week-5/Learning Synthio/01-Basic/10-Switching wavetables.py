# ============================================================
# Tutorial 10 — Switching Wavetables
# ============================================================
#
# This tutorial teaches:
# - How to create multiple waveforms
# - How to switch waveforms while playing
# - How timbre changes when the waveform changes
# - How different waveforms sound
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
# CREATE MULTIPLE WAVEFORMS
# ------------------------------------------------------------
#
# Each waveform has a unique sound.
#
# Sine: Pure tone no harmonics
# Sawtooth: Bright and fuzzy
# Square: Hollow and wood-like
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000


# ------------------------------------------------------------
# SINE WAVE
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
# SAWTOOTH WAVE
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
# SQUARE WAVE
# ------------------------------------------------------------

wave_square = np.array(
    np.where(
        np.linspace(
            0,
            1,
            SAMPLE_SIZE,
            endpoint=False,
        ) < 0.5,
        AMPLITUDE,
        -AMPLITUDE,
    ),
    dtype=np.int16,
)


# ------------------------------------------------------------
# STORE WAVEFORMS IN A LIST
# ------------------------------------------------------------

waveforms = [
    wave_sine,
    wave_saw,
    wave_square,
]


# ------------------------------------------------------------
# WAVEFORM NAMES
# ------------------------------------------------------------

waveform_names = [
    "Sine",
    "Sawtooth",
    "Square",
]


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
# PATTERN OF TONES
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
# For each note:
#
# 1. Select a waveform
# 2. Create a note using that waveform
# 3. Play the note
# 4. Move to the next waveform
#
# Listen carefully to how the timbre
# of the sound changes even though the pitch
# remains the same.
#
# ------------------------------------------------------------

wave_index = 0

while True:

    for freq in pattern:

        waveform = waveforms[wave_index]
        waveform_name = waveform_names[wave_index]

        note = synthio.Note(
            frequency=freq,
            waveform=waveform,
            envelope=envelope,
            amplitude=0.1,
        )

        synth.press(note)

        print(
            f"Playing {freq} Hz "
            f"using {waveform_name} waveform"
        )

        time.sleep(NOTE_TIME)
        synth.release(note)
        time.sleep(0.05)

        wave_index = (
            wave_index + 1
        ) % len(waveforms)
