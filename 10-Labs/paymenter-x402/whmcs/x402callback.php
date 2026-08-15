<?php
/**
 * x402 Crypto Gateway for WHMCS — Webhook Callback
 *
 * Receives payment status notifications from the x402 gateway and marks
 * the WHMCS invoice as paid when a payment completes.
 *
 * WHMCS callback entry point: modules/gateways/x402/x402callback.php
 * The gateway posts to:  https://your-whmcs/modules/gateways/x402/x402callback.php
 */

require_once __DIR__ . '/../../../init.php';
require_once __DIR__ . '/../../../includes/gatewayfunctions.php';
require_once __DIR__ . '/../../../includes/invoicefunctions.php';

$gatewayModuleName = 'x402';
$GATEWAY = getGatewayVariables($gatewayModuleName);

if (!$GATEWAY['type']) {
    die('Module Not Activated');
}

// Read the JSON payload from the x402 gateway webhook
$payload = json_decode(file_get_contents('php://input'), true);
if (!is_array($payload)) {
    $payload = $_POST; // fallback to form-encoded
}

$paymentRef = $payload['reference'] ?? '';
$status = $payload['status'] ?? '';
$txHash = $payload['transaction_hash'] ?? '';
$amount = $payload['amount'] ?? 0;

// Extract invoice ID from the payment reference (pay_{invoiceId}_{nonce})
if (!preg_match('/^pay_(\d+)_/', $paymentRef, $matches)) {
    logTransaction($GATEWAY['name'], $payload, 'Invalid payment reference');
    http_response_code(400);
    die('Invalid reference');
}
$invoiceId = (int)$matches[1];

// Look up the invoice
$invoiceId = checkCbInvoiceID($invoiceId, $GATEWAY['name']);
checkCbTransID($txHash ?: $paymentRef);

if (in_array($status, ['completed', 'confirmed'], true)) {
    // Mark the invoice as paid
    addInvoicePayment(
        $invoiceId,
        $txHash ?: $paymentRef,
        $amount ?: null,
        0,
        $gatewayModuleName
    );
    logTransaction($GATEWAY['name'], $payload, 'x402 payment completed');
    http_response_code(200);
    echo 'OK';
    exit;
}

if (in_array($status, ['failed', 'expired'], true)) {
    logTransaction($GATEWAY['name'], $payload, 'x402 payment ' . $status);
    http_response_code(200);
    echo 'OK';
    exit;
}

// Pending / unknown — acknowledge without marking paid
logTransaction($GATEWAY['name'], $payload, 'x402 payment pending');
http_response_code(200);
echo 'OK';
