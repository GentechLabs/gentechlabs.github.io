/**
 * Pure-JS Keccak-256 (Ethereum domain 0x01), zero npm dependencies.
 * Implements the standard Keccak-f[1600] permutation using BigInt 64-bit lanes.
 * Tested against known vectors in tests/x402-client.test.mjs.
 */

const RC = [
  0x0000000000000001n, 0x0000000000008082n, 0x800000000000808an, 0x8000000080008000n,
  0x000000000000808bn, 0x0000000080000001n, 0x8000000080008081n, 0x8000000000008009n,
  0x000000000000008an, 0x0000000000000088n, 0x0000000080008009n, 0x000000008000000an,
  0x000000008000808bn, 0x800000000000008bn, 0x8000000000008089n, 0x8000000000008003n,
  0x8000000000008002n, 0x8000000000000080n, 0x000000000000800an, 0x800000008000000an,
  0x8000000080008081n, 0x8000000000008080n, 0x0000000080000001n, 0x8000000080008008n,
]

const RHO = [
  0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14,
]

const MASK = (1n << 64n) - 1n

function rotl64(x, n) {
  return ((x << BigInt(n)) | (x >> BigInt(64 - n))) & MASK
}

function keccakF(A) {
  // A is a 25-element array of 64-bit BigInt lanes, index = x + 5*y
  const C = new Array(5)
  const D = new Array(5)
  const B = new Array(25)
  for (let round = 0; round < 24; round++) {
    // Theta
    for (let x = 0; x < 5; x++) {
      C[x] = A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20]
    }
    for (let x = 0; x < 5; x++) {
      D[x] = C[(x + 4) % 5] ^ rotl64(C[(x + 1) % 5], 1)
    }
    for (let x = 0; x < 5; x++) {
      for (let y = 0; y < 5; y++) {
        A[x + 5 * y] ^= D[x]
      }
    }
    // Rho + Pi: B[y + 5*((2x+3y)%5)] = rotl(A[x+5y], RHO[x+5y])
    for (let x = 0; x < 5; x++) {
      for (let y = 0; y < 5; y++) {
        const src = x + 5 * y
        const nx = y
        const ny = (2 * x + 3 * y) % 5
        const dst = nx + 5 * ny
        B[dst] = rotl64(A[src], RHO[src])
      }
    }
    // Chi
    for (let x = 0; x < 5; x++) {
      for (let y = 0; y < 5; y++) {
        const i = x + 5 * y
        A[i] = B[i] ^ ((~B[(x + 1) % 5 + 5 * y] & MASK) & B[(x + 2) % 5 + 5 * y])
      }
    }
    // Iota
    A[0] ^= RC[round]
  }
}

function keccak256Bytes(input) {
  const rate = 136 // 1088-bit rate, 256-bit capacity
  const A = new Array(25).fill(0n)

  const paddedLen = Math.ceil((input.length + 1 + 1) / rate) * rate
  const padded = new Uint8Array(paddedLen)
  padded.set(input)
  padded[input.length] = 0x01 // Keccak domain
  padded[paddedLen - 1] |= 0x80

  for (let off = 0; off < paddedLen; off += rate) {
    for (let i = 0; i < rate; i += 8) {
      let lane = 0n
      for (let k = 0; k < 8; k++) {
        lane |= BigInt(padded[off + i + k]) << BigInt(8 * k)
      }
      A[i / 8] ^= lane
    }
    keccakF(A)
  }

  const out = new Uint8Array(32)
  for (let i = 0; i < 4; i++) {
    let lane = A[i]
    for (let k = 0; k < 8; k++) {
      out[i * 8 + k] = Number(lane & 0xffn)
      lane >>= 8n
    }
  }
  return out
}

/** keccak256 of a UTF-8 string (or Uint8Array), returned as '0x' + 64 hex. */
export function keccak256(input) {
  const bytes = typeof input === 'string' ? new TextEncoder().encode(input) : input
  const digest = keccak256Bytes(bytes)
  return '0x' + Array.from(digest, (b) => b.toString(16).padStart(2, '0')).join('')
}

/** Overridable hash for parity with a signing library. */
export function setKeccak(fn) {
  keccak256 = fn
}
