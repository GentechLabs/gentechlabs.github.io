---
name: department-routing-protocol
description: Route incoming work to the correct department agent and channel based on content type, domain, and urgency. Prevents HQ flooding and ensures specialists handle their domains.
tags: [routing, coordination, channels, delegation]
---

# Department Routing Protocol

## Routing Decision Tree

When a message arrives in HQ, evaluate in this order:

### 1. Is this a direct question to me (Gentech)?
- Status updates, team coordination, scheduling → **Handle in HQ**
- "What's the status on X?" → **Handle in HQ**

### 2. Does this belong to a specialist domain?

| Content Type | Route To | Channel | Keywords/Signals |
|---|---|---|---|
| **Smart contracts, code, audits, builds** | DMOB | Labs | contract, audit, code, deploy, SDK, API integration, hackathon build, repo, PR, bug |
| **Market research, competitive intel, pricing** | YoYo | Strategies | market, competitor, price, token, DeFi, yield, LP, analysis, due diligence, trends |
| **Content, social media, brand, narrative** | Desmond | Entertainment | post, tweet, content, blog, video, podcast, brand, narrative, copy, design |

### 3. Is this cross-department?
- If it spans 2+ departments → **Handle in HQ**, pull specialists as needed
- If it's research that feeds a build → Route to **YoYo first**, handoff to **DMOB**

### 4. Is this personal/urgent?
- Personal finance, travel, schedule → **Handle in HQ** (Jordan-only)
- Urgent/blocking → **Handle in HQ**, escalate immediately

## Routing Actions

### Route to DMOB (Labs)
```
1. Summarize the request in 1-2 sentences
2. Send to Gentech Labs with context
3. Tag: "DMOB — [task summary]"
4. Log handoff in Green Room
```

### Route to YoYo (Strategies)
```
1. Summarize the research question
2. Send to Gentech Strategies with context
3. Tag: "YoYo — [research question]"
4. Log handoff in Green Room
```

### Route to Desmond (Entertainment)
```
1. Summarize the content need
2. Send to Gentech Entertainment with context
3. Tag: "Desmond — [content brief]"
4. Log handoff in Green Room
```

## Anti-Patterns (Don't Do This)

- ❌ Handling everything in HQ when a specialist exists
- ❌ Sending raw links without context or routing decision
- ❌ Routing to the wrong department (e.g., market research to DMOB)
- ❌ Skipping the handoff log in Green Room
- ❌ Routing when you should just answer (status questions, quick facts)

## Routing Examples

| Input | Route | Why |
|---|---|---|
| "What's AVAX doing?" | YoYo → Strategies | Market/price question |
| "Audit this contract" | DMOB → Labs | Smart contract work |
| "Write a tweet thread" | Desmond → Entertainment | Content creation |
| "What's the Kite hackathon timeline?" | Gentech HQ | Status/scheduling |
| "Evaluate this SDK for our stack" | DMOB → Labs | Technical evaluation |
| "What's the competitive landscape for X?" | YoYo → Strategies | Market research |
| "Summarize this blog post" | Gentech HQ | Quick research, no specialist needed |
| "Build a demo using this" | DMOB → Labs | Engineering task |

## Verification

After routing, confirm:
- [ ] Correct channel targeted
- [ ] Context included (not just a raw link)
- [ ] Handoff logged in Green Room
- [ ] Specialist acknowledged (if not, follow up in 5 min)
