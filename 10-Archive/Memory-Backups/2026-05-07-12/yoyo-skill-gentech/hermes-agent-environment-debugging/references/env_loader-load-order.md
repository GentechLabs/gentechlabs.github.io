# env_loader.load_hermes_dotenv() — Load Order & Behavior

**Source**: `/usr/local/lib/hermes-agent/hermes_cli/env_loader.py`

```python
def load_hermes_dotenv(
    *,
    hermes_home: str | os.PathLike | None = None,
    project_env: str | os.PathLike | None = None,
) -> list[Path]:
    home_path = Path(hermes_home or os.getenv("HERMES_HOME", Path.home() / ".hermes"))
    user_env = home_path / ".env"                    # ← ~/.hermes/.env
    project_env_path = Path(project_env) if project_env else None

    # Sanitize then load
    if user_env.exists():
        _sanitize_env_file_if_needed(user_env)
        _load_dotenv_with_fallback(user_env, override=True)  # Priority 1

    if project_env_path and project_env_path.exists():
        _sanitize_env_file_if_needed(project_env_path)
        # Only fills MISSING vars if user_env already loaded
        _load_dotenv_with_fallback(project_env_path, override=not loaded)
        loaded.append(project_env_path)

    return loaded
```

## Key Observations

1. **Only two locations** are ever considered:
   - `~/.hermes/.env` (always loaded first if present, `override=True`)
   - `<cwd>/.env` (only loaded if global didn't exist OR to fill remaining gaps; `override=False` when user_env already present)

2. **Profile directories are not in the loading path**. The function receives no `profile_dir` argument and makes no attempt to read `profiles/<name>/.env`.

3. **`project_env` parameter** comes from `hermes_cli/main.py`:
   ```python
   load_hermes_dotenv(project_env=PROJECT_ROOT / ".env")
   ```
   `PROJECT_ROOT` is the Hermes agent codebase root (`/usr/local/lib/hermes-agent`), NOT the profile directory.

4. **Sanitization happens pre-parse** — fixes corrupted `.env` files (duplicate keys, trailing spaces) but doesn't change source locations.

5. **Return value** is a list of loaded paths — used for debugging/logging only, not for credential aggregation.

## Implication

Setting keys in `~/.hermes/profiles/yoyo/.env` has **zero effect** on the gateway process environment. Those files serve only as backup/export artifacts.

To affect runtime environment:
- Set variables in the **shell before launching** the gateway (exports)
- Place variables in **`~/.hermes/.env`** (loaded by every Hermes CLI invocation)
- Place variables in **`/usr/local/lib/hermes-agent/.env`** (if launched from that CWD)

## Why This Design?

Historical: Early Hermes used a single global `~/.hermes/.env`. Profile `.env` files were added later for backup/portability but the env_loader was never updated to consume them. The assumption is that users will either:
- Use `~/.hermes/.env` for all credentials (single global set)
- Or launch gateways from a shell that has profile-specific exports (e.g., systemd `Environment=` or wrapper scripts)

**No automatic per-profile env resolution exists.**

## Evidence from May 2, 2026 Incident

All 4 agent PIDs inspected via `/proc/*/environ` showed:
- `NOUS_TOKEN`: NOT SET
- `ANTHROPIC_API_KEY`: NOT SET
- `ELEVENLABS_API_KEY`: NOT SET
- `OPENAI_API_KEY`: NOT SET
- `OPENCODE_GO_API_KEY`: NOT SET

Meanwhile, each profile's `.env` contained these keys. `~/.hermes/.env` existed but lacked these keys. Conclusion: profile `.env` files were never loaded.