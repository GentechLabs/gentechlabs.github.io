# Hermes Enhanced Gateway Upgrade

**Status:** Pending
**Priority:** Medium
**Assigned:** Dmob + Labs Team
**Created:** 2026-04-14

## Overview

Upgrade the Hermes gateway from portable mode to the enhanced fork for full session management, skills, memory, and config APIs.

## Current State

- Running `ProtoJay4789/hermes-agent` fork from NousResearch
- Gateway running in **portable mode** — missing APIs:
  - `/api/sessions` (session management)
  - `/api/enhancedChat` (advanced chat features)
  - `/api/skills` (skill management via API)
  - `/api/memory` (memory API)
  - `/api/config` (config API)
- Dashboard shows limited data due to missing enhanced APIs

## What the Enhanced Fork Provides

The enhanced fork (`outsourc-e/hermes-agent` per workspace logs) adds:
- Full session persistence with chat_id tracking per Telegram group
- Enhanced chat completions with streaming
- Skills API (enable/disable, browse, install)
- Memory API (read/write persistent memory)
- Config API (read/write config via dashboard)
- Better session isolation per group/department

## Benefits for Gentech

1. **Departments page** can filter sessions by exact Telegram group/chat_id
2. **Per-group session isolation** — Agency, Strategies, Labs, Entertainment sessions tracked separately
3. **Dashboard config editing** — change settings without SSH
4. **Skills management** via web UI

## Migration Steps

1. Review enhanced fork API compatibility with current setup
2. Test enhanced fork in staging profile
3. Migrate gateway to enhanced fork
4. Update dashboard Departments page to use chat_id filtering
5. Update cron jobs if API endpoints change

## References

- Current fork: `ProtoJay4789/hermes-agent` (baseline v0.9.0)
- Enhanced fork mentioned in workspace logs: `outsourc-e/hermes-agent`
- Dashboard setup: `~/.hermes/hermes-agent/`
- Service: `hermes-dashboard.service` (port 9119)
