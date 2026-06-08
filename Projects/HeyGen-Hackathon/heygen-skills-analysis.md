# HeyGen Skills Repo Analysis

**Repo:** https://github.com/heygen-com/skills ⭐214
**Purpose:** Two AI agent skills for creating avatars and generating videos via HeyGen v3 API

---

## Skills Available

### 1. heygen-avatar
- Photo/prompt → persistent digital twin (face + voice)
- Outputs `AVATAR-<NAME>.md` with group_id + voice_id
- 453 lines of prompt-driven instructions

### 2. heygen-video
- Idea → script → prompt-engineered video via v3 Video Agent
- Reads AVATAR files, handles frame check, prompt engineering, style selection
- 666 lines of prompt-driven instructions

**Legacy skills** (TTS, translation, faceswap, video editing) at heygen-com/skills-legacy

---

## Two Transport Modes (Auto-detected)

### MCP (Preferred)
- Remote MCP server: `https://mcp.heygen.com/mcp/v1/`
- OAuth auth, uses plan credits, no API key needed
- Tools: create_video_agent, get_video, list_avatars, create_speech, etc.

### CLI Fallback
- `heygen` binary — `heygen <noun> <verb>` pattern
- Needs `HEYGEN_API_KEY` env var
- Install: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash`

---

## MCP Config

```json
{
  "mcpServers": {
    "heygen": {
      "type": "http",
      "url": "https://mcp.heygen.com/mcp/v1/"
    }
  }
}
```

---

## Agent Patterns

- **Mode detection ladder:** OpenClaw plugin → CLI (API key) → MCP (OAuth) → CLI (fallback) → error
- **Skill chaining:** heygen-avatar writes AVATAR-*.md → heygen-video reads it
- **Subagent spawn pattern:** Frame Check + prompt construction in main → spawn subagent for submit + poll + deliver
- **4 modes:** Full Producer (interview-driven), Enhanced Prompt (user has script), Quick Shot (no questions), Interactive Session

---

## Quick Start (Hackathon)

```bash
# Install CLI
curl -fsSL https://static.heygen.ai/cli/install.sh | bash

# Set API key
export HEYGEN_API_KEY="your-key"

# Create a video
heygen video-agent create \
  --prompt "Your script here..." \
  --avatar-id "<look_id>" \
  --voice-id "<voice_id>" \
  --orientation landscape \
  --wait --timeout 45m
```

---

## Key Takeaways

- **No build step** — skills are Markdown instructions for AI agents
- **20 curated visual styles** via style_id (A24, editorial, cinematic, etc.)
- **Generation time:** 20-45 minutes per video
- **Duration accuracy:** ~97% with explicit avatar_id, ~80% without
- **Known bug:** video_avatar type narrators can fail — use photo_avatar or studio_avatar
- **Interactive sessions unreliable** — use one-shot mode for hackathon demos

---

*Analyzed by Gentech — May 7, 2026*
