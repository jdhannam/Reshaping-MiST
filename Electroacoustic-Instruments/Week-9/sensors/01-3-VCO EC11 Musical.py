# ============================================================
# Tutorial — VCO Control with EC11 Rotary Encoder
# ============================================================
#
# What this script demonstrates:
#
# 1. Reading an EC11 rotary encoder
# 2. Using encoder movement to select notes
# 3. Converting MIDI notes into frequencies
# 4. Controlling SynthIO pitch in real time
#
# The encoder button is not used in this tutorial.
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
import digitalio
import time


# ------------------------------------------------------------
# AUDIO SETUP (I2S)
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP17,
    word_select=board.GP18,
    data=board.GP16,
)


# ------------------------------------------------------------
# MIXER SETUP
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
# CREATE SYNTHESIZER
# ------------------------------------------------------------

synth = synthio.Synthesizer(
    sample_rate=22050
)


# ------------------------------------------------------------
# CREATE SINE WAVE WAVETABLE
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
# MIDI NOTE RANGE
# ------------------------------------------------------------
#
# MIDI 36 = C2
# MIDI 60 = Middle C
# MIDI 72 = C5
# MIDI 96 = C7
#
# ------------------------------------------------------------

MIN_NOTE = 36
MAX_NOTE = 96


# ------------------------------------------------------------
# CREATE NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    amplitude=0.15,
)

mixer.voice[0].play(synth)

synth.press(note)


# ------------------------------------------------------------
# EC11 ROTARY ENCODER
# ------------------------------------------------------------
#
# EC11 A Output -> GP2
# EC11 B Output -> GP3
#
# Push Button not used
#
# ------------------------------------------------------------

encoder_a = digitalio.DigitalInOut(board.GP2)
encoder_a.switch_to_input(pull=digitalio.Pull.UP)

encoder_b = digitalio.DigitalInOut(board.GP3)
encoder_b.switch_to_input(pull=digitalio.Pull.UP)


# ------------------------------------------------------------
# NOTE TRACKING
# ------------------------------------------------------------
#
# Start at Middle C
#
# ------------------------------------------------------------

current_note = 60

note.frequency = synthio.midi_to_hz(current_note)


# ------------------------------------------------------------
# NOTE NAMES
# ------------------------------------------------------------

NOTE_NAMES = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]


def midi_name(midi_note):

    octave = (midi_note // 12) - 1
    note_name = NOTE_NAMES[midi_note % 12]

    return note_name + str(octave)


# ------------------------------------------------------------
# ENCODER STATE
# ------------------------------------------------------------

last_a = encoder_a.value

last_print = 0

print("VCO Running")
print("Rotate encoder to change pitch")


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

while True:

    current_a = encoder_a.value

    # ----------------------------------------
    # DETECT ROTATION
    # ----------------------------------------

    if current_a != last_a:

        # Falling edge
        if not current_a:
            if encoder_b.value != current_a:
                # Clockwise
                current_note += 1

            else:
                # Counter-clockwise
                current_note -= 1

            # Keep within range
            current_note = max(MIN_NOTE,min(MAX_NOTE,current_note))
            note.frequency = (synthio.midi_to_hz(current_note))

    last_a = current_a


    # ----------------------------------------
    # SERIAL OUTPUT
    # ----------------------------------------

    if time.monotonic() - last_print > 0.25:

        print(
            "Note:",
            midi_name(
                current_note
            ),
            "| Frequency:",
            int(
                note.frequency
            ),
            "Hz"
        )

        last_print = time.monotonic()

    time.sleep(0.001)