# Firecrawl — foundationdb-init Fix

**From:** Gentech handoff `2026-07-08-firecrawl-deployment-handoff.md`
**Fix:** 5-minute grep pattern change

---

## The Bug

On subsequent boots, `fdbcli` returns:
```
Database created
ERROR: Database already exists! To change configuration, don't say `new'
```

Exit code is 1. The grep pattern `database.*configured` doesn't match `"Database already exists"` — no "configured" in the error. So grep returns non-zero, container exits 1.

## The Fix

In `docker-compose.yaml`, append `|already exists` to the grep pattern:

```yaml
# Current (broken):
- "sleep 5 && out=$(fdbcli -C /var/fdb/fdb.cluster --exec 'configure new single ssd' 2>&1); status=$$?; printf '%s\n' \"$$out\"; if [ \"$$status\" -eq 0 ]; then exit 0; fi; printf '%s\n' \"$$out\" | grep -Eiq 'already.*configured|database.*configured'"

# Fixed:
- "sleep 5 && out=$(fdbcli -C /var/fdb/fdb.cluster --exec 'configure new single ssd' 2>&1); status=$$?; printf '%s\n' \"$$out\"; if [ \"$$status\" -eq 0 ]; then exit 0; fi; printf '%s\n' \"$$out\" | grep -Eiq 'already.*configured|database.*configured|already exists'"
```

## After Fix

```bash
docker compose -f /root/firecrawl/docker-compose.yaml up -d foundationdb-init
docker logs firecrawl-foundationdb-init-1
# Should show exit 0
```

## Note

The `NUQ_BACKEND` defaults to PostgreSQL, so FDB init failure doesn't affect queue operations. This is cosmetic — fix when you have 5 minutes.
