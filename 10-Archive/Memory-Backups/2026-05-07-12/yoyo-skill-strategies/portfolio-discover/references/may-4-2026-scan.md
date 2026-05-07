# Portfolio Discovery — Session Reference (May 4, 2026)

## Source vault scan: 03-Projects/ subdirectories

| Project | Key files | Git activity | Status signal | Proposed label |
|---------|-----------|--------------|---------------|----------------|
| AAE/ | agent-escrow-architecture.md, kite-passport-technical-deep-dive.md, implementation plan files | Recent commits (style update May 4) | Hackathon deadline: May 11 (Solana Frontier) from architecture doc line 3 | `Building — Solana, Anchor, Rust — Hackathon: May 11` |
| Travel-Agent/ | Implementation-Plan.md (Phase 1 — Week of May 4, 2026), API-Adapters/, Scripts/, Docs/ | Recent commits | "Phase 1 — Foundation", "Ready to start", owner YoYo, live demo goal | `Live — Public APIs, Maps — WIP` |
| BirdeyeBIP/ | README.md (Birdeye BIP Competition — Sprint 1), oracle.py, foundry.toml | Active (feat: BirdeyeAdapter April 21) | Sprint 1 submission, no public deadline listed | `Building — Solana, x402 — TBA` |
| MultiAgentVoice/ | Integration-Plan.md (May 3, 2026), ElevenLabs SDK 1.59.0 noted | No commits (planning only) | Planning phase, integration exploration | `Planning — Voice, ElevenLabs — TBA` |
| LFJ-Experiments/ | 2026-04-28-time-based-strategy-test.md | Git log shows activity | "Date Started: April 28, 2026" — experimental trading strategy | `Building — DeFi, Trading — WIP` |
| genlayer-recon/ | index.md, sdk-comparison/, dmob-brief.md | No commits | Research into GenLayer SDK, Intelligent Contracts | `Research — GenLayer — TBA` |

**Excluded/meta folders:** hermes-kanban (tooling), DeFi/ (milestone tracker only), Job-Applications/, tech-burn-test/ (burn test contract), From-Entertainment/, Hackathons/ (reference docs), DMobs-Portfolio/ (old portfolio site), MultiAgentVoice/ listed above.

## Label mapping rationale

- **Hackathon deadline priority:** If a project file explicitly states a hackathon deadline (AAE → May 11), use it prominently in status.
- **WIP <> TBA:** Use `WIP` when there's active development and a near-term goal (travel-demo, strategy test). Use `TBA` when timeline unknown or research phase.
- **Tech stack:** Extract from tech keywords in README/architecture (Solana, Anchor, Rust, Python, x402, Public APIs, Maps, ElevenLabs, DeFi, Trading, GenLayer).
- **Ordering in output:** Deadline ascending first (May 11 project first), then WIP projects, then Research/Planning.

## projects.json schema example

```json
[
  {
    "name": "AgentEscrow",
    "status": "Building — Solana, Anchor, Rust — Hackathon: May 11",
    "desc": "Trustless AI agent marketplace on Solana for Solana Frontier Hackathon",
    "tech": ["Solana", "Anchor", "Rust"],
    "deadline": "2026-05-11"
  },
  {
    "name": "Travel-Agent",
    "status": "Live — Public APIs, Maps — WIP",
    "desc": "Travel intelligence agent with free public APIs (Phase 1: May 4–10)",
    "tech": ["Pipecat", "Maps API", "Geocoding"],
    "deadline": null
  }
]
```

## Notes for generator script

- **Path resolution:** User home may be `/root` or other; use `os.path.expanduser('~/portfolio/data/projects.json')` for write target.
- **Vault root:** `/root/vaults/gentech/` (Obsidian sync location: `cd /root/vaults/gentech && ob sync`)
- **HACKATHON-ROSTER-2026.md:** Located at `03-Projects/HACKATHON-ROSTER-2026.md` — cross-reference deadlines row 1 (Solana Frontier: May 11) and row 2 (Kite AI: May 17).
- **Kite AI Strategy Engine** not yet in vault as separate folder (currently under AAE/ or separate docs). May need to be added post-May 4.