# Secure: Idempotency key + resource binding + settle check
def handle_payment(request):
    payment_id = request.headers.get('X-PAYMENT-ID')
    if payment_consumed(payment_id):
        return error(409, "Payment already used")
    
    payment = request.headers.get('X-PAYMENT')
    resource_id = request.path
    
    if not verify_payment_for_resource(payment, resource_id):
        return error(402, "Invalid payment for resource")
    
    if not wait_for_settlement(payment, min_confirmations=12):
        return error(402, "Settlement not confirmed")
    
    response = serve_resource()
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    mark_payment_consumed(payment_id)
    return response

# Secure: Proper x402 implementation with all checks
@app.route('/api/secure')
def secure_paid_endpoint():
    payment_id = request.headers.get('X-PAYMENT-ID')
    if not payment_id or is_duplicate(payment_id):
        return error(409)
    
    payment = request.headers.get('X-PAYMENT')
    if not verify_signature(payment):
        return error(402)
    
    if not check_settlement(payment, depth=12):
        return error(402)
    
    response = jsonify(data="secure data")
    response.headers['Cache-Control'] = 'no-store, private'
    response.headers['Vary'] = 'X-PAYMENT, Authorization'
    mark_used(payment_id)
    return response

# Secure: Wallet config with env vars (no hardcoded keys)
import os
WALLET_PRIVATE_KEY = os.environ.get('X402_WALLET_KEY')
if not WALLET_PRIVATE_KEY:
    raise ConfigError("X402_WALLET_KEY not set")

# Secure: HTTPS-only facilitator
facilitator_url = "https://facilitator.coinbase.com/verify"

# Secure: Budget-limited agent loop
budget = Decimal("10.00")
spent = Decimal("0")
while spent < budget:
    result = call_paid_api()
    spent += result.cost
    process(result)

# Secure: Proper settlement with confirmation
async def settle_payment(payment):
    tx = await submit_transaction(payment)
    receipt = await wait_for_confirmation(tx, confirmations=12)
    return receipt.status

# Secure: Proper Permit2 with caller binding
def settle_permit2(payment, caller):
    if caller != msg.sender:
        raise InvalidCaller()
    permit2.permitTransferFrom(payment)

# Secure: Proper HTTP 402 response
return Response(
    status=402,
    headers={
        'PAYMENT-REQUIRED': 'amount=0.01&token=USDC&chain=eip155:8453',
        'Cache-Control': 'no-store'
    }
)

# Secure: Signed payment payload with EIP-712
def accept_payment(payload):
    if not verify_eip712_signature(payload):
        raise InvalidSignature()
    return process(payload)

# Secure: Rate-limited verification
from flask_limiter import Limiter
limiter = Limiter(key_func=lambda: request.remote_addr)
@app.route('/verify')
@limiter.limit("10 per minute")
def verify_payment():
    return process_verification()

# Secure: Canonical encoding with EIP-712
from eth_account.messages import encode_typed_data
payload = encode_typed_data(domain, types, message)
