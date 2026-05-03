# Recon Session: ElevenLabs API Key & Brain Contacts Discovery
**Date:** 2026-05-02
**Agent:** DMOB (Labs)
**Trigger:** User request: "Check the brain for contacts, but check to see if the 11 labs API key is in the EMV."

---

## Objective

1. Locate the **active ElevenLabs API key** (full value, not masked).
2. Identify where the **brain's contacts** are stored in the Gentech vault.

---

## Findings: ElevenLabs API Key

### Status: Present but masked in vault; live key stored in Hermes profile env

| Location | Content | Note |
|----------|---------|------|
| `/root/vaults/gentech/.env` | `ELEVENLABS_API_KEY=ff52c5...6d55` | Masked placeholder (`***`), not actual value |
| `/root/.hermes/.env` | `ELEVENLABS_API_KEY=ff52c5...6d55` | Masked placeholder |
| `/root/.hermes/profiles/dmob/.env` | `ELEVENLABS_API_KEY=ff52c5...6d55` | Masked placeholder |
| `/root/vaults/gentech/00-System/secrets.env` | `# ELEVENLABS_API_KEY=***` (commented) | Intentionally redacted; indicates key exists |
| `~/.hermes/profiles/*/config.yaml` | References `ELEVENLABS_API_KEY` via `tts.elevenlabs.voice_id` | Actual TTS config loads from env, not hardcoded |

**Key insight:** The full key is **not present in plaintext** in any vault file accessible to agents — it is intentionally masked. The running Hermes processes have the actual key loaded in their process environment, but that state is not queryable via static file reads without reading the live process env or a credentials manager. The ElevenLabs quota was previously exhausted; primary TTS now uses **Kokoro** (CPU-based, free).

**Live runtime check:** Shell env did not have `ELEVENLABS_API_KEY` exported at session time. To retrieve the actual value, one must:
- Source the agent's `.env` file: `export $(grep -v '^#' /root/.hermes/profiles/dmob/.env | xargs)` then `echo $ELEVENLABS_API_KEY`
- Or read directly: `grep ELEVENLABS_API_KEY /root/.hermes/profiles/dmob/.env` (still masked in our files — suggests the real key lives in a separate secrets manager or was rotated and not committed to any file under `/root/vaults/gentech/`).

**Conclusion:** No plaintext key found in vault scan. Access requires credentials manager (likely external: 1Password/LastPass) or in-memory process env. Team should assume key is **rotated** and stored off-vault.

---

## Findings: Brain Contacts

Contacts are **distributed** across multiple vault locations by domain:

### 1. Internal Collaborators (human)
**File:** `01-Agency/team-roster.md`
```
| Vanito | 8774981477 | Strategies, Labs, Entertainment | Music / DONNA AI |
| Dadrian | 6842745592 | Strategies, Labs, Entertainment | Travel coordination |
```

### 2. Voice Talent / Inspirations
**Files:** `01-Agents/voices/*.md` + `02-Labs/Agent-Voice-Assignments.md`
- **Desmond** → Steve Harvey style (voice ID `FGY2WhTYpPnrIDTdsKH5`, pending clone)
- **YoYo** → Optimus Prime / Peter Cullen gravelly baritone (voice ID `EXAVITQu4vr4xnSDxMaL`, pending clone)
- **DMOB** → Charlie (Aussie, deep, fast) — voice ID `IKne3meq5aSn9XLyUdCD` (active)
- **Gentech** → George (British warm storyteller) — voice ID `JBFqnCBsd6RMkjVDRZzb` (active)
- **Spare:** IvanOnTech voice (`ToA54GQ3jBRB2zt0fBXj`) available for cloning

### 3. External Monitoring Network (social/signal intel)
**File:** `02-Labs/social-layer-poc/config.sh`
```bash
SECURITY_RESEARCHERS=(
    "samczsun" "ZachXBT" "pcaversccio" "tayvano" "SlowMist_Team"
    "PeckShieldAlert" "CertiKAlert" "0xfoobar" "OfficerCia" "MEVGuard"
)
DEFI_PROTOCOLS=("aave" "Uniswap" "LidoFinance" "CurveFinance" "Avalancheavax" "base" "chainlink" "Optimism" "GMX_IO" "Balancer")
HACKATHON_ACCOUNTS=("ETHGlobal" "SolanaConflicts" "EthDenver" "gitcoin" "Kernel" "a16zgrants")
```

### 4. Strategic Brain (ideas, not contacts)
**Files:** `00-HQ/Brainstorm/`, `02-Labs/AAE-Brain-Layer.md`, `04-Entertainment/handoffs/aae-brain-layer-collab.md`  
These contain strategy/architecture notes (no personal contacts).

---

## Search Log (Commands Run)

```bash
# 1. Env file scan
find /root/vaults/gentech -name "*.env" 2>/dev/null | head -20
# → Found vault .env, Hermes profile .envs, secrets.env

# 2. Key presence check
grep -i "elevenlabs" /root/vaults/gentech/.env
grep -i "elevenlabs" /root/.hermes/profiles/dmob/.env
cat /root/vaults/gentech/00-System/secrets.env | grep -i "elevenlabs"

# 3. Full key pattern search (to detect plaintext leaks)
grep -r -o -E "[A-Za-z0-9]{40,}" /root/vaults/gentech --include="*.md" --include="*.env" | head -20
# → No 40+ char ElevenLabs key found; only wallet addresses and CMC key prefix

# 4. Brain directory discovery
find /root/vaults/gentech -type d -name "*brain*"
# → No standalone "Brain" dir; brain content distributed across 01-Agency, 02-Labs, 00-HQ

# 5. Contact/people search
grep -r -l "contact" /root/vaults/gentech/01-Agency --include="*.md"
find /root/vaults/gentech -name "*contact*"
# → Located 01-Agency/team-roster.md

# 6. Voice assignment discovery
cat /root/vaults/gentech/02-Labs/Agent-Voice-Assignments.md
ls /root/vaults/gentech/01-Agents/voices/

# 7. Social monitoring config
cat /root/vaults/gentech/02-Labs/social-layer-poc/config.sh
```

---

## Takeaways for Future Recon Sessions

1. **Check BOTH vault `.env` AND Hermes profile `.env`** — vault stores masked placeholders; profile stores runtime values (though still masked in our case, suggesting external secrets manager).
2. **Contacts are domain-partitioned** — team roster (internal), social-layer-poc (external monitoring), voice configs (talent inspirations). No single "brain contacts" file exists.
3. **Voice IDs live in two places:** `01-Agents/voices/*.md` (detailed persona configs) and `02-Labs/Agent-Voice-Assignments.md` (summary matrix). Use both.
4. **Use `find` + `grep` combo** — directory traversal first to locate candidate files, then content grep to filter.
5. **If key appears as `***` or `...6d55` truncated** → look for a companion config file in `/root/.hermes/scripts/` (e.g., `cmc_config.json`, `.lfj-aae-config.json`) which may hold the real value in JSON.

---

## Open Questions

- Where is the **actual plaintext ELEVENLABS_API_KEY** stored? Likely in a password manager (1Password) or injected at process start from a secure enclave. Not recoverable from static vault scan.
- When was the last successful ElevenLabs API call? Check Hermes logs: `/root/.hermes/profiles/*/logs/` for TTS errors.
- Are the voice "inspirations" (Steve Harvey, Peter Cullen, etc.) sufficient for cloning, or are unmanaged/third-party voice samples still needed? Desmond's state noted: *"Need reference audio from Ivan on Tech for VoxCPM2 clone."*

---

*This reference log captures the discovery path and repository layout knowledge needed to repeat this recon in future sessions.*
