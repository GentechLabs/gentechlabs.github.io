# 🔍 Privacy Sweep — 2026-08-22

**Scope:** `genTech-agent-kit` repo + entire `gentech` vault
**Tool:** privacy-audit skill + ripgrep (search_files)

## ✅ CRITICAL — 0 exposed secrets found

| Category | Result |
|----------|--------|
| GitHub tokens (`ghp_`/`gho_`/`github_pat_`) | ✅ None in repo or vault |
| API keys (`sk_live`, `AIza`, hardcoded) | ✅ None (1 false positive = base64 JPEG in HTML data URI) |
| Private keys / mnemonics (`PRIVATE_KEY`, `MNEMONIC`, `SEED_PHRASE`) | ✅ None live — only `os.environ.get()` refs + test vectors |
| Cloud creds (`AWS_SECRET`, `AKIA`, `MINIO`) | ✅ None |
| Live 64-hex wallet/private keys | ✅ None (all are test vectors, Solidity constants, tx hashes, build debug JSON) |

## ✅ FIXED — GitHub PAT stripped from git remotes

- **Before:** `https://ProtoJay4789:ghp_MRSHWmNiR...@github.com/...` in `.git/config`
- **After:** `https://github.com/...` (clean, no token)
- Auth still works via git credential store (`~/.git-credentials`)
- Verified: `ls-remote org` OK, raw GitHub files 200

## ⚠️ PERSONAL INFO — 13 hits, all INTENTIONAL/public

All are Jordan's own public-facing contact/portfolio material — NOT leaks:
| File | What |
|------|------|
| `06-Content/portfolio-*.html`, `index*.html` | `mailto:jordanjones0902@gmail.com` (public portfolio contact) |
| `09-Green Room/job-apps/*` | email on job apps (intentional) |
| `09-Green Room/*grant-application*.md` | email on grant apps (intentional) |
| `10-Labs/circle-grant-deck.html` | email in slide footer (intentional) |
| `10-Labs/x402-gateway/server.py` L895 | email in OpenAPI **public contact block** (intentional for API consumers) |

Per skill: portfolio/public contact email = **OK, keep**. No removal needed.

## 📁 `.env` files — all REFERENCE keys, none embed secrets
All 5 `.env`-named files use env-var *names* (`X402_API_KEY`, `OLLAMA_CLOUD_API_KEY`) or read them at runtime (`agent-gateway-fix.sh` greps `$HERMES_HOME/.env`). No hardcoded secret values.

## Verdict
**No actionable leaks.** Repo and vault are clean of live credentials. The only real fix was the git-remote PAT, which is done. Personal email is intentional (public portfolio/contact).

**Recommended (optional, low priority):** rotate the `ghp_MRSH...` PAT anyway since it was briefly in a config file; and move `~/.git-credentials` to a stricter permission if not already (`chmod 600`).