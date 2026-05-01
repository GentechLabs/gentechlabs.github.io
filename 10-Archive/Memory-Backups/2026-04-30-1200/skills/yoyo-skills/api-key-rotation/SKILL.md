---
name: api-key-rotation
description: "Securely rotate API keys across scripts, configs, and cron jobs. Save credentials, update all references, verify functionality."
category: devops
triggers:
  - API key update
  - credential rotation
  - new API key
  - update API key
  - rotate token
  - refresh API key
  - CMC API key
  - CoinMarketCap key
  - save API key securely
---

# API Key Rotation Workflow

Securely update API keys across scripts, configs, and cron jobs. Ensures all dependent systems use the new credential.

## When to Use

- User provides a new API key (CMC, exchange, service)
- API key expires or is compromised
- Adding API access to a new service
- After security audit recommends credential rotation

## Steps

### 1 — Save Key Securely

```bash
# Create secrets directory if needed
mkdir -p ~/.hermes/profiles/yoyo/secrets

# Save key with restricted permissions
echo "YOUR_KEY_HERE" > ~/.hermes/profiles/yoyo/secrets/SERVICE_api_key.txt
chmod 600 ~/.hermes/profiles/yoyo/secrets/SERVICE_api_key.txt
```

**Security Rules:**
- Never save API keys in vault (synced to GitHub)
- Use `~/.hermes/profiles/yoyo/secrets/` (not synced)
- Set permissions to 600 (owner read/write only)
- Delete key from chat after confirming save

### 2 — Update Config Files

Check common config locations:

```bash
# Check for existing config
cat ~/.hermes/scripts/SERVICE_config.json

# Update if exists
python3 << 'EOF'
import json
config_path = os.path.expanduser("~/.hermes/scripts/SERVICE_config.json")
with open(config_path, 'r') as f:
    config = json.load(f)
config["api_key"] = "NEW_KEY"
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
EOF
```

### 3 — Find All Script References

```bash
# Search for API key variable names
grep -r "SERVICE_API_KEY\|api_key.*SERVICE\|X-SERVICE-KEY" /root/vaults/gentech/03-Strategies/scripts/
grep -r "SERVICE_API_KEY\|api_key.*SERVICE" ~/.hermes/scripts/
```

**Common patterns to search:**
- `CMC_API_KEY`, `COINMARKETCAP_API_KEY`
- `EXCHANGE_API_KEY`, `TRADING_API_KEY`
- `"X-CMC_PRO_API_KEY"` in headers
- `os.environ.get("SERVICE_API_KEY")`

### 4 — Update Scripts

For each script that uses the key:

```python
# Find the line
grep -n "SERVICE_API_KEY" /path/to/script.py

# Update using Python (more reliable than sed for complex strings)
python3 << 'EOF'
with open('/path/to/script.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'OLD_KEY_PATTERN' in line:
        lines[i] = line.replace('OLD_KEY_PATTERN', 'NEW_KEY')

with open('/path/to/script.py', 'w') as f:
    f.writelines(lines)
EOF
```

**Pitfall:** Some scripts truncate keys in logs (`ff52c5...6d55`). The actual file may have the full key — verify with `xxd` or `cat | head`.

### 5 — Verify Key Works

```python
import urllib.request
import json

api_key = "YOUR_NEW_KEY"
url = "SERVICE_API_ENDPOINT"
req = urllib.request.Request(url, headers={"X-API-KEY": api_key})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        print(f"API key works! Response: {data}")
except Exception as e:
    print(f"API key error: {e}")
```

### 6 — Test Dependent Cron Jobs

```bash
# List cron jobs that might use the key
hermes cron list | grep -i "SERVICE\|watchlist\|price"

# Force-run each to verify
hermes cron run JOB_ID
```

### 7 — Confirm to User

Message the user:
- ✅ Key saved to: `~/.hermes/profiles/yoyo/secrets/SERVICE_api_key.txt`
- ✅ Files updated: [list]
- ✅ Cron jobs verified: [list]
- ✅ API test passed: [endpoint response]
- "You can safely delete the key from chat now."

## Pitfalls

| Issue | Symptom | Fix |
|-------|---------|-----|
| Key in vault (synced) | Key exposed on GitHub | Move to `~/.hermes/profiles/yoyo/secrets/` |
| Wrong permissions | `Permission denied` on read | `chmod 600` the file |
| Truncated key in logs | Script shows `ff52c5...6d55` | Check actual file with `xxd`, may be full key |
| Multiple config locations | Some scripts still use old key | Search broadly: `grep -r "OLD_KEY" ~/.hermes/` |
| API rate limits | Verification fails | Wait and retry, or test with smaller request |

## Security Checklist

- [ ] Key saved outside vault (not synced)
- [ ] File permissions set to 600
- [ ] All script references updated
- [ ] Config files updated
- [ ] Key verified working
- [ ] Cron jobs tested
- [ ] User confirmed to delete from chat
- [ ] No key in chat history (user deletes)

## Related Skills

- `finance/crypto-price-fetch` — CMC API usage patterns
- `devops/cron-job-audit` — Cron job health verification
