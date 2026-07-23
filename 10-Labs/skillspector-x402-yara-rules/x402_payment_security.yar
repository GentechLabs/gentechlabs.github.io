/*
 SPDX-FileCopyrightText: Copyright (c) 2026 10-Labs. All rights reserved.
 SPDX-License-Identifier: Apache-2.0

 x402 Payment Security Detection Rules for NVIDIA SkillSpector.

 These rules detect security vulnerabilities, malicious patterns, and
 protocol violations in AI agent skills that implement or interact with
 the x402 payment protocol (HTTP 402 Payment Required).

 Based on research from:
   - "Five Attacks on x402 Agentic Payment Protocol" (arXiv:2605.11781)
   - x402 Specification (x402.org, docs.cdp.coinbase.com)
   - Halborn x402 Security Analysis
   - AgentLISA PaymentShield threat model

 Covers: payment replay, settlement bypass, cache leakage, header injection,
 facilitator manipulation, resource binding violations, and payment prompt
 injection in AI agent contexts.
*/

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 1: PAYMENT REPLAY & IDEMPOTENCY VIOLATIONS
 ────────────────────────────────────────────────────────────────────────────
 Attack II from arXiv:2605.11781 — reusable X-PAYMENT payloads produce
 multiple grants when the server does not atomically record payment identity.
*/

rule x402_payment_replay_no_idempotency
{
 meta:
   description = "x402 payment handler missing idempotency key or nonce — enables replay attacks where one payment is reused for multiple grants"
   category = "hack_tool"
   severity = "CRITICAL"
   confidence = "0.85"
   reference = "arXiv:2605.11781 §3.2 — Attack II: Replay/Idempotency"
 strings:
   $x402_header = /X-PAYMENT/i
   $x402_verify = /(verify|validate|check)\s*(Payment|X-PAYMENT|x402)/i
   $grant_access = /(grant|serve|return|respond|deliver)\s*(resource|content|data|response|file)/i
   $has_idempotency = /(idempotency|idempotent|nonce|pay_id|payment_id|tx_id|signature_id)/i
   $has_replay_check = /(replay|duplicate|already_used|consumed|spent|single.use)/i
 condition:
   $x402_header and $x402_verify and $grant_access and
   not $has_idempotency and not $has_replay_check
}

rule x402_payment_payload_reuse
{
 meta:
   description = "X-PAYMENT payload reused without binding to resource_id — enables one-payment-many-grants attack"
   category = "hack_tool"
   severity = "HIGH"
   confidence = "0.80"
   reference = "arXiv:2605.11781 §3.2 — DGR=n attack"
 strings:
   $x402_header = /X-PAYMENT/i
   $payment_flow = /(payment|settle|facilitator|Permit2|EIP-3009|EIP-712)/i
   $has_resource_bind = /(resource_id|resourceId|resource_uri|path|endpoint|url)/i
 condition:
   $x402_header and $payment_flow and not $has_resource_bind
}

rule x402_missing_payment_consumption
{
 meta:
   description = "Payment handler does not mark X-PAYMENT as consumed after use — enables unlimited replay"
   category = "hack_tool"
   severity = "CRITICAL"
   confidence = "0.75"
   reference = "arXiv:2605.11781 §3.2 — Attack II"
 strings:
   $x402_header = /X-PAYMENT/i
   $payment_check = /(if|when|has|contains)\s*(X-PAYMENT|payment|header)/i
   $grant = /(return|send|respond|200|ok|success|grant)/i
   $has_consume = /(consume|mark_used|invalidate|delete|remove|expire|blacklist|spent)/i
 condition:
   $x402_header and $payment_check and $grant and not $has_consume
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 2: SETTLEMENT BYPASS & GRANT-BEFORE-SETTLE
 ────────────────────────────────────────────────────────────────────────────
 Attack I-A from arXiv:2605.11781 — optimistic execution grants resources
 before payment is final (revert-grant). Attack I-B — caller-unbound
 settlement preemption.
*/

rule x402_grant_before_settle
{
 meta:
   description = "Resource granted before on-chain settlement confirmation — enables revert-grant attack where unpaid service is delivered after settlement failure"
   category = "exploit"
   severity = "CRITICAL"
   confidence = "0.90"
   reference = "arXiv:2605.11781 §3.1 — Attack I-A: Revert-grant"
 strings:
   $grant_before = /(grant|serve|respond|return)\s*(resource|content|data).{0,100}(before|without|prior|optimistic)/i
   $optimistic = /(optimistic|fire.and.forget|async|immediate|instant)\s*(grant|serve|return|respond)/i
   $settle_after = /(settle|submit|send).{0,50}(payment|tx|transaction).{0,50}(after|post|async|background)/i
   $has_settle_check = /(settle|confirm|finality|confirmation|block|receipt|tx_hash)/i
 condition:
   ($grant_before or $optimistic or $settle_after) and not $has_settle_check
}

rule x402_fire_and_forget_settlement
{
 meta:
   description = "Fire-and-forget settlement pattern — server submits transaction without waiting for confirmation, enabling settlement failure after resource delivery"
   category = "exploit"
   severity = "HIGH"
   confidence = "0.85"
   reference = "arXiv:2605.11781 §4.6 — Cross-Implementation Audit"
 strings:
   $fire_forget = /(fire.and.forget|submit_and_forget|send_async|background_task)/i
   $settle_call = /(settle|submit|send|transfer)\s*(payment|tx|transaction|Permit2|USDC)/i
   $has_await = /(await|wait|confirm|receipt|block_number|tx_hash|status)/i
   $x402_context = /(x402|payment|402|facilitator)/i
 condition:
   ($fire_forget or ($settle_call and not $has_await)) and $x402_context
}

rule x402_settlement_preemption_permit2
{
 meta:
   description = "Caller-unbound Permit2 settlement — allows unauthorized settlement preemption where an observer consumes payment before the legitimate facilitator"
   category = "exploit"
   severity = "HIGH"
   confidence = "0.80"
   reference = "arXiv:2605.11781 §3.1.2 — Attack I-B: Settlement Preemption"
 strings:
   $permit2 = /Permit2/i
   $settle_call = /(settle|settlement|settlePermit2|permitTransferFrom)/i
   $has_caller_check = /(caller|sender|msg.sender|from|origin|facilitator_id)/i
   $x402_context = /(x402|payment|402|facilitator)/i
 condition:
   $permit2 and $settle_call and $x402_context and not $has_caller_check
}

rule x402_insufficient_confirmation_depth
{
 meta:
   description = "Settlement accepted with insufficient blockchain confirmation depth — increases revert-grant probability"
   category = "exploit"
   severity = "MEDIUM"
   confidence = "0.70"
   reference = "arXiv:2605.11781 §2.5 — Theorem 6: Confirmation Depth"
 strings:
   $confirm_depth = /(confirm|confirmation|block|depth)\s*(depth|number|count|threshold)/i
   $low_depth = /(1|one|single)\s*(confirmation|block|depth)/i
   $x402_settle = /(settle|finalize|confirm)\s*(payment|tx|transaction)/i
   $has_depth_check = /(depth|confirmations|blocks|threshold|k\s*[>=]|min.*confirm)/i
 condition:
   ($x402_settle and not $has_depth_check) or ($confirm_depth and $low_depth)
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 3: CACHE LEAKAGE & HEADER CONFUSION
 ────────────────────────────────────────────────────────────────────────────
 Attack III from arXiv:2605.11781 — ordinary HTTP infrastructure interacts
 with payment-gated content, causing cache leakage and header ambiguity.
*/

rule x402_cache_leakage_paid_content
{
 meta:
   description = "Paid/gated content served without Cache-Control: no-store — enables cache-based content leakage to unpaid clients"
   category = "hack_tool"
   severity = "HIGH"
   confidence = "0.85"
   reference = "arXiv:2605.11781 §3.3 — Attack III: Cache Leakage"
 strings:
   $x402_gate = /(x402|payment_required|402|paywall|paid|gated)/i
   $serve_content = /(return|send|respond|serve|deliver)\s*(content|data|resource|response|file|page)/i
   $has_cache_control = /(Cache-Control|no-store|private|no-cache|must-revalidate)/i
   $public_cache = /(Cache-Control|public|max-age|s-maxage)/i
 condition:
   $x402_gate and $serve_content and (not $has_cache_control or $public_cache)
}

rule x402_missing_cache_headers
{
 meta:
   description = "x402 payment response missing Cache-Control and Pragma headers — enables CDN/proxy cache leakage of paid content"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.75"
   reference = "arXiv:2605.11781 §3.3 — Attack III: CDN Cache Leak"
 strings:
   $x402_response = /(402|Payment Required|payment_required)/i
   $response_set = /(res\.|response\.|ctx\.|return|send|json|status)/i
   $has_cache_headers = /(Cache-Control|Pragma|Expires|no-store|private)/i
   $has_vary = /(Vary|Authorization|X-PAYMENT|Cookie)/i
 condition:
   $x402_response and $response_set and (not $has_cache_headers or not $has_vary)
}

rule x402_header_ambiguity
{
 meta:
   description = "Ambiguous or non-canonical X-PAYMENT header parsing — enables parser differential attacks between client and server"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.65"
   reference = "arXiv:2605.11781 §3.3 — Attack III: Header Ambiguity"
 strings:
   $x402_header = /X-PAYMENT/i
   $custom_parse = /(split|parse|extract|substring|indexOf|split\s*\(['\"]\s*[,;]\s*['\"]\))/i
   $header_manual = /(headers|getHeader|req\.headers|request\.headers)/i
   $has_canonical = /(canonical|EIP-712|typed|structured|standard)/i
 condition:
   $x402_header and ($custom_parse or $header_manual) and not $has_canonical
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 4: PAYMENT INJECTION & PROMPT MANIPULATION
 ────────────────────────────────────────────────────────────────────────────
 AI agent-specific vulnerabilities — malicious payment descriptions,
 recursive payment loops, and price manipulation in 402 responses.
*/

rule x402_prompt_injection_payment
{
 meta:
   description = "Prompt injection in x402 payment descriptions — malicious instructions embedded in 402 response that trick AI agents into unauthorized payments"
   category = "hack_tool"
   severity = "CRITICAL"
   confidence = "0.80"
   reference = "AgentLISA PaymentShield — AI Agent-Specific Vulnerabilities"
 strings:
   $payment_context = /(payment|pay|send|transfer|USDC|ETH|token)/i
   $injection_instruction = /(first|before|must|need|required|verify)\s*(pay|send|transfer|approve|sign)/i
   $agent_context = /(agent|AI|autonomous|auto|bot|LLM|assistant)/i
   $price_manipulation = /(\$[0-9]{2,}|[0-9]+\s*(USDC|ETH|token))\s*(to|for|in\s*order|before|first)/i
   $hidden_instruction = /(<!--|\[\/\/\]:|#\s*\()\s*.{0,100}(pay|send|transfer|payment)/i
 condition:
   ($payment_context and $injection_instruction and $agent_context) or
   ($price_manipulation and $agent_context) or
   $hidden_instruction
}

rule x402_recursive_payment_loop
{
 meta:
   description = "Recursive payment loop pattern — service references another paid service creating circular payment dependencies that drain agent budgets"
   category = "hack_tool"
   severity = "HIGH"
   confidence = "0.70"
   reference = "AgentLISA PaymentShield — Recursive Payment Loops"
 strings:
   $payment_required = /(payment.required|402|pay|charge|fee)/i
   $service_ref = /(service|endpoint|api|tool|function)\s*(requires|needs|expects|demands)/i
   $chain_ref = /(then|next|after|subsequently|also)\s*(requires|needs|call|invoke|fetch)/i
   $recursive = /(recursive|circular|loop|chain|drain|exhaust)/i
   $budget = /(budget|limit|spend|cost|balance|allowance)/i
 condition:
   (($payment_required and $service_ref and $chain_ref) or $recursive) and $budget
}

rule x402_price_inflation_detection
{
 meta:
   description = "Suspiciously high or unbounded payment amounts in x402 responses — potential price manipulation attack on autonomous agents"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.60"
   reference = "AgentLISA PaymentShield — Price Manipulation"
 strings:
   $amount_field = /(amount|price|cost|fee|value|maxAmount|required_amount)/i
   $high_amount = /(maxAmount|unlimited|no.limit|infinite|100[0-9]{2,}|[0-9]{6,})/i
   $has_max_check = /(max.*amount|limit|cap|budget|threshold|max_spend)/i
   $x402_context = /(x402|payment|402|facilitator|PAYMENT-REQUIRED)/i
 condition:
   $x402_context and $amount_field and ($high_amount or not $has_max_check)
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 5: FACILITATOR & DISCOVERY MANIPULATION
 ────────────────────────────────────────────────────────────────────────────
 Attack IV from arXiv:2605.11781 — server-selection manipulation via
 metadata gaming and Sybil flooding in Bazaar-style discovery.
*/

rule x402_malicious_facilitator_config
{
 meta:
   description = "Suspicious or hardcoded facilitator endpoint in x402 configuration — potential malicious facilitator that approves unpaid requests or leaks payment data"
   category = "malware"
   severity = "HIGH"
   confidence = "0.75"
   reference = "arXiv:2605.11781 §3.4 — Attack IV: Server Selection"
 strings:
   $facilitator_url = /(facilitator|facilitator_url|facilitatorUri|facilitatorEndpoint)/i
   $hardcoded_url = /(https?:\/\/[^'"\s]{10,200}\.(com|io|net|org|xyz|app|dev))\s*['"]?/i
   $suspicious_domain = /(ngrok|serveo|localtunnel|trycloudflare|duckdns|nip\.io|sytes\.net|dynu\.net)/i
   $x402_config = /(x402|payment|402|PAYMENT_REQUIRED|payment_required)/i
   $has_verify = /(verify|validate|check|attest|certify|trusted)/i
 condition:
   $x402_config and $facilitator_url and $hardcoded_url and
   ($suspicious_domain or not $has_verify)
}

rule x402_discovery_metadata_poisoning
{
 meta:
   description = "x402 Bazaar discovery metadata manipulation — inflated ratings, fake reviews, or misleading descriptions to steer agents toward malicious endpoints"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.65"
   reference = "arXiv:2605.11781 §3.4 — Attack IV: Metadata Gaming"
 strings:
   $discovery = /(bazaar|discovery|registry|catalog|marketplace|listing)/i
   $metadata = /(rating|review|score|popularity|trust|reputation|verified)/i
   $inflated = /(5\.0|5\/5|10\/10|perfect|top.rated|best|#1|highest)/i
   $fake_pattern = /(fake|artificial|synthetic|generated|bot|automated)\s*(rating|review|score|traffic)/i
   $x402_context = /(x402|payment|402|service|endpoint|api)/i
 condition:
   $discovery and $metadata and ($inflated or $fake_pattern) and $x402_context
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 6: RESOURCE BINDING & AUTHORIZATION VIOLATIONS
 ────────────────────────────────────────────────────────────────────────────
 Missing resource-identifier binding — payment not scoped to a specific
 resource, enabling cross-resource payment reuse.
*/

rule x402_missing_resource_binding
{
 meta:
   description = "Payment payload not bound to a specific resource identifier — enables cross-resource payment reuse where one payment unlocks multiple endpoints"
   category = "hack_tool"
   severity = "HIGH"
   confidence = "0.80"
   reference = "arXiv:2605.11781 §4.6 — Missing Resource-Identifier Binding"
 strings:
   $payment_payload = /(payment_payload|paymentPayload|signed_payment|payment_signature|X-PAYMENT)/i
   $signing = /(sign|signature|signed|EIP-712|typed_data|structured)/i
   $x402_flow = /(x402|payment|402|facilitator|settle)/i
   $has_resource_id = /(resource_id|resourceId|resource_uri|path|endpoint|url|route)/i
 condition:
   $x402_flow and $payment_payload and $signing and not $has_resource_id
}

rule x402_bearer_payment_capability
{
 meta:
   description = "X-PAYMENT header treated as bearer token without additional verification — enables payment theft and replay by any intermediary"
   category = "exploit"
   severity = "HIGH"
   confidence = "0.75"
   reference = "arXiv:2605.11781 §1 — Bearer-style payment capability"
 strings:
   $x402_header = /X-PAYMENT/i
   $bearer_pattern = /(bearer|token|credential|auth|api.key|secret)/i
   $direct_use = /(req\.headers|request\.headers|getHeader|headers\[)/i
   $has_verify = /(verify|validate|check|authenticate|authorize|verify_signature)/i
 condition:
   $x402_header and $bearer_pattern and $direct_use and not $has_verify
}

rule x402_missing_expiry_check
{
 meta:
   description = "Payment payload accepted without expiry validation — enables indefinite replay of old payment proofs"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.70"
   reference = "arXiv:2605.11781 §5 — M1: Nonce/Timestamp"
 strings:
   $payment_payload = /(payment|X-PAYMENT|signature|payload)/i
   $accept_flow = /(accept|process|handle|receive|parse)\s*(payment|payload|header|signature)/i
   $has_expiry = /(expir|deadline|timeout|ttl|valid_until|max_age|timestamp)/i
 condition:
   $payment_payload and $accept_flow and not $has_expiry
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 7: PROTOCOL IMPLEMENTATION FLAWS
 ────────────────────────────────────────────────────────────────────────────
 General implementation bugs in x402 SDKs and server code.
*/

rule x402_http_status_402_misuse
{
 meta:
   description = "HTTP 402 status code used without proper x402 payment flow — potential misuse or incomplete implementation"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.60"
   reference = "RFC 7231 §6.5.2 — HTTP 402 Payment Required"
 strings:
   $status_402 = /(402|402\s*Payment\s*Required|HTTP\/\d\.\d\s+402)/i
   $response_code = /(status|statusCode|status_code|code)\s*[:=]\s*402/i
   $has_payment_header = /(PAYMENT-REQUIRED|X-PAYMENT|payment_required|payment_uri)/i
 condition:
   ($status_402 or $response_code) and not $has_payment_header
}

rule x402_unsigned_payment_payload
{
 meta:
   description = "Payment payload accepted without cryptographic signature — enables payment forgery and tampering"
   category = "exploit"
   severity = "CRITICAL"
   confidence = "0.85"
   reference = "x402 Specification — Payment Payload Signing"
 strings:
   $payment_accept = /(accept|process|handle|receive|parse)\s*(payment|X-PAYMENT|payload)/i
   $x402_context = /(x402|payment|402|facilitator)/i
   $has_signature_check = /(verify|signature|sign|EIP-712|EIP-3009|Permit2|ecrecover|recover)/i
 condition:
   $x402_context and $payment_accept and not $has_signature_check
}

rule x402_plaintext_payment_transport
{
 meta:
   description = "x402 payment data transmitted over unencrypted HTTP — enables MitM payment interception and modification"
   category = "malware"
   severity = "HIGH"
   confidence = "0.80"
   reference = "Halborn x402 Security Analysis — Payment Interception"
 strings:
   $http_url = /http:\/\//i
   $payment_data = /(payment|X-PAYMENT|PAYMENT-REQUIRED|signature|payload)/i
   $x402_context = /(x402|payment|402|facilitator|settle)/i
   $has_tls = /(https|TLS|SSL|secure|encrypt)/i
 condition:
   $http_url and $payment_data and $x402_context and not $has_tls
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 8: AGENT WALLET & KEY EXPOSURE
 ────────────────────────────────────────────────────────────────────────────
 Exposure of private keys, seed phrases, or wallet configurations used
 for x402 payments in AI agent skills.
*/

rule x402_wallet_private_key_exposure
{
 meta:
   description = "Private key or seed phrase exposed in x402 payment skill code — enables wallet theft and unauthorized payments"
   category = "malware"
   severity = "CRITICAL"
   confidence = "0.90"
   reference = "OWASP LLM Top 10 — Sensitive Information Disclosure"
 strings:
   $private_key = /(private_key|privateKey|secret_key|secretKey|wallet_key|walletKey)/i
   $seed_phrase = /(seed_phrase|mnemonic|seed\s*words|recovery\s*phrase|backup\s*phrase)/i
   $hex_key = /0x[a-fA-F0-9]{64,}/i
   $x402_context = /(x402|payment|wallet|sign|transfer|send|USDC|ETH)/i
   $key_value = /['"][0-9a-fA-F]{64,}['"]/i
 condition:
   $x402_context and (($private_key or $seed_phrase) and ($hex_key or $key_value))
}

rule x402_hardcoded_wallet_config
{
 meta:
   description = "Hardcoded wallet address or configuration in x402 skill — indicates poor security practices and potential credential theft"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.65"
   reference = "OWASP API Security — Hardcoded Secrets"
 strings:
   $wallet_address = /0x[a-fA-F0-9]{40}/i
   $wallet_config = /(wallet|account|address|receiver|recipient|payee)/i
   $hardcoded = /['"](0x[a-fA-F0-9]{40}|[1-9A-HJ-NP-Za-km-z]{32,44})['"]/i
   $x402_context = /(x402|payment|402|settle|transfer|send)/i
 condition:
   $x402_context and $wallet_address and $wallet_config and $hardcoded
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 9: ECONOMIC DOS & BUDGET EXHAUSTION
 ────────────────────────────────────────────────────────────────────────────
 Patterns that enable resource exhaustion, budget draining, or economic
 denial of service through x402 payment loops.
*/

rule x402_verification_spam_pattern
{
 meta:
   description = "Pattern enabling verification spam — flooding endpoints with invalid payment headers to cause economic DoS"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.60"
   reference = "AgentLISA PaymentShield — Verification Spam"
 strings:
   $batch_verify = /(batch|bulk|mass|loop|iterate|for\s+each)\s*(verify|check|validate|process)/i
   $payment_header = /(X-PAYMENT|PAYMENT-REQUIRED|payment)/i
   $x402_context = /(x402|payment|402|facilitator)/i
   $has_rate_limit = /(rate.limit|throttle|backoff|cooldown|max_per_second|429)/i
 condition:
   $x402_context and $batch_verify and $payment_header and not $has_rate_limit
}

rule x402_unbounded_spending
{
 meta:
   description = "Agent skill with unbounded or missing spending limits for x402 payments — enables budget exhaustion"
   category = "hack_tool"
   severity = "HIGH"
   confidence = "0.70"
   reference = "AgentLISA PaymentShield — Budget Exhaustion"
 strings:
   $payment_action = /(pay|send|transfer|approve|settle)\s*(payment|USDC|ETH|token|amount)/i
   $agent_loop = /(while|for|loop|retry|repeat|continue|auto)/i
   $x402_context = /(x402|payment|402|agent|autonomous)/i
   $has_budget = /(budget|limit|max|cap|threshold|allowance|max_spend|spending_limit)/i
 condition:
   $x402_context and $payment_action and $agent_loop and not $has_budget
}

/*
 ────────────────────────────────────────────────────────────────────────────
 CATEGORY 10: CROSS-SDK & ENCODING DRIFT
 ────────────────────────────────────────────────────────────────────────────
 Cross-SDK serialization drift and encoding inconsistencies that enable
 parser differential attacks.
*/

rule x402_encoding_drift
{
 meta:
   description = "Non-canonical payment payload encoding — cross-SDK serialization drift enables parser differential attacks between client and server"
   category = "hack_tool"
   severity = "MEDIUM"
   confidence = "0.55"
   reference = "arXiv:2605.11781 §5 — M1: Canonical Encoding"
 strings:
   $custom_encoding = /(JSON\.stringify|JSON\.parse|JSON\.serialize|json\.dumps|json\.loads)/i
   $payment_data = /(payment|payload|signature|X-PAYMENT|amount|token|chain)/i
   $canonical_encoding = /(EIP-712|typed_data|structured_data|canonical|ABIEncode|encodeTypedData)/i
   $x402_context = /(x402|payment|402|facilitator)/i
 condition:
   $x402_context and $custom_encoding and $payment_data and not $canonical_encoding
}
