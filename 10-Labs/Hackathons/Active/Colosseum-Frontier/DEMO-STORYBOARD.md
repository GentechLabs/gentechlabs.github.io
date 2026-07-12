# AgentEscrow — Demo Storyboard

**Video Length:** 5 minutes  
**Format:** Screen recording with voiceover  
**Tool:** Solana Explorer + demo app + terminal  
**Tone:** Confident, technical, fast-paced  

---

## Pre-Recording Checklist

- [ ] All 4 programs deployed to Solana devnet
- [ ] Demo app running locally (`localhost:3000`)
- [ ] Phantom wallet funded (2 SOL minimum)
- [ ] Terminal open with Solana Explorer
- [ ] Screen recording software ready (OBS / Loom)
- [ ] Test agents pre-registered (saves time on camera)

---

## Act 1: The Hook (0:00 — 0:30)

### Visual
Black screen → white text fades in:

> **"Agents are already transacting."**
> **"There's no trust layer."**

### Voiceover
> "AI agents are getting better at doing work every day. But no one has built the financial infrastructure for them to get paid — trustlessly, verifiably, and automatically. Until now."

### Visual
Logo animation → AgentEscrow wordmark + tagline:
> "Trust infrastructure for the agent economy."

**Transition:** Quick cut to Solana Explorer showing a live transaction.

---

## Act 2: Trust Setup (0:30 — 1:30)

### Scene 1: SAP v2 Identity Registration (30s)

**Visual:** SAP Identity Layer → AgentAccount PDA

**Steps (on screen):**
1. Navigate to SAP Identity Layer
2. Click "Register Agent"
3. Fill form:
   - Agent name: `CodeBreaker`
   - Capabilities: `["security-audit", "code-review"]`
   - Pricing tier: 50,000 lamports per call
4. Click "Register" → single transaction
5. AgentAccount PDA created with identity metadata

**Voiceover:**
> "First, we create the agent's on-chain identity using SAP v2's Identity Layer. One transaction — the agent gets an AgentAccount PDA with name, capabilities, and pricing. Discoverable on SAP Explorer."

**Show:** SAP Explorer → new agent appears in discovery feed

### Scene 2: World ID Verification (15s)

**Visual:** World ID verification popup

**Steps:**
1. Click "Verify with World ID" on agent profile
2. World App popup → scan → approve
3. Verification badge appears on agent profile ✓

**Voiceover:**
> "Next, we verify the human behind the agent using World ID. This prevents Sybil attacks — one human, one verified agent. The nullifier hash is stored on-chain."

### Scene 3: Reputation NFT Mint (15s)

**Visual:** Metaplex NFT minting confirmation

**Steps:**
1. After registration, Metaplex Core NFT auto-mints
2. Show NFT in agent profile: "Scout Tier" badge
3. Show NFT metadata on Solana Explorer

**Voiceover:**
> "A soulbound reputation NFT is minted automatically — non-transferable, tied to this agent forever. Right now it's Scout tier. That changes as the agent completes jobs."

---

## Act 3: Job Lifecycle (1:30 — 3:00)

### Scene 4: Job Posting (30s)

**Visual:** Demo app → "Post Job" form

**Steps:**
1. Click "Post New Job"
2. Fill form:
   - Title: `Review Solana program for vulnerabilities`
   - Description: `Audit the AgentEscrow program for reentrancy, overflow, and PDA collision risks.`
   - Payment: 0.5 SOL
   - Deadline: 72 hours
3. Click "Post Job" → Phantom signs → approve
4. Job appears in "Open Jobs" feed with locked funds

**Voiceover:**
> "Now a human posts a job. They describe the work, set payment and deadline, and fund the escrow. The SOL is locked in a PDA — no one can touch it until the job is completed or the deadline passes."

**Show:** Solana Explorer → escrow PDA → locked balance

### Scene 5: Agent Accepts (30s)

**Visual:** Agent view → job feed → "Accept Job" button

**Steps:**
1. Switch to agent's perspective (Swig wallet)
2. Agent sees matching job in feed
3. Click "Accept Job" → Swig signs programmatically
4. Job status changes: Open → Accepted

**Voiceover:**
> "An agent sees the job, matches it to their capabilities, and accepts. The acceptance is signed by the agent's Swig wallet — a programmable smart wallet. No human keypair needed."

**Show:** Solana Explorer → job account → status field updated

### Scene 6: Work Submission (30s)

**Visual:** Agent submits deliverable

**Steps:**
1. Agent clicks "Submit Work"
2. Enter IPFS hash: `Qm...` (simulated deliverable)
3. Swig signs → submission recorded on-chain
4. Job status: Accepted → Submitted

**Voiceover:**
> "The agent completes the work, uploads the deliverable to IPFS, and submits the hash on-chain. The job is now pending human approval."

### Scene 7: Approval + Settlement (30s)

**Visual:** Human approves work

**Steps:**
1. Human sees submitted work
2. Reviews deliverable (IPFS link)
3. Clicks "Approve & Release"
4. Phantom signs → funds release to agent's Swig wallet
5. Job status: Submitted → Approved → Completed

**Voiceover:**
> "The human reviews the work, approves it, and the escrow releases. Funds flow directly to the agent's Swig wallet. Settlement is instant."

**Show:** Solana Explorer → transfer transaction → agent wallet balance updated

---

## Act 4: Reputation Update (3:00 — 3:30)

### Scene 8: Rating + NFT Update (30s)

**Visual:** Rating popup → NFT tier upgrade

**Steps:**
1. After approval, human rates agent 5/5
2. Reputation score updates on-chain
3. NFT metadata updates: jobs_completed += 1, reputation += 10
4. Show tier progression: Scout → Rookie (after 3 jobs)

**Voiceover:**
> "The human rates the agent. The reputation score updates on-chain, and the soulbound NFT reflects the new tier. Reputation is portable — any protocol can read it."

**Show:** Side-by-side: old NFT metadata → new NFT metadata

---

## Act 5: Dispute Resolution (3:30 — 4:15)

### Scene 9: Bad Submission (15s)

**Visual:** New job → agent submits garbage

**Steps:**
1. Show a second job (pre-setup)
2. Agent submits obviously bad deliverable
3. Human clicks "Dispute"

**Voiceover:**
> "Not every job goes smoothly. When an agent submits bad work, the human can dispute."

### Scene 10: Resolution (30s)

**Visual:** DisputeResolver evaluating

**Steps:**
1. Dispute opens → evidence window starts
2. Both parties submit evidence
3. DisputeResolver evaluates (AI-assisted or manual)
4. Verdict: human wins → full refund
5. Agent reputation penalized

**Voiceover:**
> "The DisputeResolver evaluates evidence from both sides. In this case, the human wins a full refund. The agent's reputation takes a hit. That's the trust layer — bad actors get penalized, good actors get rewarded."

**Show:** Solana Explorer → refund transaction → agent rep score decreased

---

## Act 6: Agent-to-Agent Payments (4:15 — 4:45)

### Scene 11: x402 Micropayment (30s)

**Visual:** Two agents paying each other

**Steps:**
1. CodeBreaker needs data from DataMiner
2. CodeBreaker pays 0.005 SOL via x402
3. DataMiner delivers data instantly
4. Both agents' reputation NFTs update

**Voiceover:**
> "For small, instant transactions between agents, we use x402 — the HTTP 402 standard for micropayments. No escrow needed for sub-cent payments. Fast, cheap, trustless."

**Show:** Transaction hash → memo field → amounts

---

## Act 7: Closing (4:45 — 5:00)

### Visual
Return to black screen → white text:

> **"SAP v2 gives agents an identity."**
> **"AgentEscrow gives them a career."**

### Voiceover
> "SAP v2 handles identity and discovery. AgentEscrow handles marketplace, reputation, and escrow. Together — the full stack for the agent economy."

### Visual
Logo + links:
```
github.com/ProtoJay4789/agent-escrow
agentescrow.app
```

**End.**

---

## Production Notes

### Recording Tips
- Use **dark mode** throughout — matches Solana brand aesthetic
- Speed up loading screens (2x) but keep transactions at 1x
- Add subtle zoom on important UI elements
- Use consistent terminal/Explorer positioning

### Audio
- Voiceover: confident, not rushed, technical but accessible
- Background: subtle ambient electronic (low volume)
- No music during code/transaction segments

### B-Roll (optional)
- Quick cuts of Solana Explorer transactions
- Agent profile pages
- World ID verification flow
- Metaplex NFT gallery

### Assets Needed
- [ ] AgentEscrow logo (SVG)
- [ ] Demo app deployed to localhost
- [ ] Pre-funded Phantom wallet
- [ ] Pre-registered test agents
- [ ] Background music track (royalty-free)
