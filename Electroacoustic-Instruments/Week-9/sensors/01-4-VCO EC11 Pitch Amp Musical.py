# ============================================================
# Tutorial — VCO Control with EC11 Rotary Encoder
# ============================================================
#
# What this script demonstrates:
#
# 1. Reading an EC11 rotary encoder
# 2. Changing synthesizer pitch using the encoder
# 3. Using the encoder push-button to switch modes
# 4. Editing pitch and volume with a single control
# 5. Storing parameter values between mode changes
#
#
# CONTROLS
#
# Rotate Encoder
#     Changes currently selected parameter
#
# Press Encoder Button
#     Switches between:
#
#     PITCH MODE
#     VOLUME MODE
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
# 36 = C2
# 60 = Middle C
# 72 = C5
# 96 = C7
#
# ------------------------------------------------------------

MIN_NOTE = 36
MAX_NOTE = 96

MIN_AMP = 0.00
MAX_AMP = 0.50


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
# EC11 ROTARY ENCODER SETUP
# ------------------------------------------------------------
#
# CLK (A)  -> GP2
# DT  (B)  -> GP3
# SW Button -> GP4
#
# ------------------------------------------------------------

encoder_a = digitalio.DigitalInOut(board.GP2)
encoder_a.switch_to_input(pull=digitalio.Pull.UP)

encoder_b = digitalio.DigitalInOut(board.GP3)
encoder_b.switch_to_input(pull=digitalio.Pull.UP)

encoder_sw = digitalio.DigitalInOut(board.GP4)
encoder_sw.switch_to_input(pull=digitalio.Pull.UP)


# ------------------------------------------------------------
# NOTE NAME LOOKUP
# ------------------------------------------------------------
#
# Used to display note names in the
# Serial Monitor.
#
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
# SYNTH PARAMETERS
# ------------------------------------------------------------
#
# These values persist while switching
# between edit modes.
#
# ------------------------------------------------------------

current_note = 60      # Middle C
current_amp = 0.15
edit_mode = "PITCH"


# ------------------------------------------------------------
# APPLY INITIAL SETTINGS
# ------------------------------------------------------------

note.frequency = synthio.midi_to_hz(current_note)
note.amplitude = current_amp


# ------------------------------------------------------------
# TRACK PREVIOUS STATES
# ------------------------------------------------------------

last_a = encoder_a.value
last_button = encoder_sw.value
last_print = 0


# ------------------------------------------------------------
# STARTUP MESSAGE
# ------------------------------------------------------------

print()
print("EC11 VCO Controller")
print("-------------------")
print("Rotate = Edit Value")
print("Button = Change Mode")
print()
print("Mode: PITCH")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

while True:

    # --------------------------------------------------------
    # BUTTON PRESSED?
    # --------------------------------------------------------
    #
    # Switch between:
    #
    # PITCH MODE
    # VOLUME MODE
    #
    # --------------------------------------------------------

    current_button = encoder_sw.value

    if (
        not current_button
        and last_button
    ):

        if edit_mode == "PITCH":
            edit_mode = "VOLUME"
        else:
            edit_mode = "PITCH"
        print(
            "Mode:",
            edit_mode
        )

        time.sleep(0.15)

    last_button = current_button


    # --------------------------------------------------------
    # READ ENCODER
    # --------------------------------------------------------

    current_a = encoder_a.value

    if current_a != last_a:

        # Falling edge detection
        if not current_a:clockwise = (encoder_b.value!= current_a)

            # --------------------------------------------
            # PITCH EDIT MODE
            # --------------------------------------------

            if edit_mode == "PITCH":
                if clockwise:
                    current_note += 1
                else:
                    current_note -= 1

                current_note = max(MIN_NOTE,min(MAX_NOTE,current_note))
                note.frequency = (synthio.midi_to_hz(current_note))

            # --------------------------------------------
            # VOLUME EDIT MODE
            # --------------------------------------------

            else:

                if clockwise:
                    current_amp += 0.01
                else:
                    current_amp -= 0.01

                current_amp = max(MIN_AMP,min(MAX_AMP,current_amp))
                note.amplitude = (current_amp)

    last_a = current_a


    # --------------------------------------------------------
    # SERIAL MONITOR OUTPUT
    # --------------------------------------------------------

    if time.monotonic() - last_print > 0.25:

        print(
            "Mode:",
            edit_mode,
            "| Note:",
            midi_name(
                current_note
            ),
            "| Freq:",
            int(
                note.frequency
            ),
            "Hz",
            "| Amp:",
            round(
                current_amp,
                2
            )
        )

        last_print = time.monotonic()

    time.sleep(0.001)