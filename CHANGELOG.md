# Changelog

## 1.21.0 — 2026-09-26

**Sound design: effects that land on the motion, mixed after the render**
- **SFX bundle in `assets/sfx/`**: 20 generated takes across 9 motion families (`impact`, `stamp`, `whoosh`, `transition`, `accent`, `paper`, `pen`, `ui`, `ambience`), all 48 kHz / stereo / PCM-16 and peaked to −3 dBFS by pure gain, so intensity stays a mix-time parameter. `library.json` holds the prompts and the per-family mix intent; `manifest.json` and `SOURCES.md` hold measured provenance; `_preview.wav` is one listen for the whole bundle.
- **`scripts/sfx-cues.mjs`** mines the cue sheet out of the finished timeline instead of a hand-written list: it walks `window.OPENER.tl` in system Chrome, classifies each motion by what actually moved (with `data:"<verb>"` as the author's override), and prunes to a listenable density — printing candidates → kept and the reason every cue was dropped. Validated run: 824 tweens → 422 candidates → 219 cues over 285 s.
- **`scripts/sfx-mix.mjs`** places that sheet on a rendered MP4: one stem per family, frame-snapped `adelay`, strength-driven gain, ±2.5‰ pitch spread seeded from the frame number, sidechain ducking of the sustained families under the voice, limiter, then muxes with **`-c:v copy`** — the video payload comes out bit-identical, so retuning audio never re-renders a frame.
- **Verification is numeric**: raw video payload hash, frame count, integrated loudness, true peak, ducking depth measured across a speech window and a gap, and stem event onsets matched against the cue sheet (median offset 0.0000 s).
- **`scripts/elevenlabs_audio.py`** gained the `sfx` subcommand (`--spec`, `--only`, `--force`, `--preview`, `--renormalize`) plus a sample-accurate trimmer and an equal-power loop crossfader — `--renormalize` re-applies the contract to files on disk with no API call, so contract changes are free.
- New reference `references/sound-design.md` (bundle contract, mining rules, density targets, ducking, ceiling, checklist, and the traps found the hard way). `SKILL.md` gains workflow step 6b, four checklist items, one trap and the package rows; `references/explainer.md` Step Zero now offers "VO + sound design" as an audio configuration.

## 1.20.0 — 2026-09-23

**ElevenLabs Audio Integration (TTS & STT)**
- Built-in zero-dependency CLI tool (`scripts/elevenlabs_audio.py`) for Text-to-Speech (TTS) and Speech-to-Text (STT) powered by ElevenLabs.
- **TTS with Word & Sentence Timestamps**: Converts voiceover scripts into studio-grade voiceover (`assets/vo.mp3`) with exact character, word, and sentence alignments (`assets/vo-timestamps.json`), plus natural pause detection for GSAP scene cuts.
- **STT for Talking-Head Avatars & Captions**: Transcribes pre-recorded video/audio using ElevenLabs Scribe (`scribe_v1`) into word-level timestamps (`assets/transcript.json`), SubRip subtitles (`.srt`), and WebVTT (`.vtt`).
- **GSAP Kinetic Typography Helpers**: Generates cue points (`assets/vo-cues.js`, `assets/captions-cues.js`) to animate word pops, color highlights, and kinetic typography in sync with spoken dialogue.
- Added comprehensive documentation and code recipes in `references/elevenlabs-audio.md`.

## 1.19.0 — 2026-09-15

**Ukuran shot — kamera ke elemen**
- "Zoom in-out" dirumuskan sebagai pergantian ukuran shot (wide ↔ medium close-up ↔ close-up) ke
  elemen yang sedang bercerita, bukan napas kamera beberapa persen yang hampir tak terlihat.
- Panduan memilih target dan waktu, dua tempo gerak, rig kamera dengan skala dari ukuran elemen
  dan klem tepi dunia, label di lapisan layar (`references/techniques.md` §3b).

## 1.18.0 — 2026-09-15

**Video sebagai layer footage**
- Semua starter membawa helper `clip(el, {at, in, out, rate, hold})`: klip video mengikuti jam
  timeline — sinkron saat diputar, tepat saat scrub — dan bisa dipotong, diperlambat, ditahan,
  di-mask, serta dianimasikan bersama elemen lain.
- `scripts/snap.mjs` dan `scripts/export-frames.mjs` menunggu frame klip siap, sehingga ekspor MP4
  tetap presisi frame.
- Panduan pemakaian, sumber klip (file sendiri, generate lewat MCP, stok berlisensi), format, dan
  pola layout di `references/techniques.md` §9b.
- Deliverable tetap `index.html` (+ `assets/` bila memakai klip atau audio), tanpa file peluncur.

## 1.17.0 — 2026-09-14

**Opener dan promo**
- Kerangka dipilih, bukan diwarisi: tiga kandidat konsep dari menu 19 konsep, sidik jari
  struktur yang dibandingkan dengan proyek sebelumnya, komponen kanonik paling banyak dua,
  dan starter opener tanpa urutan adegan contoh (`references/opener-konsep.md`,
  `assets/starter-opener.html`).
- Contoh urutan tiap konsep adalah prinsip, bukan naskah: pembuka/penutup dan momen khas
  tidak disalin; palet, bentuk, dan properti diturunkan dari brand, tiap warna menyebut
  sumbernya.
- Panduan animasi UI untuk app/SaaS, kamera yang mengikuti klik penting, dan foto dalam
  opener (foto user, generate lewat MCP, atau stok berlisensi).

**Tipografi, latar, render**
- Sorotan kata opsional; judul dan klaim tanpa titik otomatis.
- Latar tidak pernah statis; warna latar boleh berganti kapan dibutuhkan dengan pemicu
  terlihat. Grainy gradient dengan jaga-jaga encode. Menu gaya render objek.

**Explainer**
- Enam gaya: aksi kontinu, kartun kolase, jurnalisme visual, katalog putih, sketsa vintage,
  dan kartun panggung (`references/explainer.md`, `references/kartun-panggung.md`).

**After Effects**
- Dibangun langsung lewat bridge/MCP Higgsfield (`references/ae-bridge-higgsfield.md`,
  `scripts/ae/bridge/`).

**Alat kerja**
- Verifikasi visual per detik kunci (`scripts/snap.mjs`), ekspor MP4
  (`scripts/export-frames.mjs`), pemotong jeda VO (`scripts/vo-pauses.html`).
