# Session Path Resolution — ProtoJay4789 Portfolio (May 2026)

## Issue

Portfolio repo was cloned at `~/portfolio` in a prior agent session, but in the current session:

```python
FileNotFoundError: [Errno 2] No such file or directory: '/root/.hermes/profiles/dmob/home/portfolio'
```

**Cause**: Agent home isolation — each Hermes agent uses a separate home at `~/.hermes/profiles/<agent>/home/`. The `~/portfolio` path was relative to the *previous* agent's home, not the current one.

## Resolution

1. **Token-auth via subprocess**: Used Python subprocess with `input=` to pipe token non-interactively:

   ```python
   result = subprocess.run(
       ['gh', 'auth', 'login', '--with-token'],
       input=TOKEN + '\n',
       capture_output=True, text=True
   )
   ```

2. **Search for actual repo location**: Breadth-first search across `/root`:

   ```python
   result = subprocess.run(
       ['find', '/root', '-name', 'portfolio', '-type', 'd', '-not', '-path', '*/.*'],
       capture_output=True, text=True, timeout=10
   )
   ```

   Result: Not found (repo needed re-clone in this session's accessible path).

3. **Standardized location decision**: For future agent-automated repos, use an absolute path outside the agent home:
   - `/root/portfolio` — session-agnostic, all agents can access
   - Or `/opt/portfolio` for productionized installs

## Updated Process (Future Sessions)

- When cloning a repo for long-term agent automation, target `/root/<repo-name>` directly
- Record the absolute path in the vault task notes for cross-session reference
- Avoid relying on `~` (agent-home-relative) paths for persistent assets

## Files Changed
- Created: `hermes-github-operations` skill (captures Python-based GH workflows)
- Added token to `~/.hermes/.env` and exported to environment
- Verified `gh` auth and git identity configuration
