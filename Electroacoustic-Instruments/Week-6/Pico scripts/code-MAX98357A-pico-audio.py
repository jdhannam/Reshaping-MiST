import board
import audiobusio
import audiomixer
import synthio
import array
import math
import time

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,       # BCLK
    word_select=board.GP28,     # LRC
    data=board.GP26,            # DIN
)

mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)

audio.play(mixer)

synth = synthio.Synthesizer(sample_rate=22050,channel_count=1,)
mixer.voice[0].play(synth)

wave = array.array("h",[int(32767 * math.sin(2 * math.pi * i / 256))
     for i in range(256)]
)

note = synthio.Note(
    frequency=440,
    waveform=wave
)

print("Playing A4...")

synth.press(note)

while True:
    time.sleep(1)
