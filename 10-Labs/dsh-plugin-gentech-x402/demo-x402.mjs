#!/usr/bin/env node
/**
 * demo-x402.mjs — exercise the dependency-free x402 client against the live
 * GenTech gateway (discovery only; no payment is made).
 *
 * Usage:
 *   node demo-x402.mjs discover <url>
 *   node demo-x402.mjs services
 */
import { discover, pickAcceptance, version } from './src/x402-client.js'

const BASE = 'https://api.gentechlabs.net'

async function main() {
  const [cmd, arg] = process.argv.slice(2)

  if (cmd === 'services') {
    const res = await fetch(`${BASE}/.well-known/x402-bazaar`)
    const manifest = await res.json()
    const serviceNames = Array.isArray(manifest?.services)
      ? manifest.services.map((s) => (typeof s === 'string' ? s : s?.name ?? s?.path)).filter(Boolean)
      : Object.keys(manifest?.services ?? {})
    console.log(JSON.stringify({
      seller: manifest?.name,
      description: manifest?.description,
      version: manifest?.version,
      x402Version: manifest?.x402_version,
      endpointCount: Array.isArray(manifest?.endpoints) ? manifest.endpoints.length : undefined,
      services: serviceNames,
    }, null, 2))
    return
  }

  const url = arg ?? `${BASE}/v1/token-security/score/So11111111111111111111111111111111111111112`
  const { status, challenge } = await discover(url)
  console.log(JSON.stringify({
    x402ClientVersion: version,
    url,
    status,
    resource: challenge?.resource?.url,
    baseRail: challenge?.accepts?.[0] && pickAcceptance(challenge, { network: 'eip155:8453' }).network,
    cost: challenge?.accepts?.[0] ? `${Number(challenge.accepts[0].amount) / 1e6} USDC` : null,
  }, null, 2))
}

main().catch((err) => {
  console.error(err.message)
  process.exit(1)
})
