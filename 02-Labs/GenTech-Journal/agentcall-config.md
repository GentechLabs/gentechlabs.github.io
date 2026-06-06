# GenTech Journal — AgentCall Configuration

## AgentCall MCP Setup

**Status:** ✅ MCP server configured in Hermes config.yaml

### Step 1: Get Your API Key

1. Go to https://agentcall.co
2. Sign up for free (no card required)
3. Copy your API key from the dashboard
4. Set it in your environment:

```bash
export AGENTCALL_API_KEY="ac_live_xxxxxxxxxxxxx"
```

### Step 2: Provision a Phone Number

Via MCP (in Hermes):
```
Use the agentcall MCP tools to provision a US local phone number
```

Or via API:
```bash
curl -X POST https://api.agentcall.co/v1/numbers/provision \
  -H "Authorization: Bearer $AGENTCALL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "local", "country": "US"}'
```

### Step 3: Configure Inbound AI Voice

```bash
curl -X POST https://api.agentcall.co/v1/numbers/{numberId}/inbound-config \
  -H "Authorization: Bearer $AGENTCALL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ai",
    "systemPrompt": "You are a journal companion for GenTech. Listen to the user thoughts with empathy. Respond supportively. Help them reflect on their day, their goals, their challenges. After the call, summarize the conversation and save it to the vault. Include mood tags and key themes.",
    "voice": "sage",
    "firstMessage": "Hey there. This is your GenTech journal. How are you doing today? What is on your mind?",
    "language": "auto",
    "maxDurationSecs": 600
  }'
```

### Step 4: Configure Post-Call Webhook

```bash
curl -X POST https://api.agentcall.co/v1/numbers/{numberId}/webhooks \
  -H "Authorization: Bearer $AGENTCALL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": ["call.transcript"],
    "url": "http://YOUR_SERVER:3456/webhook/agentcall",
    "secret": "YOUR_WEBHOOK_SECRET"
  }'
```

### Voice Options

Available voices (pick warm/supportive):
- `sage` — Calm, warm, thoughtful (recommended for journal)
- `shimmer` — Clear, friendly
- `coral` — Warm, approachable
- `ash` — Grounded, steady

### System Prompt (Full)

```
You are a journal companion for GenTech. Listen to the user thoughts with empathy. 
Respond supportively. Help them reflect on their day, their goals, their challenges. 
After the call, summarize the conversation and save it to the vault. 
Include mood tags and key themes.

What you do:
- Listen actively to whatever the caller wants to talk about
- Ask gentle follow-up questions to help them dig deeper
- Reflect back what you hear to validate their experience
- Help them identify patterns, themes, and insights
- End with a brief summary of key points and themes

Instructions:
- Start by greeting them warmly and asking how they are
- Let them lead the conversation — do not push topics
- If they seem stressed, validate that feeling first
- If they seem excited, celebrate with them
- Keep responses concise — this is a phone call, not an essay
- Before the call ends, summarize the key themes and mood

Never:
- Give medical or legal advice
- Dismiss their feelings
- Be preachy or lecture
- Make assumptions about what they mean
- Stay on the line after they say goodbye
```
