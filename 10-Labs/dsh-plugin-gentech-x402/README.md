# dsh-plugin-gentech-x402

GenTech x402 payment plugin for **[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)** — the "everything is a plugin" agent harness (60k+ stars, MIT).

This plugin registers pay-per-call tools on `ctx.tools` so a dsh agent can **discover and pay-per-call the GenTech x402 gateway** (or any x402 resource) **without holding API keys**. It's the first x402 payment plugin in the dsh plugin ecosystem.

## Why this matters

- **Early-contributor visibility** on a 46k-star (day-one) project. The `dsh-plugin` topic is explicitly promoted for discoverability.
- Validates GenTech's x402 thesis inside a first-party DeepSeek agent harness — the same architecture our self-evolution harness uses.
- Gives dsh agents **credential-free monetized API access** — the exact "software card" / agent-commerce wedge we sell.

## Tools registered

| Tool | Cost | Purpose |
|---|---|---|
| `gentech_services` | free | List the gateway's paid services |
| `gentech_discover` | free | Probe **any** x402 URL → parsed payment-required challenge |
| `gentech_token_security` | ~$0.01 | Score a token/contract address for risk |
| `gentech_wallet_analysis` | ~$0.01 | Analyze a wallet address |
| `gentech_market_intel` | ~$0.01 | Market intelligence for a symbol/asset |

## Install

```sh
# add the plugin package to your dsh composition
npm install gentech-x402-client dsh-plugin-gentech-x402
```

Mount it in `cordis.yml`:

```yaml
- name: 'dsh-plugin-gentech-x402'
  config:
    baseUrl: 'https://api.gentechlabs.net'
    network: 'eip155:8453'   # Base USDC
```

## Settlement

By default the plugin **surfaces the 402 challenge** so the agent can present it to the user for funding. To close the loop autonomously, mount a wallet service and assign `ctx.gentechSettle`:

```js
ctx.gentechSettle = async (challenge, acceptance) => {
  // sign the acceptance (see src/x402-client.js buildEvmSettlement)
  return token
}
```

The client core is `src/x402-client.js` — a **dependency-free** x402 client (pure Node 18+, global fetch, self-contained keccak256). It implements the full `discover → accept → settle → call` flow against any x402 resource (GenTech gateway, CDP Bazaar, Meridian, PayAI).

## Verify

```sh
cd 10-Labs/dsh-plugin-gentech-x402
npm test          # 19 tests: keccak vectors + live gateway discovery + plugin registration
```

Live discovery is verified against `https://api.gentechlabs.net/v1/token-security/score/...` (HTTP 402 + payment-required challenge with Base USDC rail).

## License

MIT
