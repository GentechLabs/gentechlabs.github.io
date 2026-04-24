# 🔬 R&D Lab — Test, Report, Adjust

**Purpose:** Structured testing cycles for all AAE layers and hackathon submissions.

---

## How It Works

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  BUILD   │ →  │  TEST    │ →  │  REPORT  │ →  │  ADJUST  │
│ (Labs)   │    │ (R&D)    │    │ (R&D)    │    │ (Labs)   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                       ↑                           │
                       └───────────────────────────┘
                            Loop until ship-ready
```

## Folder Structure

```
R&D/
├── README.md              ← You are here
├── Testing-Protocol.md    ← How we test (the playbook)
├── Active/                ← Current test cycles
├── Reports/               ← Completed test reports (dated)
└── Templates/             ← Reusable test templates
```

## Agents & Roles

| Agent | Role in R&D |
|-------|-------------|
| **Dmob** | Execute tests, write test scripts, fix bugs found |
| **YoYo** | Verify research assumptions, validate data accuracy |
| **Desmond** | Test content flows, review copy accuracy |
| **Gentech** | Triage reports, assign fixes, track resolution |

## Current Test Cycles

| Cycle | Layer | Status | Started |
|-------|-------|--------|---------|
| *(none yet)* | | | |

---

*Created: 2026-04-18 — Jordan's directive: "We test, we report, we make adjustments"*