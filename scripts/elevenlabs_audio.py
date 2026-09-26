#!/usr/bin/env python3
"""
Motion Bang Bang — ElevenLabs Audio Integration (TTS, STT & SFX)
Zero-dependency Python CLI tool for:
  1. Text-to-Speech (TTS) with word & sentence timestamps for GSAP explainer synchronization.
  2. Speech-to-Text (STT) via ElevenLabs Scribe for transcribing audio/video (talking-head avatars),
     generating word-level kinetic typography cues, .srt and .vtt subtitles.
  3. Sound Effects (SFX) generation, normalised into a reusable skill bundle (see references/sound-design.md).
  4. Voices listing and inspection.
  5. GSAP synchronization boilerplate generation.

Usage:
  python scripts/elevenlabs_audio.py voices
  python scripts/elevenlabs_audio.py tts --text "Hello world" --output assets/vo.mp3
  python scripts/elevenlabs_audio.py tts --file vo-script.md --voice george --output assets/vo.mp3
  python scripts/elevenlabs_audio.py stt --file avatar.mp4 --output assets/transcript.json --srt assets/captions.srt
  python scripts/elevenlabs_audio.py sfx --text "rubber stamp pressed onto paper, dry, close mic" \
      --duration 0.6 --output assets/sfx/stamp/stamp-rubber-01.wav
  python scripts/elevenlabs_audio.py sfx --spec assets/sfx/library.json
  python scripts/elevenlabs_audio.py sync-template
"""

import os
import sys
import json
import base64
import argparse
import mimetypes
import subprocess
import tempfile
import shutil
import array
import math
import wave
import datetime
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
# SFX: Sound Effects generation + bundle normalisation
#
# ElevenLabs hands back raw PCM here, so the bundle is built without any
# lossy intermediate: 48 kHz / 16-bit / stereo WAV with the head trimmed to the
# first audible sample and a known peak. A sound placed by `adelay` is only
# frame-accurate if the file itself starts where the motion starts.
# ---------------------------------------------------------------------------

SFX_SAMPLE_RATE = 48000
SFX_PEAK_DBFS = -3.0        # 3 dB headroom so 2-3 hits on one frame stay clean
SFX_ONSET_DB = 45.0         # a sample counts as sound from the contract peak - 45 dB down
SFX_FLOOR_DB = -60.0        # ...but never lower than this, so a hissy take still gets trimmed
SFX_MIN_KEEP_S = 0.05       # a one-shot trimmed shorter than this lost its body to the tail gate
SFX_HEAD_WARN_MS = 15.0     # ~half a frame at 30 fps: beyond this the sound lands late
SFX_MIN_DURATION = 0.5      # API floor; one-shots are trimmed shorter afterwards
SFX_MAX_DURATION = 30
SFX_SOURCE = "elevenlabs /v1/sound-generation (output_format=pcm_48000)"
SFX_LICENSE_NOTE = (
    "Generated with an ElevenLabs account. Per ElevenLabs Terms of Use 4(c)(ii) the "
    "subscriber retains all rights in the Output, and 4(a) permits using Output outside "
    "the Services. Commercial use requires a PAID plan (Terms of Use 1(c): free tiers are "
    "non-commercial only). Record the plan tier in this manifest when the bundle is created."
)


def sfx_run(cmd):
    """Run an external tool with an argv list (no shell, so paths never need quoting)."""
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def sfx_gate_dbfs(peak_dbfs):
    """
    One place decides what counts as silence, so the value used to trim a file can never
    disagree with the value used to measure it afterwards. That disagreement was a real bug:
    trimming happened before gain-staging and reporting happened after, so a take that was
    provably trimmed came back wearing 69 ms of head silence.
    """
    return max(peak_dbfs - SFX_ONSET_DB, SFX_FLOOR_DB)


def sfx_probe(path, gate_dbfs=None):
    """
    Measure a PCM16 WAV with the stdlib rather than ffmpeg: exact duration, the offset of
    the first audible sample, RMS, peak and clip count. The bundle contract is defined in
    samples, so the peak must come from the samples, not from a lossy estimate.
    """
    with wave.open(str(path), "rb") as w:
        channels, rate, frames = w.getnchannels(), w.getframerate(), w.getnframes()
        data = w.readframes(frames)
    samples = array.array("h")
    samples.frombytes(data)
    if not samples:
        return {"duration_s": 0.0, "head_ms": None, "rms_dbfs": -120.0, "peak_dbfs": -120.0,
                "clipped": 0, "channels": channels, "sample_rate": rate}
    gate_dbfs = sfx_gate_dbfs(SFX_PEAK_DBFS) if gate_dbfs is None else gate_dbfs
    gate = (10 ** (gate_dbfs / 20.0)) * 32768.0
    peaks = [0] * max(1, channels)
    clipped = 0
    head = None
    for i, v in enumerate(samples):
        a = -v if v < 0 else v
        ch = i % channels
        if a > peaks[ch]:
            peaks[ch] = a
        if a >= 32760:
            clipped += 1
        if head is None and a > gate:
            head = i // channels
    peak = max(peaks)
    rms = math.sqrt(sum(v * v for v in samples) / float(len(samples)))
    to_db = lambda v: 20.0 * math.log10(v / 32768.0) if v > 0 else -120.0
    return {"duration_s": round(frames / float(rate), 4),
            "head_ms": round(head / float(rate) * 1000.0, 2) if head is not None else None,
            "rms_dbfs": round(to_db(rms), 2), "peak_dbfs": round(to_db(peak), 2),
            "clipped": clipped, "channels": channels, "sample_rate": rate}


def sfx_cut_silence(src, dst, gate_dbfs, tail=True):
    """
    Sample-accurate trim with the stdlib instead of ffmpeg's silenceremove. That filter
    compares a short window average against its threshold, so a soft attack -- a whoosh
    ramping up, the first milliseconds of a paper rustle -- makes it stop early and the file
    keeps tens of milliseconds of latency. `adelay` placement is only honest when the file
    starts where the sound starts, so the cut is done here instead. Returns the probe.
    """
    with wave.open(str(src), "rb") as w:
        channels, rate, frames = w.getnchannels(), w.getframerate(), w.getnframes()
        width = w.getsampwidth()
        data = w.readframes(frames)
    samples = array.array("h")
    samples.frombytes(data)
    gate = (10 ** (gate_dbfs / 20.0)) * 32768.0
    start = next((i // channels for i, v in enumerate(samples) if (-v if v < 0 else v) > gate), None)
    if start is None:
        raise RuntimeError("%s has no sample above %g dBFS -- nothing to keep"
                           % (Path(src).name, gate_dbfs))
    end = frames
    if tail:
        end = next(i // channels + 1 for i in range(len(samples) - 1, start * channels - 1, -1)
                   if (-samples[i] if samples[i] < 0 else samples[i]) > gate)
    with wave.open(str(dst), "wb") as out:
        out.setnchannels(channels)
        out.setsampwidth(width)
        out.setframerate(rate)
        out.writeframes(samples[start * channels:end * channels].tobytes())
    return sfx_probe(dst, gate_dbfs)


def sfx_wrap_wav(pcm_bytes, path, channels=1):
    """Wrap headerless PCM s16le into a WAV using the stdlib wave module."""
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(SFX_SAMPLE_RATE)
        w.writeframes(pcm_bytes)
    return path


def sfx_to_contract(src, dst, af=None):
    """One ffmpeg pass: sample rate, stereo, PCM 16, optional filter. Returns probe stats."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src)]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "2", "-ar", str(SFX_SAMPLE_RATE), "-c:a", "pcm_s16le", str(dst)]
    proc = sfx_run(cmd)
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg failed on %s: %s" % (src, (proc.stderr or "")[-900:]))
    return sfx_probe(dst)


def sfx_loop_xfade(src, dst, crossfade_ms=200.0):
    """
    Make a take actually loopable. The model's own loop flag does not guarantee it: what
    comes back is often a swell that ends several dB above where it starts, and a bed that
    steps in level every 6 s reads as a pulse. So the tail is moved to the front and
    crossfaded into the head, which is the DAW trick for turning any texture into a seam-free
    loop -- the loop point then joins two samples that were adjacent in the original file, so
    there is no join to hear. Costs one pass of arithmetic, no API call.
    Returns the probe of the (slightly shorter) loop.
    """
    with wave.open(str(src), "rb") as w:
        channels, rate, frames, width = w.getnchannels(), w.getframerate(), w.getnframes(), w.getsampwidth()
        data = w.readframes(frames)
    samples = array.array("h")
    samples.frombytes(data)
    n = int(rate * crossfade_ms / 1000.0)
    if channels * n * 2 >= len(samples) or n < 1:
        shutil.copyfile(str(src), str(dst))
        return sfx_probe(dst)
    head = samples[:channels * n]              # what follows the loop point
    tail = samples[len(samples) - channels * n:]
    body = samples[channels * n:len(samples) - channels * n]
    blended = array.array("h")
    for i in range(channels * n):
        t = (i // channels) / float(max(1, n - 1))
        out_g, in_g = math.sqrt(1.0 - t), math.sqrt(t)   # equal-power, uncorrelated noise sums flat
        v = tail[i] * out_g + head[i] * in_g
        blended.append(max(-32768, min(32767, int(v))))
    with wave.open(str(dst), "wb") as out:
        out.setnchannels(channels)
        out.setsampwidth(width)
        out.setframerate(rate)
        out.writeframes((blended + body).tobytes())
    return sfx_probe(dst)


def sfx_normalize(src, dst, tight=True, peak_dbfs=SFX_PEAK_DBFS, loop=False):
    """
    Bring one generated take to the bundle contract: 48 kHz / stereo / PCM 16-bit, gain-staged
    to a known peak by PURE GAIN (no limiting, so the dynamics of the take survive), then
    silence-trimmed front and back for one-shots so the file starts on its first audible
    sample. Gain comes first and trimming second because that is what makes the two agree:
    both then live on the same dBFS scale, and every bundle file lands at the same peak on
    purpose -- intensity is a mix-time parameter, not a property of the asset.
    A loop instead gets the crossfade treatment and keeps its length.
    Raises RuntimeError instead of exiting, so a batch build can keep going.
    """
    work = Path(tempfile.mkdtemp(prefix="mbb_sfx_"))
    try:
        base = work / "base.wav"
        stats = sfx_to_contract(src, base)
        if stats["peak_dbfs"] < -60:
            raise RuntimeError("take came back silent")
        gate = sfx_gate_dbfs(peak_dbfs)
        shaped = base
        if loop:
            shaped = work / "loop.wav"
            head_db, tail_db = sfx_loop_seam(base)
            if abs(tail_db - head_db) > 3.0:
                sfx_loop_xfade(base, shaped)
            else:
                # Already seamless -- crossfading twice would shorten the bed and blend blend.
                shutil.copyfile(str(base), str(shaped))
        staged = work / "gain.wav"
        stats = sfx_probe(shaped)
        delta = peak_dbfs - stats["peak_dbfs"]
        sfx_to_contract(shaped, staged, ("volume=%.2fdB" % delta) if abs(delta) > 0.1 else None)
        stage, stats = staged, None
        if tight:
            stage = work / "trim.wav"
            stats = sfx_cut_silence(staged, stage, gate)
            if stats["duration_s"] < SFX_MIN_KEEP_S:
                # The tail gate ate a short transient; keep the onset cut and let the decay run.
                loose = work / "trim-head-only.wav"
                alt = sfx_cut_silence(staged, loose, gate, tail=False)
                if alt["duration_s"] > stats["duration_s"]:
                    stage, stats = loose, alt
            if stats["duration_s"] < SFX_MIN_KEEP_S:
                raise RuntimeError("only %.2fs survived trimming -- the take is mostly silence"
                                   % stats["duration_s"])
        shutil.copyfile(str(stage), str(dst))
        return sfx_probe(dst, gate)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def sfx_quality(path, tight=True, loop=False):
    """Measure a finished bundle file against the contract; returns stats + warnings."""
    st = sfx_probe(path, sfx_gate_dbfs(SFX_PEAK_DBFS))
    warns = []
    if st["clipped"]:
        warns.append("%d clipped samples" % st["clipped"])
    if tight and st["head_ms"] is not None and st["head_ms"] > SFX_HEAD_WARN_MS:
        warns.append("head silence %s ms -- the sound will land late" % st["head_ms"])
    if tight and st["duration_s"] < SFX_MIN_KEEP_S:
        warns.append("only %.2fs survived trimming" % st["duration_s"])
    out = {"duration_s": st["duration_s"], "head_ms": st["head_ms"], "rms_dbfs": st["rms_dbfs"],
           "peak_dbfs": st["peak_dbfs"], "clipped": st["clipped"], "warnings": warns}
    if loop:
        head_db, tail_db = sfx_loop_seam(path)
        out["loop_seam_db"] = round(tail_db - head_db, 2)
        if abs(out["loop_seam_db"]) > 6.0:
            warns.append("loop seam level jumps %.1f dB" % out["loop_seam_db"])
    return out


def sfx_renormalize(path, tight=True, loop=False, peak_dbfs=SFX_PEAK_DBFS):
    """
    Re-apply the contract to a file that already exists -- no API call, so no cost. This is
    how the bundle gets repaired when the gate or the peak target changes.
    """
    work = Path(tempfile.mkdtemp(prefix="mbb_sfx_fix_"))
    try:
        tmp = work / "fix.wav"
        sfx_normalize(path, tmp, tight=tight, peak_dbfs=peak_dbfs, loop=loop)
        shutil.copyfile(str(tmp), str(path))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return sfx_quality(path, tight=tight, loop=loop)


def sfx_repair_one(asset, root, prior=None, peak_dbfs=SFX_PEAK_DBFS):
    """
    Fix pass for one bundle entry: re-apply the contract to the file we already own and
    refresh only the measured fields. The provenance in `prior` (prompt, source, date) is
    carried over, since nothing new was generated. Returns (record, None) or (None, error).
    """
    target = root / asset["file"]
    if not target.exists():
        return None, "%s does not exist yet -- run without --renormalize to generate it" % asset["file"]
    loop = bool(asset.get("loop"))
    tight = bool(asset.get("tight", True)) and not loop
    try:
        stats = sfx_renormalize(target, tight=tight, loop=loop, peak_dbfs=peak_dbfs)
    except (RuntimeError, OSError) as err:
        return None, str(err)
    rec = dict(prior or {})
    rec.update({
        "file": asset["file"].replace("\\", "/"),
        "family": asset.get("family", target.parent.name),
        "trigger": asset.get("trigger", []),
        "prompt": asset.get("prompt", rec.get("prompt", "")),
        "requested_s": asset.get("duration_seconds", rec.get("requested_s")),
        "loop": loop,
        "tight": tight,
        "sample_rate": SFX_SAMPLE_RATE,
        "channels": 2,
        "bit_depth": 16,
        "source": rec.get("source", SFX_SOURCE),
    })
    rec.update(stats)
    return rec, None


def sfx_loop_seam(path, window_ms=150.0):
    """
    A loop only reads as seamless if the level at its end matches the level at its start.
    Returns (head_rms_db, tail_rms_db) over a short window on each side. The window is a
    fifth of a second, not a few milliseconds, because that is roughly how long the ear
    integrates loudness: a 10 ms window just reports wherever a transient happened to land,
    which flags an even bed as broken.
    """
    with wave.open(str(path), "rb") as w:
        channels, rate = w.getnchannels(), w.getframerate()
        frames = w.getnframes()
        win = max(1, int(rate * window_ms / 1000.0))
        head = array.array("h"); head.frombytes(w.readframes(win))
        w.setpos(max(0, frames - win))
        tail = array.array("h"); tail.frombytes(w.readframes(win))
    def rms_db(chunk):
        left = chunk[0::channels] if channels > 1 else chunk
        if not left:
            return -120.0
        val = math.sqrt(sum(v * v for v in left) / float(len(left)))
        return 20.0 * math.log10(val / 32768.0) if val > 0 else -120.0
    return rms_db(head), rms_db(tail)


def sfx_request(api_key, prompt, duration, prompt_influence, loop):
    """POST /v1/sound-generation. Returns (pcm_bytes, None) or (None, error_text)."""
    payload = {"text": prompt, "duration_seconds": float(duration)}
    if prompt_influence is not None:
        payload["prompt_influence"] = float(prompt_influence)
    if loop:
        payload["loop"] = True
    url = "%s/sound-generation?output_format=pcm_48000" % API_BASE
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    status, response = api_request(url, method="POST",
                                   data=json.dumps(payload).encode("utf-8"), headers=headers)
    if status != 200:
        try:
            return None, json.dumps(json.loads(response), indent=2)
        except Exception:
            return None, str(response)[:2000]
    return response, None


def sfx_contract(peak_dbfs=SFX_PEAK_DBFS):
    """The contract is a property of this tool, so it is rewritten on every write -- a manifest
    can then never keep describing a rule the code stopped using."""
    return {"sample_rate": SFX_SAMPLE_RATE, "channels": 2, "bit_depth": 16,
            "peak_dbfs": peak_dbfs,
            "trim_gate_dbfs": "gain-staged first, then trimmed sample-accurately at "
                              "%g dBFS - %g dB (floor %g dBFS)" % (peak_dbfs, SFX_ONSET_DB, SFX_FLOOR_DB),
            "loop_crossfade_ms": 200,
            "placement": "ffmpeg adelay, sample-accurate at 48 kHz"}


def sfx_manifest_update(manifest_path, records, extra=None):
    """Merge records into manifest.json (keyed by relative file path), sorted by family."""
    manifest_path = Path(manifest_path)
    doc = {"version": 1, "license": SFX_LICENSE_NOTE, "contract": sfx_contract()}
    if manifest_path.exists():
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                doc.update(loaded)
        except Exception:
            pass
    for key, value in (extra or {}).items():
        if isinstance(value, dict) and isinstance(doc.get(key), dict):
            doc[key].update(value)
        else:
            doc[key] = value
    assets = {a["file"]: a for a in doc.get("assets", []) if isinstance(a, dict) and a.get("file")}
    for rec in records:
        assets[rec["file"]] = rec
    doc["contract"] = sfx_contract(doc.get("contract", {}).get("peak_dbfs", SFX_PEAK_DBFS))
    doc["assets"] = sorted(assets.values(), key=lambda a: (a.get("family", ""), a["file"]))
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def sfx_sources_md(manifest_path):
    """Write SOURCES.md next to the manifest -- derived, so it can never drift."""
    doc = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    lines = [
        "# SFX bundle provenance",
        "",
        "Audio contract: %s" % json.dumps(doc.get("contract", {}), ensure_ascii=False),
        "",
        "License: %s" % doc.get("license", ""),
        "",
        "| file | family | triggers | duration | peak | rms | head | loop | prompt |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for a in doc.get("assets", []):
        lines.append("| `%s` | %s | %s | %.2f s | %.1f dBFS | %.1f dBFS | %s | %s | %s |" % (
            a["file"], a.get("family", "-"), ", ".join(a.get("trigger", [])) or "-",
            a.get("duration_s", 0) or 0, a.get("peak_dbfs", 0) or 0, a.get("rms_dbfs", 0) or 0,
            "-" if a.get("head_ms") is None else "%.0f ms" % a["head_ms"],
            "yes" if a.get("loop") else "no",
            (a.get("prompt", "")[:60] + ("..." if len(a.get("prompt", "")) > 60 else "")).replace("|", "/")))
    flagged = [a["file"] for a in doc.get("assets", []) if a.get("warnings")]
    if flagged:
        lines += ["", "## Takes with open warnings", ""]
        for a in doc.get("assets", []):
            if a.get("warnings"):
                lines.append("- `%s` -- %s" % (a["file"], "; ".join(a["warnings"])))
    mix = {k: v for k, v in (doc.get("mix") or {}).items() if isinstance(v, dict)}
    if mix:
        lines += ["", "## Mix intent per family", "",
                  "Relative to each file's normalised peak. Every asset peaks at the same place "
                  "on purpose, so these numbers are the whole difference between a click and an "
                  "impact.", "",
                  "| family | gain | max hits/s | duck under speech |", "|---|---|---|---|"]
        for name in sorted(mix):
            row = mix[name]
            lines.append("| %s | %s dB | %s | %s |" % (
                name, row.get("gain_db", "-"), row.get("max_hits_per_s", "-"),
                "yes" if row.get("duck_under_speech") else "no"))
    lines += ["", "Every file was generated with `%s`." % SFX_SOURCE, ""]
    Path(manifest_path).with_name("SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


def sfx_build_preview(root, manifest_path, out_path):
    """Concatenate the whole bundle with 300 ms gaps so it can be auditioned in one listen."""
    doc = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    files = [root / a["file"] for a in doc.get("assets", [])]
    files = [f for f in files if f.exists()]
    if not files:
        return None
    gap = Path(tempfile.mkdtemp(prefix="mbb_gap_")) / "sil.wav"
    sfx_run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
             "-i", "anullsrc=r=%d:cl=stereo" % SFX_SAMPLE_RATE, "-t", "0.300", str(gap)])
    listfile = gap.with_name("list.txt")
    rows = []
    for f in files:
        rows += ["file '%s'" % str(gap).replace("\\", "/"), "file '%s'" % str(f).replace("\\", "/")]
    listfile.write_text("\n".join(rows), encoding="utf-8")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = sfx_run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
                    "-safe", "0", "-i", str(listfile), "-c:a", "pcm_s16le", str(out_path)])
    shutil.rmtree(gap.parent, ignore_errors=True)
    if proc.returncode != 0:
        print("[WARN] preview build failed: %s" % (proc.stderr or "")[-500:])
        return None
    return out_path


def sfx_generate_one(asset, root, api_key, peak_dbfs=SFX_PEAK_DBFS, verbose=True):
    """Generate + normalise a single spec entry. Returns (record, None) or (None, error)."""
    dst = root / asset["file"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    duration = float(asset.get("duration_seconds", 1.0))
    if duration < SFX_MIN_DURATION or duration > SFX_MAX_DURATION:
        return None, "duration_seconds %s outside %s-%s" % (duration, SFX_MIN_DURATION, SFX_MAX_DURATION)

    pcm, err = sfx_request(api_key, asset["prompt"], duration,
                           asset.get("prompt_influence"), asset.get("loop"))
    if pcm is None:
        return None, err

    workdir = Path(tempfile.mkdtemp(prefix="mbb_sfx_raw_"))
    raw = workdir / "raw.wav"
    try:
        # The API returns headerless PCM, so the channel count has to be inferred: reading
        # stereo as mono doubles the length and mangles the sound, so keep whichever
        # interpretation reproduces the duration the API was asked for.
        sfx_wrap_wav(pcm, raw, 1)
        mono_s = sfx_probe(raw)["duration_s"]
        sfx_wrap_wav(pcm, raw, 2)
        stereo_s = sfx_probe(raw)["duration_s"]
        read_channels = 1 if abs(mono_s - duration) <= abs(stereo_s - duration) else 2
        sfx_wrap_wav(pcm, raw, read_channels)
        loop = bool(asset.get("loop"))
        tight = bool(asset.get("tight", True)) and not loop   # trimming a bed would eat its swell
        sfx_normalize(raw, dst, tight=tight, peak_dbfs=peak_dbfs, loop=loop)
    except (RuntimeError, OSError) as err:
        return None, str(err)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    rec = {
        "file": asset["file"].replace("\\", "/"),
        "family": asset.get("family", dst.parent.name),
        "trigger": asset.get("trigger", []),
        "prompt": asset["prompt"],
        "requested_s": duration,
        "pcm_channels_read": read_channels,
        "sample_rate": SFX_SAMPLE_RATE,
        "channels": 2,
        "bit_depth": 16,
        "loop": loop,
        "tight": tight,
        "source": SFX_SOURCE,
        "generated": datetime.date.today().isoformat(),
    }
    rec.update(sfx_quality(dst, tight=tight, loop=rec["loop"]))
    if not tight and abs(rec["duration_s"] - duration) > duration * 0.25:
        rec["warnings"].append("loops and risers should keep their length: %.2fs vs %.2fs"
                               % (rec["duration_s"], duration))
    if verbose:
        print("[OK] %-36s %5.2fs  peak %5.1f  rms %5.1f  head %5s ms%s" % (
            rec["file"], rec["duration_s"], rec["peak_dbfs"], rec["rms_dbfs"],
            rec["head_ms"], "  ! " + "; ".join(rec["warnings"]) if rec["warnings"] else ""))
    return rec, None


def cmd_sfx(args):
    """Generate sound effects: one prompt, a whole library from a JSON spec, or a repair pass."""
    peak = float(args.peak_dbfs)
    # A repair pass re-applies the contract to files we already own, so it must not need a key.
    api_key = None if args.renormalize else get_api_key(args.api_key)

    if args.spec:
        spec_path = Path(args.spec)
        if not spec_path.exists():
            print("[ERROR] Spec not found: %s" % args.spec)
            sys.exit(1)
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        root = spec_path.parent / spec.get("root", ".")
        manifest_path = root / spec.get("manifest", "manifest.json")
        assets = spec.get("assets", [])
        wanted = None
        if args.only:
            wanted = {f.strip() for f in args.only.split(",") if f.strip()}

        print("\n[SFX] Library build -- %d entries, root %s%s"
              % (len(assets), root, " (repair pass, no API calls)" if args.renormalize else ""))
        prior = {}
        if args.renormalize and manifest_path.exists():
            try:
                prior = {a["file"]: a for a in json.loads(
                    manifest_path.read_text(encoding="utf-8")).get("assets", [])}
            except Exception:
                prior = {}
        done, skipped, failed = [], [], []
        for asset in assets:
            if wanted and not (wanted & {asset.get("family"), Path(asset["file"]).parent.name,
                                         Path(asset["file"]).stem}):
                continue
            target = root / asset["file"]
            if args.renormalize:
                rec, err = sfx_repair_one(asset, root, prior.get(asset["file"]), peak_dbfs=peak)
                if err:
                    failed.append((asset["file"], err))
                    print("[FAIL] %s -- %s" % (asset["file"], err))
                else:
                    done.append(rec)
                    print("[FIX ] %-36s %5.2fs  peak %5.1f  rms %5.1f  head %5s ms%s" % (
                        rec["file"], rec["duration_s"], rec["peak_dbfs"], rec["rms_dbfs"],
                        rec["head_ms"], "  ! " + "; ".join(rec["warnings"]) if rec["warnings"] else ""))
                continue
            if target.exists() and not args.force:
                skipped.append(asset["file"])
                print("[skip] %-34s exists (use --force to regenerate)" % asset["file"])
                continue
            rec, err = sfx_generate_one(asset, root, api_key, peak_dbfs=peak)
            if err:
                failed.append((asset["file"], err))
                print("[FAIL] %s\n%s" % (asset["file"], err))
            else:
                done.append(rec)

        if done:
            sfx_manifest_update(manifest_path, done,
                                extra={"contract": {"peak_dbfs": peak},
                                       "mix": spec.get("mix", {})})
            sfx_sources_md(manifest_path)
        print("\n" + "=" * 62)
        print("  SFX LIBRARY: %d %s | %d skipped | %d failed" % (
            len(done), "repaired" if args.renormalize else "generated", len(skipped), len(failed)))
        print("=" * 62)
        for name, err in failed:
            print("  ! %s -- %s" % (name, str(err).splitlines()[0] if err else "?"))
        if args.preview:
            pv = sfx_build_preview(root, manifest_path, root / args.preview)
            if pv:
                print("[OK] Audition the whole bundle in one listen: %s" % pv.as_posix())
        if failed:
            sys.exit(1)
        return

    if not args.text:
        print("[ERROR] Provide --text '...' (single take) or --spec library.json (batch).\n")
        sys.exit(1)
    out_path = Path(args.output)
    root = out_path.parent.parent if len(out_path.parents) > 1 else Path(".")
    asset = {
        "file": str(out_path.relative_to(root)).replace("\\", "/"),
        "prompt": args.text,
        "duration_seconds": args.duration,
        "prompt_influence": args.prompt_influence,
        "loop": args.loop,
        "tight": not (args.no_trim or args.loop),
        "family": args.family or out_path.parent.name,
        "trigger": [t.strip() for t in (args.trigger or "").split(",") if t.strip()],
    }
    manifest_path = Path(args.manifest) if args.manifest else root / "manifest.json"
    print("\n[SFX] Generating one take...")
    rec, err = sfx_generate_one(asset, root, api_key, peak_dbfs=peak)
    if err:
        print("[ERROR] ElevenLabs SFX request failed:\n%s" % err)
        sys.exit(1)
    sfx_manifest_update(manifest_path, [rec], extra={"contract": {"peak_dbfs": peak}})
    sfx_sources_md(manifest_path)
    print("[OK] Timestamp/provenance recorded in %s\n" % manifest_path)


# ---------------------------------------------------------------------------
# CLI Argument Parser Setup
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Motion Bang Bang -- ElevenLabs TTS, STT & SFX Audio Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python scripts/elevenlabs_audio.py voices --search george
  python scripts/elevenlabs_audio.py tts --text "Hello from Motion Bang Bang" --voice george --output assets/vo.mp3
  python scripts/elevenlabs_audio.py tts --file vo-script.md --voice rachel --timestamps assets/vo-timestamps.json --cues assets/vo-cues.js
  python scripts/elevenlabs_audio.py stt --file avatar.mp4 --output assets/transcript.json --srt assets/captions.srt
  python scripts/elevenlabs_audio.py sfx --spec assets/sfx/library.json --preview _preview.wav
  python scripts/elevenlabs_audio.py sfx --text "rubber stamp pressed onto paper, dry, close mic" --duration 0.6 --family stamp --trigger slam,label --output assets/sfx/stamp/stamp-rubber-02.wav
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

    # Command: sfx
    sfx_parser = subparsers.add_parser(
        "sfx",
        help="Generate Sound Effects and normalise them into the skill's SFX bundle "
             "(stereo 48 kHz PCM WAV, head-trimmed, peak-normalised by pure gain)")
    sfx_parser.add_argument("--text", help="Prompt for a single take: name the source, surface and mic perspective")
    sfx_parser.add_argument("--spec", help="Batch build from a library spec JSON (e.g. assets/sfx/library.json)")
    sfx_parser.add_argument("--output", default="assets/sfx/ui/ui-click-01.wav",
                            help="Output path for --text mode, relative to the bundle root")
    sfx_parser.add_argument("--duration", type=float, default=1.0,
                            help="Requested seconds, 0.5-30 (default: 1.0). Billing scales with this.")
    sfx_parser.add_argument("--prompt-influence", type=float, default=None,
                            help="0.0-1.0: how literally the prompt is followed (omit for model default)")
    sfx_parser.add_argument("--loop", action="store_true", help="Seamless loop (ambience/beds; implies --no-trim)")
    sfx_parser.add_argument("--no-trim", action="store_true",
                            help="Keep leading/trailing silence (risers, loops). Default trims below -40 dBFS")
    sfx_parser.add_argument("--peak-dbfs", type=float, default=SFX_PEAK_DBFS,
                            help="Peak-normalise target (default: -3.0 dBFS, leaves headroom for stacked hits)")
    sfx_parser.add_argument("--family", help="Bundle family folder label, e.g. impact / whoosh / paper")
    sfx_parser.add_argument("--trigger", help="Comma-separated motion verbs this sound answers, e.g. 'slam,block'")
    sfx_parser.add_argument("--manifest", help="Manifest path (default: next to the output / spec root)")
    sfx_parser.add_argument("--only", help="Batch: restrict to families or file names, comma-separated")
    sfx_parser.add_argument("--force", action="store_true", help="Batch: regenerate files that already exist")
    sfx_parser.add_argument("--renormalize", action="store_true",
                            help="Batch: re-apply the contract to existing files (trim gate + peak target) "
                                 "without calling the API, so this pass costs nothing")
    sfx_parser.add_argument("--preview", help="Batch: also concatenate the bundle into one audition WAV (file name)")

    # Command: sync-template
    subparsers.add_parser("sync-template", help="Print GSAP audio & video sync boilerplate code")

    args = parser.parse_args()

    if args.command == "tts":
        cmd_tts(args)
    elif args.command == "stt":
        cmd_stt(args)
    elif args.command == "sfx":
        cmd_sfx(args)
    elif args.command == "voices":
        cmd_voices(args)
    elif args.command == "sync-template":
        cmd_sync_template(args)


if __name__ == "__main__":
    main()
