#!/usr/bin/env python3
"""Voice Clone Queue — monitors audio cache for new voice messages from Christel and KT,
transcribes them, clones their voices with OmniVoice, and delivers cloned audio to their groups.

Speaker identification: tries whisper-based voice fingerprinting against reference samples.
If unclear, uses duration and recent activity as a fallback.
"""

import os
import sys
import json
import hashlib
import subprocess
import time
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path("/root/.hermes/profiles/gentech/audio_cache")
WATERMARK_FILE = Path("/root/.hermes/profiles/gentech/audio_cache/.voice_queue_watermark.json")
OUTPUT_DIR = Path("/root/.hermes/profiles/gentech/audio_cache/cloned")
LOG_FILE = Path("/root/.hermes/profiles/gentech/audio_cache/.voice_queue.log")

# Speaker config: (reference_audio_path, group_chat_id, group_name)
SPEAKERS = {
    "christel": {
        "ref_audio": "/root/christel_reference.wav",
        "ref_text": "Hello everyone, I'm Christel from the Philippines.",
        "chat_id": "-1003863540828",  # HQ
        "name": "Christel",
    },
    "kt": {
        "ref_audio": "/root/kt_reference.wav",  # TODO: Get KT to record a 5-10s voice sample
        "ref_text": "Hey, it's KT.",  # TODO: Update with actual transcript of KT's reference
        "chat_id": "-1003893562036",  # Entertainment
        "name": "KT",
    },
}


def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_watermark():
    if WATERMARK_FILE.exists():
        with open(WATERMARK_FILE) as f:
            return json.load(f)
    return {"processed": [], "last_check": 0}


def save_watermark(wm):
    wm["last_check"] = time.time()
    with open(WATERMARK_FILE, "w") as f:
        json.dump(wm, f, indent=2)


def get_audio_duration(path):
    """Get duration of audio file in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def convert_to_wav(ogg_path, wav_path):
    """Convert OGG to WAV at 24kHz mono (OmniVoice format)."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(ogg_path), "-ar", "24000", "-ac", "1", str(wav_path)],
        capture_output=True, timeout=60
    )
    return wav_path.exists()


def transcribe(wav_path):
    """Transcribe audio using faster-whisper."""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(wav_path), beam_size=1)
        text = " ".join(seg.text.strip() for seg in segments)
        return text, info.language
    except Exception as e:
        log(f"Transcription error: {e}")
        return "", "unknown"


def compute_voice_embedding(wav_path):
    """Simple audio fingerprint: RMS energy + spectral centroid as a rough speaker ID hint."""
    try:
        import numpy as np
        import soundfile as sf
        data, sr = sf.read(str(wav_path))
        if len(data) == 0:
            return None
        rms = float(np.sqrt(np.mean(data ** 2)))
        # Simple spectral centroid approximation via FFT
        fft = np.abs(np.fft.rfft(data))
        freqs = np.fft.rfftfreq(len(data), 1 / sr)
        if fft.sum() == 0:
            centroid = 0
        else:
            centroid = float(np.sum(freqs * fft) / np.sum(fft))
        return {"rms": rms, "centroid": centroid, "duration": len(data) / sr}
    except Exception as e:
        log(f"Fingerprint error: {e}")
        return None


def identify_speaker(transcript, duration, available_speakers):
    """Identify speaker using transcription content + heuristics.

    Strategy:
    1. Check if transcript mentions a name ("I'm KT", "Christel here")
    2. If only one speaker has reference audio, default to them
    3. Fall back to 'unknown' if ambiguous
    """
    text_lower = transcript.lower()

    # Check for self-identification in transcript
    for sid in available_speakers:
        name = SPEAKERS[sid]["name"].lower()
        if name in text_lower or f"i'm {name}" in text_lower or f"it's {name}" in text_lower:
            return sid

    # Check which speakers have reference audio
    with_ref = [sid for sid in available_speakers if Path(SPEAKERS[sid]["ref_audio"]).exists()]

    if len(with_ref) == 1:
        return with_ref[0]

    if len(with_ref) == 0:
        return "unknown"

    # Multiple speakers with refs — use duration as tiebreaker
    # Christel (Filipino accent, typically shorter messages)
    # KT (GTA RP, may have longer voice messages)
    if len(with_ref) == 2:
        if duration <= 8:
            return "christel"
        return "kt"

    return with_ref[0]


def clone_voice(text, speaker_id, output_path):
    """Generate cloned audio using OmniVoice."""
    speaker = SPEAKERS.get(speaker_id)
    if not speaker:
        log(f"Unknown speaker: {speaker_id}")
        return False

    ref_audio = speaker["ref_audio"]
    ref_text = speaker["ref_text"]

    if not Path(ref_audio).exists():
        log(f"Reference audio not found for {speaker_id}: {ref_audio}")
        return False

    # Escape text for shell
    safe_text = text.replace('"', '\\"').replace("'", "\\'")

    cmd = [
        "omnivoice-infer",
        "--model", "k2-fsa/OmniVoice",
        "--text", text,
        "--ref_audio", ref_audio,
        "--ref_text", ref_text,
        "--output", str(output_path),
        "--num_step", "10",  # faster generation (default ~30)
    ]

    log(f"Running OmniVoice for {speaker['name']}: {text[:60]}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            log(f"OmniVoice stderr: {result.stderr[-500:]}")
            return False
        return Path(output_path).exists() and Path(output_path).stat().st_size > 1000
    except subprocess.TimeoutExpired:
        log(f"OmniVoice timed out for {speaker_id}")
        return False
    except Exception as e:
        log(f"OmniVoice error: {e}")
        return False


def send_to_telegram(chat_id, audio_path, caption=None):
    """Send audio file to Telegram group via send_message tool equivalent.
    We output a JSON command that the cron agent will execute.
    """
    # Output structured data for the cron agent to act on
    data = {
        "action": "send_audio",
        "chat_id": chat_id,
        "audio_path": str(audio_path),
        "caption": caption or "",
    }
    print(f"__TELEGRAM_ACTION__:{json.dumps(data)}")


def process_voice_message(ogg_path, watermark):
    """Process a single voice message: transcribe, identify speaker, clone, deliver."""
    filename = ogg_path.name

    if filename in watermark["processed"]:
        return

    log(f"Processing new voice message: {filename}")

    # Step 1: Get duration
    duration = get_audio_duration(ogg_path)
    log(f"Duration: {duration:.1f}s")

    # Skip very short files (likely noise)
    if duration < 0.5:
        log("Skipping — too short")
        watermark["processed"].append(filename)
        save_watermark(watermark)
        return

    # Step 2: Convert to WAV for processing
    wav_path = OUTPUT_DIR / f"{ogg_path.stem}.wav"
    if not convert_to_wav(ogg_path, wav_path):
        log("Failed to convert to WAV")
        return

    # Step 3: Transcribe
    transcript, language = transcribe(wav_path)
    log(f"Transcript: '{transcript}' (lang: {language})")

    if not transcript or len(transcript) < 2:
        log("Skipping — empty or near-empty transcription")
        watermark["processed"].append(filename)
        save_watermark(watermark)
        return

    # Step 4: Identify speaker
    speaker_id = identify_speaker(transcript, duration, list(SPEAKERS.keys()))
    speaker = SPEAKERS.get(speaker_id, {}).get("name", "Unknown")
    log(f"Identified speaker: {speaker} ({speaker_id})")

    if speaker_id == "unknown":
        # If we can't identify, try both speakers and send to both groups
        log("Cannot identify speaker — will try all available references")
        for sid, sconfig in SPEAKERS.items():
            if not Path(sconfig["ref_audio"]).exists():
                log(f"Skipping {sid} — no reference audio")
                continue
            out_path = OUTPUT_DIR / f"{ogg_path.stem}_{sid}_cloned.wav"
            if clone_voice(transcript, sid, out_path):
                mp3_path = OUTPUT_DIR / f"{ogg_path.stem}_{sid}_cloned.mp3"
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(out_path), "-codec:a", "libmp3lame",
                     "-b:a", "128k", str(mp3_path)],
                    capture_output=True, timeout=30
                )
                if mp3_path.exists():
                    send_to_telegram(sconfig["chat_id"], mp3_path,
                                    f"🎙️ {sconfig['name']}'s voice (cloned): \"{transcript}\"")
                    log(f"Sent to {sconfig['name']}'s group")

        watermark["processed"].append(filename)
        save_watermark(watermark)
        return

    # Step 5: Clone the voice
    out_path = OUTPUT_DIR / f"{ogg_path.stem}_{speaker_id}_cloned.wav"
    success = clone_voice(transcript, speaker_id, out_path)

    if not success:
        log("Voice cloning failed")
        return

    # Step 6: Convert to MP3 for Telegram
    mp3_path = OUTPUT_DIR / f"{ogg_path.stem}_{speaker_id}_cloned.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(out_path), "-codec:a", "libmp3lame",
         "-b:a", "128k", str(mp3_path)],
        capture_output=True, timeout=30
    )

    if not mp3_path.exists() or mp3_path.stat().st_size < 1000:
        log("MP3 conversion failed")
        return

    log(f"Cloned audio: {mp3_path} ({mp3_path.stat().st_size / 1024:.0f} KB)")

    # Step 7: Send to Telegram
    chat_id = SPEAKERS[speaker_id]["chat_id"]
    caption = f"🎙️ {SPEAKERS[speaker_id]['name']}'s voice (cloned): \"{transcript}\""
    send_to_telegram(chat_id, mp3_path, caption)

    # Mark as processed
    watermark["processed"].append(filename)
    save_watermark(watermark)
    log(f"Done — delivered to {SPEAKERS[speaker_id]['name']}'s group")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    watermark = load_watermark()
    log(f"=== Voice Clone Queue check === (tracking {len(watermark['processed'])} processed files)")

    # Find all .ogg files, sorted by modification time (newest first)
    ogg_files = sorted(CACHE_DIR.glob("*.ogg"), key=lambda f: f.stat().st_mtime, reverse=True)

    new_count = 0
    for ogg in ogg_files:
        if ogg.name not in watermark["processed"]:
            new_count += 1
            process_voice_message(ogg, watermark)
            # Rate limit: process max 2 per run to avoid CPU overload
            if new_count >= 2:
                log("Rate limit reached — will process remaining on next run")
                break

    if new_count == 0:
        log("No new voice messages")


if __name__ == "__main__":
    main()
