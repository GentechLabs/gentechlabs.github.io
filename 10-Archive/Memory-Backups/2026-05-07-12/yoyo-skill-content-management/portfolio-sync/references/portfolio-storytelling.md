# Portfolio Storytelling Templates

These narrative blocks explain *why* the GenTech agent stack is different. Use verbatim or adapt for the "How Our Agent Stack Is Different" section.

---

## 1. Multi-Layer Agent Architecture (AAE)

> The night we cracked agent economy design, we didn't just build a bot — we built **layers of negotiable intent**. Each agent (Strategist, Marketer, Engineer) has defined deliverables, escrowed payment terms, and validation hooks. This isn't a single prompt; it's a coordinated workforce where agents can subcontract to each other and audit completion before payment releases.
>
> **Example:** A content request flows Strategist → Marketer → Engineer, with each gate requiring deliverable validation before funds move. Agents don't just execute — they negotiate, validate, and release.

---

## 2. Brain System · Green Room · Mess Hall

> We treat agents like employees, not tools. Every agent has a **brain system** (context store), a **green room** (safe testing environment), and access to the **mess hall** (cross-agent coordination channel). When an agent hits an error, it doesn't just fail — it retreats to the green room, logs the incident, and signals the team for a standup. We troubleshoot in production, then patch the brain so the mistake doesn't repeat.
>
> **In practice:** An agent error triggers a Mess Hall post → team discusses → brain updated → same error never happens twice.

---

## 3. Error-First · Build Back Better

> We don't hide failures. Every error is a **training signal**. When something breaks, we: (1) Capture the error in the Mess Hall, (2) Analyze root cause in the Green Room, (3) Update the agent's brain (context + safeguards), (4) Deploy the fix. This creates compounding reliability — each failure makes the system smarter.
>
> **Result:** Agents get more capable over time, not less. We measure error rate reduction week-over-week.

---

## 4. 4-Department Agent Collaboration

> GenTech runs as a **virtual company** with four departments:
>
> - **Strategies (YoYo):** Numbers-first, risk-aware, portfolio optimization, LP monitoring, on-chain analytics — the quant mind.
> - **Social Growth (DMOB):** Distribution engine, X/Twitter amplification, hackathon visibility, content scaling — the megaphone.
> - **Marketing (Desmond):** Narrative positioning, brand voice, release comms, technical documentation — the storyteller.
> - **Engineering (Jordan):** Infrastructure, orchestration layer, prompt engineering, deployment automation — the builder.
>
> Each agent has a department, a role, and clear escalation paths. Projects aren't solo efforts — they're cross-functional deliveries where each department contributes its specialty.

---

**Usage:** Place these as individual `.methodology-card` blocks in the `#methodology` section. Add a brief intro heading: "How Our Agent Stack Is Different" or "Why GenTech Agents Are Different".
