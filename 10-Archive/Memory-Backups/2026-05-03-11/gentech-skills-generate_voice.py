#!/usr/bin/env python3
"""
Generate premium audio with ElevenLabs voice ID.
Usage: python3 generate_voice.py --text "script" --voice-id Rxk9LQxvNFEplpjjsjuN --output out.mp3
"""

import argparse, subprocess, json, os, sys

def generate_elevenlabs(text, voice_id, output_path, model="eleven_multilingual_v2",
                       stability=0.5, similarity_boost=0.8, style=0.4):
    """Generate audio via ElevenLabs REST API."""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not set in environment")
        sys.exit(1)

    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": True
        }
    }

    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
        '-H', f'xi-api-key: {api_key}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)
    ], capture_output=True, timeout=30)

    if result.returncode == 0 and result.stdout:
        with open(output_path, 'wb') as f:
            f.write(result.stdout)
        return True, output_path
    else:
        return False, result.stderr[:500]

def trim_audio(input_path, output_path, duration_sec=60, bitrate="192k"):
    """Trim audio to exact duration (Instagram Story length)."""
    result = subprocess.run([
        'ffmpeg', '-i', input_path, '-t', str(duration_sec),
        '-c:a', 'libmp3lame', '-b:a', bitrate, output_path
    ], capture_output=True, timeout=30)
    return result.returncode == 0

def get_duration(path):
    """Return duration in seconds."""
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', path
    ], capture_output=True, text=True)
    return float(result.stdout.strip()) if result.returncode == 0 else 0

def get_file_size(path):
    return os.path.getsize(path) // 1024

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate premium TTS audio with ElevenLabs")
    parser.add_argument("--text", required=True, help="Script text (or path to .txt file)")
    parser.add_argument("--voice-id", required=True, help="ElevenLabs voice ID")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    parser.add_argument("--model", default="eleven_multilingual_v2", help="ElevenLabs model ID")
    parser.add_argument("--stability", type=float, default=0.5, help="Voice stability (0-1)")
    parser.add_argument("--similarity", type=float, default=0.8, help="Similarity boost (0-1)")
    parser.add_argument("--style", type=float, default=0.4, help="Style expressiveness (0-1)")
    parser.add_argument("--trim", type=float, default=None, help="Trim to N seconds (default: none)")
    parser.add_argument("--bitrate", default="192k", help="MP3 bitrate for trim")

    args = parser.parse_args()

    # Load text from file if provided path exists
    if os.path.isfile(args.text):
        with open(args.text, 'r') as f:
            text = f.read()
    else:
        text = args.text

    print(f"Generating audio with voice ID: {args.voice_id}")
    print(f"Text length: {len(text)} characters")

    success, info = generate_elevenlabs(
        text, args.voice_id, args.output,
        model=args.model, stability=args.stability,
        similarity_boost=args.similarity, style=args.style
    )

    if success:
        duration = get_duration(args.output)
        size = get_file_size(args.output)
        print(f"✓ Generated: {args.output} ({size} KB, {duration:.1f}s)")

        if args.trim:
            trimmed = args.output.replace('.mp3', f'-{int(args.trim)}s.mp3')
            if trim_audio(args.output, trimmed, args.trim, args.bitrate):
                dur_trim = get_duration(trimmed)
                size_trim = get_file_size(trimmed)
                print(f"✓ Trimmed to {args.trim}s: {trimmed} ({size_trim} KB, {dur_trim:.1f}s)")
            else:
                print("✗ Trim failed")
    else:
        print(f"✗ Generation failed: {info}")
        sys.exit(1)
