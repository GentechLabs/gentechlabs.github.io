# Python Constants Syntax Pitfall — Multiline String Contamination

## Problem

Constants defined on a single line that **includes literal `\n` escape sequences** instead of actual newlines cause Python to treat the entire block as one continuous statement. The constants never get defined, leading to `NameError` at runtime.

### Broken Example (what we found)

```python
# Alert thresholds\\nEFFICIENCY_WARNING_THRESHOLD = 30.0  # Below 30% → efficiency warning\\nEFFICIENCY_RED_THRESHOLD = 25.0      # Below 25% → red alert (severe)\\nOUT_OF_RANGE_WARNING_MINUTES = 10    # After 10min out of range → warning\\nOUT_OF_RANGE_RED_MINUTES = 15        # After 15min total → red alert (10 + 5 confirm)
```

**How it happens:** Copy-pasting from formatted documentation (e.g., Obsidian, PDFs, or web pages) that uses `\n` to represent line breaks in plain-text excerpts. When those `\n` literals are pasted into a Python file, they become part of the string/comment rather than actual newlines.

**Symptoms:**
- Script runs but crashes with `NameError: name 'EFFICIENCY_RED_THRESHOLD' is not defined`
- `grep` shows all constants on one extremely long line
- Syntax highlighting may show weird coloring across the line

### Correct Format

```python
# Alert thresholds
EFFICIENCY_WARNING_THRESHOLD = 30.0  # Below 30% → efficiency warning
EFFICIENCY_RED_THRESHOLD = 25.0      # Below 25% → red alert (severe)
OUT_OF_RANGE_WARNING_MINUTES = 10    # After 10min out of range → warning
OUT_OF_RANGE_RED_MINUTES = 15        # After 15min total → red alert (10 + 5 confirm)
```

Each assignment on its own line, actual newline characters (`\n`), no escape sequences.

---

## Detection

```bash
# Find lines with suspiciously long length + multiple \n literals
grep -n '\\\\n' /path/to/script.py

# Or check if constants are defined on same line
grep -n 'EFFICIENCY_.*THRESHOLD' /path/to/script.py
```

If output shows multiple constants on one line → broken.

---

## Fix

1. Open the file in a proper editor (Vim, VS Code, nano — NOT cat in terminal)
2. Replace the entire crammed line with individual lines (copy from correct example above)
3. Save and re-run syntax check: `python3 -m py_compile script.py`
4. Test execution: `python3 script.py`

---

## Prevention

When copying code snippets from any formatted source (Obsidian, web pages, PDFs, Slack/Discord):
- **Never** copy raw text that shows `\n` literally
- Use code block "Copy" button if available
- Paste into a plain-text editor first to strip formatting, then into Python file
- Run `cat -A file.py` to visualize control characters — look for `\n` appearing as `\n` (two chars) instead of actual newline

---

## Session Context (2026-05-02)

**Affected file:** `/root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py` line 72

**Impact:** Script completely non-functional — crashed before any LP monitoring could occur. Crypto watchlist delivery halted.

**Resolution:** Manually split crammed line into four separate assignment statements with real newlines.

**Time to fix:** ~2 minutes once identified.
