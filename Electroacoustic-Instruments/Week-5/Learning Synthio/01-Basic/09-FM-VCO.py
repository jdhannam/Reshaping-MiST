# ============================================================
# Tutorial 9 — Basic FM Synthesis (Carrier + Modulator)
# ============================================================
#
# This tutorial teaches:
#
# - What a Carrier oscillator is
# - What a Modulator oscillator is
# - How frequency modulation (FM) works
# - How modulation depth changes timbre
# - How ADSR and FM can be combined
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
# CREATE A SINE WAVE
# ------------------------------------------------------------
#
# A sine wave is traditionally used in FM synthesis.
#
# The oscillator we hear is called the Carrier.
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
    attack_time=0.05,
    decay_time=0.2,
    sustain_level=0.6,
    release_time=0.3,
)


# ------------------------------------------------------------
# FM PARAMETERS
# ------------------------------------------------------------
#
# FM = Frequency Modulation
#
# One oscillator changes the pitch of another.
#
# Carrier:
#     The oscillator we hear.
#
# Modulator:
#     The oscillator changing the carrier pitch.
#
# ------------------------------------------------------------

FM_RATE = 50.0

#
# scale controls modulation depth.
#
# Larger values create a brighter,
# more metallic sound.
#
FM_DEPTH = 0.05


# ------------------------------------------------------------
# CREATE THE MODULATOR
# ------------------------------------------------------------
#
# This oscillator runs at 50 Hz and
# continuously changes the carrier pitch.
#
# ------------------------------------------------------------

fm_modulator = synthio.LFO(
    rate=FM_RATE,
    scale=FM_DEPTH,
    offset=0,
)


# ------------------------------------------------------------
# CREATE THE CARRIER NOTE
# ------------------------------------------------------------
#
# bend receives the modulation signal.
#
# The carrier frequency will wobble
# rapidly around its target pitch.
#
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    envelope=envelope,
    bend=fm_modulator,
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

NOTE_TIME = 0.5


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen to how the timbre changes.
#
# Experiment:
#
# FM_RATE = 5
# FM_RATE = 20
# FM_RATE = 50
# FM_RATE = 100
#
#
# FM_DEPTH = 0.01
# FM_DEPTH = 0.05
# FM_DEPTH = 0.10
# FM_DEPTH = 0.20
#
# Increasing depth creates more
# dramatic frequency modulation.
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        note.frequency = freq

        synth.press(note)

        print(
            f"Carrier={freq} Hz  "
            f"Modulator={FM_RATE} Hz  "
            f"Depth={FM_DEPTH}"
        )

        time.sleep(NOTE_TIME)

        synth.release(note)

        time.sleep(0.05)