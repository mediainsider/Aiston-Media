#!/usr/bin/env bash
# Builds score.wav from compose.py: MIDI -> FluidSynth (FluidR3_GM) -> mastering.
# Needs: python3 + mido, fluidsynth, fluid-soundfont-gm, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
END=$(python3 -c "import json;print(json.load(open('../marks.json'))['end'])")
python3 compose.py
fluidsynth -ni -q -g 0.5 -r 48000 -R 1 -C 0 -o synth.reverb.room-size=0.82 -o synth.reverb.width=1.0 -o synth.reverb.level=0.75 -o synth.reverb.damp=0.35 \
  -F raw.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 score.mid
ffmpeg -y -loglevel error -i raw.wav -af "atrim=0:${END},highpass=f=35,lowpass=f=15000,\
aecho=0.8:0.6:120|260:0.18|0.12,acompressor=threshold=-20dB:ratio=2.5:attack=30:release=400,\
afade=t=in:d=0.4,afade=t=out:st=$(python3 -c "print(${END}-2.4)"):d=2.4,loudnorm=I=-17:TP=-1.5:LRA=11" -ar 48000 score.wav
rm raw.wav
echo "wrote score.wav"
