# ============================================================
# WAVETABLE DRONE SYNTH
# ============================================================
#
# WHAT THIS PROGRAM DOES
# ----------------------
# It plays a slowly evolving drone made of THREE oscillators.
# Each oscillator uses a "wavetable": a collection of different
# waveform shapes (called FRAMES). Instead of playing just one
# shape, each oscillator slowly glides through the frames, so
# the tone gradually changes character over time.
#
# HOW IT WORKS (THE BIG IDEA)
# ---------------------------
#   1. Load WAV files from the /sounds folder and cut them into
#      frames of 256 samples each.
#   2. Create three notes, each playing its own copy of a waveform.
#   3. Use slow LFOs (Low Frequency Oscillators) to pick a
#      POSITION in the wavetable for each note.
#   4. Blend the two frames nearest that position to make a smooth
#      waveform, and give it to the note.
#   5. Repeat forever, so the sound keeps morphing.
#
# FILES YOU NEED ON THE PICO
# --------------------------
#   CIRCUITPY/
#     |-- code.py          (this file)
#     |-- sounds/          (folder of WAV files)
#           |-- wave1.wav
#           |-- wave2.wav
#           |-- ...
#
# WAV FILE REQUIREMENTS
# ---------------------
#   * 16-bit
#   * Mono (NOT stereo)
#   * PCM format (the normal, uncompressed kind)
#   Audacity can export files in this format.
#
# HARDWARE
# --------
#   An I2S DAC (for example PCM5102 or MAX98357) wired to:
#       GP17 -> bit clock (BCK)
#       GP18 -> word select (LCK / LRCK)
#       GP16 -> data (DIN)
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# An import loads a library (a module) so we can use its tools.
# ------------------------------------------------------------

import board           # names for the Pico's pins (board.GP16 etc.)
import audiobusio      # sends digital audio out through I2S pins
import audiomixer      # lets us control audio volume and routing
import synthio         # the synthesizer engine: notes, envelopes, LFOs
import ulab.numpy as np  # fast number crunching for lists of samples
import os              # lets us look inside folders (to find WAV files)
import time            # lets us pause the program (time.sleep)


# ------------------------------------------------------------
# AUDIO SETUP
# This block tells the Pico how to get sound out of the
# synthesizer and into your speaker or headphones.
#
# The chain looks like this:
#       synth  ->  mixer  ->  audio (I2S pins)  ->  DAC  ->  speaker
#
# The sample rate is how many audio samples are made each second.
# A higher number sounds better but makes the Pico work harder.
# 22050 is a good, safe choice for the Raspberry Pi Pico (RP2040).
# ------------------------------------------------------------


SAMPLE_RATE = 22050

# Create the I2S output, using the three pins from the wiring list.
audio = audiobusio.I2SOut(
    bit_clock=board.GP17,
    word_select=board.GP18,
    data=board.GP16,
)

# Create a mixer. It sits between the synth and the output and
# gives us a convenient place to control levels.
mixer = audiomixer.Mixer(
    voice_count=1,              # one input channel (our synth)
    sample_rate=SAMPLE_RATE,    # must match the synth's sample rate
    channel_count=1,            # 1 = mono sound
    bits_per_sample=16,         # 16-bit audio
    samples_signed=True,        # samples can be positive or negative
)

# Connect the mixer to the I2S output so its sound goes to the DAC.
audio.play(mixer)

# Create the synthesizer itself. This is the "engine" that
# turns our notes into audio.
synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)

# Connect the synth to the first mixer channel.
mixer.voice[0].play(synth)


# ------------------------------------------------------------
# SETTINGS FOR LOADING THE WAV FILES
# You can change these to change how the files are used.
# ------------------------------------------------------------

# The folder on the Pico where your WAV files live.
SOUND_FOLDER = "/sounds"

# How many samples make up ONE frame (one waveform shape).
# 256 is a common size for wavetables.
FRAME_SIZE = 256

# How many frames to take from EACH WAV file:
#
#   FRAMES_PER_FILE = 1
#       Each file gives ONE frame (its first 256 samples).
#       Use this for short "single-cycle" WAV files, where
#       each file is one waveform shape.
#
#   FRAMES_PER_FILE = None
#       Cut each file into as many 256-sample frames as it holds.
#       Use this for ONE long wavetable file that already holds
#       many shapes one after another.
FRAMES_PER_FILE = 1

# When FRAMES_PER_FILE is None, never load more than this many
# frames from one file. This protects the Pico's limited memory.
MAX_AUTO_FRAMES = 64


# ------------------------------------------------------------
# FIND THE WAV FILES
# os.listdir gives us the names of everything in the folder.
# We keep only names that end in ".wav" and sort them
# alphabetically, so wave1.wav comes before wave2.wav.
# ------------------------------------------------------------

wavetable_files = sorted(
    f for f in os.listdir(SOUND_FOLDER)
    if f.lower().endswith(".wav")   # .lower() so ".WAV" also counts
)


# ------------------------------------------------------------
# FUNCTION: load_frames_from_wav
#
# A function is a reusable block of code. This one opens a WAV
# file, finds the audio data inside it, and returns a list of
# frames (each frame is an array of 256 samples).
#
# Why do we read the file ourselves? A WAV file starts with a
# "header" (information about the file) and only THEN comes the
# audio. We need to skip the header to reach the real samples.
# ------------------------------------------------------------

def load_frames_from_wav(path, num_frames):
    """Return a list of int16 arrays, each FRAME_SIZE samples long."""

    # "with open(...)" opens the file and closes it automatically
    # when we are finished with it. "rb" means read as raw bytes.
    with open(path, "rb") as f:

        # Every WAV file starts with a 12-byte opening header.
        # We don't need it, so read 12 bytes and throw them away.
        f.read(12)

        # After the opening header, the file is divided into CHUNKS.
        # Each chunk starts with 8 bytes: a 4-letter name, then a
        # number saying how big the chunk is. We look through the
        # chunks until we find the one named "data", which holds
        # the actual audio samples.
        while True:
            chunk_header = f.read(8)

            # If we ran out of file without finding "data", stop.
            if len(chunk_header) < 8:
                raise ValueError("No data chunk found in " + path)

            chunk_id = chunk_header[0:4]    # the 4-letter name
            # The size is stored as 4 bytes, "little-endian" order.
            chunk_size = int.from_bytes(chunk_header[4:8], "little")

            if chunk_id == b"data":
                break   # found it! Leave the loop.

            # Not the data chunk, so skip over its contents.
            # (Chunks always have an even length, so we add 1 byte
            # of padding when the size is odd.)
            f.seek(chunk_size + (chunk_size & 1), 1)

        # If we were told "None", work out how many frames the file
        # holds. Each sample is 2 bytes, so one frame is
        # FRAME_SIZE * 2 bytes. We keep the answer between
        # 1 and MAX_AUTO_FRAMES.
        if num_frames is None:
            num_frames = max(1, min(chunk_size // (FRAME_SIZE * 2),
                                    MAX_AUTO_FRAMES))

        # Read the raw audio bytes. 2 bytes per 16-bit sample.
        raw = f.read(num_frames * FRAME_SIZE * 2)

    # If the file was shorter than we asked for, "raw" has fewer
    # bytes than we need. Make a full-size, empty (all zero =
    # silent) buffer and copy what we did read into the start of it.
    buf = bytearray(num_frames * FRAME_SIZE * 2)
    buf[0:len(raw)] = raw

    # Turn the raw bytes into an array of 16-bit numbers.
    # Each number is one sample of the waveform (-32768 to 32767).
    data = np.frombuffer(buf, dtype=np.int16)

    # Slice the long array into separate frames of FRAME_SIZE samples.
    # Frame 0 is samples 0-255, frame 1 is samples 256-511, and so on.
    return [data[i * FRAME_SIZE:(i + 1) * FRAME_SIZE]
            for i in range(num_frames)]


# ------------------------------------------------------------
# LOAD EVERY FILE INTO ONE BIG LIST CALLED "frames"
# This is our wavetable: a list of waveform shapes.
# ------------------------------------------------------------

frames = []   # start with an empty list

for filename in wavetable_files:
    # Load the frames from this file and add them to the list.
    frames.extend(load_frames_from_wav(SOUND_FOLDER + "/" + filename,
                                       FRAMES_PER_FILE))
    print("Loaded:", filename)   # shows progress in the serial console

# How many frames do we have in total?
NUM_WAVES = len(frames)
print("Total frames:", NUM_WAVES)

# Scanning needs at least two frames to move between.
# If there are fewer, stop and explain the problem.
if NUM_WAVES < 2:
    raise RuntimeError("Need at least 2 frames to scan. "
                       "Add more WAVs to /sounds.")


# ------------------------------------------------------------
# CLASS: Wavetable
#
# A class is a blueprint for making objects that bundle data
# and behaviour together. Our Wavetable object remembers a
# POSITION in the wavetable. Whenever the position changes, it
# blends the two nearest frames to make a new waveform.
#
# Example: position 2.25 means "25% of the way from frame 2
# to frame 3". The waveform becomes 75% frame 2 + 25% frame 3.
#
# Blending (instead of jumping from frame to frame) makes the
# sound change smoothly, with no clicks.
# ------------------------------------------------------------

class Wavetable:

    # __init__ runs once, when we create a new Wavetable.
    def __init__(self):
        self.num_waves = NUM_WAVES

        # This is the waveform the note will play. We make our OWN
        # COPY of the first frame, because each oscillator needs its
        # own buffer to change. (If they shared one, all three
        # oscillators would always sound identical.)
        self.waveform = np.array(frames[0], dtype=np.int16)

        # Remember the current position (starts at the first frame).
        self._wave_pos = 0.0

    # This makes "wave_pos" readable like a normal variable:
    # print(wavetable1.wave_pos)
    @property
    def wave_pos(self):
        return self._wave_pos

    # This runs automatically whenever we SET the position:
    # wavetable1.wave_pos = 2.25
    # It does the blending work.
    @wave_pos.setter
    def wave_pos(self, pos):

        # Keep the position inside the table (0 to the last frame).
        pos = min(max(pos, 0), self.num_waves - 1)
        self._wave_pos = pos

        # Split the position into a whole part and a fractional part.
        # For 2.25:  i = 2  and  frac = 0.25
        i = int(pos)
        frac = pos - i

        # Pick the frame below and the frame above the position.
        # (min() stops us reading past the end of the list.)
        a = frames[i]
        b = frames[min(i + 1, self.num_waves - 1)]

        # Blend them: mostly "a" when frac is small, mostly "b" when
        # frac is large. The [:] means we write the result INTO the
        # existing waveform buffer, rather than making a new one.
        # The note is already using that buffer, so it hears the
        # change straight away.
        self.waveform[:] = np.array(a * (1 - frac) + b * frac,
                                    dtype=np.int16)


# Make three wavetable objects, one for each oscillator.
wavetable1 = Wavetable()
wavetable2 = Wavetable()
wavetable3 = Wavetable()


# ------------------------------------------------------------
# ENVELOPE
# An envelope shapes the volume of a note over time.
# For a drone we want a very slow fade in and fade out.
# ------------------------------------------------------------

envelope = synthio.Envelope(
    attack_time=2.0,     # seconds to fade IN when the note starts
    decay_time=0.0,      # no dip after the fade in
    sustain_level=1.0,   # then stay at full volume
    release_time=2.0,    # seconds to fade OUT when the note is released
)


# ------------------------------------------------------------
# NOTES (THE THREE OSCILLATORS)
#
# midi_to_hz converts a MIDI note number into a frequency in Hz.
# MIDI note 60 is middle C, and 48 is the C an octave below.
# Subtracting 12 goes DOWN one octave. Subtracting 7 goes down
# a "perfect fifth".
#
# So we get a C, a G, and a lower C, a classic drone chord.
# ------------------------------------------------------------

midi_note = 48   # the "root" note of the drone (C)

# Lowest note: one octave below the root.
note = synthio.Note(
    synthio.midi_to_hz(midi_note - 12),
    waveform=wavetable1.waveform,   # plays wavetable 1's waveform
    envelope=envelope,
    amplitude=0.3,   # volume of this note (0.0 silent to 1.0 full)
)

# Middle note: a fifth below the root.
note2 = synthio.Note(
    synthio.midi_to_hz(midi_note - 7),
    waveform=wavetable2.waveform,
    envelope=envelope,
    amplitude=0.3,
)

# Top note: the root itself.
note3 = synthio.Note(
    synthio.midi_to_hz(midi_note),
    waveform=wavetable3.waveform,
    envelope=envelope,
    amplitude=0.3,
)

# Three notes at 0.3 each add up to about 0.9, which leaves just
# enough room to avoid clipping (distortion). If the sound
# distorts, lower these numbers.
# "bend" changes a note's pitch. Here, a very slow LFO nudges the
# top note slightly out of tune and back again (a gentle drift),
# which makes the chord feel alive.
#   rate = how fast the LFO cycles (0.005 Hz = once every 200 s)
#   scale = how far it moves, measured in octaves (0.25 = a quarter
#           of an octave, which is a noticeable detune)
#   phase_offset = where in its cycle the LFO starts (0 to 1)

note3.bend = synthio.LFO(rate=0.005, scale=0.25, phase_offset=0.5)


# ------------------------------------------------------------
# LFOs THAT MOVE THE WAVETABLE POSITION
#
# An LFO (Low Frequency Oscillator) is a very slow wave used to
# CONTROL something rather than make sound. Here, each LFO
# slides a wavetable position back and forth, so the timbre
# (tone colour) keeps changing.
#
# Each LFO outputs a value we can read with ".value".
# We multiply that by NUM_WAVES ("scale") so it covers the whole
# range of frames, from the first to the last.
# ------------------------------------------------------------

# LFO 1: ramps from the FIRST frame up to the LAST frame.
# The waveform (0, 32767) is a rising line: low, then high.
# rate=0.005 means one full pass takes 200 seconds. Very slow!

wave_lfo = synthio.LFO(
    rate=0.005,
    waveform=np.array((0, 32767), dtype=np.int16),
)
wave_lfo.scale = NUM_WAVES

# LFO 2: ramps the OPPOSITE way, from the LAST frame down to the
# FIRST. The waveform (32767, 0) is a falling line. It also runs
# at a different speed (0.01 Hz) and starts part way through its
# cycle (phase_offset=0.25). Because it differs from LFO 1, the
# two oscillators never sound the same.

wave_lfo2 = synthio.LFO(
    rate=0.01,
    waveform=np.array((32767, 0), dtype=np.int16),
)
wave_lfo2.scale = NUM_WAVES
wave_lfo2.phase_offset = 0.25

# LFO 3: a smooth sine wave that sweeps up and down, instead of
# a one-way ramp. A sine wave moves between -1 and +1. We want it
# to move between 0 and NUM_WAVES instead, so:
#   scale  = NUM_WAVES / 2   makes it swing by half the table
#   offset = NUM_WAVES / 2   shifts it up so it never goes below 0

wave_lfo3 = synthio.LFO(
    rate=0.02,
    scale=NUM_WAVES / 2,
    offset=NUM_WAVES / 2,
)

# IMPORTANT: LFOs only update when the synth runs them. Adding
# them to synth.blocks tells the synth "keep these running".
# Without this step, their values would never change.

synth.blocks.append(wave_lfo)
synth.blocks.append(wave_lfo2)
synth.blocks.append(wave_lfo3)


# ------------------------------------------------------------
# START THE SOUND
# press() starts notes playing. We press all three at once by
# passing them together inside brackets. The envelope makes them
# fade in over 2 seconds.
# ------------------------------------------------------------

synth.press((note, note2, note3))


# ------------------------------------------------------------
# MAIN LOOP
#
# "while True" repeats forever (until you stop the program).
# Each time round the loop we:
#   1. Read the current value of each LFO.
#   2. Copy it into the matching wavetable's position.
#      (This triggers the blending code in the Wavetable class
#      and updates the waveform the note is playing.)
#   3. Print the positions so we can watch them change.
#   4. Wait a short time, so we don't hog the processor.
# ------------------------------------------------------------

while True:

    # Copy each LFO's position into its wavetable.
    
    wavetable1.wave_pos = wave_lfo.value
    wavetable2.wave_pos = wave_lfo2.value
    wavetable3.wave_pos = wave_lfo3.value

    # Print the three positions to the serial console, rounded
    # to two decimal places (%.2f).
    
    print("%.2f %.2f %.2f" % (wavetable1.wave_pos,
                              wavetable2.wave_pos,
                              wavetable3.wave_pos))

    # Pause for 0.05 seconds (20 updates per second).
    # Increase this if the sound glitches; decrease it for smoother
    # (but more demanding) morphing.
    
    time.sleep(0.05)


# ============================================================
# THINGS TO TRY
# ============================================================
#
# 1. Speed things up so you can hear the changes quickly:
#    change the LFO rates (0.005, 0.01, 0.02) to 0.1, 0.15, 0.2.
#
# 2. Change midi_note to 55 (G) or 60 (middle C) and listen to
#    how the drone's pitch and mood change.
#
# 3. Try other chord shapes by changing the numbers subtracted
#    from midi_note (for example: -12, -5 and 0).
#
# 4. Swap the WAV files in /sounds for others and notice how
#    each set of waveforms gives the drone a different character.
#
# 5. Change the envelope attack_time to 0.1 for a quick start
#    instead of a slow fade in.
#
# 6. Set FRAMES_PER_FILE = None and use one long wavetable WAV
#    for a much richer sweep.
#
# ============================================================
