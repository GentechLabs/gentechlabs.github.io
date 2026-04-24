# TTS Alternatives — ElevenLabs Replacement Stack

## 🥇 VoxCPM2 (Recommended)
- **Repo:** https://github.com/OpenBMB/VoxCPM
- **Model:** https://huggingface.co/openbmb/VoxCPM2
- **Install:** `pip install voxcpm`
- **Features:** 2B params, 30 languages, voice cloning, voice design from text, 48kHz studio output
- **VRAM:** ~6-8 GB
- **License:** Apache-2.0 (commercial friendly)
- **Speed:** RTF ~0.3 on RTX 4090

## 🥈 Fish Speech S2-Pro (Best Quality)
- **Repo:** https://github.com/fishaudio/fish-speech
- **Model:** https://huggingface.co/fishaudio/s2-pro
- **Features:** 4B params, 80+ languages, 15,000+ emotion tags, fine-grained control
- **VRAM:** ~12-16 GB
- **License:** Restrictive (check before commercial use)
- **Speed:** RTF 0.195 on H200

## 🥉 VibeVoice Realtime 0.5B (Lightest)
- **Model:** https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B
- **Wrapper:** https://github.com/marhensa/vibevoice-realtime-openai-api
- **Features:** 0.5B params, ~300ms latency, streaming text input, 7 preset voices
- **VRAM:** ~2 GB
- **License:** Research only (watermark + AI disclaimer)

## Status
- Planning phase — need GPU for inference
- VoxCPM2 selected as primary ElevenLabs replacement
- VibeVoice 0.5B good for low-resource streaming use cases
