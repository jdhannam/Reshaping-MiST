# ============================================================
# Tutorial — Comparing Different LFO Waveforms
# ============================================================
#
# What this script demonstrates:
# - How different LFO shapes affect modulation
# - How to modulate a filter with an LFO
# - How waveform shape changes the sound
#
# ============================================================

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
# CREATE A SAWTOOTH WAVEFORM
# ------------------------------------------------------------
#
# A sawtooth wave contains many harmonics.
#
# This makes filter movement much easier to hear.
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
# ADSR ENVELOPE
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.02,
    decay_time=0.10,
    sustain_level=0.7,
    release_time=0.20,
)

# ------------------------------------------------------------
# CREATE CUSTOM LFO WAVEFORMS
# ------------------------------------------------------------
#
# These waveforms are used to control modulation.
#
# ------------------------------------------------------------

# SINE LFO
wave_sine_lfo = np.array(
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

# SQUARE LFO
square_values = []
for i in range(SAMPLE_SIZE)
    if i < SAMPLE_SIZE // 2:
        square_values.append(AMPLITUDE)
    else:
        square_values.append(-AMPLITUDE)

wave_square_lfo = np.array(
    square_values,
    dtype=np.int16,
)

# SAW LFO
wave_saw_lfo = np.array(
    np.linspace(
        -AMPLITUDE,
        AMPLITUDE,
        SAMPLE_SIZE,
        endpoint=False,
    ),
    dtype=np.int16,
)

# ------------------------------------------------------------
# AVAILABLE LFOS
# ------------------------------------------------------------
#
# Uncomment ONE and use it below.
#
# ------------------------------------------------------------

# Default triangle LFO
# used when No waveform is specified.
# Synthio generates a triangle wave automatically.

lfo_triangle = synthio.LFO(
    rate=2.0,
    scale=600,
    offset=1200,
)

# Sine LFO
lfo_sine = synthio.LFO(
    waveform=wave_sine_lfo,
    rate=2.0,
    scale=600,
    offset=1200,
)

# Square LFO
lfo_square = synthio.LFO(
    waveform=wave_square_lfo,
    rate=2.0,
    scale=600,
    offset=1200,
)

# Saw LFO
lfo_saw = synthio.LFO(
    waveform=wave_saw_lfo,
    rate=2.0,
    scale=600,
    offset=1200,
)

# ------------------------------------------------------------
# CHOOSE WHICH LFO TO TEST
# ------------------------------------------------------------
#
# Change this line to:
# lfo_triangle
# lfo_sine
# lfo_square
# lfo_saw
#
# ------------------------------------------------------------

selected_lfo = lfo_triangle

# ------------------------------------------------------------
# FILTER
# ------------------------------------------------------------
#
# The filter cutoff is controlled by the LFO.
#
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=selected_lfo,
    Q=1.2,
)

# ------------------------------------------------------------
# VIBRATO LFO
# ------------------------------------------------------------
#
# A second LFO controlling pitch.
#
# ------------------------------------------------------------

lfo_vibrato = synthio.LFO(
    rate=5.0,
    scale=0.02,
    offset=0,
)

# ------------------------------------------------------------
# CREATE NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    bend=lfo_vibrato,
    amplitude=0.12,
)

# ------------------------------------------------------------
# PATTERN
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

NOTE_TIME = 0.6

# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Triangle
#     Smooth linear rise and fall
#
# Sine
#     Smooth curved rise and fall
#
# Square
#     Instant jumps between two positions
#
# Saw
#     Smooth rise with sudden reset
#
# ------------------------------------------------------------

while True:

    for freq in pattern:
        note.frequency = freq
        synth.press(note)
        print(f"Playing {freq} Hz with selected LFO waveform")
        time.sleep(NOTE_TIME)
        synth.release(note)
        time.sleep(0.05)