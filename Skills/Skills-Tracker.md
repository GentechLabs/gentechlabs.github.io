# Skills Tracker — Gentech Agent Stack

Last updated: 2026-05-07

Master list of all skills installed across the Gentech agent ecosystem. Review pending installs here, suggest removals, track what's active.

---

## 🔐 Blockchain · Web3 · Smart Contract Security

### ✅ Installed
| Skill | Agent | Notes |
|-------|-------|-------|
| solidity-auditor (pashov) | Dmob | Fast Solidity security review, <5 min |
| x-ray (pashov) | Dmob | Pre-audit scan: threat model, invariants, git analysis |
| foundry-solidity-dev | Dmob | Foundry quick reference |
| requesting-code-review | Dmob | Pre-commit security scan pipeline |
| test-driven-development | Dmob | TDD workflow |
| systematic-debugging | Dmob | Bug diagnosis |
| huggingface-hub | Dmob | Model download/upload via hf CLI |

### 🔲 Pending Review
| Skill | Why | Priority |
|-------|-----|----------|
| ~~ZealynxSecurity/krait~~ | 90% precision on 40 Code4rena blind contests | APPROVED |
| ~~trailofbits/skills~~ | Top-tier security firm — vulnerability detection | APPROVED |
| CDSecurity/cdsecurity-skills | Smart contract security skills | MEDIUM |
| quillai-network/quillshield_skills | Invariant detection, flash loan + oracle attack chains | MEDIUM |
| PlamenTSV/plamen | Autonomous Web3 security audit agent | MEDIUM |
| SunWeb3Sec/DeFiHackLabs | Reproduce DeFi hacks in Foundry (learning) | MEDIUM |
| SunWeb3Sec/DeFiVulnLabs | Common smart contract vulnerabilities (learning) | MEDIUM |
| rosarioborgesi/ethernaut-challenges | Ethernaut challenges (learning) | MEDIUM |
| Frankcastleauditor/Solana-Audit-Arena | Weekly Solana security competition | LOW |
| ~~immunefi-team/Web3-Security-Library~~ | 13+ months stale, removed per audit | DROPPED |

---

## 💰 DeFi · Investments · Trading

### ✅ Installed
| Skill | Agent | Notes |
|-------|-------|-------|
| (none yet) | — | — |

### 🔲 Pending Review
| Skill | Why | Priority |
|-------|-----|----------|
| ~~NethermindEth/defi-skills~~ | Natural language → unsigned DeFi transactions | APPROVED |
| HKUDS/AI-Trader | 100% automated agent-native trading | MEDIUM |
| almanak-co/sdk | Production DeFi strategy framework for quants | MEDIUM |
| TauricResearch/TradingAgents | Multi-agent LLM financial trading | MEDIUM |
| krakenfx/kraken-cli | AI-native CLI for crypto/stocks/forex trading | MEDIUM |
| openCMC/skills-for-ai-agents-by-CoinMarketCap | CoinMarketCap data skills for agents | LOW |
| moonpay/skills | On-ramps, swaps, wallets via MoonPay CLI | LOW |
| circlefin/skills | Circle (USDC) development skills | LOW |
| Minara-AI/skills | AI CFO skills | LOW |

---

## 🎬 Entertainment · Content · Podcasting

### ✅ Installed
| Skill | Agent | Notes |
|-------|-------|-------|
| Agent-Reach | All | Web browsing, YouTube, video, social platforms |

### 🔲 Pending Review
| Skill | Why | Priority |
|-------|-----|----------|
| ~~calesthio/OpenMontage~~ | 12 pipelines, 52 tools, 500+ video production skills | APPROVED |
| zhouxiaoka/autoclip | AI video clipping + highlight generation | MEDIUM |
| gitroomhq/postiz-agent | Social media scheduling via agent | MEDIUM |
| siddharthvaddem/openscreen | Open-source screen recording/demos | LOW |
| ~~OpenBMB/VoxCPM~~ | VoxCPM2 TTS — voice design + cloning (ElevenLabs replacement) | APPROVED |
| microsoft/VibeVoice | Voice AI reference | LOW |

---

## 🧠 Agent Infrastructure · Meta

### ✅ Installed
| Skill | Agent | Notes |
|-------|-------|-------|
| hermes-council | All | 5-persona adversarial deliberation MCP |
| hermes-agent-self-evolution | All | DSPy + GEPA skill optimizer |
| plan / writing-plans | All | Task planning and execution |
| message-queue-digest | All | Recovery workflow — scan message backlog on restart, triage by urgency, auto-send summary. Created 2026-04-17 |
| agent-catchup-digest | All | "While You Were Away" digest with PRIORITY/CONTEXT/FYI classification, timestamps. Includes watchdog script for Termux failover. See `/opt/hermes-agents/desmond/skills/agent-catchup-digest/` |

### 🔲 Pending Review
| Skill | Why | Priority |
|-------|-----|----------|
| googleworkspace/cli | Drive, Gmail, Calendar, Sheets CLI | MEDIUM |
| addyosmani/agent-skills | Production engineering skills | MEDIUM |
| hristo2612/jinn | Lightweight AI gateway daemon | LOW |
| usestrix/strix | AI hackers for vulnerability finding | LOW |
| vxcontrol/pentagi | Autonomous penetration testing | LOW |
| zubair-trabzada/geo-seo-claude | AI search optimization / SEO | LOW |
| paperclipai/paperclip | Zero-human company orchestration | FUTURE |

---

## ❌ Dropped

| Skill | Reason | Date |
|-------|--------|------|
| hermes-workspace (3rd party) | Backend connection issues, native GMC works better | 2026-04-16 |
| immunefi-team/Web3-Security-Library | 13+ months stale, removed per consolidation audit | 2026-05-07 |

---

## Rules
- Any agent can suggest additions via HQ chat
- Jordan approves all installs
- Review pending list periodically
- When dropping: move to ❌ with reason and date
- **AUTO-TRACK:** Any time a GitHub link is shared AND a skill is installed from it, add it to the ✅ Installed section IMMEDIATELY. No exceptions. Don't wait for Jordan to ask.
