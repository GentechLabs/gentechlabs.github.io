# DataHub Local Instance — Working Config (Aug 3 2026)

**Status: RUNNING ✅** — all services healthy, sample datapack loaded, GraphQL queryable.

## Access
- **Frontend UI:** http://localhost:9002 (user: datahub / pass: datahub)
- **GMS (API):** http://localhost:28080  ← REMAPPED off 8080 (isolated from x402 gateway)
- **Schema registry:** 28081 (remapped; 8081 was taken by hummingbot-broker)

## Port remaps (CRITICAL — do not touch 8080/8081)
- `DATAHUB_MAPPED_GMS_PORT=28080` (8080 is the live x402 gateway)
- `DATAHUB_MAPPED_SCHEMA_REGISTRY_PORT=28081` (8081 was hummingbot-broker)

## How to start (compose, not the CLI which pins stale tags)
```bash
cd /tmp
export DATAHUB_MAPPED_GMS_PORT=28080
export DATAHUB_MAPPED_SCHEMA_REGISTRY_PORT=28081
export DATAHUB_VERSION=v1.5.0.6
export DATAHUB_TOKEN_SERVICE_SIGNING_KEY=gentech-signing-key-2026
export DATAHUB_TOKEN_SERVICE_SALT=gentech-salt-2026
docker compose -f /tmp/dh-compose.yml --profile quickstart -p datahub up -d
```

## Key fixes that got it working (documented for rebuild)
1. **kafka-setup image** doesn't exist at `v1.5.0.6` — pinned to `:head` in compose (line ~190)
2. **schema-registry** couldn't resolve `broker:29092` DNS on first boot — restart after broker healthy
3. **8081 port conflict** (hummingbot-broker) — remapped to 28081
4. **datahub-upgrade failed** with "signingKey must be set" — must set `DATAHUB_TOKEN_SERVICE_SIGNING_KEY` + `DATAHUB_TOKEN_SERVICE_SALT` env vars (correct names, not AUTHENTICATION_TOKEN_...)
5. Order: broker/mysql/zookeeper/elastic/neo4j → schema-registry → kafka-setup → datahub-upgrade (36 steps, SUCCEEDED) → gms → frontend → actions

## Sample data
- `datahub datapack load showcase-ecommerce` — loaded successfully (54 events, 1,049 entities)
- Queryable via GraphQL: search `total: 4` for "order", lineage via `lineage(input:{direction:DOWNSTREAM})`

## GraphQL notes
- Search field is `searchResults` (NOT `results`)
- Lineage field: `dataset(urn:...) { lineage(input: { direction: DOWNSTREAM, start:0, count:N }) { total } }`
- Full schema at http://localhost:28080/api/graphql via introspection

## Next build step (lineage-guard agent)
Agent reads DataHub MCP (or direct GraphQL on 28080) to answer "what breaks if I drop this table?" → blast radius via downstream lineage → write risk report back to graph. Monetize via x402 gateway.
