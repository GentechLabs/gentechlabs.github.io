# 🗺️ GenTech Agency: Multi-Agent Brain Map

**Version:** 1.0 (Post-Gemma 4 Migration)
**Goal:** Maximize department-specific performance by matching model characteristics to agent roles.

---

## 🧠 The Model Distribution

| Agent | Department | Role | Recommended "Brain" | Core Strength |
| :--- | :--- | :--- | :--- | :--- |
| **Gentech** | **HQ** | Dispatch & Synthesis | **Claude 3.5 / Llama 405B** | High-level logic, orchestration, "God View" |
| **DMOB** | **Labs** | Code & Audit | **DeepSeek-Coder / Codestral** | Formal verification, Solidity precision, debugging |
| **YoYo** | **Strategies** | Research & Moats | **Llama 70B+ / Mistral Large** | Deep knowledge, academic synthesis, nuance |
| **Desmond**| **Entertainment**| Content & Brand | **Gemma 4 (31B)** | Speed, articulation, narrative flow, tool-use |

---

## 🔄 Interaction Flow

**1. Input:** Jordan sends a voice/text command to **HQ**.
**2. Dispatch:** **Gentech** (High-Intelligence Brain) analyzes the request $\rightarrow$ routes to specific department.
**3. Execution:** 
   - If Code $\rightarrow$ **DMOB** (Code Brain) builds $\rightarrow$ pushes to GitHub.
   - If Research $\rightarrow$ **YoYo** (Deep Brain) analyzes $\rightarrow$ pushes to Vault.
   - If Content $\rightarrow$ **Desmond** (Articulate Brain) packages $\rightarrow$ pushes to Socials.
**4. Consolidation:** Agents discuss in **Mess Hall** $\rightarrow$ **Gentech** synthesizes a single update for Jordan.

---

## 🛠️ Implementation Note
- **Gemma 4 as the Base:** We can keep Gemma 4 as the "fallback" for all agents to ensure basic tool-use and vault sync stay consistent.
- **Specialization as Overlays:** We use specialized models for the *core reasoning* of each department.

#brainmap #org-chart #multi-agent #ollama #cloud-models