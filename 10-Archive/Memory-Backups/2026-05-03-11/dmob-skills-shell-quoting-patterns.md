# Shell Quoting Patterns for Programmatic Command Execution

## The Problem

When building shell commands from Python variables that contain newlines, spaces, or shell metacharacters, raw string interpolation produces invalid shell syntax:

```bash
SyntaxError: unterminated string literal
# or
syntax error near unexpected token `)'
```

## Root Cause

The shell parses the command string BEFORE any command runs. Unquoted newlines terminate the command prematurely. Unescaped quotes break string grouping.

## Safe Patterns

### 1. `repr()` for Simple Arguments
Best for: single-line or moderate-length strings passed as `-m "msg"` flags.

```python
msg = "Fix: merge duplicate LP cron jobs\n- Added debounce logic"
terminal(f"git commit -m {repr(msg)}")
# Produces: git commit -m 'Fix: merge duplicate LP cron jobs\n- Added debounce logic'
# Shell sees one properly-quoted argument
```

**Why it works:** `repr()` returns a Python literal that, when printed, is valid shell syntax for that string. Newlines become `\n` (not literal newlines).

### 2. Heredoc for Large Blobs
Best for: multi-line commit messages, config files, patches > ~200 chars.

```python
blob = open("changes.txt").read()
terminal(
    "git commit -F - <<'EOF'\n"
    f"{blob}\n"
    "EOF"
)
```

**Key details:**
- `<<'EOF'` — single-quoted delimiter prevents shell expansion inside blob
- Closing `EOF` must be alone on its own line with no indentation
- Add explicit `\n` before closing EOF if blob doesn't end with newline

### 3. Write-to-Temp-File
Best for: very large payloads (>10KB) or repeated use.

```python
import tempfile, os

with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write(commit_msg)
    tmp_path = f.name

try:
    terminal(f"git commit -F {tmp_path}")
finally:
    os.unlink(tmp_path)
```

Avoids shell quoting entirely because path has no spaces/metacharacters (tempfile guarantees safe name).

### 4. `shlex.quote()` for Multiple Arguments
When you must build a compound command where parts may contain spaces:

```python
import shlex

author = "John Doe <john@example.com>"
file = "my file.txt"
cmd = f"git commit --author={shlex.quote(author)} {shlex.quote(file)}"
terminal(cmd)
```

**Caution:** `shlex.quote()` works per-argument. You still need to assemble the full command carefully. For multi-arg safety, prefer `subprocess.run([...], shell=False)` when possible.

### 5. Don't Use `shell=True` Blindly
If you control the command structure, avoid shell entirely:

```python
# ✅ shell=False — no quoting needed for arguments
terminal("git commit -m 'message'", shell=False)  # If API supports
```

Hermes `terminal()` tool executes via `/bin/bash -c` by default, so you're in shell context. The patterns above work within that constraint.

## Anti-Patterns to Avoid

| Pattern | Why it breaks |
|---------|---------------|
| `f"git commit -m {msg}"` where `msg` has `\n` | Shell sees newline as command terminator |
| `f'git commit -m "{msg}"'` without escaping embedded quotes | Embedded `"` closes the string early; rest becomes syntax error |
| Triple-quoted f-strings passed raw to shell | Newlines become literal newlines; shell splits into multiple commands |
| Concatenating with `+` and hoping for the best | Same issue — raw newlines hit the shell parser |

## Detection Checklist

Before calling `terminal()` with an f-string or formatted command:

- [ ] Does the variable contain a newline (`\n`)?
  - If yes → must use `repr()`, heredoc, or temp file
- [ ] Does it contain double quotes (`"`) or single quotes (`'`)?
  - If yes → `repr()` is safest; manual quoting risks mismatch
- [ ] Is it longer than 200 characters?
  - If yes → consider heredoc or temp file for readability
- [ ] Will it be written to a file anyway (e.g., `-F` flag)?
  - If yes → temp file may be cleaner than shell quoting

## Debugging Steps

If you hit `unterminated string literal` or `syntax error near`:

1. **Print the actual command string** before calling `terminal()`:
   ```python
   print(repr(command_string))  # See exact representation
   ```
2. **Manually copy/paste** that printed string into a shell to confirm it's valid.
3. If invalid, apply the appropriate pattern above.
4. For heredocs, verify closing delimiter is on its own line (no leading spaces).

## Related Skills

- `systematic-debugging`: Use this pattern knowledge when Phase 1 reveals quoting errors
- `writing-plans`: Plan quoting strategy before implementing complex command construction
- `test-driven-development`: Write a minimal test that exercises the command with problematic input before writing full logic

## Session Reference

**Date:** 2026-05-02
**Context:** Consolidating Yoyo's D5 LP cron jobs; failed `git commit` with multi-line message.
**Discovery:** Using `repr(commit_msg)` in f-string resolved `SyntaxError: unterminated string literal`.
**Applied to:** `d5-lp-consolidated.py` commit (318 lines) with ~800-char multi-line message.
**Result:** Clean commit without shell parsing errors; Obsidian sync later (CLI unavailable).
**Pattern generalization:** Any time a Python variable with newlines/quotes is embedded directly into a shell command string, wrap with `repr()` or switch to heredoc/temp-file pattern.
