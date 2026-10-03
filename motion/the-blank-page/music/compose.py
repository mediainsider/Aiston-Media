"""Original score for "The Blank Page", timed to the scene markers in ../marks.json.

Writes score.mid; render.sh turns it into score.wav with FluidSynth + FluidR3_GM.
Key of D major, ~72 bpm feel. Piano carries the story; strings arrive with the
feeling words and lift at the focus shift.
"""
import json
import pathlib
import mido

HERE = pathlib.Path(__file__).parent
M = json.loads((HERE.parent / "marks.json").read_text())
END = M["end"]

TPB = 480
BPM = 72
SEC = BPM / 60 * TPB          # ticks per second
EIGHTH = 60 / BPM / 2         # 0.4167s

PIANO, STRINGS, CELLO, PAD, LOW, VIOLIN = range(6)
PROGRAMS = {PIANO: 0, STRINGS: 49, CELLO: 42, PAD: 89, LOW: 48, VIOLIN: 40}

events = []  # (time_sec, order, channel, message)


def note(ch, t, n, dur, vel):
    events.append((t, 1, ch, mido.Message("note_on", channel=ch, note=n, velocity=max(1, min(127, int(vel))))))
    events.append((t + dur, 0, ch, mido.Message("note_off", channel=ch, note=n, velocity=0)))


def cc_ramp(ch, points, ctl=11, step=.08):
    """Linear expression ramp through (time, value) points."""
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        t = t0
        while t < t1:
            v = v0 + (v1 - v0) * (t - t0) / (t1 - t0)
            events.append((t, 0, ch, mido.Message("control_change", channel=ch, control=ctl, value=int(v))))
            t += step
    t, v = points[-1]
    events.append((t, 0, ch, mido.Message("control_change", channel=ch, control=ctl, value=int(v))))


# Chord shapes: (bass, [upper voicing])
CH = {
    "D":    (38, [62, 66, 69]),
    "D/F#": (42, [62, 66, 69]),
    "A/C#": (37, [57, 61, 64]),
    "A":    (45, [57, 61, 64]),
    "Asus": (45, [57, 62, 64]),
    "Bm":   (35, [59, 62, 66]),
    "Bm/A": (33, [59, 62, 66]),
    "G":    (43, [59, 62, 67]),
    "Gmaj7": (43, [59, 62, 66]),
    "Em":   (40, [59, 64, 67]),
    "F#":   (42, [58, 61, 66]),
    "F#sus": (42, [59, 61, 66]),
}


def arpeggio(t0, t1, chord, vel=58, octave=0, pattern=(0, 7, 12, 16, 19, 16, 12, 7), bass=True, rate=EIGHTH):
    """Broken-chord piano accompaniment from t0 to t1."""
    b, up = CH[chord]
    if bass:
        note(PIANO, t0, b + 12, (t1 - t0) * .95, vel + 6)
        note(PIANO, t0 + .02, b + 24, (t1 - t0) * .9, vel - 4)
    root = up[0] + octave
    # build pattern from chord tones above the bass, spread over ~1.5 octaves
    tones = sorted({b + 24 + i for i in (0,)} | {u + octave for u in up} | {u + 12 + octave for u in up})
    seq = [tones[i % len(tones)] for i in (0, 1, 2, 3, 4, 3, 2, 1)]
    t, i = t0 + rate, 0
    while t < t1 - .05:
        accent = 6 if i % 4 == 0 else 0
        note(PIANO, t, seq[i % len(seq)], rate * 2.2, vel - 10 + accent - (i % 2) * 4)
        t += rate
        i += 1


def pad(ch, t0, t1, chord, vel=50, lift=0):
    b, up = CH[chord]
    for n in up:
        note(ch, t0, n + lift, t1 - t0 + .15, vel)


def run(changes, t_end, fn):
    for (t0, c), (t1, _) in zip(changes, changes[1:] + [(t_end, None)]):
        fn(t0, t1, c)


# ---------------------------------------------------------------- 1 · opening (love)
s2 = M["cross"] - 5.7          # scene 2 begins ≈ 8.2s
open_ch = [(0.35, "D"), (2.35, "A/C#"), (4.35, "Bm"), (6.35, "G")]
run(open_ch, s2, lambda a, b, c: arpeggio(a, b, c, vel=52))
for t, n, d in [(1.2, 78, 1.0), (2.4, 76, 1.6), (4.4, 74, 1.0), (5.4, 73, .8), (6.4, 74, 1.8)]:
    note(PIANO, t, n, d, 66)
pad(PAD, 2.3, s2 + .4, "D", 34)

# ---------------------------------------------------------------- 2 · the frantic list (tension)
cross, s3 = M["cross"], M["s3"]
crumple = cross + 1.1
t = s2
while t < crumple:   # anxious low ostinato, quickening
    rate = EIGHTH / 2 if t > cross - 2 else EIGHTH * .75
    note(PIANO, t, 47, rate * 1.4, 54 + (t - s2) * 3)
    note(PIANO, t + .01, 59 if int((t - s2) / rate) % 2 else 54, rate, 40 + (t - s2) * 2)
    t += rate
for (a, c) in [(s2, "Bm"), (s2 + 2, "G"), (s2 + 4, "Em"), (cross - .4, "F#sus")]:
    b, up = CH[c]
    note(LOW, a, b + 12, 2.2 if c != "F#sus" else crumple - a, 64)
    note(LOW, a, b + 24, 2.2 if c != "F#sus" else crumple - a, 56)
note(LOW, cross + .4, 54, crumple - cross - .4, 70)   # F# sus resolving into the crumple
note(LOW, cross + .4, 58, crumple - cross - .4, 66)
cc_ramp(LOW, [(s2, 50), (cross, 118), (crumple, 96), (crumple + .25, 0), (s3, 0)])
note(PIANO, crumple + .05, 35, 2.6, 60)               # a single low B as the page falls away

# ---------------------------------------------------------------- 3 · the blank page (hope)
s4, s5 = M["s4"], M["s5"]
blank = [(s3, "D"), (s3 + 2.6, "A/C#"), (s4 - .4, "Bm"), (s4 + 2.6, "G"), (s4 + 4.4, "Asus")]
run(blank, s5, lambda a, b, c: arpeggio(a, b, c, vel=50, octave=12, rate=EIGHTH))
for t, n, d in [(s3 + .6, 81, 1.6), (s3 + 2.6, 80, 1.8), (s4 - .3, 78, 1.4), (s4 + 1.0, 76, 1.2), (s4 + 2.6, 74, 1.8), (s4 + 4.5, 76, 1.4)]:
    note(PIANO, t, n, d, 62)
pad(PAD, s3 + .3, s5, "D", 30)

# ---------------------------------------------------------------- 4 · the feeling words (warmth)
s6 = M["s6"]
feel = [(s5, "G"), (s5 + 2.9, "D/F#"), (s5 + 5.8, "Em"), (s5 + 8.7, "A")]
run(feel, s6, lambda a, b, c: (arpeggio(a, b, c, vel=54), pad(STRINGS, a, b, c, 58, -12)))
cc_ramp(STRINGS, [(s5, 30), (s5 + 3, 80), (s6, 92)])
cello = [(s5 + .2, 59, 2.6), (s5 + 2.9, 57, 1.4), (s5 + 4.3, 54, 1.4), (s5 + 5.8, 55, 2.6), (s5 + 8.7, 52, 1.4), (s5 + 10.1, 57, 1.4)]
for t, n, d in cello:
    note(CELLO, t, n, d + .1, 76)
cc_ramp(CELLO, [(s5, 60), (s5 + 1.5, 100), (s6, 104)])

# ---------------------------------------------------------------- 5 · look at those words / ask yourself (build)
ask, s6end = M["ask"], M["s6end"]
step3 = [(s6, "Bm"), (s6 + 1.45, "G"), (s6 + 2.9, "D"), (s6 + 4.3, "A")]
run(step3, ask, lambda a, b, c: (arpeggio(a, b, c, vel=56), pad(STRINGS, a, b, c, 62, -12)))
build = [(ask, "G"), (ask + 1.85, "A"), (ask + 3.7, "Bm"), (ask + 5.55, "Bm/A")]
run(build, s6end, lambda a, b, c: (arpeggio(a, b, c, vel=60), pad(STRINGS, a, b, c, 70, -12), pad(STRINGS, a, b, c, 60)))
cc_ramp(STRINGS, [(s6, 88), (ask, 92), (s6end - .6, 116), (s6end, 100)])
for t, n, d in [(s6 + .2, 74, 1.3), (s6 + 1.5, 71, 1.3), (s6 + 2.9, 69, 1.3), (s6 + 4.3, 73, 1.4),
                (ask + .1, 74, 1.8), (ask + 1.9, 76, 1.8), (ask + 3.7, 78, 1.8), (ask + 5.6, 76, 1.8)]:
    note(VIOLIN, t, n, d, 72)
cc_ramp(VIOLIN, [(s6, 40), (ask, 84), (s6end, 104), (s6end + .8, 40)])

# ---------------------------------------------------------------- 6 · "a very different way" (breathe)
s7, s8 = M["s7"], M["s8"]
breathe = [(s6end, "G"), (s7 + 2.4, "D/F#")]
run(breathe, s8, lambda a, b, c: (arpeggio(a, b, c, vel=46, octave=12, rate=EIGHTH * 1.5), pad(STRINGS, a, b, c, 48, -12)))
cc_ramp(STRINGS, [(s6end, 100), (s6end + 1.2, 60), (s8, 62)])

# ---------------------------------------------------------------- 7 · the shift in focus (lift)
shift, s8end = M["shift"], M["s8end"]
pre = [(s8, "Em"), (s8 + 1.7, "Asus")]
run(pre, shift, lambda a, b, c: (arpeggio(a, b, c, vel=52), pad(STRINGS, a, b, c, 60, -12)))
lift = [(shift, "G"), (shift + 1.8, "A"), (shift + 3.6, "D"), (shift + 5.4, "Bm")]
run(lift, s8end, lambda a, b, c: (arpeggio(a, b, c, vel=62), pad(STRINGS, a, b, c, 74, -12), pad(STRINGS, a, b, c, 66)))
for t, n, d in [(shift + .1, 74, 1.7), (shift + 1.9, 76, 1.7), (shift + 3.6, 78, 1.7), (shift + 5.4, 81, 1.5)]:
    note(VIOLIN, t, n, d, 80)
for t, n, d in [(shift, 55, 1.8), (shift + 1.8, 57, 1.8), (shift + 3.6, 50, 1.8), (shift + 5.4, 47, 1.6)]:
    note(CELLO, t, n, d, 80)
cc_ramp(STRINGS, [(s8, 62), (shift, 92), (s8end - .5, 120), (s8end + .5, 104)])
cc_ramp(VIOLIN, [(shift, 70), (s8end, 110)])

# ---------------------------------------------------------------- 8 · close (resolve)
s9 = M["s9"]
close = [(s8end, "G"), (s9 + 1.2, "Asus"), (s9 + 2.6, "A"), (s9 + 3.6, "D")]
run(close, END, lambda a, b, c: (arpeggio(a, b, c, vel=56 if c != "D" else 50, rate=EIGHTH * (1 if c != "D" else 1.5)),
                                 pad(STRINGS, a, b, c, 68, -12)))
for t, n, d in [(s8end + .1, 78, 1.8), (s9 + 1.2, 76, 1.3), (s9 + 2.6, 73, 1.0), (s9 + 3.6, 74, END - s9 - 3.6)]:
    note(VIOLIN, t, n, d, 74)
note(PIANO, s9 + 3.6, 86, 3.5, 58)
note(PIANO, s9 + 4.6, 81, 2.8, 50)
cc_ramp(STRINGS, [(s8end, 104), (s9 + 3.6, 96), (END, 20)])
cc_ramp(VIOLIN, [(s8end, 100), (s9 + 3.6, 86), (END, 10)])

# ---------------------------------------------------------------- write MIDI
mid = mido.MidiFile(ticks_per_beat=TPB)
track = mido.MidiTrack()
mid.tracks.append(track)
track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
vols = {PIANO: 104, STRINGS: 84, CELLO: 80, PAD: 60, LOW: 92, VIOLIN: 74}
pans = {PIANO: 64, STRINGS: 54, CELLO: 44, PAD: 64, LOW: 70, VIOLIN: 84}
for ch, prog in PROGRAMS.items():
    track.append(mido.Message("program_change", channel=ch, program=prog, time=0))
    track.append(mido.Message("control_change", channel=ch, control=7, value=vols[ch], time=0))
    track.append(mido.Message("control_change", channel=ch, control=10, value=pans[ch], time=0))
    track.append(mido.Message("control_change", channel=ch, control=91, value=88, time=0))   # reverb send
    track.append(mido.Message("control_change", channel=ch, control=11, value=100 if ch in (PIANO, PAD) else 0, time=0))
    if ch == PIANO:
        track.append(mido.Message("control_change", channel=ch, control=64, value=0, time=0))

events.sort(key=lambda e: (e[0], e[1]))
last = 0
for t, _, _, msg in events:
    tick = int(round(max(0, t) * SEC))
    track.append(msg.copy(time=tick - last))
    last = tick
mid.save(HERE / "score.mid")
print(f"wrote score.mid, {len(events)} events, {END:.2f}s")
