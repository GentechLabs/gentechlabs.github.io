#!/usr/bin/env python3
"""
Validate Watchdog alert format.

Usage:
    python3 validate_alert_format.py < input.txt
    # or pipe your generated output through this before sending

Rules:
- If healthy: EXACTLY "STATUS:OK" (no whitespace, no newline trailing if possible)
- If broken: ONE LINE starting with "🚨 Watchdog Alert:" containing the summary
- Never multi-line, never bullet points, never paragraphs

Exit codes:
  0 — format is valid
  1 — format violation (print corrected version to stderr)
"""

import sys

def validate(text):
    text = text.strip()
    lines = text.split('\n')

    # Must be exactly one line
    if len(lines) > 1:
        return False, "MULTI-LINE output detected ({0} lines). Reduce to one line.".format(len(lines))

    line = lines[0].strip()

    if line == "STATUS:OK":
        return True, "OK (silence rule)"

    if not line.startswith("🚨 Watchdog Alert:"):
        return False, "Missing required prefix '🚨 Watchdog Alert:'"

    # Must contain some summary after the colon
    if len(line) <= len("🚨 Watchdog Alert:"):
        return False, "Alert line too short — needs actual problem summary after prefix"

    # Check for forbidden formatting markers within the line
    forbidden = ['**', '* -', '•', '1.', '2.', '3.', '  *', '\t*', '✅', '🔴', '⚠️', '📊']
    for marker in forbidden:
        if marker in line:
            return False, "Contains formatting marker '{0}' — remove bullets/formatting".format(marker)

    # Check if it's suspiciously long (more than 300 chars likely means paragraph crammed into one line)
    if len(line) > 300:
        return False, "Line too long ({0} chars) — likely contains too much detail, compress".format(len(line))

    return True, "OK (alert format)"

if __name__ == "__main__":
    input_text = sys.stdin.read()
    ok, reason = validate(input_text)
    if ok:
        sys.exit(0)
    else:
        sys.stderr.write("FORMAT VIOLATION: {0}\n".format(reason))
        sys.stderr.write("Expected: one line only, starting with '🚨 Watchdog Alert:' or exactly 'STATUS:OK'\n")
        sys.exit(1)
