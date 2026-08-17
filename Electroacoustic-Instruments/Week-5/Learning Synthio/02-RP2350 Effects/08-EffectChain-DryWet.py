# ============================================================
# Tutorial — Delay + Reverb with Dry/Wet Mix
# ============================================================
#
# This tutorial teaches:
#
# - How to chain multiple effects (delay → reverb)
# - How dry/wet mix works for each effect
# - How delay and reverb interact
# - How to listen for differences between dry, wet, and blended signals
#
# ============================================================
#
# IMPORTANT
#
# Requires:
# - RP2350-based board
# - CircuitPython 10+
# - audiodelays module
# - audiofreeverb module
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import audiobusio
import synthio
import audiodelays
import audiofreeverb
import ulab.numpy as np
import time


# ------------------------------------------------------------
# AUDIO SETUP
# ------------------------------------------------------------
#
# Signal Chain:
#
# Synth  →  Delay  →  Reverb  →  DAC
#
# ------------------------------------------------------------

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,
    word_select=board.GP28,
    data=board.GP26,
)


# ------------------------------------------------------------
# CREATE THE SYNTHESIZER
# ------------------------------------------------------------

SAMPLE_RATE = 22050

synth = synthio.Synthesizer(
    sample_rate=SAMPLE_RATE,
    channel_count=1,
)


# ------------------------------------------------------------
# DRY/WET MIX SETTINGS
# ------------------------------------------------------------
#
# Students should uncomment ONE setting at a time
# to hear how dry/wet mix affects delay and reverb.
#
# ------------------------------------------------------------

# --- Delay Mix Options ---
# delay_mix = 0.0   # 100% dry (no echo)
# delay_mix = 1.0   # 100% wet (only echoes)
delay_mix = 0.4     # blended (recommended starting point)

# --- Reverb Mix Options ---
# reverb_mix = 0.0  # 100% dry (no reverb)
# reverb_mix = 1.0  # 100% wet (only reverb tail)
reverb_mix = 0.5    # blended (recommended starting point)


# ------------------------------------------------------------
# CREATE THE DELAY EFFECT
# ------------------------------------------------------------
#
# delay_ms
#     Time between repeats
#
# decay
#     How quickly echoes fade
#
# mix
#     Dry/wet balance for delay
#
# ------------------------------------------------------------

delay = audiodelays.Echo(
    mix=delay_mix,
    delay_ms=250,
    decay=0.6,
    max_delay_ms=500,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CREATE THE REVERB EFFECT
# ------------------------------------------------------------
#
# roomsize
#     Size of virtual room (0.0 small, 1.0 huge)
#
# damp
#     High-frequency absorption
#
# mix
#     Dry/wet balance for reverb
#
# ------------------------------------------------------------

reverb = audiofreeverb.Freeverb(
    roomsize=0.7,
    damp=0.3,
    mix=reverb_mix,
    buffer_size=1024,
    channel_count=1,
    sample_rate=SAMPLE_RATE,
)


# ------------------------------------------------------------
# CONNECT THE SIGNAL CHAIN
# ------------------------------------------------------------
#
# Synth → Delay → Reverb → DAC
#
# ------------------------------------------------------------

delay.play(synth)
reverb.play(delay)
audio.play(reverb)


# ------------------------------------------------------------
# CREATE A WAVETABLE
# ------------------------------------------------------------

SAMPLE_SIZE = 256
AMPLITUDE = 32000

wave_saw = np.array(
    np.linspace(-AMPLITUDE, AMPLITUDE, SAMPLE_SIZE, endpoint=False),
    dtype=np.int16,
)


# ------------------------------------------------------------
# ADSR ENVELOPE
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=0.05,
    decay_time=0.20,
    sustain_level=0.60,
    release_time=0.50,
)


# ------------------------------------------------------------
# CREATE A NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=220,
    waveform=wave_saw,
    envelope=envelope,
    amplitude=0.15,
)


# ------------------------------------------------------------
# PATTERN OF NOTES
# ------------------------------------------------------------

pattern = [
    220, 247, 262, 294,
    330, 349, 392, 440,
]

NOTE_TIME = 0.5


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
#
# Listen for:
#
# Delay:
#   - Short repeats
#   - Echo spacing
#   - Echo decay
#
# Reverb:
#   - Room ambience
#   - Tail length
#   - High-frequency damping
#
# DRY/WET MIX:
#   - dry only → clean notes
#   - wet only → only echoes/reverb
#   - blended → musical effect
#
# ------------------------------------------------------------

while True:

    for freq in pattern:

        note.frequency = freq
        synth.press(note)

        print(
            f"Playing {freq} Hz — "
            f"Delay mix={delay_mix}, Reverb mix={reverb_mix}"
        )

        time.sleep(NOTE_TIME)
        synth.release(note)

        # Allow delay + reverb tails to be heard
        time.sleep(0.40)
