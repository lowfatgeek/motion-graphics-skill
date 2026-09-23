#!/usr/bin/env python3
"""
Motion Bang Bang — ElevenLabs Audio Integration (TTS & STT)
Zero-dependency Python CLI tool for:
  1. Text-to-Speech (TTS) with word & sentence timestamps for GSAP explainer synchronization.
  2. Speech-to-Text (STT) via ElevenLabs Scribe for transcribing audio/video (talking-head avatars),
     generating word-level kinetic typography cues, .srt and .vtt subtitles.
  3. Voices listing and inspection.
  4. GSAP synchronization boilerplate generation.

Usage:
  python scripts/elevenlabs_audio.py voices
  python scripts/elevenlabs_audio.py tts --text "Hello world" --output assets/vo.mp3
  python scripts/elevenlabs_audio.py tts --file vo-script.md --voice george --output assets/vo.mp3
  python scripts/elevenlabs_audio.py stt --file avatar.mp4 --output assets/transcript.json --srt assets/captions.srt
  python scripts/elevenlabs_audio.py sync-template
"""

import os
import sys
import json
import base64
import argparse
import mimetypes
from pathlib import Path
import urllib.request
import urllib.error

# Common ElevenLabs preset voices mapped to their official Voice IDs
PRESET_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",      # Calm, young American female
    "adam": "pNInz6obpgDQGcFmaJgB",        # Deep, narrative American male
    "charlie": "IKne3meq5aSn9XLyUdCD",     # Confident, Australian male
    "george": "JBFqnCBsd6RMkjVDRZzb",      # Warm, British storyteller
    "sarah": "EXAVITQu4vr4xnSDxMaL",       # Reassuring, confident American female
    "brian": "nPczCjzI2devNBz1zQrb",       # Deep, resonant narrator
    "laura": "FGY2WhTYpPnrIDTdsKH5",       # Quirky, upbeat American female
    "river": "SAz9YHcvj6GT2YYXdXww",       # Confident, natural American
    "josh": "TxGEqnHWrfWFTfGW9XjX",        # Young, conversational American male
    "alice": "Xb7hH8MSUJpSbSDYk0k2",       # Confident, articulate British female
    "bill": "pqHfZKP75CvOlQylNhV4",        # Trustworthy, mature American male
    "callum": "N2lVS1w4EtoT3dr4eOWO",      # Intense, dramatic Transatlantic male
    "chris": "iP95p4xoKVk53GoZ742B",       # Conversational, casual American male
    "daniel": "onwK4e9ZLuTAKqWW03F9",      # Authoritative, deep British male
    "eric": "cjVigY5qzO86Huf0OWal",        # Friendly, natural American male
    "jessica": "cgSgspJ2msm6clMCkdW9",     # Playful, bright American female
    "liam": "TX3LPaxmHKxFdv7VOQHJ",        # Articulate, young American male
    "matilda": "XrExE9yKIg1WjnnlVkGX",     # Warm, friendly American female
    "will": "bIHbv24MWmeRgasZH58o",        # Friendly, warm American male
}

API_BASE = "https://api.elevenlabs.io/v1"


def get_api_key(args_key=None):
    """Retrieve API key from argument, environment variable, or .env file."""
    if args_key:
        return args_key
    env_key = os.environ.get("ELEVENLABS_API_KEY")
    if env_key:
        return env_key

    # Check for .env file in current directory or repo root
    cwd = Path.cwd()
    search_paths = [cwd / ".env", cwd.parent / ".env"]
    for p in search_paths:
        if p.exists():
            try:
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("ELEVENLABS_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
            except Exception:
                pass

    print("\n[ERROR] ELEVENLABS_API_KEY not found!")
    print("Please set the environment variable:")
    print("  Windows PowerShell: $env:ELEVENLABS_API_KEY=\"sk_...\"")
    print("  Linux/macOS bash:   export ELEVENLABS_API_KEY=\"sk_...\"")
    print("Or pass --api-key <your_key> on the command line.\n")
    sys.exit(1)


def resolve_voice_id(name_or_id):
    """Resolve a friendly name alias to ElevenLabs Voice ID."""
    key = name_or_id.lower().strip()
    return PRESET_VOICES.get(key, name_or_id)


def api_request(url, method="GET", data=None, headers=None):
    """Perform HTTP request using standard urllib."""
    headers = headers or {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        return e.code, err_msg
    except Exception as e:
        return 500, str(e)


# ---------------------------------------------------------------------------
# TTS: Text-to-Speech with Character & Word Alignment
# ---------------------------------------------------------------------------

def parse_alignment_to_words_and_sentences(alignment, original_text):
    """
    Parse character alignment data from ElevenLabs /with-timestamps endpoint
    into structured word-level and sentence-level timestamps.
    """
    chars = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])

    if not chars or len(chars) != len(starts) or len(chars) != len(ends):
        return {"words": [], "sentences": [], "pauses": [], "duration": 0.0}

    words = []
    current_word = []
    word_start = None
    last_end = 0.0

    for i, ch in enumerate(chars):
        s = starts[i]
        e = ends[i]
        last_end = max(last_end, e)

        # Check if character is whitespace
        if ch.isspace():
            if current_word:
                word_str = "".join(current_word)
                words.append({
                    "word": word_str,
                    "start": round(word_start, 3),
                    "end": round(prev_end, 3),
                    "duration": round(prev_end - word_start, 3)
                })
                current_word = []
                word_start = None
        else:
            if word_start is None:
                word_start = s
            current_word.append(ch)
            prev_end = e

    if current_word and word_start is not None:
        words.append({
            "word": "".join(current_word),
            "start": round(word_start, 3),
            "end": round(last_end, 3),
            "duration": round(last_end - word_start, 3)
        })

    # Group words into sentences based on punctuation and pauses
    sentences = []
    pauses = []
    current_sentence_words = []
    sentence_start = None

    for i, w in enumerate(words):
        if sentence_start is None:
            sentence_start = w["start"]
        current_sentence_words.append(w)

        # Detect pause before next word if gap >= 0.35s
        is_last_word = (i == len(words) - 1)
        has_punctuation = any(w["word"].endswith(p) for p in [".", "!", "?", "\n"])
        has_comma = any(w["word"].endswith(p) for p in [",", ";", ":"])

        if not is_last_word:
            gap = round(words[i + 1]["start"] - w["end"], 3)
            if gap >= 0.35:
                pauses.append({
                    "after_word": w["word"],
                    "start": w["end"],
                    "end": words[i + 1]["start"],
                    "duration": gap
                })

        # Cut sentence on punctuation or significant pause (>= 0.6s) or end of words
        should_split = False
        if is_last_word:
            should_split = True
        elif has_punctuation:
            should_split = True
        elif not is_last_word and (words[i + 1]["start"] - w["end"]) >= 0.6:
            should_split = True

        if should_split and current_sentence_words:
            sent_text = " ".join(item["word"] for item in current_sentence_words)
            sent_end = current_sentence_words[-1]["end"]
            sentences.append({
                "index": len(sentences) + 1,
                "text": sent_text,
                "start": round(sentence_start, 3),
                "end": round(sent_end, 3),
                "duration": round(sent_end - sentence_start, 3),
                "word_count": len(current_sentence_words)
            })
            current_sentence_words = []
            sentence_start = None

    total_duration = round(last_end, 3)
    return {
        "words": words,
        "sentences": sentences,
        "pauses": pauses,
        "duration": total_duration,
        "word_count": len(words)
    }


def cmd_tts(args):
    """Execute Text-to-Speech request with timestamps."""
    api_key = get_api_key(args.api_key)

    # Resolve text input
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[ERROR] Script file not found: {args.file}")
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8")
        # Strip markdown headers or comments if user asks
        lines = [line.strip() for line in text.splitlines()]
        text = " ".join([l for l in lines if l and not l.startswith("#") and not l.startswith("<!--")])
    elif args.text:
        text = args.text.strip()
    else:
        print("[ERROR] Please provide speech text via --text '...' or --file <path>.")
        sys.exit(1)

    voice_id = resolve_voice_id(args.voice)
    model_id = args.model

    print(f"\n[TTS] Generating voiceover...")
    print(f"  Voice: {args.voice} ({voice_id})")
    print(f"  Model: {model_id}")
    print(f"  Chars: {len(text)} | Approx words: {len(text.split())}")

    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": args.stability,
            "similarity_boost": args.similarity,
            "style": args.style,
            "use_speaker_boost": True
        }
    }

    url = f"{API_BASE}/text-to-speech/{voice_id}/with-timestamps"
    if args.output_format:
        url += f"?output_format={args.output_format}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    status, response = api_request(url, method="POST", data=json.dumps(payload).encode("utf-8"), headers=headers)
    if status != 200:
        print(f"\n[ERROR] ElevenLabs API error ({status}):")
        try:
            err_json = json.loads(response)
            print(json.dumps(err_json, indent=2))
        except Exception:
            print(response)
        sys.exit(1)

    data = json.loads(response.decode("utf-8"))
    audio_base64 = data.get("audio_base64")
    alignment = data.get("alignment", {})

    if not audio_base64:
        print("[ERROR] No audio data returned from ElevenLabs API.")
        sys.exit(1)

    audio_bytes = base64.b64decode(audio_base64)

    # Save audio file
    out_audio = Path(args.output)
    out_audio.parent.mkdir(parents=True, exist_ok=True)
    out_audio.write_bytes(audio_bytes)
    print(f"[OK] Audio saved: {out_audio} ({len(audio_bytes):,} bytes)")

    # Parse timestamps
    timing_data = parse_alignment_to_words_and_sentences(alignment, text)
    timing_data["voice_id"] = voice_id
    timing_data["model_id"] = model_id
    timing_data["audio_file"] = str(out_audio.as_posix())

    # Calculate WPM
    dur_min = timing_data["duration"] / 60.0
    wpm = round(timing_data["word_count"] / dur_min) if dur_min > 0 else 0
    timing_data["words_per_minute"] = wpm

    # Save timestamps JSON
    out_json = Path(args.timestamps)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(timing_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Timestamps saved: {out_json}")

    # Generate GSAP cues JS if requested
    if args.cues:
        out_cues = Path(args.cues)
        generate_gsap_cues_file(timing_data, out_cues)
        print(f"[OK] GSAP Cues saved: {out_cues}")

    # Print summary table
    print("\n" + "=" * 65)
    print(f"  VOICEOVER TIMING SUMMARY (Duration: {timing_data['duration']}s | WPM: {wpm})")
    print("=" * 65)
    print(f"{'#':<3} | {'START':<7} | {'END':<7} | {'DUR':<6} | {'SENTENCE / TEXT'}")
    print("-" * 65)
    for s in timing_data["sentences"]:
        short_txt = (s['text'][:42] + '...') if len(s['text']) > 45 else s['text']
        print(f"{s['index']:<3} | {s['start']:>6.2f}s | {s['end']:>6.2f}s | {s['duration']:>5.2f}s | {short_txt}")
    print("=" * 65)
    if timing_data["pauses"]:
        print(f"Detected {len(timing_data['pauses'])} natural pauses (>= 0.35s) ideal for scene cuts.")
    print(f"\nGSAP Timeline sync cue: tl.addLabel('scene_start', 0.0);")
    print(f"HTML audio element:    <audio id=\"vo\" src=\"{out_audio.as_posix()}\" preload=\"auto\"></audio>\n")


# ---------------------------------------------------------------------------
# STT: Speech-to-Text via ElevenLabs Scribe API
# ---------------------------------------------------------------------------

def build_multipart_form(fields, file_field_name, file_path):
    """Build multipart/form-data payload with streaming support."""
    boundary = "----WebKitFormBoundaryMotionBangBang" + os.urandom(8).hex()
    body = bytearray()

    for k, v in fields.items():
        if v is None:
            continue
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{v}\r\n".encode("utf-8"))

    mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "application/octet-stream"
    filename = Path(file_path).name

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="{file_field_name}"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"))
    body.extend(Path(file_path).read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    return body, f"multipart/form-data; boundary={boundary}"


def format_timestamp_srt(seconds):
    """Format seconds into SRT timestamp: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds):
    """Format seconds into WebVTT timestamp: HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def group_words_into_captions(words, max_words=6, max_duration=2.5, pause_break=0.4):
    """Group individual words into comfortable 1-2 line caption segments."""
    captions = []
    current_words = []
    seg_start = None

    for i, w in enumerate(words):
        if seg_start is None:
            seg_start = w["start"]
        current_words.append(w)

        is_last = (i == len(words) - 1)
        current_dur = w["end"] - seg_start
        has_punctuation = any(w["text"].endswith(p) for p in [".", "!", "?", "\n"])

        split = False
        if is_last:
            split = True
        elif len(current_words) >= max_words or current_dur >= max_duration:
            split = True
        elif has_punctuation:
            split = True
        elif not is_last and (words[i + 1]["start"] - w["end"]) >= pause_break:
            split = True

        if split and current_words:
            captions.append({
                "index": len(captions) + 1,
                "start": round(seg_start, 3),
                "end": round(current_words[-1]["end"], 3),
                "text": " ".join(item["text"] for item in current_words),
                "speaker": current_words[0].get("speaker_id"),
                "words": current_words
            })
            current_words = []
            seg_start = None

    return captions


def export_srt(captions, srt_path):
    """Export caption segments to SubRip (.srt) format."""
    lines = []
    for cap in captions:
        lines.append(str(cap["index"]))
        lines.append(f"{format_timestamp_srt(cap['start'])} --> {format_timestamp_srt(cap['end'])}")
        lines.append(cap["text"])
        lines.append("")
    Path(srt_path).write_text("\n".join(lines), encoding="utf-8")


def export_vtt(captions, vtt_path):
    """Export caption segments to WebVTT (.vtt) format."""
    lines = ["WEBVTT\n"]
    for cap in captions:
        lines.append(f"{format_timestamp_vtt(cap['start'])} --> {format_timestamp_vtt(cap['end'])}")
        lines.append(cap["text"])
        lines.append("")
    Path(vtt_path).write_text("\n".join(lines), encoding="utf-8")


def cmd_stt(args):
    """Execute Speech-to-Text transcription via ElevenLabs Scribe API."""
    api_key = get_api_key(args.api_key)
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERROR] Audio/video file not found: {args.file}")
        sys.exit(1)

    print(f"\n[STT] Transcribing audio with ElevenLabs Scribe...")
    print(f"  File: {file_path} ({file_path.stat().st_size:,} bytes)")
    print(f"  Model: {args.model}")

    fields = {
        "model_id": args.model,
        "timestamps_granularity": "word",
        "tag_audio_events": "true" if args.tag_events else "false",
        "diarize": "true" if args.diarize else "false",
    }
    if args.language:
        fields["language_code"] = args.language

    body, content_type = build_multipart_form(fields, "file", file_path)
    url = f"{API_BASE}/speech-to-text"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": content_type
    }

    status, response = api_request(url, method="POST", data=body, headers=headers)
    if status != 200:
        print(f"\n[ERROR] ElevenLabs STT API error ({status}):")
        try:
            err_json = json.loads(response)
            print(json.dumps(err_json, indent=2))
        except Exception:
            print(response)
        sys.exit(1)

    stt_data = json.loads(response.decode("utf-8"))
    raw_words = stt_data.get("words", [])

    # Filter actual spoken words (ignore pure spacing elements or audio tags)
    clean_words = []
    for w in raw_words:
        w_type = w.get("type", "word")
        txt = w.get("text", "").strip()
        if w_type == "word" and txt:
            clean_words.append({
                "text": txt,
                "start": round(w.get("start", 0.0), 3),
                "end": round(w.get("end", 0.0), 3),
                "duration": round(w.get("end", 0.0) - w.get("start", 0.0), 3),
                "speaker": w.get("speaker_id")
            })

    captions = group_words_into_captions(clean_words)

    result = {
        "source_file": str(file_path.as_posix()),
        "language_code": stt_data.get("language_code"),
        "language_probability": stt_data.get("language_probability"),
        "full_text": stt_data.get("text"),
        "total_words": len(clean_words),
        "total_captions": len(captions),
        "duration": clean_words[-1]["end"] if clean_words else 0.0,
        "captions": captions,
        "words": clean_words
    }

    # Save output JSON
    out_json = Path(args.output)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Transcript saved: {out_json}")

    # Export SRT if requested
    if args.srt:
        out_srt = Path(args.srt)
        out_srt.parent.mkdir(parents=True, exist_ok=True)
        export_srt(captions, out_srt)
        print(f"[OK] SRT Subtitles saved: {out_srt}")

    # Export WebVTT if requested
    if args.vtt:
        out_vtt = Path(args.vtt)
        out_vtt.parent.mkdir(parents=True, exist_ok=True)
        export_vtt(captions, out_vtt)
        print(f"[OK] WebVTT Subtitles saved: {out_vtt}")

    # Export GSAP cues if requested
    if args.cues:
        out_cues = Path(args.cues)
        generate_gsap_cues_file({
            "words": [{"word": w["text"], "start": w["start"], "end": w["end"]} for w in clean_words],
            "sentences": [{"index": c["index"], "text": c["text"], "start": c["start"], "end": c["end"]} for c in captions],
            "duration": result["duration"]
        }, out_cues)
        print(f"[OK] GSAP Cues saved: {out_cues}")

    # Print summary
    print("\n" + "=" * 65)
    print(f"  TRANSCRIPTION SUMMARY (Language: {result['language_code']} | Words: {len(clean_words)})")
    print("=" * 65)
    print(f"{'#':<3} | {'START':<7} | {'END':<7} | {'CAPTION TEXT'}")
    print("-" * 65)
    for c in captions[:10]:
        short_txt = (c['text'][:45] + '...') if len(c['text']) > 48 else c['text']
        print(f"{c['index']:<3} | {c['start']:>6.2f}s | {c['end']:>6.2f}s | {short_txt}")
    if len(captions) > 10:
        print(f"... and {len(captions) - 10} more caption segments.")
    print("=" * 65 + "\n")


# ---------------------------------------------------------------------------
# GSAP Cues Generator & Sync Templates
# ---------------------------------------------------------------------------

def generate_gsap_cues_file(timing_data, output_path):
    """Generate a clean JavaScript module with timing markers for GSAP timelines."""
    content = f"""// Generated by Motion Bang Bang (ElevenLabs Audio Sync)
// Total Duration: {timing_data.get('duration', 0.0)}s

export const AUDIO_DURATION = {timing_data.get('duration', 0.0)};

export const SENTENCE_CUES = {json.dumps(timing_data.get('sentences', []), indent=2)};

export const WORD_CUES = {json.dumps(timing_data.get('words', []), indent=2)};

/**
 * Helper to bind GSAP timeline to word kinetic typography
 * @param {{ timeline: gsap.core.Timeline, container: HTMLElement, wordClass?: string }}
 */
export function buildKineticTypography({{ timeline, container, wordClass = 'kinetic-word' }}) {{
  container.innerHTML = WORD_CUES.map(w => `<span class="${{wordClass}}" data-start="${{w.start}}">${{w.word || w.text}}</span> `).join('');
  const elements = container.querySelectorAll(`.${{wordClass}}`);

  WORD_CUES.forEach((cue, i) => {{
    const el = elements[i];
    timeline.fromTo(el,
      {{ opacity: 0.25, scale: 0.95, color: '#888' }},
      {{ opacity: 1, scale: 1.08, color: '#fff', duration: 0.15, ease: 'back.out(2)' }},
      cue.start
    );
    timeline.to(el,
      {{ scale: 1, color: '#ddd', duration: 0.2 }},
      cue.end
    );
  }});
}}
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def cmd_voices(args):
    """List available voices from ElevenLabs account."""
    api_key = get_api_key(args.api_key)
    url = f"{API_BASE}/voices"
    headers = {"xi-api-key": api_key}

    status, response = api_request(url, headers=headers)
    if status != 200:
        print(f"[ERROR] Failed to fetch voices ({status}): {response}")
        sys.exit(1)

    data = json.loads(response.decode("utf-8"))
    voices = data.get("voices", [])

    if args.search:
        q = args.search.lower()
        voices = [v for v in voices if q in v["name"].lower() or q in v.get("category", "").lower()]

    if args.category:
        voices = [v for v in voices if v.get("category") == args.category]

    if args.json:
        print(json.dumps(voices, indent=2))
        return

    print("\n" + "=" * 80)
    print(f"  ELEVENLABS VOICES ({len(voices)} available)")
    print("=" * 80)
    print(f"{'NAME':<28} | {'VOICE ID':<22} | {'CATEGORY':<12} | {'LABELS'}")
    print("-" * 80)
    for v in voices:
        labels = v.get("labels") or {}
        lbl_str = ", ".join(f"{k}:{val}" for k, val in list(labels.items())[:3])
        print(f"{v['name'][:27]:<28} | {v['voice_id']:<22} | {v.get('category', ''):<12} | {lbl_str}")
    print("=" * 80)
    print("\nTip: Pass a voice name (e.g. --voice george) or Voice ID to 'tts'.\n")


def cmd_sync_template(args):
    """Print GSAP audio & video sync starter code."""
    template = """
<!-- ========================================================================
     MOTION BANG BANG -- GSAP AUDIO & TALKING-HEAD VIDEO SYNC PATTERN
     ======================================================================== -->

<!-- 1. For Audio Voiceover (TTS) -->
<audio id="vo" src="assets/vo.mp3" preload="auto"></audio>

<!-- 2. Or for Talking-Head Avatar Video (STT) -->
<video id="talking-head" src="assets/avatar.mp4" playsinline preload="auto" muted></video>

<!-- 3. Dynamic Kinetic Captions Container -->
<div id="captions" class="cinematic-captions"></div>

<script type="module">
  import gsap from 'https://cdn.jsdelivr.net/npm/gsap@3.12.5/+esm';

  const tl = gsap.timeline({ paused: true });
  const vo = document.querySelector('#vo');
  const video = document.querySelector('#talking-head');
  const media = vo.getAttribute('src') ? vo : video;

  let mediaReady = false;

  function start() {
    tl.play(0);
    if (media) {
      media.currentTime = 0;
      media.play().then(() => mediaReady = true).catch(() => {});
    }
  }

  // Frame-accurate lock between GSAP ticker and media playback
  gsap.ticker.add(() => {
    if (!mediaReady || tl.paused() || !media) return;
    const diff = Math.abs(media.currentTime - tl.time());
    if (diff > 0.08) {
      media.currentTime = tl.time();
    }
  });

  // Autoplay with safe interaction fallback
  if (media) {
    media.play().then(() => {
      mediaReady = true;
      media.currentTime = 0;
      tl.play(0);
    }).catch(() => {
      const unlock = () => {
        window.removeEventListener('pointerdown', unlock);
        window.removeEventListener('keydown', unlock);
        start();
      };
      window.addEventListener('pointerdown', unlock);
      window.addEventListener('keydown', unlock);
    });
  } else {
    tl.play(0);
  }
</script>
"""
    print(template)


# ---------------------------------------------------------------------------
# CLI Argument Parser Setup
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Motion Bang Bang -- ElevenLabs TTS & STT Audio Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python scripts/elevenlabs_audio.py voices --search george
  python scripts/elevenlabs_audio.py tts --text "Hello from Motion Bang Bang" --voice george --output assets/vo.mp3
  python scripts/elevenlabs_audio.py tts --file vo-script.md --voice rachel --timestamps assets/vo-timestamps.json --cues assets/vo-cues.js
  python scripts/elevenlabs_audio.py stt --file avatar.mp4 --output assets/transcript.json --srt assets/captions.srt
  python scripts/elevenlabs_audio.py sync-template
"""
    )
    parser.add_argument("--api-key", help="ElevenLabs API Key (defaults to ELEVENLABS_API_KEY environment variable)")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # Command: tts
    tts_parser = subparsers.add_parser("tts", help="Generate Text-to-Speech audio with word & sentence timestamps")
    tts_parser.add_argument("--text", help="Text to speak")
    tts_parser.add_argument("--file", help="Path to markdown or text file containing script")
    tts_parser.add_argument("--voice", default="george", help="Voice name alias (e.g. george, rachel, adam) or Voice ID (default: george)")
    tts_parser.add_argument("--model", default="eleven_multilingual_v2", help="ElevenLabs model ID (default: eleven_multilingual_v2)")
    tts_parser.add_argument("--output", default="assets/vo.mp3", help="Output audio file path (default: assets/vo.mp3)")
    tts_parser.add_argument("--timestamps", default="assets/vo-timestamps.json", help="Output JSON timestamps file path (default: assets/vo-timestamps.json)")
    tts_parser.add_argument("--cues", help="Optional output JS module file for GSAP cues (e.g. assets/vo-cues.js)")
    tts_parser.add_argument("--output-format", default="mp3_44100_128", help="Audio output format (default: mp3_44100_128)")
    tts_parser.add_argument("--stability", type=float, default=0.5, help="Voice stability (0.0 to 1.0, default: 0.5)")
    tts_parser.add_argument("--similarity", type=float, default=0.75, help="Similarity boost (0.0 to 1.0, default: 0.75)")
    tts_parser.add_argument("--style", type=float, default=0.0, help="Style exaggeration (0.0 to 1.0, default: 0.0)")

    # Command: stt
    stt_parser = subparsers.add_parser("stt", help="Transcribe audio/video to text with word timestamps (ElevenLabs Scribe)")
    stt_parser.add_argument("--file", required=True, help="Path to audio or video file (mp3, wav, mp4, mov, etc.)")
    stt_parser.add_argument("--model", default="scribe_v1", help="STT model ID (default: scribe_v1)")
    stt_parser.add_argument("--language", help="Optional ISO language code (e.g. en, id, ja, fr, es)")
    stt_parser.add_argument("--output", default="assets/transcript.json", help="Output JSON transcript path (default: assets/transcript.json)")
    stt_parser.add_argument("--srt", help="Optional output SRT subtitle path (e.g. assets/captions.srt)")
    stt_parser.add_argument("--vtt", help="Optional output WebVTT subtitle path (e.g. assets/captions.vtt)")
    stt_parser.add_argument("--cues", help="Optional output JS module file for GSAP word cues (e.g. assets/captions-cues.js)")
    stt_parser.add_argument("--tag-events", action="store_true", default=True, help="Tag audio events like laughter/applause (default: True)")
    stt_parser.add_argument("--diarize", action="store_true", default=False, help="Identify speaker IDs (default: False)")

    # Command: voices
    voices_parser = subparsers.add_parser("voices", help="List available ElevenLabs voices")
    voices_parser.add_argument("--search", help="Search voices by name or description")
    voices_parser.add_argument("--category", help="Filter by category (premade, cloned, generated)")
    voices_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: sync-template
    subparsers.add_parser("sync-template", help="Print GSAP audio & video sync boilerplate code")

    args = parser.parse_args()

    if args.command == "tts":
        cmd_tts(args)
    elif args.command == "stt":
        cmd_stt(args)
    elif args.command == "voices":
        cmd_voices(args)
    elif args.command == "sync-template":
        cmd_sync_template(args)


if __name__ == "__main__":
    main()
