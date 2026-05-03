# Smart Routing Message Template — Department Brief

**Trigger:** User says "use smart routing" or explicitly delegates by specialist
**Goal:** One actionable message per department, <30 seconds read time, clear ownership

---

## Template Structure

```
🚀 **[Sprint Name] — [Timebox]**

**Lead:** [Agent Name] | **Deadline:** [Date] | **Prize/Priority:** [Value]

**Status Baseline:**
- ✅ [Done items]
- 🔄 [In-progress items]
- 📋 [Planned/not started]

**Today's Critical Path ([Date]):**

1. **[Task Category 1]** — [specific deliverable]
   - [Subtask bullet if needed]
   - [Subtask bullet]

2. **[Task Category 2]** — [specific deliverable]
   - [Subtask bullet]

3. **[Task Category 3]** — [specific deliverable]
   - [Subtask bullet]

**Dependencies:**
- [External dependency with owner + eta]
- [Blocking item if any]

**Questions:**
- [Specific answer needed from lead]
- [Clarification required]

📁 Reference: [vault path to sprint plan or strategy doc]
📁 Handoff: [Green Room path if continuation]

—

**Additional notes:**
- [Opportunity scouting, sidetrack research, etc.]
```

---

## Example — Labs (DMOB)

```
🚀 **Solana Frontier Sprint — Day 2 Priority**

**Lead:** DMOB | **Deadline:** May 11 (9 days) | **Prize:** $230K + $680K sidetracks

**Status from Apr 28:**
- ✅ 4 Anchor programs scaffolded (916 LOC)
- ✅ AgentRegistry + JobEscrow deployed to devnet
- 🔄 Reputation + DisputeResolver: in progress
- 🔄 TypeScript SDK: not started

**Today's Critical Path (May 2):**

1. **Deploy Reputation program** to devnet
   - Verify tier calculation logic (Scout→Rookie→Pro→Legend)
   - Confirm NFT minting with Metaplex simulation

2. **Finish DisputeResolver deployment**
   - Poster-as-judge flow (hackathon simplification)
   - Fund routing (poster/worker/split) verification

3. **Kick off TypeScript SDK**
   - Wrap all 12 instructions
   - Phantom wallet adapter integration

4. **Integration test plan**
   - Happy path flow
   - Dispute + resolution edge cases

**Questions:**
- Any blockers on reputation tier math or dispute fund routing?
- SDK starting point: anchor-gen-client or custom TS client?

📁 Sprint plan: `/root/vaults/gentech/02-Labs/sprint-plan-solana-frontier-kite-ai.md`

—

**Also on radar:**
- 🔍 X402 payments protocol ($135K) — technical feasibility scan
- 🏷️ Solana Agent Hackathon registration status check
```

---

## Tag Format (copy-paste)

```
DMOB — [action summary]
Desmond — [content summary]
YoYo — [research/analysis summary]
```

**Do NOT** merge multiple agent tags in one message — send separate Telegram messages.

---

## File Naming for Handoffs

If the routing continues across sessions, create handoff file:
`09-Green Room/active-handoffs/YYYY-MM-DD-brief-description.md`

Keep it minimal — 10–15 lines max. Link to the message thread + sprint plan.
