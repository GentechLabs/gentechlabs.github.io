# Code4rena HTML Card Fallback Pattern — Session 2026-05-02

## Problem
Push segment extraction stopped working — C4 site no longer embeds `self.__next_f.push` with structured JSON. The contests data is now rendered as HTML cards.

## Solution: HTML Card Parsing

Selectors observed on `https://code4rena.com/contests` (May 2, 2026):
- Contest cards: `<div class="competition-card">` or `<div[^>]*contest[^>]*>` (looser)
- Title: within first `<h3>` tag inside the card
- Prize: regex `\$([\d,]+)` within card text
- Deadline: `<time[^>]*datetime="([^"]+)"` attribute (ISO format)

## Python snippet
```python
import re, requests
html = requests.get('https://code4rena.com/contests', headers={'User-Agent': 'Mozilla/5.0'}).text
cards = re.findall(r'<div[^>]*contest[^>]*>.*?</div>\s*(?=<div|$)', html, re.DOTALL)
for card in cards[:10]:
    title_m = re.search(r'<h3[^>]*>(.*?)</h3>', card, re.DOTALL)
    prize_m = re.search(r'\$([\d,]+)', card)
    date_m = re.search(r'<time[^>]*datetime="([^"]+)"', card)
    if title_m and prize_m:
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
        prize = f"${prize_m.group(1)}"
        deadline = date_m.group(1) if date_m else "TBD"
        print(f"Contest: {title} | Prize: {prize} | Deadline: {deadline}")
```

## Pitfalls
- Cards may be truncated if page uses lazy loading; ensure full HTML fetch (no SPA needed for initial cards)
- Date `datetime` may be Unix timestamp in ms; convert: `datetime.fromtimestamp(int(ts)/1000, tz=timezone.utc)`
- Prize field may include multiple ranges; split on `–` and take max if needed

## Validation
Saved raw HTML to `Contest-Scans/c4_raw_YYYY-MM-DD.html` for future structure diffing.
