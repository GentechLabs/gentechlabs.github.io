/**
 * x402Client — dependency-free x402 (pay-per-call) client core.
 *
 * Pure Node.js (>=18, global fetch). Zero npm runtime deps (keccak256 is a
 * tiny self-contained pure-JS implementation; pass your own via setKeccak for
 * parity with your signing lib). Works against any x402 resource — our GenTech
 * gateway, CDP Bazaar, Meridian, PayAI, etc.
 *
 * x402 flow:
 *   1. GET the resource -> 402 Payment Required + `payment-required` header
 *   2. Parse the challenge (resource, accepts[], extensions)
 *   3. Pick a payment rail (network + asset) the wallet can fund
 *   4. Build a settlement envelope for that rail (EVM exact-amount here)
 *   5. POST the payment-required JSON + `x-402-token` header -> 200
 *
 * @module gentech-x402
 */

import { keccak256 as _keccak256, setKeccak as _setKeccak } from './keccak.js'

export const keccak256 = _keccak256
export const setKeccak = _setKeccak

/* ------------------------------------------------------------------ */

/** Minimal JSON-schema-ish validator for the challenge header. */
export function parsePaymentRequired(raw) {
  if (typeof raw !== 'string' || raw.length === 0) {
    throw new Error('x402: missing payment-required header')
  }
  let json
  try {
    // The header value is base64url JSON (may also be served raw).
    json = JSON.parse(
      raw.startsWith('{') ? raw : Buffer.from(raw, 'base64url').toString('utf8'),
    )
  } catch (err) {
    throw new Error(`x402: unparseable payment-required header: ${err.message}`)
  }
  const { resource, accepts, extensions } = json
  if (!resource || typeof resource.url !== 'string') {
    throw new Error('x402: challenge missing resource.url')
  }
  if (!Array.isArray(accepts) || accepts.length === 0) {
    throw new Error('x402: challenge missing accepts[]')
  }
  return { resource, accepts, extensions: extensions ?? {} }
}

/** Choose an acceptance entry for the given network (default: first). */
export function pickAcceptance(challenge, { network } = {}) {
  const list = challenge.accepts
  if (network) {
    const match = list.find((a) => a.network === network)
    if (match) return match
  }
  return list[0]
}

/**
 * EVM exact-amount settlement. Produces the signed envelope the caller POSTs
 * as the `x-402-token`. `sign` must be `async (digestHex) => {r,s,v}` over the
 * payment-intent digest (hex).
 */
export async function buildEvmSettlement(acceptance, { nonce, payer, sign }) {
  if (acceptance.scheme !== 'exact') {
    throw new Error(`x402: unsupported scheme '${acceptance.scheme}' (only 'exact' EVM)`)
  }
  const digest = keccak256(
    JSON.stringify({
      type: 'exact',
      network: acceptance.network,
      asset: acceptance.asset,
      amount: acceptance.amount,
      payTo: acceptance.payTo,
      nonce,
    }),
  )
  const sig = await sign(digest)
  return {
    type: 'evm',
    scheme: 'exact',
    network: acceptance.network,
    asset: acceptance.asset,
    amount: acceptance.amount,
    payer,
    recipient: acceptance.payTo,
    nonce,
    digest,
    signature: { r: sig.r, s: sig.s, v: sig.v },
  }
}

/**
 * Discover the x402 challenge for a resource URL. Returns
 * `{ status, challenge, body }` where `challenge` is the parsed
 * payment-required object (null when the endpoint answered without one).
 */
export async function discover(url, { fetchImpl = fetch, timeoutMs = 15_000 } = {}) {
  const ctl = AbortSignal.timeout(timeoutMs)
  const res = await fetchImpl(url, {
    method: 'GET',
    headers: { accept: 'application/json' },
    signal: ctl,
  })
  const raw = res.headers.get('payment-required')
  if (res.status === 402 && raw) {
    return { status: res.status, challenge: parsePaymentRequired(raw) }
  }
  let body = null
  try {
    body = await res.json()
  } catch {
    /* ignore */
  }
  return { status: res.status, challenge: null, body }
}

/**
 * Call the protected endpoint with an `x-402-token` settlement header.
 */
export async function call(
  url,
  { settlement, fetchImpl = fetch, timeoutMs = 30_000, method = 'POST', headers = {}, body } = {},
) {
  const ctl = AbortSignal.timeout(timeoutMs)
  const res = await fetchImpl(url, {
    method,
    headers: {
      accept: 'application/json',
      'content-type': 'application/json',
      'x-402-token': settlement,
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: ctl,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`x402: ${res.status} ${res.statusText} ${text.slice(0, 300)}`)
  }
  return res.json()
}

/** Convenience: full discover -> accept -> settle -> call pipeline. */
export async function payAndCall(url, { network, settle, ...rest }) {
  const { challenge } = await discover(url)
  if (!challenge) {
    throw new Error(`x402: no payment challenge at ${url}`)
  }
  const acceptance = pickAcceptance(challenge, { network })
  const token = await settle(challenge, acceptance)
  return call(url, { settlement: token, ...rest })
}

export const version = '1.0.0'
