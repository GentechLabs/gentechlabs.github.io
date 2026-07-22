# Agent Registration API

ERC-8004 standard agent registration service for the GenTech Labs ecosystem.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/agents/register` | Register new agent |
| GET | `/api/v1/agents/{agent_id}` | Get agent details |
| GET | `/api/v1/agents` | List all agents (filterable) |
| POST | `/api/v1/services/register` | Register service offering |
| GET | `/api/v1/services` | List all services |
| DELETE | `/api/v1/agents/{agent_id}` | Unregister agent |

## Deployment

```bash
bash deploy.sh
```

Server runs on port 8001.

## Usage Example

```bash
# Register an agent
curl -X POST http://localhost:8001/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent",
    "owner_address": "0x...",
    "metadata": {
      "name": "My Agent",
      "description": "Description here",
      "category": "category",
      "capabilities": ["capability1", "capability2"]
    },
    "signature": "0x..."
  }'

# List agents
curl http://localhost:8001/api/v1/agents
```

## Status

✅ Deployed and verified (PID: 2394217)