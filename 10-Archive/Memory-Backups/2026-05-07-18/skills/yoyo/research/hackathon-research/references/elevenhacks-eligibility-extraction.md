# ElevenHacks Eligibility Extraction Pattern

## Problem
Official rules pages often use JavaScript rendering, making direct `curl` ineffective. The eligibility text is embedded in a DOM structure that requires browser navigation to access.

## Solution Sequence

```python
# Step 1: Navigate to legal page directly
browser_navigate("https://hacks.elevenlabs.io/legal/official-rules")

# If that fails, navigate to main and click footer link
browser_navigate("https://hacks.elevenlabs.io/")
browser_click(ref="e2")  # Official Rules footer link

# Step 2: Extract full snapshot once page loads
snapshot = browser_snapshot(full=True)

# Step 3: Find Eligibility heading and extract following list items
# Look for heading "Eligibility" [level=2, ref=e2] then parse subsequent list items
```

## ElevenHacks Eligibility Rules (as of May 2026)

Extracted verbatim from official rules:

1. At least 18 years old (or age of majority in jurisdiction) AND have active ElevenLabs account in good standing
2. Not on OFAC Specially Designated Nationals and Blocked Persons List; not under OFAC sanction; not immediate family of sanctioned individual
3. Not resident of Brazil, Québec, Italy, or any OFAC-sanctioned country (Cuba, Iran, North Korea, Syria, Crimea)
4. Not employee/official of federal/state/provincial/local government body or agency, or family member of such individual

## Additional Exclusion
- Sponsor (Eleven Labs Inc.), X Corp, their parents/affiliates/subsidiaries, and immediate family members of employees are ineligible to win prizes.

## Key Keywords Pattern
When scanning extracted page content, look for these trigger words to find the eligibility section:
- "Eligibility" (heading)
- "To be eligible"
- "must be at least"
- "NOT be a resident"
- "OFAC"
- "government"

## Cache Location
This reference mirrors the authoritative source at:
`https://hacks.elevenlabs.io/legal/official-rules`

**Last verified**: 2026-05-03 (browser navigation successful; text extracted via snapshot)

## Vault Parallel
The official eligibility rules are also summarized in:
- `02-Labs/ElevenHacks-Research.md` (historical research)
- `06-Content/research/elevenhacks-season1.md` (season documentation)

However, the live official rules page is the authoritative source and should be used for compliance decisions.