# ============================================================
# Tutorial — LFO Rate and Depth Control with 10K Pots
# ============================================================
#
# What this tutorial teaches:
#
# 1. What an LFO is
# 2. How an LFO modulates a filter
# 3. How LFO rate affects modulation speed
# 4. How LFO depth affects modulation amount
# 5. How to control an LFO using potentiometers
#
# Pot 1 = LFO Rate
# Pot 2 = LFO Depth
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import audiobusio
import audiomixer
import synthio
import analogio
import ulab.numpy as np
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
# MIXER
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
# SYNTH
# ------------------------------------------------------------

synth = synthio.Synthesizer(
    sample_rate=22050
)

mixer.voice[0].play(synth)


# ------------------------------------------------------------
# POTENTIOMETERS
# ------------------------------------------------------------
#
# Pot 1 -> A0 / GP26 -> LFO Rate
# Pot 2 -> A1 / GP27 -> LFO Depth
#
# ------------------------------------------------------------

pot_rate = analogio.AnalogIn(board.GP26)
pot_depth = analogio.AnalogIn(board.GP27)


# ------------------------------------------------------------
# CREATE SAW WAVEFORM
# ------------------------------------------------------------
#
# Saw waves contain many harmonics.
# This makes filter modulation easier to hear.
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
# ENVELOPE
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.02,
    decay_time=0.10,
    sustain_level=0.7,
    release_time=0.20,
)


# ------------------------------------------------------------
# LFO LIMITS
# ------------------------------------------------------------
#
# Rate:
# 0.1 Hz = very slow
# 10 Hz  = very fast
#
# Depth:
# 100 Hz cutoff movement
# up to
# 3000 Hz cutoff movement
#
# ------------------------------------------------------------

MIN_RATE = 0.1
MAX_RATE = 10.0

MIN_DEPTH = 100
MAX_DEPTH = 3000


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def scale_pot(value, minimum, maximum):
    return minimum + (value / 65535) * (maximum - minimum)


# ------------------------------------------------------------
# CREATE LFO
# ------------------------------------------------------------
#
# The LFO controls filter cutoff.
#
# offset = centre cutoff frequency
# scale  = modulation depth
#
# ------------------------------------------------------------

filter_lfo = synthio.LFO(
    rate=2.0,
    scale=600,
    offset=1200,
)


# ------------------------------------------------------------
# FILTER
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=filter_lfo,
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
    amplitude=0.12,
)


# ------------------------------------------------------------
# START NOTE
# ------------------------------------------------------------

synth.press(note)


# ------------------------------------------------------------
# SMOOTHING
# ------------------------------------------------------------

smooth_rate = 2.0
smooth_depth = 600

SMOOTHING = 0.1
last_print = 0


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

print("LFO Tutorial Running")
print("Pot 1 = LFO Rate")
print("Pot 2 = LFO Depth")

while True:

    # --------------------------------------------------------
    # READ POTENTIOMETERS
    # --------------------------------------------------------

    raw_rate = pot_rate.value
    raw_depth = pot_depth.value

    # --------------------------------------------------------
    # CONVERT TO LFO VALUES
    # --------------------------------------------------------

    target_rate = scale_pot(raw_rate,MIN_RATE,MAX_RATE,)
    target_depth = scale_pot(raw_depth,MIN_DEPTH,MAX_DEPTH,)

    # --------------------------------------------------------
    # SMOOTH VALUES
    # --------------------------------------------------------

    smooth_rate += (target_rate - smooth_rate) * SMOOTHING
    smooth_depth += (target_depth - smooth_depth) * SMOOTHING

    # --------------------------------------------------------
    # UPDATE LFO
    # --------------------------------------------------------

    filter_lfo.rate = smooth_rate
    filter_lfo.scale = smooth_depth

    # --------------------------------------------------------
    # SERIAL MONITOR
    # --------------------------------------------------------

    if time.monotonic() - last_print > 0.25:

        print(
            "Rate:",
            round(smooth_rate, 2),
            "Hz | Depth:",
            int(smooth_depth)
        )

        last_print = time.monotonic()

    time.sleep(0.01)