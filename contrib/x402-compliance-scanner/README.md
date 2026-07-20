# x402 Compliance Scanner

A reference implementation for validating x402 endpoint compliance against the protocol specification.

Part of the [x402](https://github.com/x402-foundation/x402) ecosystem — an open standard for internet-native payments.

## What it checks

| Check | What it validates |
|-------|------------------|
| HTTP 402 | Endpoint returns 402 Payment Required |
| Required fields | `status`, `x402version`, `accepts`, `network`, `asset`, `amount`, `payment_address` |
| accepts[] schema | Each payment option has `type`, `scheme`, `network`, `amount`, `asset`, `payTo` |
| x402 version | Must be `2`, `"2"`, or `"x402-v2"` |
| Amount format | Positive integer string |
| CORS | `Access-Control-Allow-Origin` header present |
| Settlement flow | 402 → payment auth → 200 resource (optional, requires valid payment) |

## Usage

```bash
# Scan a single endpoint
python3 scanner.py scan https://api.example.com/v1/resource

# Scan all x402-gated endpoints (via OpenAPI discovery)
python3 scanner.py scan-all https://api.example.com

# With payment auth for settlement flow test
python3 scanner.py scan https://api.example.com/v1/resource "scheme=exact;network=base-sepolia;..."
```

## Exit codes

- `0` — all checks passed
- `1` — one or more checks failed

## Integration

Use as a standalone CLI tool or import the `scan_endpoint()` function:

```python
from scanner import scan_endpoint

results = scan_endpoint("https://api.example.com/v1/resource")
print(results["summary"])
```

## Contributing

This is a community contribution to the x402 ecosystem. PRs welcome for:

- Additional network-specific checks
- Settlement flow verification for new chains
- Receipt validation patterns
- Integration with CI/CD pipelines

## License

Apache 2.0 — same as the x402 specification.
