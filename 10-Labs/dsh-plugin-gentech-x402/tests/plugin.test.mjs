import { test } from 'node:test'
import assert from 'node:assert/strict'

// --- Mock the @deepseek-ai/dsh-tools contract -------------------------
const registered = []
const mockCtx = {
  tools: {
    register(def) {
      registered.push(def)
    },
  },
  gentechSettle: undefined,
}

// defineTool returns its argument unchanged in our mock.
const defineToolMock = (def) => def

// Load the plugin with a mocked module graph.
const pluginUrl = new URL('../src/plugin.js', import.meta.url)
const pluginModule = await import(pluginUrl)

// We can't swap the import statically, so instead re-register via a tiny
// loader that rewrites the import. Simpler: assert on the export shape and
// drive x402-client directly for the round-trip.

test('plugin exports a valid apply function', () => {
  assert.equal(typeof pluginModule.apply, 'function')
  assert.equal(pluginModule.name, 'gentech-x402')
  assert.ok(Array.isArray(pluginModule.inject))
  assert.ok(pluginModule.inject.includes('tools'))
})

test('x402-client discover round-trips against live gateway (no payment)', async () => {
  // Reuse the real client via plugin's internal import path.
  const client = await import('../src/x402-client.js')
  const url = 'https://api.gentechlabs.net/v1/token-security/score/So11111111111111111111111111111111111111112'
  const { status, challenge } = await client.discover(url)
  assert.equal(status, 402)
  assert.ok(challenge)
  const acceptance = client.pickAcceptance(challenge, { network: 'eip155:8453' })
  assert.equal(acceptance.network, 'eip155:8453')
  // amount is atomic units (10000 = 0.01 USDC)
  assert.equal(acceptance.amount, '10000')
})

test('buildEvmSettlement produces a signed envelope deterministically', async () => {
  const client = await import('../src/x402-client.js')
  const acceptance = {
    scheme: 'exact',
    network: 'eip155:8453',
    asset: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    amount: '10000',
    payTo: '0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734',
  }
  const env = await client.buildEvmSettlement(acceptance, {
    nonce: '0x1',
    payer: '0xpayer',
    sign: async () => ({ r: '0xaa', s: '0xbb', v: 27 }),
  })
  assert.equal(env.scheme, 'exact')
  assert.equal(env.network, 'eip155:8453')
  assert.equal(env.amount, '10000')
  assert.equal(env.signature.v, 27)
  assert.ok(env.digest.startsWith('0x'))
  assert.equal(env.digest.length, 66)
})

test('x402 client keccak matches third known vector', async () => {
  const client = await import('../src/x402-client.js')
  // keccak-256("hello") = 1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8
  assert.equal(
    client.keccak256('hello'),
    '0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8',
  )
})

test('parsePaymentRequired rejects malformed input', async () => {
  const client = await import('../src/x402-client.js')
  assert.throws(() => client.parsePaymentRequired(''), /missing payment-required/)
  assert.throws(() => client.parsePaymentRequired('not-base64-{{{{'), /unparseable|unexpected/i)
})
