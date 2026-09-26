<div align="center">

<img src="icon.svg" width="112" alt="Motion Bang Bang icon">

# Motion Bang Bang

**An agent skill that turns your AI coding agent into a motion designer.**<br>
Openers, promos, product demos, kinetic typography, and explainers — built as a single `index.html` that plays like video, not like slides.

[![Version](https://img.shields.io/badge/version-1.21.0-2f6fd6?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-3fa34d?style=flat-square)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-1c2a4a?style=flat-square)](#install)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Gemini%20CLI%20%C2%B7%20Cursor-7a5af5?style=flat-square)](#install)

<img src="docs/gallery/hero.jpg" alt="A grid of styles Motion Bang Bang can build: grainy gradient opener, SaaS product tour, flat pop promo with photos, visual journalism explainer, continuous action explainer, cartoon collage explainer" width="100%">

[What you can make](#what-you-can-make) · [Style gallery](#style-gallery) · [Workflow](#recommended-workflow) · [Example prompts](#example-prompts) · [Install](#install) · [FAQ](#faq)

</div>

---

## Why

Ask an AI agent for "a video" and you usually get **slides**: one section per idea, a title, a photo, a fade between them. Motion Bang Bang encodes what a working motion designer insists on — one continuous world, a camera that actually moves, a subject that persists, text that lives inside the scene — as **rules an agent can check in its own code**, plus starters that make the right architecture the easy path.

It also stops every project from looking the same. The look is **derived from your brand** through a required style brief, the structure is **chosen from a menu of concepts**, and nothing is inherited from the starter or copied from a reference.

## What you can make

| | Output | Typical length |
|---|---|---|
| 🎬 **Openers & promos** | product launches, app promos, campaign spots, teasers | 15–40 s |
| 🖥️ **Product & SaaS demos** | UI assembled and used on screen, camera following the clicks | 20–60 s |
| 🔤 **Kinetic typography** | lyric-style statements, event announcements, manifestos | 10–30 s |
| 📺 **Bumpers, idents, channel intros** | short brand moments that loop | 3–10 s |
| 🧭 **Explainers** | six explainer styles, optional voice-over sync, 16:9 or 9:16 | 30–120 s |
| 🎥 **Video layers** | your own or generated clips placed like footage — inside devices, frames, and masks, locked to the timeline | — |
| 🎧 **Sound design** | voice-over generated to word timestamps, then 20 bundled sound effects cued off the finished animation and mixed onto the MP4 without re-rendering a frame | — |
| 🎞️ **After Effects builds** | cartoon explainers built directly inside AE through the Higgsfield MCP bridge | — |

Every deliverable is one `index.html`: double-click to play, autoplay + loop, `?debug=1` for a scrub bar, and an optional frame-by-frame export to MP4.

## Style gallery

> Each frame below is a **single static scene** built for this README with **fictional brands and data**. The portrait, product photos, port photo, engraving, and cartoon cutouts were generated with GPT Image 2.5; everything else is HTML, CSS, and SVG. Real projects take their palette, type, and imagery from your brand.

<table>
<tr>
<td width="50%"><img src="docs/gallery/01-grainy-gradient.jpg" alt="Grainy gradient opener"><br><b>Grainy gradient</b> · opener<br><sub>Glowing layered shapes, soft grain, a camera that travels through them. Tech, AI, music, premium launches.</sub></td>
<td width="50%"><img src="docs/gallery/02-kinetic-colorblock.jpg" alt="Kinetic typography in poster color-block"><br><b>Poster color-block</b> · kinetic typography<br><sub>Huge cropped words, solid color fields that slam in on the beat. Events, music, launches.</sub></td>
</tr>
<tr>
<td><img src="docs/gallery/03-saas-ui-tour.jpg" alt="SaaS product tour"><br><b>Product tour with claims</b> · SaaS demo<br><sub>Real UI lifted out of the dashboard, the camera zooms into what gets clicked. SaaS, dashboards, B2B.</sub></td>
<td><img src="docs/gallery/04-flat-vector.jpg" alt="Flat vector illustration promo"><br><b>Flat vector illustration</b> · promo<br><sub>Solid fills, stylized hands, UI drawn flat, shapes with gentle overshoot. Fintech, consumer apps.</sub></td>
</tr>
<tr>
<td><img src="docs/gallery/07-flat-pop-photo.jpg" alt="Flat pop with photos promo"><br><b>Flat pop with photos</b> · promo<br><sub>Photo cutouts popping in, stickers, brand color fields that change with a visible trigger. Consumer apps, campaigns.</sub></td>
<td><img src="docs/gallery/05-continuous-action.jpg" alt="Continuous action explainer"><br><b>Continuous action</b> · explainer<br><sub>One subject that never stops, numbers and maps living inside the world. Speed, routes, processes.</sub></td>
</tr>
<tr>
<td><img src="docs/gallery/09-visual-journalism.jpg" alt="Visual journalism explainer"><br><b>Visual journalism</b> · explainer<br><sub>Black ground, real photos with source tags, highlighter, dashed annotations. News, current issues.</sub></td>
<td><img src="docs/gallery/08-white-catalog.jpg" alt="White catalog explainer"><br><b>White catalog</b> · explainer<br><sub>White grid, product cutouts, mixed script and heavy sans. Products, brands.</sub></td>
</tr>
<tr>
<td><img src="docs/gallery/10-vintage-sketch.jpg" alt="Vintage sketch explainer"><br><b>Vintage sketch</b> · explainer<br><sub>Sepia paper, engraving art, classic serifs, rust notes. History, biography.</sub></td>
<td><img src="docs/gallery/11-cartoon-collage.jpg" alt="Cartoon collage explainer"><br><b>Cartoon collage</b> · explainer<br><sub>Cream paper, flat illustration cutouts, color pills, handwriting. Science, education.</sub></td>
</tr>
<tr>
<td><img src="docs/gallery/06-cartoon-stage.jpg" alt="Cartoon stage explainer"><br><b>Cartoon stage</b> · explainer<br><sub>One living stage per scene, jointed characters, no captions. Education with characters.</sub></td>
<td><img src="docs/gallery/12-more-combinations.jpg" alt="Style brief with three concept candidates and one recommended pick"><br><b>…and many more</b><br><sub>10 styles × 19 concepts × 9 render families — three candidates, one pick.</sub></td>
</tr>
</table>

## The menus behind the looks

<details>
<summary><b>10 style directions</b> — the skin, derived from your brand</summary>

| Direction | Background | Typography | Signature motion | Good for |
|---|---|---|---|---|
| Cinematic dark | near-black gradient, particles, bloom only on objects | bold clean grotesk | push-through, light in front of the lens | creative tools, gaming, tech |
| Poster color-block | large solid color fields changing per scene | ultra-heavy display, giant cropped letters | block wipes, text slamming the frame edge | consumer apps, music, events |
| Editorial light | white/cream, generous space, hairlines | display serif + small grotesk | calm slides, lines that draw | productivity, finance, SaaS |
| Paper & print | paper texture, collage, stamps, tape | handwriting + serif | objects flying in and landing | education, community, food |
| Retro / analog | faded color, grain, scanlines | 70s–90s geometric | controlled glitch, rough zoom, freeze | nostalgia, music, entertainment |
| Brutalist mono | black and white, hard grid | monospace + condensed | hard cuts, shifting blocks, blinking cursor | developer tools |
| Pastel playful | stacked pastels, big round shapes | heavy rounded sans | elastic bounce, blooming shapes | kids, health, lifestyle |
| Luxury dark | black + gold/bronze, soft shadows | tall wide-tracked serif | slow motion, sweeping light, depth | fashion, automotive, property |
| Flat pop with photos | neutral light alternating with solid brand fields | rounded heavy sans + giant cropped words | cutouts popping in, stickers, fields snapping on the beat | consumer apps, fintech, e-commerce |
| Grainy gradient | deep base, saturated glowing shapes, fine grain | small clean grotesk or minimal heavy display | layers opening, camera through the shape, a guiding orb | tech, AI, music, creative launches |

</details>

<details>
<summary><b>19 opener concepts</b> — the structure, chosen per product</summary>

| # | Concept | Good for |
|---|---|---|
| 1 | One continuous shot | creative tools, hardware, spaces |
| 2 | Pure typography | strong taglines, events, releases |
| 3 | Problem → gone | productivity, utilities |
| 4 | Before / after | editors, filters, optimization |
| 5 | Journey inside the UI | apps with a distinctive UI |
| 6 | Product macro | hardware, packaging, F&B, fashion |
| 7 | Object metaphor | security, cloud, finance |
| 8 | Living number | milestones, performance |
| 9 | One feature, fully demoed | apps with one clear edge |
| 10 | Diegetic question → answer | AI, search, support |
| 11 | Rhythmic collage | music, lifestyle, community |
| 12 | Logo as stage | brands with a strong logo shape |
| 13 | Object relay | e-commerce, delivery, marketplaces |
| 14 | Brand system showcase | launches, rebrands, communities |
| 15 | Claim → how → result | new features, generative AI, creative tools |
| 16 | Living UI ecosystem | B2B SaaS, AI assistants, workflows |
| 17 | Flat pop with photos | consumer apps, fintech, campaigns |
| 18 | Through the gradient shapes | tech, AI, security, premium launches |
| 19 | Product tour with claims | SaaS, team tools, dashboards |

Each concept ships as principles and a menu of openings, transitions, and endings — never as a script to copy.

</details>

<details>
<summary><b>6 explainer styles</b> — each with its own starter</summary>

| Style | Look | Best for |
|---|---|---|
| Continuous action | flowing vector world, one subject that never leaves, changing viewpoints | speed, routes, processes |
| Cartoon collage | cream paper, flat illustration cutouts, handwriting, color pills | science, education |
| Visual journalism | black, real photos with source tags, highlighter, dashed annotations | news, current issues |
| White catalog | white grid, photo cutouts, mixed typography, scribbles | products, brands |
| Vintage sketch | sepia paper, engraving art, classic serifs, rust annotations | history, biography |
| Cartoon stage | one stage per scene, jointed characters, no captions | education with characters |

</details>

## Recommended workflow

```mermaid
flowchart LR
  A[Brief<br>product, logo, audience,<br>length, ratio] --> B[Style brief<br>3 concept candidates,<br>palette with sources]
  B --> C{You approve}
  C --> D[Assets<br>your photos & logo<br>or generated via MCP]
  D --> E[Build<br>index.html]
  E --> F[Verify frames<br>snap.mjs / ?debug=1]
  F --> G[Your feedback]
  G --> E
  G --> H[Deliver<br>HTML · MP4 · voice-over sync]
```

1. **Brief the agent.** Name the product, attach the logo or site, say who it is for, the length, and the ratio. Mention a style if you have one in mind — the name is enough.
2. **Approve the style brief.** The agent answers with three concept candidates, one recommendation, a structure fingerprint, and a palette where every color states its source. Change anything before a line of code is written.
3. **Settle the assets.** Your own photos and logo come first. If you have none, the agent can generate them through an image MCP (fictional faces, logos added in code) — or pick a concept that needs no photos.
4. **Let it build.** You get one `index.html`. The agent captures key seconds and checks them against the rules before handing over.
5. **Review and iterate.** Open it, scrub with `?debug=1`, and describe what feels off. Feedback lands on the same file.
6. **Deliver.** Keep the HTML, export MP4 with `scripts/export-frames.mjs`, or send a voice-over and the timeline re-times itself to it.

> **Tip:** start each new video in a **new chat**. The skill is read when it is first invoked, and a long chat keeps earlier decisions in context.

## Example prompts

```text
Make a 30-second opener for my note-taking app. Logo and screenshots attached.
```
```text
Build a 45-second product tour of our HR dashboard in the "product tour with claims" style, 16:9.
```
```text
Promo for a ticketing app in the flat pop with photos style — generate fictional people, 9:16, 20 seconds.
```
```text
Kinetic typography for our festival announcement: "City of Sound, 3 nights, 48 stages". Loud, color-block.
```
```text
Explain how a container port works in 60 seconds, visual journalism style, no voice-over.
```
```text
Promo for our editing app with a screen recording playing inside a laptop mockup, 30 seconds. Clip attached.
```
```text
A cartoon explainer on why volcanoes erupt, for kids, 9:16, I will send a voice-over later.
```

**Getting better results**

- Say *which style*, not *which scenes*. "Grainy gradient" gives you the look; listing a reference's scenes gives you a copy.
- Hand over real brand material — logo, site, app screenshots, photos. The palette and shapes are derived from it.
- Want one specific moment? Ask for it explicitly; otherwise the agent composes new ones.
- Keep text short. Openers carry one feeling, explainers one argument.

## Install

Motion Bang Bang follows the open **Agent Skills** layout: a folder with `SKILL.md` (frontmatter + instructions), `references/`, `assets/`, `scripts/`. It also ships as a Claude Code **plugin**.

### As a plugin (Claude Code)

```
/plugin marketplace add lowfatgeek/motion-graphics-skill
```
```
/plugin install motion-bang-bang@motion-bang-bang
```

Update later with `/plugin marketplace update motion-bang-bang`.

### Manual (any agent)

```bash
git clone https://github.com/lowfatgeek/motion-graphics-skill
```

| Agent | Where it goes |
|---|---|
| Claude Code | `~/.claude/skills/motion-bang-bang` (Windows: `C:\Users\<you>\.claude\skills\motion-bang-bang`) |
| Codex CLI | your Codex skills folder, or add to `AGENTS.md`: *"For motion graphics / explainers, read and follow `motion-bang-bang/SKILL.md`."* |
| Gemini CLI · Cursor · others | copy into the project and reference `SKILL.md` from `GEMINI.md`, `.cursor/rules`, or the system prompt |
| Plain chat (no agent) | paste `SKILL.md` + the relevant file in `references/` as instructions; attach a starter from `assets/` |

> Install **one copy** only. Two copies with the same skill name (for example a plugin and a manual folder) conflict, and the plugin wins.

The skill triggers on requests like "make an opener…", "promo video…", "explainer…", or a complaint that a web animation "looks like PowerPoint".

## Requirements

| To… | You need |
|---|---|
| **Watch** the result | a browser + internet (GSAP and fonts load from a CDN). Nothing else. |
| Generate Voiceover (TTS) | ElevenLabs API key (`scripts/elevenlabs_audio.py tts`) — optional |
| Transcribe & Caption Avatars (STT) | ElevenLabs API key (`scripts/elevenlabs_audio.py stt`) — optional |
| Put sound effects on a video | bundled `assets/sfx/` library + system Chrome + ffmpeg (`scripts/sfx-cues.mjs`, `scripts/sfx-mix.mjs`) — nothing installed, no re-render |
| Verify frames automatically | Node + puppeteer (`scripts/snap.mjs`) — optional; `?debug=1` works by hand |
| Export MP4 | Node + puppeteer + ffmpeg (`scripts/export-frames.mjs`) — optional |
| Sync to voice-over | ElevenLabs timestamps, ffmpeg, **or** browser pause detector (`scripts/vo-pauses.html`) |
| Use video clips | MP4 (H.264) or WebM files in `assets/` — optional |
| Generate images | any image MCP the agent can call — optional |
| Build in After Effects | After Effects + the Higgsfield MCP bridge — optional |

A deliverable never needs `npm install` to be watched.

## How the rules work

- **Style brief before code** — concept, structure fingerprint, palette with sources, display font, background surface and motion, render family, transitions, one special moment.
- **Structure from a menu** — three concept candidates per project, at most two "canonical" components, and a different fingerprint from the previous video.
- **Examples are principles, not scripts** — openings and endings differ from the concept's example, signature moments are transformed, and the example's colors and shapes never carry over.
- **Living typography** — sentence case, emphasis by order, size, or pause; word highlights and punctuation only when they add meaning.
- **A background that never sits still** — a chosen background motion, and color changes with a visible trigger.
- **Video as footage layers** — clips follow the timeline clock, so scrubbing and MP4 export stay frame-accurate.
- **Sound after the picture** — effects are mined from the finished timeline and mixed onto the MP4 with the video stream copied, so retuning audio never re-renders a frame.
- **A camera that works** — breathing drift, motivated push-throughs, and in UI demos a camera that follows the important clicks.
- **Structural anti-slide checks** — no fading sections, a persistent subject or world, at most two text levels, varied transitions with real depth.
- **Readable on phones** — no text under 30 px on a 1080-wide stage.

Full detail lives in `SKILL.md` and `references/`.

## ElevenLabs Audio Integration (TTS, STT & SFX)

Motion Bang Bang includes zero-dependency CLI tooling (`scripts/elevenlabs_audio.py`) for automated voiceovers and video transcription powered by **ElevenLabs**, plus a bundled sound-effects library that any project can use without generating anything.

### 1. Text-to-Speech (TTS) with Word & Sentence Timestamps
Convert voiceover scripts into studio audio and extract word-level and sentence-level timestamps for exact GSAP sync:
```bash
# Set your API key
export ELEVENLABS_API_KEY="sk_..."   # or $env:ELEVENLABS_API_KEY in PowerShell

# Generate voiceover audio, timestamps, and GSAP cue points
python scripts/elevenlabs_audio.py tts \
  --text "Motion Bang Bang creates cinematic web animations." \
  --voice george \
  --output assets/vo.mp3 \
  --timestamps assets/vo-timestamps.json \
  --cues assets/vo-cues.js
```
The resulting `assets/vo-timestamps.json` gives you duration, WPM, sentence boundaries, and natural pauses ($\ge 0.35$s) ideal for scene cuts.

### 2. Speech-to-Text (STT) for Talking-Head Avatars
Transcribe talking-head videos (e.g., from HeyGen, Synthesia, D-ID, or webcam recordings) or audio tracks using ElevenLabs Scribe:
```bash
python scripts/elevenlabs_audio.py stt \
  --file assets/avatar.mp4 \
  --output assets/transcript.json \
  --srt assets/captions.srt \
  --vtt assets/captions.vtt \
  --cues assets/captions-cues.js
```
Generate word-by-word kinetic typography captions that pop dynamically as the avatar speaks, or export standard `.srt` / `.vtt` subtitles.

### 3. Sound Effects — the bundled library
`assets/sfx/` ships 20 takes across 9 motion families: impacts, camera whooshes, paper, pens, UI clicks, rubber stamps, bell and counter accents, one riser, one room-tone bed. All were generated from the prompts in `assets/sfx/library.json` and normalised to a single contract (48 kHz / stereo / PCM-16, −3 dBFS peak by pure gain, trimmed to a ≤ 15 ms head), so nothing in the library is louder than anything else *before* the mixer decides intensity.

```bash
# one listen for the whole bundle
python scripts/elevenlabs_audio.py sfx --spec assets/sfx/library.json --preview _preview.wav
# extend it: add a block to library.json and re-run — existing files are skipped, so only new rows are billed
python scripts/elevenlabs_audio.py sfx --spec assets/sfx/library.json
# re-apply the contract after changing a gate or peak target: no API call, no billing
python scripts/elevenlabs_audio.py sfx --spec assets/sfx/library.json --renormalize
```

### 4. Placing effects on a rendered video
Two scripts, nothing installed, and the video stream is **copied** — the approved picture comes out bit-identical:
```bash
node scripts/sfx-cues.mjs --why                                   # window.OPENER.tl → assets/sfx-cues.json
node scripts/sfx-mix.mjs --video final.mp4 --vo assets/vo.wav --stems sfx-stems
```
The miner classifies every tween by what actually moved and prunes to a density the ear can follow (a validated 285-second explainer: 824 tweens → 422 candidates → 219 cues). The mixer builds one stem per family, snaps each hit onto the frame grid, ducks the sustained families ~13 dB under the narration, limits, muxes, then prints measured loudness and true peak. Full guide: [`references/sound-design.md`](references/sound-design.md).

For detailed architecture, voice aliases, and GSAP sync patterns, see [`references/elevenlabs-audio.md`](references/elevenlabs-audio.md).

## Repository layout

```
SKILL.md                         rules & workflow (read by the agent)
.claude-plugin/                  plugin + marketplace manifests
references/
  opener-konsep.md               19 opener concepts, UI animation, photos in openers
  anti-ppt.md                    slide patterns → fixes
  techniques.md                  typography, camera, transitions, backgrounds, render families
  explainer.md                   explainer styles, camera recipes, VO re-timing
  kartun-panggung.md             cartoon stage explainers
  architecture.md                stage, camera rig, determinism, export
  ae-bridge-higgsfield.md        building inside After Effects via the MCP bridge
  elevenlabs-audio.md            TTS voiceover with timestamps & STT avatar captions
  sound-design.md                SFX bundle contract, cue mining, ducking, mix verification
  roadmap.md                     where the skill is heading
assets/
  starter-opener.html            opener / promo architecture (GSAP + Three.js)
  starter-explainer*.html        one starter per explainer style
  sfx/                           20 sound effects in 9 families + library.json, manifest, SOURCES
scripts/
  elevenlabs_audio.py            ElevenLabs TTS & STT audio CLI engine (zero dependencies)
  sfx-cues.mjs                   mine a cue sheet from the rendered GSAP timeline
  sfx-mix.mjs                    place the cues on a rendered MP4 (stems, ducking, mux, copy video)
  snap.mjs                       verify: capture key seconds
  export-frames.mjs              export: frame-by-frame PNG → MP4
  vo-pauses.html                 voice-over pause detection, no ffmpeg needed
  serve.py                       no-cache dev server (optional)
  ae/bridge/                     After Effects bridge helpers
docs/gallery/                    README preview images
```

## FAQ

<details>
<summary><b>Is the output a video file?</b></summary>

The deliverable is an `index.html` that plays like a video: autoplay, loop, no player chrome. When you need a file, `scripts/export-frames.mjs` renders it frame by frame to MP4, and `scripts/sfx-mix.mjs` puts sound effects on the result afterwards without touching a single video frame.
</details>

<details>
<summary><b>Where do the whooshes and clicks come from?</b></summary>

From the animation itself, not from a guess. `scripts/sfx-cues.mjs` walks the finished GSAP timeline in Chrome, classifies every motion into a family (camera move → whoosh, object landing → impact, stroke drawing → pen, word appearing → paper), and prunes the list to a density the ear can follow. `scripts/sfx-mix.mjs` then places the bundled takes onto the rendered MP4 frame-exactly, ducks the sustained families under the narration, and **copies** the video stream — so retuning the sound never re-renders the picture. Effects are never placed by hand and never embedded in `index.html`.
</details>

<details>
<summary><b>Can I edit talking-head avatar videos and add captions?</b></summary>

Yes! Place your talking-head video in `assets/avatar.mp4`, run `python scripts/elevenlabs_audio.py stt --file assets/avatar.mp4` to extract word timestamps, and use the GSAP synchronization pattern in `references/elevenlabs-audio.md` to overlay kinetic pop typography, animated badges, and graphic lower-thirds locked to the speaker's words.
</details>

<details>
<summary><b>If I only have a script, how is the voiceover created?</b></summary>

Provide your script in markdown or plain text, then run `python scripts/elevenlabs_audio.py tts --file vo-script.md --voice george --output assets/vo.mp3`. It generates the audio voiceover along with `assets/vo-timestamps.json` containing exact start and end times for every word and sentence, allowing the GSAP timeline to re-time itself automatically.
</details>

<details>
<summary><b>Will every video end up looking the same?</b></summary>

That is the main thing the skill prevents. The palette and shapes come from your brand, the structure comes from a concept chosen for your product, and each project must differ from the previous one in both skin and structure.
</details>

<details>
<summary><b>Can I give it a reference video?</b></summary>

Yes. The agent takes rhythm, energy, and motion language from it — not the palette, fonts, layout, scene order, or signature moments.
</details>

<details>
<summary><b>Do I need photos?</b></summary>

Only for photo-based styles. Use your own, a licensed stock set, or let the agent generate fictional people and props through an image MCP. Otherwise pick an illustrated or typographic style.
</details>

<details>
<summary><b>Can I use video clips?</b></summary>

Yes. Clips become footage layers: trimmed, masked, graded, and animated with the rest of the scene, always in sync with the timeline — including frame-by-frame MP4 export. Use your own footage, licensed stock, or clips generated through a video MCP.
</details>

<details>
<summary><b>Can it build in After Effects?</b></summary>

Yes, for cartoon explainers: with After Effects open and the Higgsfield MCP bridge connected, the agent builds compositions, characters, and keyframes directly in AE.
</details>

## Contributing

Issues and pull requests are welcome. When you add a rule, describe which failure it prevents and offer it as a menu option rather than a single "right answer". Bump `version` in `SKILL.md` and the plugin manifests, and add a line to `CHANGELOG.md`.

## Credits & Acknowledgments

**Motion Bang Bang** is an independent project forked and adapted from [**Bang Motion**](https://github.com/bangtutorial/bang-motion), originally conceived and developed by [**Bang Tutorial**](https://youtube.com/bangtutorial).
Immense gratitude and credit go to Bang Tutorial for establishing the foundational motion design architecture, the Anti-PPT methodology, starter templates, and creative directions that power this skill.

## License

[MIT](LICENSE) © 2026 lowfatgeek · Based on [Bang Motion](https://github.com/bangtutorial/bang-motion) © 2026 [Bang Tutorial](https://youtube.com/bangtutorial)
