# ============================================================
# Tutorial 1.1 — Temperature Controlled VCO
# ============================================================
#
# What this script demonstrates:
#
# 1. How to read the Pico's onboard temperature sensor
# 2. How to convert temperature into a control signal
# 3. How to control a Synthio VCO using sensor data
# 4. How sensor values can be mapped to musical pitch
#
# In Tutorial 1:
#
#     Frequency = 220 Hz
#
# The oscillator frequency never changes.
#
# In this script:
#
#     Temperature Sensor
#              │
#              ▼
#      Frequency Calculation
#              │
#              ▼
#            Synthio
#
# As the temperature changes, the oscillator pitch changes.
#
# This is the first example of a sensor controlling
# a synthesizer parameter.
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
#
# These modules provide access to:
#
# - Pico pin definitions
# - Audio output hardware
# - Audio mixing
# - Synthio synthesis engine
# - Mathematics for creating waveforms
# - Temperature sensor access
# - Timing functions
#
# ------------------------------------------------------------

import board                 # Pico pin definitions
import microcontroller       # Internal temperature sensor
import audiobusio            # I2S digital audio output
import audiomixer            # Audio mixer
import synthio               # Synthesizer engine
import ulab.numpy as np      # Numerical calculations
import time                  # Delays and timing


# ------------------------------------------------------------
# AUDIO OUTPUT SETUP
# ------------------------------------------------------------
#
# I2S sends digital audio data to an external DAC.
#
# Change these pins if your hardware uses different wiring.
#
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,
    word_select=board.GP28,
    data=board.GP26,
)


# ------------------------------------------------------------
# AUDIO MIXER
# ------------------------------------------------------------
#
# The mixer combines audio sources before sending
# them to the DAC.
#
# voice_count
#     Number of sound sources connected.
#
# sample_rate
#     Number of samples generated each second.
#
# ------------------------------------------------------------

mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)

# Send mixer output to the DAC.

audio.play(mixer)


# ------------------------------------------------------------
# CREATE THE SYNTHESIZER
# ------------------------------------------------------------
#
# The synthesizer generates audio from Notes.
#
# ------------------------------------------------------------

synth = synthio.Synthesizer(
    sample_rate=22050
)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------
#
# A wavetable contains one cycle of a waveform.
#
# Synthio repeatedly loops through the waveform
# to produce a continuous sound.
#
# This example uses a sine wave.
#
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000


# Generate one cycle of a sine wave.

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
# CREATE A NOTE
# ------------------------------------------------------------
#
# The Note defines:
#
# - Frequency (pitch)
# - Waveform (tone colour)
# - Amplitude (volume)
#
# We start at 220 Hz.
#
# The frequency will be updated continuously
# by the temperature sensor.
#
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_sine,
    amplitude=0.1,
)


# ------------------------------------------------------------
# CONNECT THE SYNTH TO THE MIXER
# ------------------------------------------------------------

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# START THE NOTE
# ------------------------------------------------------------
#
# The note begins playing immediately.
#
# We do NOT stop and restart the note.
#
# Instead we change:
#
#     note.frequency
#
# while the note is playing.
#
# ------------------------------------------------------------

synth.press(note)


# ------------------------------------------------------------
# TEMPERATURE TO FREQUENCY MAPPING
# ------------------------------------------------------------
#
# Raw temperature values are measured in degrees Celsius.
#
# Musical pitch is measured in Hertz.
#
# We therefore need to convert one range
# into another.
#
# Example:
#
# 20 °C  →  220 Hz
# 35 °C  →  880 Hz
#
# This process is called "mapping".
#
# ------------------------------------------------------------

MIN_TEMP = 20
MAX_TEMP = 35

MIN_FREQ = 220
MAX_FREQ = 880


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Continuously:
#
# 1. Read temperature
# 2. Convert temperature to frequency
# 3. Update oscillator frequency
# 4. Print values for debugging
#
# Try:
#
# - Touching the RP2040 chip
# - Holding your finger on the board
# - Cooling the board with airflow
#
# Listen for pitch changes.
#
# ------------------------------------------------------------

while True:

    # --------------------------------------------------------
    # READ TEMPERATURE
    # --------------------------------------------------------
    #
    # The Pico contains an internal temperature sensor.
    #
    # CircuitPython allows us to access it using:
    #
    #     microcontroller.cpu.temperature
    #
    # --------------------------------------------------------

    temperature = microcontroller.cpu.temperature


    # --------------------------------------------------------
    # LIMIT THE TEMPERATURE RANGE
    # --------------------------------------------------------
    #
    # Prevent extreme values causing frequencies
    # outside our intended range.
    #
    # --------------------------------------------------------

    if temperature < MIN_TEMP:
        temperature = MIN_TEMP

    if temperature > MAX_TEMP:
        temperature = MAX_TEMP


    # --------------------------------------------------------
    # MAP TEMPERATURE TO FREQUENCY
    # --------------------------------------------------------
    #
    # Formula:
    #
    # output = min_output + ((input - min_input) / (max_input - min_input)) × output_range
    #
    # --------------------------------------------------------

    frequency = (
        MIN_FREQ
        + (
            (temperature - MIN_TEMP)
            / (MAX_TEMP - MIN_TEMP)
        )
        * (MAX_FREQ - MIN_FREQ)
    )


    # --------------------------------------------------------
    # UPDATE THE VCO FREQUENCY
    # --------------------------------------------------------
    #
    # This is the important line.
    #
    # The sensor controls the oscillator pitch.
    #
    # --------------------------------------------------------

    note.frequency = frequency


    # --------------------------------------------------------
    # DEBUG OUTPUT
    # --------------------------------------------------------
    #
    # Print values to the serial monitor so
    # students can see the relationship between
    # temperature and frequency.
    #
    # --------------------------------------------------------

    print(
        "Temperature:",
        round(temperature, 1),
        "°C",
        "| Frequency:",
        round(frequency, 1),
        "Hz"
    )


    # --------------------------------------------------------
    # SHORT DELAY
    # --------------------------------------------------------
    #
    # Reduces CPU usage and prevents the serial
    # monitor updating too quickly.
    #
    # --------------------------------------------------------

    time.sleep(0.1)