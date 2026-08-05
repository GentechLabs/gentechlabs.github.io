# Glama Build Failure — genTech-shop (Fixed Aug 4 2026)

**Trigger:** Glama CI email (Aug 4 8:40 AM) — "The build for genTech-shop has failed."

## Root Cause
`server.py` imported `from mcp.server.fastmcp import FastMCP`. The `mcp` package at
**v2.0.0** no longer ships `mcp.server.fastmcp` — FastMCP was split out into a
standalone `fastmcp` package. Glama's build installs `requirements.txt` (which pinned
`mcp>=1.0.0`, resolving to 2.0.0) then imports the server → `ModuleNotFoundError`.

## Fix (verified locally, pushed)
- `server.py`: `from mcp.server.fastmcp import FastMCP` → `from fastmcp import FastMCP`
- `requirements.txt`: added `fastmcp>=2.0.0`
- Verified: fresh venv install → server imports → all 4 tools register
  (`gaming_deals`, `release_calendar`, `poe2_build_health`, `gaming_hub_status`)
- Commits: `08338cf` (fix) + `6dafd6d` (glama.json license field) → pushed to
  `ProtoJay4789/genTech-shop` main

## Lesson (applies to ALL our MCP servers)
`mcp.server.fastmcp` is **deprecated/removed in mcp v2**. Any repo importing it will
fail a fresh build. Use `from fastmcp import FastMCP` + pin `fastmcp>=2.0.0`.
Check other repos for the same import: `grep -r "mcp.server.fastmcp" /root/repos/`.
