# The Conversation: "How do I want them to feel?" (motion graphic)

A 75-second, 1920×1080, 60fps explainer built from the course script. A sheet of paper is the main visual: the words get handwritten onto it as the script goes.

- `the-blank-page.mp4`: the rendered video
- `index.html`: the animation source. Open it in a browser to watch it play live.
- `render.mjs`: a frame-accurate renderer (Playwright and ffmpeg) that splits the work across parallel workers

## Scenes

| Approx. time | Script beat | Visual |
|---|---|---|
| 0–7s | "If you're thinking about talking to somebody you love…" | A heart icon and the opening line |
| 7–15s | "Don't start by writing down everything you want to tell them." | A page fills with a frantic list, gets scribbled out, then crumples away |
| 15–20s | Step 1: "Take a blank piece of paper." | A fresh page slides in and glows |
| 20–26s | Step 2: "At the top write: HOW DO I WANT THEM TO FEEL?" | The pen writes the heading and it gets underlined |
| 26–38s | "Loved. Safe. Worthy. Heard. Supported. Not alone. Whatever feels right…" | Each word is handwritten with a heart beside it |
| 38–50s | Step 3: "Look at those words… Are the words I'm about to use likely to make them feel this way?" | The words are highlighted, then the question appears in a speech box |
| 51–57s | "That's a very different way to prepare for a difficult conversation." | Full-screen statement |
| 57–70s | "Away from: How do I make them change? Towards: How do I create a conversation where change might become possible?" | A focus ring moves from one card to the other |
| 70–75s | "There is a big difference." | Closing card with a beating heart and a brush underline |

## Editing and re-rendering

All timing lives in `build()` in `index.html`, and each scene starts relative to the end of the one before it. To slow a scene down to match a voiceover, increase the hold time before its `hide(...)` call.

```bash
npm install
node render.mjs                          # writes the-blank-page.mp4 (60fps)
node render.mjs out.mp4 30 --workers 4   # 30fps, 4 parallel workers
node render.mjs --stills 10,30,60 ./     # PNG preview frames
```
