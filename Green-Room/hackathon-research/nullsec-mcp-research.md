# 🔒 Nullsec MCP — Research Notes

**Source:** https://www.trynullsec.com/
**Found:** May 26, 2026

---

## What Nullsec Is

**Nullsec** = Security analysis platform for the AI agent era

**Tagline:** "AI-powered security & audit analysis for the agentic era"

**What it does:**
- Identifies critical security risks before production
- Scans for leaked API keys
- Checks missing security headers
- Analyzes AI-native products, agent infrastructure, vector APIs, LLM application stacks

---

## MCP Security Registry

**Nullsec MCP** = Security registry for Base MCP plugins

**Features:**
- Paste any MCP server URL → get full security report in 10 seconds
- Classifies every permission
- Scores every contract interaction
- Security-first approach to MCP plugin layer

---

## Why It Matters for GenTech

1. **Agent security** — We're building agent infrastructure (AAE, travel agent, DeFi governance)
2. **MCP plugin security** — We use MCP servers (Let's FG, Hive, etc.)
3. **Base integration** — Base is opening agent gateway, Nullsec secures plugin layer
4. **Production readiness** — Before going mainnet, we need security vetting
5. **OWASP compliance** — We already installed AGT for governance, Nullsec adds another layer

---

## Integration Opportunities

### For Agent Arena (AAE)
- Scan MCP servers before agents use them
- Verify DeFi protocol integrations
- Score contract interactions
- Detect permission issues

### For Travel Agent
- Verify Let's FG MCP security
- Check payment integrations
- Score booking channel reliability

### For DeFi Governance
- Integrate with AGT policy engine
- Add Nullsec scanning to pre-flight checks
- Score agent actions before execution

---

## How It Could Work

```
Agent wants to use MCP server
    ↓
Nullsec scans MCP server
    ↓
Security report generated
    ↓
Permission classification
    ↓
Contract interaction scoring
    ↓
Agent decides: Use / Don't Use / Use with Caution
```

---

## Next Steps

1. **Test Nullsec** with one of our MCP servers
2. **Get API access** if available
3. **Integrate** into agent workflow
4. **Add to security stack** alongside AGT

---

## Status

- [ ] Nullsec website accessed
- [ ] API documentation reviewed
- [ ] Tested with our MCP servers
- [ ] Integration plan created
- [ ] Added to security workflow

---

**Note:** Nullsec appears to be the security infrastructure layer we've been looking for. It complements AGT (governance) by providing MCP server vetting and contract interaction scoring.
