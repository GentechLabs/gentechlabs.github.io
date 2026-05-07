# ElevenLabs Agents Pricing & Integration Notes
**Retrieved**: 2026-05-03  
**Sources**: [ElevenLabs Pricing — Agents](https://elevenlabs.io/pricing?product=agents), [Agents Overview](https://docs.elevenlabs.io/agents/overview), [Burst Pricing Guide](https://docs.elevenlabs.io/agents/guides/burst-pricing)

## Product Segmentation
ElevenLabs separates its offerings into distinct products with **separate subscriptions and credit pools**:
- **ElevenCreative** — Text-to-speech, voice cloning, sound effects, music (subject of earlier TTS discussion)
- **ElevenAgents** — Conversational voice AI agents with tool calling, workflows, knowledge base
- **ElevenAPI** — API credits for programmatic access to various models

**Key takeaway**: An ElevenLabs subscription for one product (e.g., ElevenCreative) does *not* include access or credits for another product (e.g., ElevenAgents). The same `ELEVENLABS_API_KEY` may work across products, but usage quotas are independent.

## ElevenAgents Subscription Tiers
| Tier | Price (mo) | Credits / month | Seats | Notable features |
|------|------------|-----------------|-------|------------------|
| Free | $0 | 10,000 | 1 | Build for free |
| Starter | $6 | 30,000 | 1 | Commercial license, instant voice cloning |
| Creator | $22 ($11 first month) | 121,000 | 1 | Professional voice cloning, additional credits |
| Pro | $99 | 600,000 | – | 44.1kHz PCM output, 192kbps audio |
| Scale | $299 | 1,800,000 | 3 | Workspace seats, team collaboration, 3 professional voice clones |
| Business | $990 | 6,000,000 | 10 | Low-latency TTS (5¢/min), 10 professional voice clones |
| Enterprise | Custom | Custom | Custom | Custom terms, DPA/SLAs, BAAs, priority support |

**Credits** are the unit of usage for ElevenAgents (character-based). Unlike TTS minutes, agents consume credits per conversation/interaction.

## Startup Grants Program
- **12 months free** for qualifying startups
- **33M characters** included
- Covers building, launching, and testing
- Requires application approval

## Burst Pricing (Concurrency)
- Enabled per agent
- Allows up to **3×** your normal concurrency limit during spikes
- Excess calls charged at **2×** the standard rate
- Calls beyond burst limit are rejected
- Useful for handling traffic volatility while maintaining cost predictability

## Integration Readiness
- **SDKs**: Python (`elevenlabs`), JavaScript/TypeScript (`@elevenlabs/elevenlabs-js`), cURL
- **Tool calling**: Agents can call external APIs/tools (function calling)
- **Webhooks**: Post-call webhooks supported
- **Deploy options**: Web widget, React SDK, iOS (Swift), Android (Kotlin), React Native, SIP trunk, Twilio, WhatsApp, batch calls
- **Monitoring**: Real-time analytics, conversation analysis, experiments, A/B testing

## Common Pitfalls & Gotchas
- **Do not assume** TTS subscription covers Agents — they are separate
- Credits do **not** roll over or pool across products
- UI-based features (e.g., visual workflow builder) are not API features; check both
- Personal accounts may lack enterprise capabilities (SSO, elevated concurrency)
- Admin policies may block OAuth connections for Workspace accounts
- Burst pricing can lead to unexpected overages if not monitored

## Verification Checklist
- [ ] Confirm which product(s) the user's current subscription includes
- [ ] Verify desired features exist in the target tier (compare feature matrix)
- [ ] Check for free tier suitability or startup grant eligibility
- [ ] Review rate limits and concurrency caps for expected load
- [ ] Test API access with existing key (if available)
- [ ] Document all costs: subscription + expected overage + seat fees

## Quick Answer for Common Question
**"Can I use my current ElevenLabs subscription for voice agents?"**  
→ **No.** ElevenAgents requires its own subscription. TTS (ElevenCreative) credits and Agents credits are separate. You must add an ElevenAgents plan (minimum $6/mo Starter) to use the voice agents platform.

## Reference Links
- Pricing selector (switch between products): https://elevenlabs.io/pricing?product=agents
- API pricing (for comparison): https://elevenlabs.io/pricing/api
- Agents Overview: https://docs.elevenlabs.io/agents/overview
- Burst pricing: https://docs.elevenlabs.io/agents/guides/burst-pricing
- Startup Grants: Refer to ElevenLabs docs / Impact Program section
