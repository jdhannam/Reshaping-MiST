
Example 1 — Random Notes from a Scale
import random

scale = [
    220, 247, 262, 294,
    330, 349, 392, 440
]

note.frequency = random.choice(scale)


Example 2 — Generative Arpeggiator
chord = [
    220,
    262,
    330,
]

note.frequency = random.choice(chord)



Example 3 — Random Melody + Fixed Rhythm
while True:

    note.frequency = random.choice(scale)

    synth.press(note)

    time.sleep(0.25)

    synth.release(note)

    time.sleep(0.05)
	
	
Example 4 — Random Rhythm
durations = [
    0.125,
    0.25,
    0.5,
]

duration = random.choice(durations)


Example 5 — Evolving Drone
filter_lfo.rate = random.uniform(
    0.05,
    0.5
)




Example 6 — Probability-Based Music
scale = [
    220,
    220,
    220,
    247,
    262,
    330,
]


Example 7 — Generative Chord Progression
chords = [

    (220,262,330),   # Am

    (262,330,392),   # C

    (349,440,523),   # F

    (392,494,587),   # G

]
current_chord = random.choice(chords)