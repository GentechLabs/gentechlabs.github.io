# x402 Bazaar Indexing — Bug Fix + Contribution (Aug 15)

## What happened
Jordan flagged the GitHub inbox notification on **x402-foundation/x402 issue #3045** (CDP Bazaar Indexing Failure). We posted our own data point Aug 11. New activity Aug 15 sharpened the open question (registration-write admission path). Jordan: "let's put this bug to rest."

## Root cause found — TWO real bugs in OUR gateway
1. **Discovery schema wrong for GET resource** — `info.input` declared `method: GET` + `bodyType: json` + `body`. CDP's `QueryDiscoveryInfo` schema for GET/HEAD/DELETE has NO `body` field (uses `queryParams`/`pathParams`). Validator rejected: `(root).input.body: Invalid type. Expected: object, given: null`. Fixed: GET → `pathParams`, removed `bodyType`/`body`.
2. **nginx dropped the 402 challenge** — default 4k `proxy_buffer_size` too small for our 402 `WWW-Authenticate` header ("upstream sent too big header"). Fixed: `proxy_buffer_size 16k; proxy_buffers 4 16k;` on api.gentechlabs.net server blocks.

## Fixes deployed live
- `10-Labs/x402-gateway/server.py` — discovery schema corrected
- `x402-api.service` restarted (safe-restart procedure, endpoint verified up)
- `/etc/nginx/sites-enabled/gentech` — proxy buffer raised, reloaded
- **CDP validator now: `valid: true`, `simulation: accepted`** (was `rejected`)

## Remaining crux (the actual #3045 bug)
Even fully valid, `index: null` — resource still not catalogued. Supports the thread's converging hypothesis: a **registration-write admission path** (not settlement, not crawl) gates catalog entry. We're now the cleanest v2 control case.

## Contribution posted
- Comment: https://github.com/x402-foundation/x402/issues/3045#issuecomment-5304000669
- By: ProtoJay4789, Aug 15 20:04 UTC
- Positions GenTech as a helpful contributor who fixed their own stack + isolated the remaining blocker.

## Files
- `10-Labs/x402-gateway/server.py` (schema fix)
- `/etc/nginx/sites-enabled/gentech` (proxy buffer fix, backup at /tmp/gentech.bak)
- `/tmp/x402-comment.md` (comment draft)
