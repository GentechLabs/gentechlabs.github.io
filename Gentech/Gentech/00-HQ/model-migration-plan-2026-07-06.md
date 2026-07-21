# Model Migration Plan — Z.AI → OpenCode Go + Nous

## Timeline

| Date | Milestone |
|------|-----------|
| **Now — July 27** | Use Z.AI subscription (burn down credits) |
| **July 28** | Cancel Z.AI subscription |
| **July 28-29** | Migrate to OpenCode Go + Nous Research Portal |

---

## Current VPS Status

**Z.AI (Primary):**
- Model: GLM 4.7
- API Key: `301c64ba77334ff396e48ecd313201f1.Tg3XUkaookgzPDKe`
- Error: 401 (令牌已过期或验证不正确 — token expired or invalid)
- Action: Need valid API key to continue using until July 28

**OpenCode Go (Fallback):**
- Model: DeepSeek V4 Flash
- API Key: `${OPENCODE_GO_API_KEY}`
- Endpoint: `https://api.opencode.com` → ❌ NXDOMAIN
- Action: Need correct endpoint for migration

**Nous Research Portal:**
- Status: Not configured yet
- Action: Set up before July 28

---

## Migration Tasks

### Phase 1: Fix Z.AI (Now — July 27)

**Tasks:**
1. [ ] Get valid Z.AI API key (current key expired)
2. [ ] Test Z.AI connection
3. [ ] Verify GLM 4.7 and GLM 5.2 work
4. [ ] Continue using Z.AI until July 27

**Blocker:** Need valid API key

---

### Phase 2: Fix OpenCode Go (July 28-29)

**Tasks:**
1. [ ] Find correct OpenCode Go endpoint from documentation
2. [ ] Update config:
   ```yaml
   opencode-go:
     base_url: https://correct-endpoint.com
   ```
3. [ ] Test DeepSeek V4 Flash
4. [ ] Test DeepSeek V4 Pro
5. [ ] Set as fallback provider

**Resources:**
- OpenCode Go documentation
- API key already present in `.env`

---

### Phase 3: Configure Nous Research Portal (July 28-29)

**Tasks:**
1. [ ] Get Nous Research Portal API key
2. [ ] Add to `.env`:
   ```bash
   NOUS_API_KEY=your_nous_key_here
   ```
3. [ ] Add to `config.yaml`:
   ```yaml
   providers:
     nous:
       base_url: https://api.nousresearch.com
       client_id: nous-research
       client_secret: ${NOUS_API_KEY}
       type: oauth
   ```
4. [ ] Test Nous Research models
5. [ ] Set as fallback for specific tasks

---

### Phase 4: Switch Primary Provider (July 28-29)

**Tasks:**
1. [ ] Update default model:
   ```bash
   hermes config set model default deepseek-v4-flash
   hermes config set model provider opencode-go
   ```
2. [ ] Configure fallback chain:
   ```yaml
   fallback_providers:
     - provider: opencode-go
       model: deepseek-v4-flash
     - provider: nous
       model: nous-hermes-4
   ```
3. [ ] Test full fallback chain
4. [ ] Update cron job models (if pinned)
5. [ ] Cancel Z.AI subscription

---

## Model Selection Strategy

### Daily Tasks (Cheap)
**Primary:** DeepSeek V4 Flash (OpenCode Go)
**Cost:** ~$0.05/1M output tokens
**Use case:** Regular conversations, quick tasks

### Complex Tasks (Quality)
**Primary:** DeepSeek V4 Pro (OpenCode Go) or Nous Hermes 4
**Cost:** ~$0.20-0.50/1M output tokens
**Use case:** Audits, deep analysis, Sunday Review

### Vision Tasks (Specialized)
**Primary:** DeepSeek V4 Flash (OpenCode Go)
**Cost:** ~$0.05/1M output tokens
**Use case:** Image analysis

---

## Cost Comparison

| Provider | Model | Cost (Output) | Monthly (est.) |
|----------|-------|---------------|----------------|
| Z.AI | GLM 4.7 | $1.00/1M | $3,100 |
| OpenCode Go | DeepSeek V4 Flash | $0.05/1M | $155 |
| OpenCode Go | DeepSeek V4 Pro | $0.20/1M | $620 |
| Nous | Hermes 4 | TBD | TBD |
| **Target mix** | Flash (70%) + Pro (30%) | ~$0.11/1M | **$341** |

**Savings:** $2,759/month (89% reduction)

---

## Blockers

| Issue | Impact | Resolution |
|-------|--------|------------|
| Z.AI key expired | Cannot use until July 28 | Get valid API key |
| OpenCode Go endpoint wrong | Cannot set as primary | Find correct endpoint |
| No Nous API key | Cannot configure portal | Get API key |

---

## Next Actions

**Immediate:**
1. Get valid Z.AI API key to continue using until July 28
2. Find OpenCode Go correct endpoint

**July 28-29:**
1. Configure OpenCode Go with correct endpoint
2. Get and configure Nous Research Portal API key
3. Switch primary provider
4. Cancel Z.AI subscription

---

**Plan created:** July 6, 2026
**Migration date:** July 28, 2026
**Savings target:** $2,759/month (89%)

---

**Status:** ⏳ Waiting for valid Z.AI API key to continue Phase 1