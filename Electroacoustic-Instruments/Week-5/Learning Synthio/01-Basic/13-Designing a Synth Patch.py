# ============================================================
# Tutorial 26 — Designing a Synth Patch
# ============================================================
#
# This tutorial teaches:
#
# - How to combine multiple synthesis techniques
# - How synthesizer "patches" are created
# - How oscillators, filters, envelopes, and LFOs
#   work together
# - How to create a classic synthesizer PAD sound
#
# ============================================================
#
# A synthesizer patch is a recipe for creating sound.
#
# Oscillators + Envelope + Filter + Modulation = Sound
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


# ------------------------------------------------------------
# CREATE THE SYNTHESIZER
# ------------------------------------------------------------

synth = synthio.Synthesizer(
    sample_rate=22050,
)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE TWO WAVETABLES
# ------------------------------------------------------------
#
# Oscillator 1
#     Sawtooth
#
# Oscillator 2
#     Slightly detuned sawtooth
#
# Detuning creates a richer sound.
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
# CREATE A PAD ENVELOPE
# ------------------------------------------------------------
#
# Pad sounds usually have:
#
# Slow Attack
# Long Release
#
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.75,
    decay_time=0.50,
    sustain_level=0.75,
    release_time=1.50,
)


# ------------------------------------------------------------
# CREATE A FILTER LFO
# ------------------------------------------------------------
#
# Slowly open and close the filter.
#
# This creates movement
# while the note is playing.
#
# ------------------------------------------------------------

filter_lfo = synthio.LFO(
    rate=0.20,
    scale=700,
    offset=1200,
)


# ------------------------------------------------------------
# CREATE A LOW PASS FILTER
# ------------------------------------------------------------
#
# Low-pass filters remove high frequencies.
#
# Pad sounds often use filters to create
# smooth textures.
#
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=filter_lfo,
    Q=1.0,
)


# ------------------------------------------------------------
# CREATE A VIBRATO LFO
# ------------------------------------------------------------
#
# A slow vibrato.
#
# ------------------------------------------------------------

vibrato_lfo = synthio.LFO(
    rate=4.5,
    scale=0.01,
    offset=0,
)


# ------------------------------------------------------------
# CREATE TWO OSCILLATORS
# ------------------------------------------------------------
#
# Oscillator 2 is slightly detuned.
#
# This creates a larger sound.
#
# ------------------------------------------------------------

note1 = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    bend=vibrato_lfo,
    amplitude=0.08,
)

note2 = synthio.Note(
    frequency=221.5,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    bend=vibrato_lfo,
    amplitude=0.08,
)


# ------------------------------------------------------------
# DEFINE CHORDS
# ------------------------------------------------------------
#
# Instead of single notes,
# we will play full chords.
#
# ------------------------------------------------------------

chords = [
    (220, 262, 330), # A minor
    (262, 330, 392), # C major
    (349, 440, 523), # F major
    (392, 494, 587), # G major
]


# ------------------------------------------------------------
# CHORD TIMING
# ------------------------------------------------------------

CHORD_TIME = 3.0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# This is a simple PAD patch.
# that combines previous tutorials:
#
# Tutorial 3: ADSR
# Tutorial 4: Polyphony
# Tutorial 6: LFO modulation
# Tutorial 8: Dual oscillators
# Tutorial 4 Filters: Low-pass filter
#
# ------------------------------------------------------------

while True:

    for root, third, fifth in chords:

        note1.frequency = root
        note2.frequency = root + 1.5

        chord_note2 = synthio.Note(
            frequency=third,
            waveform=wave_saw,
            envelope=envelope,
            filter=filter_lpf,
            bend=vibrato_lfo,
            amplitude=0.08,
        )

        chord_note3 = synthio.Note(
            frequency=fifth,
            waveform=wave_saw,
            envelope=envelope,
            filter=filter_lpf,
            bend=vibrato_lfo,
            amplitude=0.08,
        )

        synth.press(
            (
                note1,
                note2,
                chord_note2,
                chord_note3,
            )
        )

        print(f"Chord: {root}, {third}, {fifth}")

        time.sleep(CHORD_TIME)

        synth.release(
            (
                note1,
                note2,
                chord_note2,
                chord_note3,
            )
        )

        #
        # Allow the long release to fade.
        #

        time.sleep(1.0)