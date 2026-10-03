# The Conversation: four questions (motion graphic)

A 13-second, 1920×1080, 60fps animated version of the "What am I seeing?" graphic.

- `the-conversation-questions.mp4`: the rendered video
- `index.html`: the animation source. Open it in a browser to watch it play live.
- `render.mjs`: renders `index.html` to MP4 one frame at a time, using Playwright and ffmpeg

## Timeline

| Time | Beat |
|------|------|
| 0.0–2.0s | The glowing frame draws on and the photo wipes in with a slow push-in, sun glow and lens flare |
| 1.4s | The logo wipes in, then a shine passes across it |
| 2.2s | Eye icon pops in, then "What am I **seeing?**" |
| 3.8s | Lightbulb icon (it switches on), then "What might I **be missing?**" |
| 5.4s | People icon, then "Who is this person to me, **beyond the problem I'm worried about?**" |
| 7.2s | Heart icon, then "And then write something **you love about them.**" |
| 8.6s | The red brush stroke paints underneath |
| 9–13s | Hold: heartbeat, blinking eye, particles drifting, a light running around the frame |

## Re-rendering

```bash
npm install          # playwright
node render.mjs                      # writes the-conversation-questions.mp4 (60fps, 13s)
node render.mjs out.mp4 30 13        # custom output, fps, seconds
node render.mjs --stills 2.5,12 ./   # PNG preview frames
```

To change the copy, timing or colours, edit `index.html`. Each icon's start time is set by `--d` and each question's by `data-start`.
