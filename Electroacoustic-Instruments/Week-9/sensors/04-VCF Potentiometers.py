# ============================================================
# Tutorial 5 — Real-Time VCF Control with 10K Potentiometers
# ============================================================
#
# This tutorial teaches:
#
# 1. What a Voltage Controlled Filter (VCF) does
# 2. How a Low-Pass Filter changes timbre
# 3. How to control filter cutoff with a potentiometer
# 4. How to control resonance (Q) with a potentiometer
# 5. How filters affect a sawtooth waveform
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
#
# Pico W / Pico 2
#
# GP10 = BCLK
# GP11 = LRCLK / WS
# GP12 = DATA
#
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
# CREATE A SAWTOOTH WAVETABLE
# ------------------------------------------------------------
#
# A saw wave contains many harmonics,
# making filter effects easy to hear.
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256

wave_saw = np.linspace(
    -32000,
    32000,
    SAMPLE_SIZE,
    dtype=np.int16,
)


# ------------------------------------------------------------
# CREATE ADSR ENVELOPE
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.20,
    sustain_level=0.6,
    release_time=0.3,
)


# ------------------------------------------------------------
# POTENTIOMETER SETUP
# ------------------------------------------------------------
#
# Pot 1 -> A0 / GP26 -> Filter Cutoff
# Pot 2 -> A1 / GP27 -> Resonance (Q)
#
# Wiring:
#
# 3.3V ---- Pot ---- GND
#              |
#            Wiper
#              |
#            ADC Pin
#
# ------------------------------------------------------------

pot_cutoff = analogio.AnalogIn(board.GP26)
pot_q = analogio.AnalogIn(board.GP27)


# ------------------------------------------------------------
# FILTER RANGES
# ------------------------------------------------------------
#
# Cutoff:
# Low values = dark sound
# High values = bright sound
#
# Q:
# Controls resonance around the cutoff frequency
#
# ------------------------------------------------------------

MIN_CUTOFF = 100
MAX_CUTOFF = 5000

MIN_Q = 0.7
MAX_Q = 8.0


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def scale_pot(value, minimum, maximum):
    """Convert ADC value into a useful range."""
    return minimum + (value / 65535) * (maximum - minimum)


def exponential_cutoff(value):
    """
    Exponential scaling gives a more
    natural filter sweep.
    """

    position = value / 65535
    return MIN_CUTOFF * ((MAX_CUTOFF / MIN_CUTOFF) ** position)


# ------------------------------------------------------------
# CREATE INITIAL FILTER
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=800,
    Q=1.2,
)


# ------------------------------------------------------------
# CREATE NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    filter=filter_lpf,
    amplitude=0.15,
)


# ------------------------------------------------------------
# DEFINE A SIMPLE SCALE
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

NOTE_TIME = 0.4


# ------------------------------------------------------------
# SMOOTHING
# ------------------------------------------------------------

smooth_cutoff = 800
smooth_q = 1.2
SMOOTHING = 0.1
last_print = 0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

print("VCF Tutorial Running")
print("Pot 1 = Filter Cutoff")
print("Pot 2 = Filter Resonance (Q)")

while True:

    for freq in pattern:

        # ------------------------------------
        # Read potentiometers
        # ------------------------------------

        raw_cutoff = pot_cutoff.value
        raw_q = pot_q.value

        # ------------------------------------
        # Convert to filter values
        # ------------------------------------

        target_cutoff = exponential_cutoff(raw_cutoff)
        target_q = scale_pot(raw_q,MIN_Q,MAX_Q,)

        # ------------------------------------
        # Smooth values
        # ------------------------------------

        smooth_cutoff += (target_cutoff - smooth_cutoff) * SMOOTHING
        smooth_q += (target_q - smooth_q) * SMOOTHING

        # ------------------------------------
        # Create updated filter
        # ------------------------------------

        note.filter = synthio.Biquad(
            synthio.FilterMode.LOW_PASS,
            frequency=smooth_cutoff,
            Q=smooth_q,
        )

        # ------------------------------------
        # Play note
        # ------------------------------------

        note.frequency = freq
        synth.press(note)

        # ------------------------------------
        # Print status
        # ------------------------------------

        if time.monotonic() - last_print > 0.25:

            print(
                "Note:",
                freq,
                "Hz | Cutoff:",
                int(smooth_cutoff),
                "Hz | Q:",
                round(smooth_q, 2),
            )

            last_print = time.monotonic()

        time.sleep(NOTE_TIME)

        synth.release(note)

        time.sleep(0.05)