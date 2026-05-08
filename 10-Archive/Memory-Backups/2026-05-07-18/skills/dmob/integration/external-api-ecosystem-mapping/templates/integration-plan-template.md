# Integration Plan Template — Third-Party API Ecosystem

**Domain:** [fill]  
**Date:** YYYY-MM-DD  
**Agent:** DMOB  
**Source:** [e.g., public-apis/public-apis, RapidAPI directory, domain-specific registry]

---

## 1. Purpose & Scope

What agent capability are we building?
- Primary user need: [e.g., book flights, check crypto prices, generate videos]
- Core features: [list 3–5]
- Domain categories to scan: [from source index]

---

## 2. Source Repository Analysis

| Field | Value |
|-------|-------|
| Repository | [URL] |
| Clone location | `/tmp/[repo]/` |
| Last refreshed | [date] |
| Total categories | [count] |
| Total APIs in source | [count] |
| Relevant categories identified | [list] |

---

## 3. Extraction Log

**Sections scanned:** [e.g., Transportation, Geocoding, Weather]

**Parsing command used:**
```bash
python scripts/parse-public-apis.py --sections "Transportation,Geocoding,Weather" --output api-catalog.json
```

**Regex pattern:**
```python
pattern = r'\| \[(.*?)\]\((.*?)\) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|'
```

---

## 4. Filtered API Inventory

| API | URL | Auth | HTTPS | CORS | Free Tier | Use Case | Priority |
|-----|-----|------|-------|------|-----------|----------|----------|
| [Name](url) | description | `No/apiKey/OAuth` | Yes/No | Yes/No/Unknown | e.g., 1000 req/mo | what it does | Tier 1/2/3 |

*(Populate from `api-catalog.json`)*

---

## 5. Tiering Rationale

### Tier 1 (Phase 1 — Ship Immediately)
**Criteria:** Free tier sufficient for MVP, simple auth, core feature coverage
- [ ] API 1 — reason
- [ ] API 2 — reason

### Tier 2 (Phase 2 — Post-MVP)
**Criteria:** Paid rate low but essential, limited free tier, medium complexity
- [ ] API 1 — reason

### Tier 3 (Phase 3+ — Backlog)
**Nice-to-have:** Expensive, niche, or low coverage
- [ ] API 1 — reason

---

## 6. Integration Architecture

```
[Agent Name]
      ↓
[Skill Module: domain_skills.py]
      ↓
[API Gateway Layer: retry, fallback, quota]
      ↓
[External APIs]
```

**Fallback chains:**
- Primary: [API A] → Fallback: [API B] → Fallback: [cached/error]

---

## 7. Cost Analysis

| API | Free Tier Limit | Unit Cost | Est. Monthly Usage | Est. Monthly Cost | Billing Alert |
|-----|----------------|-----------|-------------------|-------------------|---------------|
| [Name] | [number] | [$/call] | [number] | [$] | [80% threshold] |

**Total estimated monthly (Tier 1 only):** $X  
**Total estimated monthly (all phases):** $Y

---

## 8. Skill Blueprint

File: `skills/domain_agent_v1.py`

```python
from hermes.skills import SkillBase
import httpx
import os

class DomainAgentSkill(SkillBase):
    """[Domain] agent using public APIs."""
    
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
    
    @skill(priority=1)
    async def core_feature(self, ...):
        """Primary API call."""
        pass
    
    async def _fallback(self, ...):
        """Backup provider."""
        pass
```

---

## 9. Credential Management

```
~/.hermes/profiles/dmob/
├── .env.[domain]              # Local dev env vars (gitignored)
├── secrets/
│   └── [domain]/              # Hermes secret store entries
│       ├── api_key_1
│       ├── client_id
│       └── client_secret
└── cache/
    └── [domain]_quotas.json   # Monthly usage tracking
```

**Rotation policy:** [e.g., quarterly, on expiry]

---

## 10. Monitoring & Quotas

Cron: `0 */6 * * * cd /root/vaults/gentech && python scripts/check_quotas.py --domain [domain]`

Alert at 80% free tier usage. Auto-disable at 100% (fail-safe).

---

## 11. Quickstart Checklist

- [ ] Apply for API keys in order (Tier 1 first)
- [ ] Store credentials in Hermes secret store
- [ ] Clone skill template to `skills/domain_agent_v1.py`
- [ ] Test each endpoint with `scripts/test_apis.py`
- [ ] Wire skill into Hermes config
- [ ] Deploy to Telegram bot
- [ ] Monitor quota for 48h

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API downtime | Fallback chain + cached responses |
| Rate limit exceeded | Quota monitoring + graceful degradation |
| OAuth token expiry | Auto-refresh logic + secret rotation |
| Terms of Service violation | Review TOS for commercial use, add attribution |
| Data privacy | No PII sent to third-party without consent |

---

## 13. References

- Source repo: [URL]
- API docs: [individual links]
- Related skills: [travel-planning, blockchain-operations, etc.]

---

*Template version 1.0 — Replace bracketed placeholders per domain.*
