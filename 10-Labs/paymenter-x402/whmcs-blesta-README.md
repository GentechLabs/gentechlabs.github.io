# x402 Crypto Gateway — WHMCS & Blesta Ports

Port of the [Paymenter x402 gateway](../README.md) to the two largest hosting
billing platforms: **WHMCS** and **Blesta**. Same x402 protocol, same gasless
crypto payments (USDC/USDT/SOL/ETH), same GenTech gateway backend.

## Why these two

- **WHMCS** — the dominant web-hosting billing platform (tens of thousands of
  hosts). Its customers are exactly the game-server / VPS / web-hosting buyers
  who already hold crypto.
- **Blesta** — the leading open-source alternative, popular with smaller hosts
  and game-server providers.

Both are much larger markets than Paymenter. Porting the same gateway pattern
gives us three billing-platform integrations from one codebase.

## Structure

```
whmcs/
  x402.php            module definition + config + payment link
  x402callback.php    webhook callback (marks invoice paid)
blesta/
  x402.php            merchant gateway class
  x402_pay.php        payment page helper
  x402_callback.php   webhook callback
  config.json         gateway settings schema
  language/en_us/     English language strings
test_x402_ports.php   test harness (24 assertions)
```

## Install — WHMCS

1. Copy the `whmcs/` contents into `modules/gateways/x402/`:
   ```
   modules/gateways/x402/x402.php
   modules/gateways/x402/x402callback.php
   ```
2. In WHMCS admin: **Setup → Payments → Payment Gateways** → activate
   **x402 Crypto Gateway**.
3. Configure: gateway URL (default `https://api.gentechlabs.net/x402`),
   merchant wallet, chain, token.
4. Set the webhook URL in your x402 gateway config to:
   `https://your-whmcs/modules/gateways/x402/x402callback.php`

## Install — Blesta

1. Copy the `blesta/` folder into `components/gateways/merchant/x402/`.
2. In Blesta admin: **Settings → Payment Gateways** → install **x402**.
3. Configure the same fields.
4. Set the webhook URL to:
   `https://your-blesta/components/gateways/merchant/x402/x402_callback.php`

## How it works

1. Customer checks out and selects **"Pay with Crypto (x402)"**.
2. The module builds an x402 payment URL and redirects the customer.
3. Customer pays with their wallet (gasless, instant).
4. The x402 gateway posts a webhook; the callback marks the invoice paid.

## Verify

```bash
php -l whmcs/x402.php whmcs/x402callback.php blesta/x402.php blesta/x402_pay.php blesta/x402_callback.php
php test_x402_ports.php   # 24 assertions, all pass
```

## License

MIT — open-source contribution from GenTech Labs.
