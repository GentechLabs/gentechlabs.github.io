import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  keccak256,
  parsePaymentRequired,
  pickAcceptance,
  discover,
  version,
} from '../src/x402-client.js'

test('keccak256 matches known vector (empty string)', () => {
  // keccak-256("") = c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
  assert.equal(
    keccak256(''),
    '0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470',
  )
})

test('keccak256 matches known vector ("abc")', () => {
  // keccak-256("abc") = 4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45
  assert.equal(
    keccak256('abc'),
    '0x4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45',
  )
})

test('keccak256 handles hex input via fromHex path (empty byte array)', () => {
  const empty = new Uint8Array(0)
  assert.equal(
    keccak256(empty),
    '0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470',
  )
})

test('parsePaymentRequired parses base64url header', () => {
  const challenge = {
    resource: { url: 'https://api.gentechlabs.net/v1/token-security' },
    accepts: [{ scheme: 'exact', network: 'eip155:8453', asset: '0xabc', amount: '10000', payTo: '0xdef' }],
    extensions: { bazaar: {} },
  }
  const raw = Buffer.from(JSON.stringify(challenge)).toString('base64url')
  const parsed = parsePaymentRequired(raw)
  assert.equal(parsed.resource.url, challenge.resource.url)
  assert.equal(parsed.accepts.length, 1)
  assert.equal(parsed.accepts[0].amount, '10000')
})

test('parsePaymentRequired accepts raw JSON too', () => {
  const raw = JSON.stringify({ resource: { url: 'x' }, accepts: [{ scheme: 'exact' }] })
  const parsed = parsePaymentRequired(raw)
  assert.equal(parsed.resource.url, 'x')
})

test('pickAcceptance filters by network and defaults to first', () => {
  const ch = {
    accepts: [
      { scheme: 'exact', network: 'algorand:wGHE2' },
      { scheme: 'exact', network: 'eip155:8453' },
    ],
  }
  assert.equal(pickAcceptance(ch, { network: 'eip155:8453' }).network, 'eip155:8453')
  assert.equal(pickAcceptance(ch).network, 'algorand:wGHE2')
})

test('discover hits live gateway and gets a 402 challenge', async () => {
  const { status, challenge } = await discover('https://api.gentechlabs.net/v1/token-security/score/So11111111111111111111111111111111111111112')
  assert.equal(status, 402)
  assert.ok(challenge, 'expected a payment-required challenge')
  assert.equal(challenge.resource.url, 'https://api.gentechlabs.net/v1/token-security')
  assert.ok(Array.isArray(challenge.accepts))
  assert.ok(challenge.accepts.length >= 1)
  // The gateway advertises Base USDC as its primary rail.
  assert.ok(challenge.accepts.some((a) => a.network === 'eip155:8453'))
})

test('version export present', () => {
  assert.equal(version, '1.0.0')
})
