# Forge Handoff — Firecrawl Deployment

**From:** Gentech (VPS)
**To:** Forge (Desktop)
**Created:** July 8, 2026
**Priority:** LOW — System is working, cosmetic fix only

---

## Situation

Firecrawl web scraper is deployed at `/root/firecrawl/` and fully operational. The attempt was to get it running so we can use it as a web scraping backend. Scraping works — verified with a live `example.com` scrape returning 200 + markdown content.

**Access:** `http://localhost:3005` or `http://2.24.195.196:3005`

---

## ✅ What Gentech Did

| Item | Status | Details |
|------|--------|---------|
| Docker compose up | ✅ Running | All services started |
| Scrape endpoint test | ✅ Working | `POST /v1/scrape` returns valid markdown |
| Health check | ✅ OK | Root returns `{"message":"Firecrawl API"}` |
| foundationdb-init fix attempt | ⚠️ Partially | Container still exits code 1 |

### Running Containers

| Container | Status | Port |
|-----------|--------|------|
| `firecrawl-api-1` | ✅ Up | `0.0.0.0:3005->3002/tcp` |
| `firecrawl-redis-1` | ✅ Up | — |
| `firecrawl-rabbitmq-1` | ✅ Up (healthy) | — |
| `firecrawl-nuq-postgres-1` | ✅ Up | — |
| `firecrawl-playwright-service-1` | ✅ Up | — |
| `firecrawl-foundationdb-1` | ✅ Up | — |
| `firecrawl-foundationdb-init-1` | ❌ Exited (1) | One-shot init |

---

## 🐛 The Bug: foundationdb-init Fails on Restart

### Root Cause

The init container runs this entrypoint:

```bash
sleep 5 && out=$(fdbcli -C /var/fdb/fdb.cluster --exec 'configure new single ssd' 2>&1); \
status=$?; printf '%s\n' "$out"; \
if [ "$status" -eq 0 ]; then exit 0; fi; \
printf '%s\n' "$out" | grep -Eiq 'already.*configured|database.*configured'
```

On **first boot**, `fdbcli` creates the database and exits 0 → container exits 0 (success).
On **subsequent boots**, `fdbcli` returns:

```
Database created
ERROR: Database already exists! To change configuration, don't say `new'
```

Exit code is 1 (error), so the fallback grep runs. **But the grep pattern `database.*configured` doesn't match `"Database already exists"`** — there's no "configured" in the error message. So grep returns non-zero, container exits 1.

### The Fix (5 minutes)

In `/root/firecrawl/docker-compose.yaml`, line 202, change the grep pattern to also match `"already exists"`:

```yaml
# Current (broken):
- "sleep 5 && out=$(fdbcli -C /var/fdb/fdb.cluster --exec 'configure new single ssd' 2>&1); status=$$?; printf '%s\n' \"$$out\"; if [ \"$$status\" -eq 0 ]; then exit 0; fi; printf '%s\n' \"$$out\" | grep -Eiq 'already.*configured|database.*configured'"

# Fixed:
- "sleep 5 && out=$(fdbcli -C /var/fdb/fdb.cluster --exec 'configure new single ssd' 2>&1); status=$$?; printf '%s\n' \"$$out\"; if [ \"$$status\" -eq 0 ]; then exit 0; fi; printf '%s\n' \"$$out\" | grep -Eiq 'already.*configured|database.*configured|already exists'"
```

Just append `|already exists` to the grep pattern.

**After fix:** `docker compose -f /root/firecrawl/docker-compose.yaml up -d foundationdb-init`

The container should exit 0 on subsequent starts.

---

## 📡 API Tested

Scrape is working:

```bash
curl -s -X POST http://localhost:3005/v1/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

Returns:
```json
{"success":true,"data":{"markdown":"Example Domain...","metadata":{"statusCode":200,...}}}
```

---

## 🔧 Forge Tasks

### [Task 1] Fix foundationdb-init grep pattern (5 min)

1. Edit `docker-compose.yaml` — append `|already exists` to the grep pattern
2. Run `docker compose -f /root/firecrawl/docker-compose.yaml up -d foundationdb-init`
3. Verify: `docker logs firecrawl-foundationdb-init-1` shows exit 0

### [Task 2] Verify API is usable (10 min, if interested)

Test more complex scrapes:
- JavaScript-rendered pages
- Search/crawl endpoints
- Rate limiting behavior

### [Task 3] Consider integrating with cron jobs

Possibilities to discuss:
- Use Firecrawl for daily web scraping cron jobs
- Replace browser-based scrapping in existing cron workflows
- Feed scraped data into vault research pipeline

---

## 🤔 Notes

- The `NUQ_BACKEND` defaults to PostgreSQL (not FoundationDB), so the FDB init failure doesn't affect queue operations
- FDB infrastructure is there for when you want to switch to `NUQ_BACKEND=fdb` — it just needs a clean init
- The `AUTUMN_SECRET_KEY` warning in logs is harmless (optional telemetry)
- Resources: API uses 2 CPUs / 4GB RAM (Playwright), 4 CPUs / 8GB RAM (API)

---

## 📂 Files

| Path | Purpose |
|------|---------|
| `/root/firecrawl/docker-compose.yaml` | Main compose config (needs grep fix) |
| `/root/firecrawl/docker-compose.override.yaml` | Local overrides |

---

**Priority:** Low — the system is working. Fix it when you have 5 minutes of cleanup time.
**Verified:** ✅ Scrape endpoint functional. FoundationDB init failure is cosmetic.
