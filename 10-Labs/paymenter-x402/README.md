# Paymenter x402 Crypto Gateway

Accept **gasless crypto payments** in Paymenter via the x402 protocol.  
Powered by [GenTech Labs](https://gentechlabs.net).

## How it works

1. Customer checks out and selects **"Pay with Crypto (x402)"**
2. A QR code + payment URL is generated
3. Customer pays with their wallet (Solana, Base, Ethereum, or Polygon)
4. x402 gateway confirms the transaction — **gasless, instant settlement**
5. Paymenter marks the invoice as paid

## Installation

```bash
# Clone into Paymenter extensions directory
cd /var/www/paymenter
git clone https://github.com/ProtoJay4789/paymenter-x402 extensions/Gateways/X402

# Or via composer
composer require gentech/paymenter-x402
```

Then enable the gateway in Paymenter admin panel → Gateways → x402 Crypto Gateway.

## Configuration

| Field | Description |
|-------|-------------|
| **x402 Gateway URL** | Your x402 gateway endpoint (default: `https://api.gentechlabs.net/x402`) |
| **x402 API Key** | API key for the gateway (optional for public gateways) |
| **Merchant Wallet Address** | Your wallet where payments settle |
| **Blockchain Network** | Solana, Base, Ethereum, or Polygon |
| **Accepted Token** | USDC, USDT, SOL, or ETH |

## Self-hosting the x402 gateway

You can run your own x402 gateway instead of using GenTech's public endpoint:

```bash
git clone https://github.com/ProtoJay4789/x402-gateway
cd x402-gateway
pip install -r requirements.txt
python server.py
```

See the [x402 gateway docs](https://gentechlabs.net/docs/x402) for details.

## Contributing

This is an open-source contribution from GenTech Labs.  
Everyone gets paid — x402 is about making agent-to-agent payments universal.

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — do whatever you want, just give credit.
