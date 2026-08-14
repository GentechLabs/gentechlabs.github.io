/**
 * dsh-plugin-gentech-x402 — GenTech x402 payment plugin for DeepSeek Harness.
 *
 * Registers a `gentech` tool namespace on `ctx.tools` so a dsh agent can
 * discover and pay-per-call the GenTech x402 gateway (or any x402 resource)
 * without holding API keys. Zero npm deps beyond the dsh-tools contract.
 *
 * Tools registered (all under the `gentech_` prefix):
 *   - gentech_services          — list the gateway's paid services (free)
 *   - gentech_token_security    — score a token (mint/address)  ~$0.01/call
 *   - gentech_wallet_analysis   — analyze a wallet              ~$0.01/call
 *   - gentech_market_intel      — market intelligence for a symbol ~$0.01/call
 *   - gentech_discover          — generic: probe ANY x402 URL, return challenge
 *
 * Settlement: the plugin calls `ctx.gentechSettle(challenge, acceptance)` if a
 * settlement service is mounted; otherwise it returns the 402 challenge so the
 * agent can surface it to the user for funding. Mount a wallet plugin to close
 * the loop.
 *
 * @module dsh-plugin-gentech-x402
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import {
  discover,
  pickAcceptance,
  version as clientVersion,
} from './x402-client.js'

export const name = 'gentech-x402'
export const inject = ['tools']

/** Runtime configuration for the gentech x402 plugin. */
export const Config = undefined // plain fields, no schema coercion

/** Service catalog the gateway advertises (bazaar manifest v9.1.0). */
const SERVICE_ENDPOINTS = {
  'token_security': '/v1/token-security/score/{mint}',
  'wallet_analysis': '/v1/wallet-analysis/{address}',
  'market_intelligence': '/v1/market-intel/{symbol}',
  'agent_discovery': '/v1/agent-discovery',
  'defi_lp_analytics': '/v1/defi-lp-analytics',
  'nft_search': '/v1/nft-search',
  'treasury_defender': '/v1/treasury-defense',
  'lineage_guard': '/v1/lineage-guard',
  'sie_inference': '/v1/sie/inference',
}

export function apply(ctx, config = {}) {
  const baseUrl = config.baseUrl ?? 'https://api.gentechlabs.net'
  const network = config.network ?? 'eip155:8453'

  /** Perform the x402 round-trip for a gateway service URL. */
  async function x402RoundTrip(path, settle) {
    const url = `${baseUrl}${path}`
    const { challenge } = await discover(url)
    if (!challenge) {
      return { ok: false, error: `no x402 challenge at ${url} (not a paid resource?)` }
    }
    const acceptance = pickAcceptance(challenge, { network })
    const token = await settle(challenge, acceptance)
    const res = await fetch(url, {
      method: 'GET',
      headers: { accept: 'application/json', 'x-402-token': token },
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      return { ok: false, error: `gateway ${res.status}: ${text.slice(0, 200)}` }
    }
    const data = await res.json()
    const assetName = acceptance.extra?.name ?? 'USDC'
    const cost = `${Number(acceptance.amount) / 1e6} ${assetName}`
    return {
      ok: true,
      service: challenge.resource.description,
      cost,
      network: acceptance.network,
      data,
    }
  }

  // --- Free tool: list services --------------------------------------
  ctx.tools.register(defineTool({
    name: 'gentech_services',
    description:
      'List the GenTech x402 gateway paid services (token security, wallet analysis, market intel, etc.) and their endpoint shapes. Free — no payment required to list.',
    parameters: {},
    output: {
      schema: { type: 'object' },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value, null, 2) }],
    },
    async execute() {
      return { baseUrl, services: SERVICE_ENDPOINTS }
    },
  }))

  // --- Free tool: generic x402 probe ---------------------------------
  ctx.tools.register(defineTool({
    name: 'gentech_discover',
    description:
      'Probe any x402-protected URL and return its parsed payment-required challenge (resource, accepted payment rails, amount). Use this to inspect what a paid API costs before calling it.',
    parameters: {
      url: { type: 'string', required: true, description: 'The x402 resource URL to probe.' },
    },
    output: {
      schema: { type: 'object' },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value, null, 2) }],
    },
    async execute(args) {
      const { status, challenge, body } = await discover(args.url)
      return { status, url: args.url, challenge, body }
    },
  }))

  // --- Convenience paid tools ----------------------------------------
  const serviceTools = [
    {
      name: 'gentech_token_security',
      desc: 'Score a token or contract address for risk (0-100) via the GenTech x402 gateway. Paid ~$0.01/call.',
      path: '/v1/token-security/score/',
      paramName: 'mint',
    },
    {
      name: 'gentech_wallet_analysis',
      desc: 'Analyze a wallet address (holdings, risk, activity) via the GenTech x402 gateway. Paid ~$0.01/call.',
      path: '/v1/wallet-analysis/',
      paramName: 'address',
    },
    {
      name: 'gentech_market_intel',
      desc: 'Get market intelligence for a crypto symbol/asset via the GenTech x402 gateway. Paid ~$0.01/call.',
      path: '/v1/market-intel/',
      paramName: 'symbol',
    },
  ]

  for (const t of serviceTools) {
    ctx.tools.register(defineTool({
      name: t.name,
      description: t.desc,
      parameters: {
        [t.paramName]: {
          type: 'string',
          required: true,
          description: `The ${t.paramName} to query.`,
        },
      },
      output: {
        schema: { type: 'object' },
        render: (_args, value) => [{ type: 'text', text: JSON.stringify(value, null, 2) }],
      },
      async execute(args) {
        const settle = ctx.gentechSettle
        const path = `${t.path}${encodeURIComponent(args[t.paramName])}`
        if (typeof settle !== 'function') {
          // No settlement service mounted — surface the 402 challenge.
          const { challenge } = await discover(`${baseUrl}${path}`)
          return {
            ok: false,
            needsWallet: true,
            message: 'This call is pay-per-use via x402. No settlement service is mounted. Surface this 402 challenge to the user to fund:',
            challenge,
          }
        }
        return x402RoundTrip(path, settle)
      },
    }))
  }

  // Settlement capability seam — a wallet plugin can assign ctx.gentechSettle.
  ctx.gentechSettle ??= undefined

  return { clientVersion, baseUrl, network }
}
