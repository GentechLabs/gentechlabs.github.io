"""
GenTech Voicebox — Kokoro TTS Server
Open-source ElevenLabs alternative running on RTX 3070.
FastAPI endpoints for text-to-speech generation.
"""
import os, io, time, json, uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
import soundfile as sf
import uvicorn

PORT = int(os.environ.get("VOICEBOX_PORT", 3022))

# Lazy-load Kokoro (takes ~7s on first call)
_pipeline = None
_model = None

def get_kokoro():
    global _pipeline, _model
    if _pipeline is None:
        from kokoro import KPipeline, KModel
        t0 = time.time()
        _model = KModel()
        _pipeline = KPipeline(lang_code='a')
        print(f"  Kokoro loaded in {time.time()-t0:.1f}s")
    return _pipeline, _model

# Available voices
VOICES = {
    "af_heart": "American English - Heart (female, warm)",
    "af_bella": "American English - Bella (female, friendly)",
    "af_nicole": "American English - Nicole (female, clear)",
    "af_aoede": "American English - Aoede (female, expressive)",
    "am_adam": "American English - Adam (male, deep)",
    "am_michael": "American English - Michael (male, calm)",
}

app = FastAPI(title="GenTech Voicebox", version="1.0.0")

class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0

@app.get("/health")
def health():
    return {"status": "ok", "service": "gentech-voicebox", "model": "kokoro-82m"}

@app.get("/voices")
def list_voices():
    return {"voices": VOICES}

@app.post("/tts")
def tts(req: TTSRequest):
    if req.voice not in VOICES:
        raise HTTPException(400, f"Unknown voice. Available: {list(VOICES.keys())}")
    if not req.text.strip():
        raise HTTPException(400, "text required")
    if len(req.text) > 1000:
        raise HTTPException(400, "text too long (max 1000 chars)")

    pipeline, _ = get_kokoro()
    audio_chunks = []
    generator = pipeline(req.text, voice=req.voice, speed=req.speed)
    for gs, ps, audio in generator:
        audio_chunks.append(audio)

    if not audio_chunks:
        raise HTTPException(500, "No audio generated")

    combined = audio_chunks[0] if len(audio_chunks) == 1 else __import__('numpy').concatenate(audio_chunks)
    buf = io.BytesIO()
    sf.write(buf, combined, 24000, format="WAV")
    buf.seek(0)
    return Response(content=buf.read(), media_type="audio/wav",
                    headers={"X-Duration-Sec": f"{len(combined)/24000:.1f}"})

if __name__ == "__main__":
    print(f"🤖 GenTech Voicebox starting on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
