# AgentEscrow Demo Video Script

**Duration:** 2 minutes 30 seconds  
**Format:** Screen recording + voiceover  
**Target:** Kite AI hackathon judges  
**Tone:** Technical but accessible. Show, don't tell.

---

## 🎬 Opening (0:00–0:15)

**[Visual: Terminal window with `forge test` running. Tests passing in green.]**

**Voiceover:**
> "Most hackathon demos show you a prototype. We're going to show you production code — fifty-three tests, zero failures, and a trust layer that AI agents actually need."

**[Text overlay: "AgentEscrow — Trust Layer for the Agentic Economy"]**

---

## 📝 The Problem (0:15–0:35)

**[Visual: Simple diagram — User → Agent → ??? → Service Provider]**

**Voiceover:**
> "Imagine you ask an AI agent to analyze Solana LST yields. It needs to call three paid APIs. But here's the problem: who pays? How do you know the agent actually did the work? And what if it hallucinates the result?"

**[Visual: Three bullets appear — 'No proof of work' / 'Human approval bottleneck' / 'Slow traditional rails']**

**Voiceover:**
> "Today, agents run on prepaid budgets with no proof of work, or they need human approval for every transaction. That's not autonomy — that's a chatbot with extra steps."

---

## ⚖️ The Solution (0:35–1:05)

**[Visual: Switch to code — `AgentEscrow.sol` opening lines]**

**Voiceover:**
> "AgentEscrow is a modular, chain-agnostic trust layer. The buyer locks USDC in a smart contract. The agent executes the work autonomously. And an AI validator checks quality before funds are released."

**[Visual: Scroll through contract — highlight `createEscrow`, `validateWork`, `releaseFunds`]**

**Voiceover:**
> "EIP-712 signatures. Reentrancy guards. Replay attack protection. This isn't a toy — it's production security patterns."

---

## 🔗 Kite AI Integration (1:05–1:35)

**[Visual: Architecture diagram — zoom into Kite chain section]**

**Voiceover:**
> "Here's where Kite AI fits. Agent Passport gives every agent an identity. The AA SDK enables gasless transactions. And attestations post proof-of-execution to the Kite chain."

**[Visual: Animated flow — arrow from Agent → Kite Chain → Attestation record]**

**Voiceover:**
> "Every transaction becomes a reputation event. Agents build on-chain track records. High-reputation agents get better rates and faster settlement. It's not just payment — it's trust infrastructure."

---

## 🧪 Live Demo (1:35–2:05)

**[Visual: Terminal — run through the test suite]"

```bash
$ forge test
[PASS] testCreateEscrow
[PASS] testValidateWithSignature
[PASS] testReleaseFunds
[PASS] testSignatureReplayProtection
...
Suite result: 53 passed, 0 failed
```

**Voiceover:**
> "Let's run it. Create escrow — buyer locks funds. Validate with signature — the AI validator cryptographically approves the work. Release funds — seller gets paid. And if something goes wrong, deadline-based refunds protect the buyer."

**[Visual: Quick flash of each test passing]"

---

## 🎯 Closing (2:05–2:30)

**[Visual: GitHub repo page + architecture diagram side by side]"

**Voiceover:**
> "AgentEscrow is built for the agentic future — where billions of autonomous transactions need a trust layer. We've got the contracts. We've got the tests. And we've got a clear path to Kite AI integration."

**[Text overlay: "github.com/ProtoJay4789/arc-hackathon"]"

**Voiceover:**
> "Gentech Labs. Building the infrastructure AI agents will actually use."

**[Fade to black. Logo: Gentech Labs]"

---

## 📹 Recording Checklist

- [ ] Record terminal `forge test` run (1080p, dark theme)
- [ ] Record VS Code scroll-through of `AgentEscrow.sol`
- [ ] Record architecture diagram walkthrough
- [ ] Voiceover track (Jordan or Desmond — 2:30 max)
- [ ] Background music (subtle, instrumental)
- [ ] Export to MP4 (1080p, 30fps)
- [ ] Upload to YouTube unlisted OR Loom
- [ ] Add link to submission form

## 🎨 Visual Assets Needed

1. **Opening card** — "AgentEscrow — Trust Layer for the Agentic Economy" + Gentech logo
2. **Problem diagram** — simple 3-node flow with question marks
3. **Architecture diagram** — use `agentescrow-kite-architecture.html`
4. **Terminal recordings** — `forge test`, `forge build`
5. **Code highlights** — key functions in `AgentEscrow.sol`
6. **Closing card** — GitHub link + Gentech Labs branding

## 📎 Tools

- **Screen recording:** OBS (free) or Loom
- **Video editing:** DaVinci Resolve (free) or iMovie
- **Voiceover:** Phone voice memo → Audacity for cleanup
- **Music:** Uppbeat.io (free, no copyright)
