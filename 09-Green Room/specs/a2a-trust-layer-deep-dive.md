# Multi-Agent Trust Layer — Deep Dive (borrow for a2a design)

**Source:** [github.com/Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) — `advanced_ai_agents/multi_agent_apps/multi_agent_trust_layer/`
**Date:** 2026-08-03
**Author:** Shubham Saboo / Unwind AI · Apache-2.0 · repo 130K★
**Status:** ✅ Verified working — ran the demo, trust scoring + scope narrowing + policy + audit all pass.
**Local:** cloned at `/root/repos/awesome-llm-apps/` (depth-1)

---

## TL;DR

A reference implementation of a **trust layer for multi-agent systems**: verifiable agent identity with human sponsor, 0–1000 trust scoring with behavioral adjustment, **cryptographically narrowed delegation chains**, role-based policy enforcement, and a full audit trail. This is a strong reference architecture for our a2a module's **trust + delegation-scope** substrate. Apache-2.0 → we can genuinely build on it, not just borrow ideas.

---

## The 5 mechanisms (with the meat)

### 1. Agent Identity + Human Sponsor
`AgentIdentity` = agent_id + public_key + **human_sponsor** (accountable email) + organization + roles. Every agent is anchored to a human who owns accountability. Registry supports register/revoke.

> **Our angle:** maps directly to our `agent-handoff-enforcement`. We have the board but no formal identity anchor. An agent should carry *who sponsors it* (Jordan for Gentech, etc.) so accountability is explicit.

### 2. Trust Scoring Engine (0–1000)
`TrustScore` with level bands: 900+ TRUSTED, 700+ STANDARD, 500+ PROBATION, 300+ RESTRICTED, <300 SUSPENDED. Behavioral deltas:
- `task_completed` +10 · `stayed_in_scope` +5 · `delegation_success` +15
- `scope_violation_attempt` **−50** · `inaccurate_output` −30 · `resource_exceeded` −20 · `security_violation` **−100** · `delegation_failure` −25
- Bounded 0–1000, full history kept per agent.

> **Our angle:** this is the "self-audit" loop of a2a. Our `harness-critic` audits outputs, but doesn't score *behavior over time* into a reputation that gates future delegation. A trust score is the durable signal that answers "should I delegate to this agent again?"

### 3. Delegation Scope with Narrowing (the standout)
`DelegationScope` = allowed_actions / denied_actions / allowed_domains / max_tokens / time_limit / **max_sub_delegations** / custom_constraints. `.narrow()` computes the intersection for sub-delegation — a child delegation can ONLY be a subset of the parent's scope (allowed_actions ∩, denied ∪, min of limits). Delegations are signed, expiring, and revocable.

> **Our angle:** this is the "discover→talk→self-audit" trust core. When Gentech delegates to Forge, the scope should *narrow* — Forge can do exactly what Gentech authorized and nothing more. This is cryptographically-gated least-privilege for agent-to-agent, which is exactly what Jordan's a2a priority needs. **This is the mechanism most worth adopting.**

### 4. Policy Engine (role + trust gating)
`MultiAgentPolicyEngine.evaluate()` checks: agent has trust score → not suspended → role policy (base_trust_required, allowed/denied actions) → delegation scope → RESTRICTED requires human approval. Returns `(allowed, reason)`.

> **Our angle:** mirrors our `founder-guard` / human-judgment stance — restricted-level agents require human sign-off. Formalizes the "human gates everything destructive" rule we already follow.

### 5. Full Audit Trail
Every authorization logged: `(timestamp, event_type, agent_id, action, delegation_id, result, details)`. Filterable by agent.

> **Our angle:** this IS the evidence lineage we just borrowed from LoopX, but structured as a queryable log instead of a handoff stub. Stronger form of the same idea.

---

## The critical bug they fixed (worth noting)
The `.narrow()` method has a comment + fix: an empty `allowed_actions` set previously collapsed to "all allowed" (a classic least-privilege security hole — empty set read as wildcard). They switched to a `None` sentinel meaning "all" vs empty set meaning "nothing". **Lesson: in delegation logic, an empty allow-list must mean DENY, never ALLOW.** This is exactly the kind of footgun our a2a module must avoid.

---

## What to borrow vs. what we already have

| Trust-layer primitive | We already have | Borrow? |
|---|---|---|
| Agent identity + human sponsor | Handoff board (no formal identity) | ✅ Adopt — anchor each agent to a sponsor |
| Trust scoring (0–1000, behavioral) | `harness-critic` output audit (no score-over-time) | ✅ Adopt — durable reputation gates delegation |
| Delegation scope + narrowing | No formal least-privilege delegation | 🔴 **STRONGEST — adopt** |
| Role-based policy engine | `founder-guard`, human-judgment rules | 🟡 Formalize into role policies |
| Audit trail | LoopX evidence-lineage stub (just added) | ✅ Upgrade to queryable log |
| Cryptographically signed delegations | No | ⚠️ Nice-to-have — real crypto sigs |
| LLM-dependent? | — | ❌ Core is pure Python, no OpenAI needed for the mechanisms |

---

## Verdict

**Build on it.** Apache-2.0, verified working, pure-Python core (no LLM dependency in the trust mechanisms). The **delegation-scope narrowing** and **trust scoring** are the two mechanisms that most advance Jordan's a2a priority — they turn "agent-to-agent comms" from message-passing into *governed, least-privilege delegation with reputation*.

## Action items
- [ ] Port the trust-layer core (`TrustLayer` / `DelegationScope` / `TrustScoringEngine`) into our a2a module design as the governance substrate
- [ ] Map our agents to identity+roles: Gentech=orchestrator(900), Forge=specialist, ClawWork workers, GTA executor
- [ ] Wire delegation-scope narrowing into `agent-handoff-enforcement` (child handoffs can only be subsets of parent scope)
- [ ] Cross-ref the `multi_mcp_agent_router` pattern for the KeeperHub MCP wiring (specialist agents with per-tool scoping)
