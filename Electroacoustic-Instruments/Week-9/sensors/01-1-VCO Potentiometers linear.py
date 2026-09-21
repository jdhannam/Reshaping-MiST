# ============================================================
# Tutorial — VCO Control with 10k Potentiometers
# ============================================================
#
# What this script demonstrates:
#
# 1. Reading analog values from 10K potentiometers
# 2. Mapping potentiometers to synthesizer controls
# 3. Controlling oscillator pitch and amplitude
# 4. Smoothing sensor data for stable operation
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
# These pins are examples.
# Use any free DIGITAL pins that match your hardware.
#
# IMPORTANT:
# Keep ADC pins free for sensors and potentiometers.
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


# ------------------------------------------------------------
# WAVETABLE SETTINGS
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
# SYNTH CONTROL RANGES
# ------------------------------------------------------------

MIN_FREQ = 50
MAX_FREQ = 2000

MIN_AMP = 0.0
MAX_AMP = 0.5


# ------------------------------------------------------------
# CREATE NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    amplitude=0.1,
)

mixer.voice[0].play(synth)
synth.press(note)

print("VCO running.")


# ------------------------------------------------------------
# POTENTIOMETER SETUP
# ------------------------------------------------------------
#
# ADC PINS
#
# Pot 1 -> A0 / GP26
# Pot 2 -> A1 / GP27
#
# One side  -> 3.3V
# Other side -> GND
# Wiper -> ADC pin
#
# ------------------------------------------------------------

pot_freq = analogio.AnalogIn(board.GP26)
pot_amp = analogio.AnalogIn(board.GP27)


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def scale_pot(value, minimum, maximum):
    """Convert ADC value to a useful range."""
    return minimum + (value / 65535) * (maximum - minimum)


def exponential_pitch(value):
    """
    More natural pitch response.
    Human hearing is logarithmic.
    """

    position = value / 65535

    return MIN_FREQ * ((MAX_FREQ / MIN_FREQ) ** position)


# ------------------------------------------------------------
# SMOOTHING VARIABLES
# ------------------------------------------------------------

smooth_freq = 220
smooth_amp = 0.1
SMOOTHING = 0.1
last_print = 0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

while True:

    # Read potentiometers

    raw_freq = pot_freq.value
    raw_amp = pot_amp.value

    # Convert to synth values

    target_freq = exponential_pitch(raw_freq)

    target_amp = scale_pot(
        raw_amp,
        MIN_AMP,
        MAX_AMP,
    )

    # Simple low-pass smoothing

    smooth_freq += (target_freq - smooth_freq) * SMOOTHING
    smooth_amp += (target_amp - smooth_amp) * SMOOTHING

    # Update oscillator

    note.frequency = smooth_freq
    note.amplitude = smooth_amp

    # Print 4 times per second

    if time.monotonic() - last_print > 0.25:

        print(
            "Freq:",
            int(smooth_freq),
            "Hz   Amp:",
            round(smooth_amp, 2),
        )

        last_print = time.monotonic()

    time.sleep(0.01)