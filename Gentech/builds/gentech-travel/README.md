# Gentech Travel Agent — MCP Integration Research

## Travala Travel MCP
| Detail | Value |
|--------|-------|
| **MCP URL** | `https://travel-mcp.travala.com/mcp` |
| **Hotels** | 2.2M+ |
| **Tools** | search_hotel, search_package, book, cancel_booking, manage_booking |
| **Rewards** | 10% cbBTC rebate on every booking |
| **Payments** | USDC on Base via x402 |
| **Identity** | ERC-8004 agent reputation tracking |
| **Setup** | Claude Desktop → Connect Travala MCP → Install Coinbase Agentic Wallet MCP |

## Coinbase Payments MCP (@coinbase/payments-mcp)
| Detail | Value |
|--------|-------|
| **Install** | `npx @coinbase/payments-mcp@latest` |
| **Stack** | Wallets + onramps + payments via x402 |
| **Lang** | TypeScript |
| **GitHub** | https://github.com/coinbase/payments-mcp |

## Integration Plan
1. Scaffold GitHub repo: `gentech-travel/`
2. Connect to Travala MCP (5 hotel tools)
3. Connect Coinbase Payments MCP (x402 payments)
4. Build freemium tier (10 searches/mo free → $15/mo premium)
5. Add LetsFG for flights, Organic Maps for navigation
6. Deploy + list on Atelier
