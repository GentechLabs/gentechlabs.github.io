# Public API Extraction — Reference Scripts

> Scripts for harvesting APIs from public directories (public-apis repo and derivatives).

---

## 📜 `scripts/extract-public-apis.py`

**Purpose:** Extract APIs from `public-apis/README.md` by semantic category.

**Usage:**
```bash
# Extract travel-relevant APIs
python scripts/extract-public-apis.py /tmp/public-apis/README.md travel > travel-apis.json

# Extract geocoding + weather only
python scripts/extract-public-apis.py README.md geocoding weather > geo-weather.json

# From within Hermes
hermes chat -q "Run scripts/extract-public-apis.py /path/to/README.md travel"
```

**Output:** JSON dict mapping category → list of API records:
```json
{
  "Transportation": [
    {
      "name": "Amadeus for Developers",
      "url": "https://developers.amadeus.com/self-service",
      "description": "Travel Search - Limited usage",
      "auth": "OAuth",
      "https": "Yes",
      "cors": "Unknown"
    }
  ],
  ...
}
```

**Semantic keyword matching:** The script filters `###` subsections in the Index by checking if *any* keyword appears in the category name (case-insensitive). For travel, keywords are: `travel`, `transport`, `geocod`, `weather`, `photo`, `image`, `flight`, `hotel`, `currency`, `finance`, `food`, `event`, `location`, `map`, `place`, `tourism`, `booking`.

---

## 🧩 Extensibility

To extract for a *different project domain*, supply appropriate keywords:

| Project | Keywords |
|----------|----------|
| Travel | `travel transport geocod weather photo image flight hotel currency finance food event location map place tourism booking` |
| DeFi | `blockchain cryptocurrency finance defi nft` |
| Government Data | `government open-data environment science` |
| AI/ML | `machine-learning ai nlp vision image` |

The same script works across domains — no modifications needed.

---

## 📈 Workflow Integration

```bash
# 1. Clone public-apis (if not already cached)
git clone --depth=1 https://github.com/public-apis/public-apis /tmp/public-apis

# 2. Run extraction
cd /root/vaults/gentech/03-Strategies
python references/scripts/extract-public-apis.py /tmp/public-apis/README.md travel > references/public-apis/extracted-travel-apis.json

# 3. Generate markdown summary (via Python or manual)
python -c "
import json
with open('references/public-apis/extracted-travel-apis.json') as f:
    data = json.load(f)
for cat, apis in data.items():
    print(f'{cat}: {len(apis)} APIs, {sum(1 for a in apis if a[\"auth\"]==\"No\")} free')
"

# 4. Sync vault
ob sync
```

---

## 🔍 Parsing Notes

The public-apis README uses this table format:
```
### Category Name
API | Description | Auth | HTTPS | CORS
|:---|:---|:---|:---|:---|
| [Name](URL) | Description | auth | Yes/No | Yes/No/Unknown |
```

The script:
1. Finds all `### Category` headers in the Index section
2. Locates the `|:---|:---|...` separator immediately after (max 10 lines)
3. Reads rows until first non-`|`-prefixed line (blank line or next header)
4. Splits by `|` delimiter; extracts name+URL via regex
5. Normalizes whitespace; preserves original casing

**Edge cases handled:**
- Categories with no table (skipped)
- Rows with empty fields (included but blank)
- Malformed rows (skipped gracefully)
- Tables with extra columns (truncated to first 6 fields)

---

## 🛠️ Future Enhancements

- Add `--output <file>` flag to write directly to vault path
- Add `--tier <tier>` filter (free-only, keyed-only, all)
- Add `--sort-by <field>` (auth, https, name)
- Generate Markdown category tables automatically from JSON output
- Watch mode: re-run on file change and refresh derived documents
