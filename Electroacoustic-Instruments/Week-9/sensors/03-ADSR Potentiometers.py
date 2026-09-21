# ============================================================
# Tutorial 3B — Controlling ADSR with 10K Potentiometers
# ============================================================
#
# This tutorial teaches:
#
# 1. What ADSR envelopes are
# 2. How to control Attack with a potentiometer
# 3. How to control Release with a potentiometer
# 4. How envelope settings change the shape of notes
#
# Pot 1 = Attack
# Pot 2 = Release
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
import analogio
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

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# CREATE SINE WAVE
# ------------------------------------------------------------
#
# A sine wave lets students focus on
# hearing the envelope shape.
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
# POTENTIOMETER SETUP
# ------------------------------------------------------------
#
# Pot 1 → A0 / GP26 → Attack
# Pot 2 → A1 / GP27 → Release
#
# ------------------------------------------------------------

pot_attack = analogio.AnalogIn(board.GP26)
pot_release = analogio.AnalogIn(board.GP27)


# ------------------------------------------------------------
# ENVELOPE RANGES
# ------------------------------------------------------------
#
# Attack:
# 0.01s = sharp note
# 2.00s = slow fade in
#
# Release:
# 0.01s = sudden stop
# 3.00s = long fade out
#
# ------------------------------------------------------------

MIN_ATTACK = 0.01
MAX_ATTACK = 2.0

MIN_RELEASE = 0.01
MAX_RELEASE = 3.0


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def scale_pot(value, minimum, maximum):
    return minimum + (value / 65535) * (maximum - minimum)


# ------------------------------------------------------------
# CREATE INITIAL ENVELOPE
# ------------------------------------------------------------

attack_time = 0.05
release_time = 0.30

envelope = synthio.Envelope(
    attack_time=attack_time,
    decay_time=0.20,
    sustain_level=0.60,
    release_time=release_time,
)


# ------------------------------------------------------------
# CREATE NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    envelope=envelope,
    amplitude=0.15,
)


# ------------------------------------------------------------
# PATTERN
# ------------------------------------------------------------

pattern = [
    220,
    247,
    262,
    294,
    330,
    349,
    392,
    440,
]

NOTE_TIME = 0.5


# ------------------------------------------------------------
# SMOOTHING
# ------------------------------------------------------------

smooth_attack = attack_time
smooth_release = release_time
SMOOTHING = 0.1
last_print = 0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

print("ADSR Control Tutorial")
print("Pot 1 = Attack")
print("Pot 2 = Release")

while True:

    for freq in pattern:

        # ------------------------------------
        # Read potentiometers
        # ------------------------------------

        raw_attack = pot_attack.value
        raw_release = pot_release.value

        # ------------------------------------
        # Convert to envelope values
        # ------------------------------------

        target_attack = scale_pot(
            raw_attack,
            MIN_ATTACK,
            MAX_ATTACK,
        )

        target_release = scale_pot(
            raw_release,
            MIN_RELEASE,
            MAX_RELEASE,
        )

        # ------------------------------------
        # Smooth values
        # 
        # += is shorthand for x = x + 1
        # Take the current value of x, add 1 to it, and store the result back in x.
        # ------------------------------------

        smooth_attack += (target_attack - smooth_attack) * SMOOTHING
        smooth_release += (target_release - smooth_release) * SMOOTHING

        # ------------------------------------
        # Create updated envelope
        # ------------------------------------

        note.envelope = synthio.Envelope(
            attack_time=smooth_attack,
            decay_time=0.20,
            sustain_level=0.60,
            release_time=smooth_release,
        )

        # ------------------------------------
        # Set note frequency
        # ------------------------------------

        note.frequency = freq

        # ------------------------------------
        # Trigger envelope
        # ------------------------------------

        synth.press(note)

        # ------------------------------------
        # Display values
        # ------------------------------------

        if time.monotonic() - last_print > 0.25:

            print(
                "Note:",
                freq,
                "Hz | Attack:",
                round(smooth_attack, 2),
                "s | Release:",
                round(smooth_release, 2),
                "s",
            )

            last_print = time.monotonic()

        time.sleep(NOTE_TIME)

        synth.release(note)

        time.sleep(0.05)