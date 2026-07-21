# gentech-x402 — Python SDK for GenTech Labs x402 Gateway

**Easy integration with GenTech Labs x402 Gateway — 16 AI-powered API endpoints with USDC micropayments on Base, Solana, Avalanche, BNB, or OKX.**

---

## 🚀 Installation

```bash
pip install gentech-x402
```

---

## ⚡ Quick Start

### 1. Set your wallet private key

```bash
export GENTECH_PRIVATE_KEY="your-wallet-private-key"
```

**⚠️ Security:** Never commit private keys to Git! Use environment variables.

### 2. Import and use the SDK

```python
import asyncio
from gentech_x402 import GenTechGateway

async def main():
    # Initialize gateway (uses GENTECH_PRIVATE_KEY env var)
    gateway = GenTechGateway()

    # Check gateway health (free)
    health = await gateway.health()
    print("Gateway status:", health["status"])

    # Search games ($0.005)
    result = await gateway.games_search("zelda breath of the wild")
    print("Game results:", result)

    # Analyze wallet ($0.025)
    analysis = await gateway.wallet_analyze(
        "0x7ebff188f2Eba16518C02864589b1403a5d1296a",
        "base"
    )
    print("Wallet analysis:", analysis)

    # Check token risk ($0.01)
    risk = await gateway.token_risk(
        "0x4200000000000000000000000000000000000042",
        "base"
    )
    print("Token risk:", risk)

# Run async
asyncio.run(main())
```

---

## 🔄 Synchronous Usage

```python
from gentech_x402 import GenTechGatewaySync

gateway = GenTechGatewaySync()

# Health check (free)
health = gateway.health()

# Game search ($0.005)
result = gateway.games_search("elden ring")

# Airdrop checker ($0.01)
airdrops = gateway.airdrops_check("0x7ebff188f2Eba16518C02864589b1403a5d1296a")
```

---

## 📚 Available Methods

### Gaming Endpoints

| Method | Price | Description |
|--------|-------|-------------|
| `games_search(query)` | $0.005 | Search games across platforms |
| `games_cheapest(query)` | $0.005 | Find cheapest game prices |
| `games_news()` | $0.001 | Get latest gaming news |
| `games_release()` | $0.001 | Get game release information |

### Movies Endpoints

| Method | Price | Description |
|--------|-------|-------------|
| `movies_search(query)` | $0.005 | Search movies |
| `movies_cheapest(query)` | $0.005 | Find cheapest watch options |
| `movies_details(movie_id)` | $0.001 | Get movie details |
| `movies_trailers(movie_id)` | $0.001 | Get movie trailers |

### DeFi / Analytics Endpoints

| Method | Price | Description |
|--------|-------|-------------|
| `wallet_analyze(address, chain)` | $0.025 | AI-powered wallet analytics |
| `token_risk(address, chain)` | $0.01 | AI-powered token risk assessment |
| `airdrops_check(address)` | $0.01 | Check airdrop eligibility |
| `nft_search(query)` | $0.005 | Search NFTs and collections |

### Search & Intelligence

| Method | Price | Description |
|--------|-------|-------------|
| `intel_search(query)` | $0.005 | Unified search across games + movies |
| `intel_cheapest(query)` | $0.005 | Find cheapest across all categories |
| `agentscan(target)` | $0.10 | AI-powered agent reconnaissance |

### Utilities

| Method | Price | Description |
|--------|-------|-------------|
| `shipping_track(tracking_number)` | $0.005 | Multi-carrier shipping tracker |
| `health()` | Free | Gateway health check |
| `pricing()` | Free | Get pricing information |
| `openapi()` | Free | Get OpenAPI specification |

---

## ⚙️ Configuration

### Custom Configuration

```python
from gentech_x402 import GenTechGateway, GatewayConfig

config = GatewayConfig(
    gateway_url="https://api.gentechlabs.net",
    network_id="eip155:8453",  # Base mainnet
    asset_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC on Base
    pay_to_address="0x7ebff188f2Eba16518C02864589b1403a5d1296a",
    max_fee=1000000,  # 1 USDC max fee
    timeout=300  # 5 minutes
)

gateway = GenTechGateway(private_key="your-key", config=config)
```

### Supported Networks

| Network | Chain ID | Recommended? |
|---------|----------|--------------|
| **Base** | `eip155:8453` | ✅ Best (lowest fees) |
| **Solana** | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | ✅ Good |
| **Avalanche** | `eip155:43114` | ⚡ Alternative |
| **BNB Chain** | `eip155:56` | ⚡ Alternative |
| **OKX X Layer** | `eip155:196` | ⚡ Alternative |

---

## 🛡️ Error Handling

```python
from gentech_x402 import GenTechGateway, PaymentRequiredError, RateLimitError

async def safe_search(query):
    gateway = GenTechGateway()

    try:
        result = await gateway.games_search(query)
        return result
    except PaymentRequiredError:
        print("Payment verification failed — check wallet balance")
    except RateLimitError:
        print("Rate limited — please slow down")
    except Exception as e:
        print(f"Error: {e}")
```

---

## 💰 Payment Flow

The SDK automatically handles:

1. **Payment creation** — x402 payment message generated
2. **Signing** — Wallet signs payment message
3. **Verification** — Gateway verifies payment via x402 facilitator
4. **Execution** — Endpoint executes if payment valid
5. **Settlement** — Payment settled automatically on-chain

No manual payment handling required!

---

## 📊 Example: Batch Requests

```python
import asyncio
from gentech_x402 import GenTechGateway

async def batch_search():
    gateway = GenTechGateway()

    # Parallel game search
    queries = ["elden ring", "zelda", "starfield", "diablo 4"]
    tasks = [gateway.games_search(q) for q in queries]
    results = await asyncio.gather(*tasks)

    for q, result in zip(queries, results):
        print(f"Results for '{q}':")
        print(result)
        print("---")

asyncio.run(batch_search())
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install gentech-x402[dev]

# Run tests
pytest
```

---

## 🔐 Security Best Practices

1. **Never commit private keys** — Use environment variables
2. **Use testnet for development** — Don't waste real USDC
3. **Monitor costs** — Track payment amounts per endpoint
4. **Validate responses** — Always check return data structure
5. **Handle errors gracefully** — Use try/except blocks

---

## 📚 Full Documentation

- **Getting Started Guide:** https://api.gentechlabs.net/openapi.json
- **API Examples:** See [EXAMPLES.md](../EXAMPLES.md)
- **x402 Protocol:** https://x402.org

---

## 🤝 Contributing

Contributions welcome! Please open issues or pull requests on GitHub.

---

## 📜 License

MIT License — see LICENSE file for details

---

## 📞 Support

- **GitHub:** https://github.com/ProtoJay4789/gentech-vault
- **X/Twitter:** [@GenTechLabs](https://x.com/GenTechLabs)
- **Email:** hello@gentechlabs.net

---

**GenTech Labs** — Building the agent economy with x402 micropayments

**Version:** 1.0.0
**Last Updated:** July 7, 2026