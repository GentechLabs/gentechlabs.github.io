# Pricing Extraction from JS-Heavy Sites — Reference

**Problem:** Modern SaaS sites (Next.js, React, Vue) render pricing via client-side JS. Traditional `requests`/`curl` returns empty divs. API endpoints are obfuscated or require auth.

**Solution:** Use `curl` to fetch the **server-side rendered HTML** (the initial HTML payload before hydration), then parse the embedded JSON/component props with regex.

---

## Technique (Composio Case Study)

Composio.dev uses Next.js with SSR. Pricing data is embedded in the HTML as React component props within `<script>` tags and template attributes.

### Step 1 — Fetch Raw HTML
```bash
curl -sL -o /tmp/pricing.html "https://composio.dev/pricing"
```

### Step 2 — Extract with Positional Context
The pricing cards are rendered server-side with explicit props: `name="Totally Free" price="$0" calls="20K Tool Calls/Mo" support="Community Support"`.

Use regex to extract the full card content, then drill down:

```python
import re

html = open('/tmp/pricing.html').read()

# Find the pricing grid section
pricing_start = html.find('grid gap-px bg-black')
pricing_section = html[pricing_start:pricing_start+15000]

# Split on card boundaries
cards = re.split(r'<a class="group relative', pricing_section)

for card in cards[1:]:  # skip header
    name = re.search(r'<h3[^>]*>([^<]+?)</h3>', card)
    price = re.search(r'class="font-sans text-4xl[^>]*>([^<]+?)<', card)
    calls = re.search(r'(\d+K? Tool Calls/Mo)', card)
    support = re.search(r'>(Email|Community|Slack) Support<', card)
    overage = re.search(r'\$(\d+\.?\d*)/1K', card)
```

### Step 3 — Fallback: API Endpoint Discovery
If SSR doesn't contain pricing, inspect network tab in browser DevTools:
1. Open pricing page
2. Filter XHR/fetch requests
3. Look for `pricing`, `plans`, `api/pricing` endpoints
4. Test endpoint directly: `curl https://composio.dev/api/pricing`

*(Composio didn't expose a public pricing API — fell back to SSR HTML parsing.)*

---

## Why This Works

Next.js `next/dynamic` and `next/script` still render initial page state in HTML for SEO. Component props get inlined as HTML attributes or JSON in `<script type="application/ld+json">`.

**Key markers to search:**
- `data-utm-placement="pricing-*"` — Composio's tracking attributes
- Component names like `PricingCard`, `PlanCard` in classNames
- Structured data: `"@type": "Product"` with `"offers"` array

---

## Regex Patterns That Worked

```python
# Extract plan name
r'<h3[^>]*class="[^"]*text-\[22px\][^"]*"[^>]*>([^<]+?)</h3>'

# Extract price (font-sans text-4xl is unique to pricing)
r'class="font-sans text-4xl[^"]*leading-none[^"]*"[^>]*>([^<]+?)<'

# Extract tool calls
r'(\d+K? Tool Calls/Mo)'

# Extract overage rate
r'\$(\d+\.?\d*)/1K ADDITIONAL CALLS'
```

---

## Common Pitfalls & Fixes

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| HTML is empty/404 | `curl` returns signup page | Add user-agent: `curl -A "Mozilla/5.0"` |
| Content obfuscated | Text appears as `\u003c` escapes | Use `html.unescape()` in Python |
| Multiple card versions (mobile/desktop) | Duplicate data | Filter by unique attributes (e.g. `data-placement`) |
| Dynamic pricing (per-user) | HTML has `{{price}}` placeholders | Need auth cookie; fall back to manual entry |

---

## Alternative Approaches

1. **Use official API** (if exists): `GET /api/pricing` with `Accept: application/json`
2. **Screenshot + OCR** — last resort (pricing as image)
3. **Browser automation** — `playwright`/`selenium` to render JS then extract
4. **Manual entry** — if automated fails, document source URL + date

---

## When This Techniques Fails

- **Pricing behind login** — Need auth credentials (ask user)
- **Per-customer custom pricing** — Must contact sales
- **Dynamic regional pricing** — Use VPN/proxy to test geos
- **A/B test variants** — Clear cookies; fetch multiple times

**Fallback strategy:** If SSR extraction fails after 3 attempts, switch to **browser automation** via Playwright:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto("https://composio.dev/pricing")
    page.wait_for_load_state("networkidle")
    cards = page.query_selector_all(".pricing-card")
    # extract textContent
```

---

## Verification Checklist

- [ ] HTML contains visible pricing text (not just JS placeholders)
- [ ] At least 2 pricing tiers extracted (confirms pattern)
- [ ] Price format matches expected (`$0`, `$29`, `$229`)
- [ ] Overage rates captured (if listed)
- [ ] Support levels identified (Community/Email/Slack)

---

## Source

**Document created from:** Composio pricing analysis session (2026-05-03)
**URL scraped:** https://composio.dev/pricing
**Method:** SSR HTML parsing with positional context + regex
**Reliability:** High for SSR sites; Medium for fully client-rendered SPAs
