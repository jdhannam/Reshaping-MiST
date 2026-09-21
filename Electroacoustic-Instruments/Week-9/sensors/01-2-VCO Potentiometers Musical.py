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
# 5. Using musical note scaling for natural pitch control
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
# I2S Pins:
# GP17 = BCLK
# GP18 = LRCLK / WS SCL
# GP16 = DATA SDA
#
# ADC Pins:
# GP26 = A0
# GP27 = A1
# GP28 = A2
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
# MUSICAL PITCH RANGE
# ------------------------------------------------------------
#
# MIDI Note Numbers
#
# 36 = C2
# 60 = Middle C
# 72 = C5
# 96 = C7
#
# ------------------------------------------------------------

MIN_NOTE = 36
MAX_NOTE = 96

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
print("Pot 1 = Pitch")
print("Pot 2 = Amplitude")


# ------------------------------------------------------------
# POTENTIOMETER SETUP
# ------------------------------------------------------------
#
# Pot 1 -> A0 / GP26 -> Pitch
# Pot 2 -> A1 / GP27 -> Amplitude
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

pot_pitch = analogio.AnalogIn(board.A0)
pot_amp = analogio.AnalogIn(board.A1)


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def scale_pot(value, minimum, maximum):
    """
    Convert ADC value (0–65535)
    into a chosen range.
    """

    return minimum + (value / 65535) * (maximum - minimum)


def pot_to_frequency(value):
    """
    Convert potentiometer position
    into a musical note.

    This produces an exponential pitch response,
    which sounds natural to human hearing.
    """

    position = value / 65535
    midi_note = (MIN_NOTE + position * (MAX_NOTE - MIN_NOTE))

    return synthio.midi_to_hz(midi_note)


# ------------------------------------------------------------
# SMOOTHING
# ------------------------------------------------------------
#
# Small smoothing helps eliminate
# noisy ADC readings.
#
# ------------------------------------------------------------

smooth_freq = 220
smooth_amp = 0.1
SMOOTHING = 0.1
last_print = 0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

while True:

    # ----------------------------------------
    # Read potentiometers
    # ----------------------------------------

    raw_pitch = pot_pitch.value
    raw_amp = pot_amp.value

    # ----------------------------------------
    # Convert to synth values
    # ----------------------------------------

    target_freq = pot_to_frequency(raw_pitch)

    target_amp = scale_pot(
        raw_amp,
        MIN_AMP,
        MAX_AMP,
    )

    # ----------------------------------------
    # Simple low-pass smoothing
    # ----------------------------------------

    smooth_freq += (target_freq - smooth_freq) * SMOOTHING
    smooth_amp += (target_amp - smooth_amp) * SMOOTHING

    # ----------------------------------------
    # Update oscillator
    # ----------------------------------------

    note.frequency = smooth_freq
    note.amplitude = smooth_amp

    # ----------------------------------------
    # Serial monitor output
    # ----------------------------------------

    if time.monotonic() - last_print > 0.25:

        print(
            "Freq:",
            int(smooth_freq),
            "Hz",
            "Amp:",
            round(smooth_amp, 2),
        )

        last_print = time.monotonic()

    time.sleep(0.01)