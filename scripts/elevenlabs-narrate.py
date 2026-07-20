#!/usr/bin/env python3
"""
ElevenLabs narration for GenTech content pipeline.
Uses your ElevenLabs API key for TTS.
"""

import os, sys, json, requests, base64

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VAULT = "/root/vaults/gentech"
OUTPUT = f"{VAULT}/assets/content-pipeline"

def narrate_script(script_path, voice="sarah"):
    """Read a script and narrate it with ElevenLabs."""
    if not ELEVENLABS_API_KEY:
        print("⚠️ ELEVENLABS_API_KEY not set")
        return None
    
    with open(script_path) as f:
        text = f.read()
    
    # Truncate to ElevenLabs limits
    text = text[:5000]
    
    # Voice IDs
    voices = {
        "yoyo": "xQbwtCgzouB5QdCSd0Z7",
        "sarah": "EXAVITQu4vr4xnSDxMaL",
        "george": "JBFqnCBsd6RMkjVDRZzb",
    }
    voice_id = voices.get(voice, voices["yoyo"])
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        
        os.makedirs(OUTPUT, exist_ok=True)
        audio_path = f"{OUTPUT}/latest-narration.mp3"
        with open(audio_path, "wb") as f:
            f.write(resp.content)
        print(f"🎙️ Narration saved: {audio_path} ({len(resp.content)} bytes)")
        return audio_path
    except Exception as e:
        print(f"❌ ElevenLabs error: {e}")
        return None

if __name__ == "__main__":
    script_path = f"{OUTPUT}/latest-script.txt"
    if not os.path.exists(script_path):
        print("❌ No script found. Run content-pipeline.py first.")
        sys.exit(1)
    narrate_script(script_path)
