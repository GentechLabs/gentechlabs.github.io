# Agent Reach — Installed 2026-04-16

CLI tool for giving AI agents read/search access to 14+ internet platforms.

## Status (9/16 channels ready)

### Ready to use (no config needed):
- ✅ GitHub — repos, issues, PRs, search
- ✅ YouTube — video info + subtitle extraction
- ✅ Reddit — search, read posts/comments (rdt-cli)
- ✅ Web pages — Jina Reader (`curl https://r.jina.ai/URL`)
- ✅ Full web search — Exa semantic search (free, no API key)
- ✅ RSS/Atom feeds
- ✅ WeChat articles
- ✅ V2EX
- ✅ Bilibili — videos, subtitles, search (yt-dlp + bili-cli)

### Needs config:
- Twitter/X
- Xiaohongshu (Little Red Book)
- Weibo
- Xiaoyuzhou (podcasts → Whisper transcription)
- Xueqiu (stocks)
- Douyin (TikTok China)
- LinkedIn

## Commands
- `agent-reach doctor` — Check channel status
- `agent-reach install --env=auto` — Auto-configure

## Use Case
Default web browsing/video research tool for Gentech agents.
- Video grabbing (YouTube, Bilibili via yt-dlp)
- Web research (Jina Reader, Exa search)
- Social monitoring (Reddit, GitHub)

## Notes
- Installed in Hermes venv: `/root/.hermes/hermes-agent/venv/bin/agent-reach`
- Version: 1.4.0
- Skill installed: `/root/.agents/skills/agent-reach`
- Cookie-based auth for optional channels (stored locally only)
