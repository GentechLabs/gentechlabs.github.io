# 🎬 YouTube Tools — Status & Solutions

## Current Stack
| Tool | Status | What It Does |
|------|--------|--------------|
| youtube-content skill | ✅ Working | Fetch transcripts (public videos) |
| Browser Use (Nous) | ✅ Active | Browse YouTube directly |
| Hyperbrowser | 🆓 Free signup | Backup browser automation |

## Transcript Fetching
```bash
# Plain text
python3 /opt/hermes-agents/yoyo/skills/media/youtube-content/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 /opt/hermes-agents/yoyo/skills/media/youtube-content/scripts/fetch_transcript.py "URL" --timestamps
```

## Supported URL Formats
- youtube.com/watch?v=VIDEO_ID
- youtu.be/VIDEO_ID
- youtube.com/shorts/VIDEO_ID
- youtube.com/embed/VIDEO_ID
- Raw 11-character video ID

## Output Formats
- Chapters (timestamped topic shifts)
- Summary (5-10 sentences)
- Twitter/X thread
- Blog post
- Quotes with timestamps

## Limitations
- Public videos only (age-restricted needs browser + cookies)
- No video downloading
- Region-locked content may fail

## Backup Options
- **Hyperbrowser:** app.hyperbrowser.ai/signup (5K free credits)
- **Browser Use:** Via Nous subscription, browse YouTube directly

## Date Updated
2026-04-17
