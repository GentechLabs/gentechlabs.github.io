# Project Architectural Layers

## Layer 9: GenLayer Utility Layer
- **Definition**: Specialized execution environment (GenVM) serving as "Infrastructure."
- **Role**: Acts as the verifier/judge for AI-driven actions.
- **Contrast**: While agents operate as "Users" (calling APIs, moving funds), Layer 9 (GenLayer nodes) decides if those actions were correct.
- **Application (AAE)**:
    - Transition from a "Single Point of Failure" to a "Consensus of Experts."
    - Implemented as a "Council of Bots" architecture where nodes provide consensus on AgentEscrow (AAE) outcomes.
    - Different bots may handle the roles, but they share a unified "Intelligence" budget.
