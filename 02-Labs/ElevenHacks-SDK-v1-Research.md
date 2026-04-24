# ElevenAgents React SDK v1.0 — Research Note
**Source:** @ElevenLabsDevs tweet (Apr 23, 2026)
**Relevance:** ElevenHacks #6 submission

## Key Changes in v1.0

### 1. Unified API (Web + React Native)
- `@elevenlabs/react-native` now re-exports `@elevenlabs/react` with thin platform strategy layer (~40 lines, down from 1000+)
- Same `ConversationProvider`, same hooks, same methods
- Change import path only: `@elevenlabs/react` → `@elevenlabs/react-native`

### 2. Granular Hooks (Performance)
- 6 new hooks subscribe to individual slices of conversation state
- Components only re-render when their specific data changes
- `useConversationStatus` — connection status only
- `useConversationControls` — start/end session
- No more full re-renders on every state change

### 3. useConversation still works (backwards compat)
- Convenient wrapper over granular hooks
- Returns same shape: status, mode, mute, isSpeaking, controls
- Migrate to `ConversationProvider` + `useConversation` first, then optimize incrementally

### 4. useConversationClientTool 🔥 NEW
- React components register tools the agent can invoke
- Tools tied to **component lifecycle** — register on mount, unregister on unmount
- Always uses latest closure values (state, props)
- **This is the big one for hackathons** — dynamic tool registration from the UI layer

```tsx
useConversationClientTool('getLocation', () => {
  return `${location.lat},${location.lng}`;
});
```

### 5. Private Internal Classes
- `Input`, `Output`, `wake lock` no longer public
- Replaced by documented methods:
  - `setVolume({ volume })` instead of `conversation.output.gain.gain.value`
  - `getInputByteFrequencyData()` instead of `conversation.input.analyser.getByteFrequencyData()`
  - `setMicMuted(true)` instead of `conversation.input.setMuted(true)`

### 6. External Mute State Management
- `ConversationProvider` accepts `isMuted` and `onMutedChange` props
- Persist mute state across sessions or sync with app-level state

## Hackathon Implications
- **useConversationClientTool** is the killer feature — build agent-driven UIs where the agent can call tools defined in React components
- SDK v1.0 = clean, documented API = faster dev cycle
- Breaking change means most existing tutorials/outdated code will fail — being on v1.0 day-one is an advantage
- Game + agent interaction = the agent can call client-side tools to affect game state