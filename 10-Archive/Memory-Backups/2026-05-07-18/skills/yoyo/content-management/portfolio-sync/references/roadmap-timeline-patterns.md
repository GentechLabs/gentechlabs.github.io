# Roadmap Timeline Patterns

## Vertical Timeline (Current Implementation)

The portfolio uses a vertical timeline for the roadmap section. This replaced the earlier horizontal `.roadmap-step` pattern.

### CSS Pattern (Inline Styles)

```html
<div style="position: relative; padding-left: 40px;">
    <div style="position: absolute; left: 15px; top: 0; bottom: 0; width: 3px; background: #22c55e;"></div>
    
    <div style="margin-bottom: 30px; position: relative;">
        <div style="position: absolute; left: -33px; top: 5px; width: 12px; height: 12px; background: #22c55e; border-radius: 50%;"></div>
        <div style="color: #22c55e; font-weight: bold; font-size: 0.9em; margin-bottom: 5px;">PHASE NAME</div>
        <div style="color: #fbbf24; font-weight: 600;">Project Name</div>
        <div style="color: #60a5fa; font-size: 0.85em;">Date Range</div>
        <div style="color: #9ca3af; font-size: 0.9em; margin-top: 5px;">Description text.</div>
    </div>
</div>
```

### Color Scheme
- Green line + dots: `#22c55e` (primary green)
- Phase names: `#22c55e` (green, bold)
- Project names: `#fbbf24` (orange/amber)
- Dates: `#60a5fa` (light blue)
- Descriptions: `#9ca3af` (grey)

### Key Elements
1. **Container**: `position: relative; padding-left: 40px;`
2. **Vertical line**: Absolute positioned, 3px wide, green
3. **Phase dot**: 12px circle, absolute positioned at `-33px` left
4. **Phase header**: Green, bold, 0.9em font
5. **Project entries**: Stacked vertically within each phase

## Legacy Horizontal Pattern (Deprecated)

The earlier implementation used horizontal `.roadmap-step` classes:

```css
.roadmap {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
}
.roadmap-step {
    background: #0a0a0a;
    border: 2px solid #22c55e;
    color: #22c55e;
    padding: 12px 24px;
    border-radius: 30px;
    font-weight: bold;
}
```

**Status**: Deprecated as of May 6, 2026. The vertical timeline provides better readability for projects with descriptions and dates.

## Roadmap Data Structure

Current roadmap phases and projects (as of May 2026):

### RESEARCH
- **genlayer-recon** (Apr-May 2026): GenLayer SDK deep-dive, Intelligent Contracts prototype, integration pathways for AgentEscrow/Kite.

### PROTOTYPE
- **Job-Applications Agent** (Apr 2026): Task pipeline automation for outreach + tracking.
- **AgentEscrow (v1)** (Apr 2026): Multi-agent escrow contract, Phantom wallet integration.

### DEVELOPMENT
- **Travel-Agent** (May-Jun 2026): Public API aggregation, voice-first interface, Phase 1 foundation.
- **auto-rebalance-gas-abstraction** (May-Jun 2026): Gas optimization engine, scenario-based rebalancing, measurable savings.

### PRODUCTION
- **Hermes-kanban** (Apr 2026-ongoing): Obsidian-Kanban bridge, 8+ sprints shipped, REST API + CLI.
- **AAE Dashboard** (May 2026): Live yield analytics, multi-chain LP tracking, DCA automation.
- **DMobs-Portfolio** (Apr 2026): Social amplification showcase, distribution-ready design.
