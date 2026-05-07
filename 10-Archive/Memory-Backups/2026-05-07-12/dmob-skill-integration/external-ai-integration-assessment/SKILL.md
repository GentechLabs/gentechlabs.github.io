---
name: external-ai-integration-assessment
description: Evaluate third-party AI services (voice agents, LLM APIs, specialized tools) for integration into Gentech's agent ecosystem — assess pricing, features, compatibility, and integration path.
category: integration
triggers:
  - "evaluate external AI service"
  - "check pricing for AI vendor"
  - "assess third-party tool for integration"
  - "can I use my current subscription with X"
  - "does vendor Y support feature Z"
  - "research third-party AI platform"
---

# External AI Integration Assessment

## Purpose
Determine whether a third-party AI service can be integrated into our systems and at what cost. Covers voice agents, LLM APIs, specialized AI tools, and platforms.

## When to Use
- Before committing to an external AI service integration
- When user asks about using existing subscriptions with a new product
- When comparing vendors for a capability (e.g., voice agents, function calling)

## Process

### 1. Identify Product Segmentation
Many vendors offer multiple distinct products with separate billing. Enumerate all relevant products from the vendor. Example: ElevenLabs has ElevenCreative (TTS), ElevenAgents (voice agents), and ElevenAPI (API credits). These are separate subscriptions.

### 2. Gather Official Sources
- Pricing page (UI subscription tiers)
- API documentation (usage-based costs)
- Developer docs / SDK references
- Integration guides / tooling docs
- FAQ (especially about subscription overlap)

### 3. Map Current Subscriptions
- Identify which product(s) the user's current subscription covers
- Determine if the desired service falls under that product umbrella or requires a separate subscription
- Check if the same API key works across products but credits are segregated

### 4. Document Pricing Model
- Tier structure (Free, Starter, Pro, Enterprise)
- Billing method: subscription vs pay-as-you-go vs credits
- Credit units (characters, minutes, tokens) and allocation per tier
- Burst/concurrency options and overage rates
- Free tier limits and startup grant programs

### 5. Assess Integration Readiness
- SDK availability (Python, JavaScript/TypeScript, etc.)
- Tool calling / function calling support
- Webhooks / event subscriptions
- Authentication mechanism (API key, OAuth)
- Rate limits and concurrency caps

### 6. Check Constraints
- Account type restrictions (personal vs Workspace vs Enterprise)
- Regional availability
- Data residency / privacy implications
- Usage quotas and hard limits

### 7. Produce Recommendation
- Feasibility with current setup (Yes/No/Conditional)
- Required subscription tier and monthly cost estimate for expected usage
- Integration steps / proof-of-concept path
- Risks and mitigations (cost overruns, rate limits)

## Common Pitfalls

### Single-Subscription Assumption
Assuming a single subscription covers all vendor products. Many companies modularize offerings (e.g., ElevenLabs TTS ≠ Agents, OpenAI ChatGPT Plus ≠ API). Always verify product boundaries explicitly.

### Separate Credit Pools
Even when the same API key works, different products often maintain separate credit/usage quotas. TTS credits don't transfer to Agents.

### UI vs API Disconnect
Features available in the web dashboard may not be exposed via API (or vice versa). Check both documentation branches.

### Hidden Cost Dimensions
- Burst pricing (2× rate during spikes)
- Seat fees for team plans
- Overage charges beyond included credits
- Minimum commitments

### Account Type Blocks
Personal accounts frequently lack enterprise features; admin policies may block OAuth connections or specific integrations.

## Verification

- Cross-check pricing page against API docs for consistency
- Test API access with the user's key (if available) to confirm permissions
- Review official FAQ regarding subscription overlap questions
- Source all statements with URLs and retrieval dates

## Deliverables

- **Comparison table**: Product, current coverage, required tier, monthly cost
- **Integration checklist**: Authentication, SDKs, rate limits, compliance
- **Reference links**: Official pricing, API docs, developer guides

## Related Skills

- `managed-integration-platforms` — operating middleware like Composio that connects to many services
- `research` — broader domain and market reconnaissance

## Reference Materials

- `references/elevenlabs-agents-pricing-2026-05.md` — ElevenLabs Agents pricing tiers, credit system, burst pricing, and integration readiness notes from 2026-05 investigation.
