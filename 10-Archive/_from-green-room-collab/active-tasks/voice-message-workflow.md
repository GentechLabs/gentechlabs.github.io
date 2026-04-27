# Voice Message Workflow — Active

## Rule
When a response is more than ~3 sentences or involves explanation/update:
1. Write the text version (for reading)
2. Generate Edge TTS voice message (for listening)
3. Send both — user picks their preference

## Voice Settings
| Agent | Voice | Rate |
|-------|-------|------|
| YoYo | en-GB-RyanNeural | -5% |
| Dmob | en-US-AndrewNeural | -10% |
| Desmond | en-US-GuyNeural | +2% |
| Jordan | en-US-AndrewNeural | -12% |

## Text Formatting for TTS
- Line breaks between thoughts = natural pauses
- Ellipses (...) = dramatic beat
- Short sentences, not walls of text
- Read aloud before generating — if you'd pause, add punctuation

## Audio Cleanup
ffmpeg -af "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=80,lowpass=f=12000,afftdn=nf=-25" -ar 44100 -b:a 192k

## Output Path
/opt/hermes-agents/yoyo/audio_cache/voice-{topic}.mp3

## Name Pronunciations (MUST FOLLOW)
- Dmob = "D-mob" (not D-M-O-B, not "the mob")
- DeFi = "Deh-Fye" (not "Dee-Fee")
- YoYo = "Yo-Yo"
- Desmond = "Dez-mund"
- Jordan = normal
