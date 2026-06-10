# Travala Travel MCP — Integration Spec

**Source:** https://github.com/travala/travel-mcp
**Date:** June 10, 2026
**Status:** Live on Base, x402 payments enabled

## What Is It

MCP server for hotel search and booking via Travala.com. Enables AI agents to search hotels, compare room packages, and complete bookings — including payment — through natural language.

**Key stats:**
- 2.2M+ hotel properties (Marriott, Hilton, IHG)
- x402 protocol on Base (USDC, ~$0.01 per transaction)
- No API key or signup required for search endpoints
- cbBTC rewards for agents that complete bookings

## MCP Server URL

```
https://travel-mcp.travala.com/mcp
```

## Tools (6 total)

### 1. `travala_search_hotel`
Search hotels by location and dates.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | ✓ | City, region, or hotel name |
| `checkIn` | string | ✓ | YYYY-MM-DD |
| `checkOut` | string | ✓ | YYYY-MM-DD |
| `rooms` | string[] | ✓ | Room occupancy (e.g. `["2"]` = 1 room, 2 adults) |
| `lat`/`lng` | number | — | Coordinates for precise results |
| `minPrice`/`maxPrice` | number | — | Price range per night USD |
| `filters` | string[] | — | `all_inclusive`, `free_breakfast`, `swimming_pool`, `ocean_view` |
| `response_format` | string | — | `markdown` (default) or `json` |

**Returns:** Hotels with name, star rating, price, amenities, `sessionId`.

### 2. `travala_search_package`
Get room types and rate plans for a specific hotel.

| Parameter | Type | Required |
|-----------|------|----------|
| `hotelId` | string | ✓ |
| `sessionId` | string | — |
| `checkIn`/`checkOut` | string | — |
| `rooms` | string[] | — |
| `filters` | string[] | — |
| `response_format` | string | — |

**Returns:** Room types, rate plans, meal inclusions, refund policies, `packageId`.

### 3. `travala_book`
Book a hotel package and initiate x402 payment.

| Parameter | Type | Required |
|-----------|------|----------|
| `packageId` | string | ✓ |
| `sessionId` | string | ✓ |
| `customer.firstName` | string | ✓ |
| `customer.lastName` | string | ✓ |
| `customer.email` | string | ✓ |
| `customer.phone` | string | ✓ |

**Returns:** Booking confirmation + x402 payment instructions.

### 4. `travala_book_status`
Recovery lookup for failed/timed-out bookings.

| `interpretation` | `httpStatus` | Meaning |
|---|---|---|
| `completed` | 200 | Booking succeeded — do NOT retry |
| `in_progress` | 202 | Still settling — wait and poll |
| `not_found` | 404 | Safe to retry |
| `invalid_request` | 400 | Check params/session |
| `server_error` | 5xx | Don't retry — check email |

### 5. `travala_manage_bookings`
Look up existing booking details.

### 6. `travala_cancel_booking`
Cancel an existing booking.

## Agent Registration & Rewards

- Register at [8004scan.io/agents](https://8004scan.io/agents) for ERC-8004 agentId
- Set `rewardWallet` (any EVM address on Base)
- Payout in **cbBTC** after booking completes (post check-in, subject to refund window)
- Without editing these values, bookings go to default agent — you earn nothing

## Payment Flow

1. `travala_book` returns HTTP 402 with x402 payment details
2. Need `@coinbase/payments-mcp` installed alongside for payment completion
3. USDC on Base, gasless, ~$0.01 per transaction
4. Traveler gets final approval on payment

## GenTech Travels Integration Plan

### Layer 1: Travala MCP (data + booking)
- Connect to `https://travel-mcp.travala.com/mcp`
- Use for hotel search, room comparison, booking
- Public endpoints — no API key needed

### Layer 2: x402 Payment Stack
- Use our existing Q402/EIP-7702 for gasless payments
- Or use Coinbase payments MCP for Base-native flow
- USDC settlement on Base

### Layer 3: Privacy Layer (our differentiator)
- Travala = public agent bookings (visible on-chain)
- GenTech Travels = private agent bookings
- Telegram/Discord/X integration for booking flow
- No public wallet address exposed

### Layer 4: Agent Bill Pay
- Subscribe to GenTech Travels → agent can book hotels
- $15/mo Agent Pass includes travel bookings
- Per-booking fee on top (our margin)

### Layer 5: Social Features
- Trip Squad — shared bookings with friends
- "Who's in Bangkok next week?" — agent matches travelers
- Group hotel discounts via aggregated bookings

## Competitive Advantage

| Feature | Travala MCP | GenTech Travels |
|---------|-------------|-----------------|
| Hotel search | ✅ 2.2M+ | ✅ Via Travala MCP |
| x402 payments | ✅ USDC/Base | ✅ Multi-chain |
| Privacy | ❌ Public on-chain | ✅ Private by default |
| Social | ❌ Solo bookings | ✅ Trip Squad |
| Platform | ❌ Claude Desktop only | ✅ Telegram/Discord/X |
| Agent registration | ✅ ERC-8004 | ✅ ERC-8004 + ERC-8183 |
| Rewards | ✅ cbBTC | ✅ cbBTC + GEN token |

## Next Steps

1. Install Travala MCP server
2. Test search flow end-to-end
3. Register agent at 8004scan.io/agents
4. Build privacy wrapper around booking flow
5. Deploy GenTech Travels as Travala MCP + privacy layer
