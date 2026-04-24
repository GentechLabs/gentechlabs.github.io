---
title: ElevenLabs React SDK v1.0
date: 2026-04-23
source: https://x.com/ElevenLabsDevs/status/2047385937752043684
tags: [elevenlabs, hackathon, sdk, react, elevenhacks]
status: active
---

# ElevenAgents React SDK v1.0

## Key Release Details
- **Date**: April 2026
- **Author**: ElevenLabs Developers (@ElevenLabsDevs)
- **Packages**: `@elevenlabs/client`, `@elevenlabs/react`, `@elevenlabs/react-native`

## Why v1.0 (Breaking Change)
Three problems drove this release:
1. **Different APIs on web & React Native** — RN lacked WebSocket mode, features shipped twice
2. **Poor render performance** — single context provider caused re-renders on any state change
3. **Fragile upgrades** — internal classes (Input, Output, Connection) exposed in public API

## What's New
### Unified API
- `@elevenlabs/react-native` now re-exports `@elevenlabs/react` with ~40 lines of platform code (down from 1000+)
- Same ConversationProvider, hooks, and methods across web & RN
- Just change import path for RN

### 6 Granular Hooks
- `useConversationStatus` — connection status only
- `useConversationControls` — startSession, endSession
- `useConversationAgent` — agent info
- `useConversationVolume` — volume state
- `useConversationMuted` — mute state
- `useConversationSpeaker` — speaker state
- Components re-render only when their slice changes

### Dynamic Client Tools
- `useConversationClientTool` — React components register tools the agent can invoke
- Tied to component lifecycle (register on mount, unregister on unmount)
- Uses latest closure values

### Stable API Surface
- `setVolume({ volume })` replaces `conversation.output.gain.gain.value = v`
- `getInputByteFrequencyData()` replaces `conversation.input.analyser.getByteFrequencyData()`
- `setMicMuted(true)` replaces `conversation.input.setMuted(true)`
- Transport layers can be swapped without breaking user code

### Controlled State
- `ConversationProvider` accepts `isMuted` and `onMutedChange` props
- External state management support

## Strategic Implications for GenTech
### ElevenHacks #6 Submission
- **`useConversationClientTool`** is the killer feature — lets us build a game where the AI agent triggers in-game actions via voice
- Our "REP Grind" concept can use dynamic client tools for:
  - Voice-triggered skill assessments
  - Real-time RP scoring during conversation
  - Agent-driven challenges that respond to player speech patterns
- Building on the full conversation SDK (not just TTS) differentiates us from basic hackathon entries

### Code References
```typescript
// Basic agent connection
import { ConversationProvider, useConversationControls, useConversationStatus } from '@elevenlabs/react';

function Agent() {
  const { startSession, endSession } = useConversationControls();
  const { status } = useConversationStatus();
  
  return (
    <button onClick={() => startSession({ agentId: 'agent_...' })}>
      Start
    </button>
  );
}

// Dynamic client tool
const { registerTool } = useConversationClientTool();
// Register tools tied to component lifecycle
```