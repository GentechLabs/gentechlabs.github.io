# Test Cases for x402 Payment Security YARA Rules

This directory contains test samples for validating the x402 YARA rules.

## Structure

- `positive/` — Code samples that SHOULD trigger rules (true positives)
- `negative/` — Code samples that should NOT trigger rules (false positive checks)

## Running Tests

```bash
# Using yara directly
yara -r ../x402_payment_security.yar positive/

# Verify no matches on negative samples
yara -r ../x402_payment_security.yar negative/
```

## Test Samples

### Positive: Payment Replay (x402_payment_replay_no_idempotency)

```python
# Vulnerable: No idempotency key
def handle_payment(request):
    payment = request.headers.get('X-PAYMENT')
    if verify_payment(payment):
        return serve_resource()  # No replay check!
```

### Positive: Grant Before Settle (x402_grant_before_settle)

```python
# Vulnerable: Optimistic grant
@app.route('/api/data')
def paid_endpoint():
    payment = request.headers.get('X-PAYMENT')
    if payment:
        # Grant immediately, settle later
        response = serve_content()
        background_submit_settlement(payment)
        return response
```

### Positive: Cache Leakage (x402_cache_leakage_paid_content)

```python
# Vulnerable: No Cache-Control on paid content
@app.route('/premium')
@x402_required
def premium_data():
    return jsonify(data="sensitive"), 200
    # Missing: Cache-Control: no-store
```

### Positive: Private Key Exposure (x402_wallet_private_key_exposure)

```python
# Vulnerable: Hardcoded private key
WALLET_PRIVATE_KEY = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
```

### Negative: Secure Implementation

```python
# Secure: Idempotency + resource binding + settle check
def handle_payment(request):
    payment_id = request.headers.get('X-PAYMENT-ID')
    if payment_consumed(payment_id):
        return error(409, "Payment already used")
    
    payment = request.headers.get('X-PAYMENT')
    resource_id = request.path
    
    if not verify_payment_for_resource(payment, resource_id):
        return error(402, "Invalid payment")
    
    if not wait_for_settlement(payment, min_confirmations=12):
        return error(402, "Settlement not confirmed")
    
    response = serve_resource()
    response.headers['Cache-Control'] = 'no-store'
    mark_payment_consumed(payment_id)
    return response
```
