# ============================================================
# Tutorial 7 — Touch Controlled VCO → VCF → VCA Synth
# ============================================================
#
# Signal Flow
#
#    VCO → VCF → VCA → Output
#
# MPR121 Touch Pads
#
# Touch 0 = VCO Mode
# Touch 1 = VCF Mode
# Touch 2 = VCA Mode
# Touch 3 = Play Note
#
# Pot A (A0 / GP26)
# Pot B (A1 / GP27)
#
# VCO Mode
# ----------
# Pot A = Pitch
# Pot B = Oscillator Level
#
# VCF Mode
# ----------
# Pot A = Filter Cutoff
# Pot B = Resonance (Q)
#
# VCA Mode
# ----------
# Pot A = Attack
# Pot B = Release
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import board
import busio
import audiobusio
import audiomixer
import synthio
import analogio
import adafruit_mpr121
import ulab.numpy as np
import time


# ------------------------------------------------------------
# MPR121 I2C SETUP
# ------------------------------------------------------------

i2c = busio.I2C(board.GP9, board.GP8)
mpr121 = adafruit_mpr121.MPR121(i2c)


# ------------------------------------------------------------
# I2S AUDIO OUTPUT
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

pot_a = analogio.AnalogIn(board.GP26)
pot_b = analogio.AnalogIn(board.GP27)


# ------------------------------------------------------------
# CREATE A SAW WAVE
# ------------------------------------------------------------
#
# Saw waves contain many harmonics.
# This makes filter effects easier to hear.
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
# HELPER FUNCTIONS
# ------------------------------------------------------------

def scale_pot(value, minimum, maximum):
    return minimum + (value / 65535) * (maximum - minimum)


def pot_to_frequency(value):
    """
    Exponential pitch scaling using MIDI notes.
    """
    position = value / 65535
    midi_note = (36 +position * (96 - 36))

    return synthio.midi_to_hz(midi_note)


def pot_to_cutoff(value):
    """
    Exponential filter sweep.
    """
    position = value / 65535
    
    return 100 * ((5000 / 100) ** position)


# ------------------------------------------------------------
# INITIAL PARAMETERS
# ------------------------------------------------------------

frequency = 220
osc_level = 0.20

cutoff = 1000
resonance = 1.2

attack = 0.05
release = 0.30

mode = "VCO"


# ------------------------------------------------------------
# CREATE FILTER
# ------------------------------------------------------------

filter_lpf = synthio.Biquad(
    synthio.FilterMode.LOW_PASS,
    frequency=cutoff,
    Q=resonance,
)


# ------------------------------------------------------------
# CREATE ENVELOPE
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=attack,
    decay_time=0.20,
    sustain_level=0.70,
    release_time=release,
)


# ------------------------------------------------------------
# CREATE NOTE
# ------------------------------------------------------------

note = synthio.Note(
    frequency=frequency,
    waveform=wave_saw,
    amplitude=osc_level,
    filter=filter_lpf,
    envelope=envelope,
)


# ------------------------------------------------------------
# STATE VARIABLES
# ------------------------------------------------------------

note_is_playing = False
last_print = 0


# ------------------------------------------------------------
# STARTUP MESSAGE
# ------------------------------------------------------------

print()
print("Touch Controlled Synth")
print("----------------------")
print("Touch 0 = VCO")
print("Touch 1 = VCF")
print("Touch 2 = VCA")
print("Touch 3 = PLAY NOTE")
print()


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

while True:

    # --------------------------------------------------------
    # MODE SELECTION
    # --------------------------------------------------------

    if mpr121[0].value:

        if mode != "VCO":
            mode = "VCO"
            print("Mode = VCO")

        time.sleep(0.2)

    elif mpr121[1].value:

        if mode != "VCF":
            mode = "VCF"
            print("Mode = VCF")

        time.sleep(0.2)

    elif mpr121[2].value:

        if mode != "VCA":
            mode = "VCA"
            print("Mode = VCA")

        time.sleep(0.2)


    # --------------------------------------------------------
    # READ POTS
    # --------------------------------------------------------

    raw_a = pot_a.value
    raw_b = pot_b.value


    # --------------------------------------------------------
    # VCO MODE
    # --------------------------------------------------------

    if mode == "VCO":

        frequency = pot_to_frequency(raw_a)
        osc_level = scale_pot(raw_b,0.02,0.50,)


    # --------------------------------------------------------
    # VCF MODE
    # --------------------------------------------------------

    elif mode == "VCF":
        cutoff = pot_to_cutoff(raw_a)
        resonance = scale_pot(raw_b,0.70,8.00,)


    # --------------------------------------------------------
    # VCA MODE
    # --------------------------------------------------------

    elif mode == "VCA":
        attack = scale_pot(raw_a,0.01,2.00,)
        release = scale_pot(raw_b,0.01,3.00,)


    # --------------------------------------------------------
    # UPDATE SYNTH COMPONENTS
    # --------------------------------------------------------

    note.frequency = frequency
    note.amplitude = osc_level

    note.filter = synthio.Biquad(
        synthio.FilterMode.LOW_PASS,
        frequency=cutoff,
        Q=resonance,
    )

    note.envelope = synthio.Envelope(
        attack_time=attack,
        decay_time=0.20,
        sustain_level=0.70,
        release_time=release,
    )


    # --------------------------------------------------------
    # TOUCH PAD 3 = PLAY NOTE
    # --------------------------------------------------------

    if mpr121[3].value:

        if not note_is_playing:
            synth.press(note)
            note_is_playing = True

    else:

        if note_is_playing:
            synth.release(note)
            note_is_playing = False


    # --------------------------------------------------------
    # STATUS OUTPUT
    # --------------------------------------------------------

    if time.monotonic() - last_print > 0.5:

        print(
            "Mode:", mode,
            "| Freq:", int(frequency),
            "| Level:", round(osc_level, 2),
            "| Cutoff:", int(cutoff),
            "| Q:", round(resonance, 2),
            "| Attack:", round(attack, 2),
            "| Release:", round(release, 2),
        )

        last_print = time.monotonic()

    time.sleep(0.01)