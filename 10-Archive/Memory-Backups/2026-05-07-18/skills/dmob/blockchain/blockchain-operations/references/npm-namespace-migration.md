# NPM Namespace Migration Pattern

## Context
Protocols frequently migrate from vendor-specific namespaces to foundation-owned namespaces to establish neutrality and community governance.

**Example migration:** `@dexterai/x402` (legacy) → `@x402/*` (current)

## Detection Checklist
- [ ] Search both namespaces on npm: `curl registry.npmjs.org/@dexterai/x402` and `curl registry.npmjs.org/@x402/core`
- [ ] Compare version histories: legacy may have higher versions (3.1.1) while new namespace is at 2.x — this doesn't mean regression; it's a restart with new package IDs
- [ ] Check repository redirect: old GitHub repo may show "We've moved" notice linking to new org (coinbase/x402 → x402-foundation/x402)
- [ ] Look for migration guide in new repo root (MIGRATION.md, UPGRADING.md, or README migration section)

## Breaking Change Signals
- Package ID change alone is breaking (requires `npm install` with new name)
- Major version bump across namespace (1.x → 2.x)
- API surface changes documented in CHANGELOG (look for "BREAKING" or "Migration Guide")
- Old namespace marked deprecated (npm `deprecated` flag set)

## Action Items
1. Update all imports across codebase
2. Update CI/CD (GitHub Actions, Dockerfiles) with new package names
3. Update documentation, blog posts, examples
4. Communicate timeline for legacy namespace EOL

## x402-Specific Notes
- `@dexterai/x402` latest: 3.1.1 (maintained but superseded)
- `@x402/*` unified version: 2.11.0 across all packages (core, evm, svm, stellar, extensions, mcp, express, next, fetch, axios, hono, paywall)
- Migration guide: Not formally published yet; use namespace substitution + API adapter (v2 provides backwards compatibility layer for v1)
