#!/usr/bin/env python3
"""
Extract and decode Next.js `self.__next_f.push()` segments from HTML.

These segments contain embedded application state in Next.js apps that
don't expose public APIs. The data is URL-encoded, unicode-escaped, and
wrapped in a JS array — not valid JSON directly.

Usage:
  python3 extract_nextjs_push.py /tmp/code4rena_contests.html > decoded.txt

Outputs all push segments as decoded JSON-compatible strings to stdout.
"""

import re
import sys
import html


def extract_push_segments(html_content: str) -> list[tuple[str, str]]:
    """
    Find all `self.__next_f.push([...])` calls in HTML/JS.

    Returns list of (index, encoded_data) tuples.
    """
    # Matches: self.__next_f.push([1,"...encoded..."])
    pattern = re.compile(
        r'self\.__next_f\.push\(\[(\d+),"([^"]*)"\]\)',
        re.DOTALL
    )
    return [(idx, data) for idx, data in pattern.findall(html_content)]


def decode_segment(encoded: str) -> str:
    """Reverse Next.js's encoding: URL-unescape + unicode-escape."""
    # First, HTML unescape (some sites embed as entities)
    unescaped = html.unescape(encoded)
    # Then decode unicode escapes like \u003c → <
    try:
        return unescaped.encode().decode('unicode_escape')
    except Exception:
        # Fallback: raw
        return unescaped


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_nextjs_push.py <html-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        html_content = f.read()

    segments = extract_push_segments(html_content)
    if not segments:
        print("No push segments found.", file=sys.stderr)
        sys.exit(1)

    # Sort by length descending - longest usually has main data
    segments.sort(key=lambda x: len(x[1]), reverse=True)

    for idx, encoded in segments:
        decoded = decode_segment(encoded)
        print(f"\n{'='*60}")
        print(f"Segment index: {idx} | length: {len(decoded)}")
        print(f"{'='*60}")
        print(decoded)


if __name__ == "__main__":
    main()
