<?php
/**
 * x402 Crypto Gateway for Blesta — Webhook Callback
 *
 * Receives payment status notifications from the x402 gateway and marks
 * the Blesta invoice as paid when a payment completes.
 *
 * Blesta callback entry point: components/gateways/merchant/x402/x402_callback.php
 * The gateway posts to:  https://your-blesta/components/gateways/merchant/x402/x402_callback.php
 */

require_once dirname(__FILE__) . DIRECTORY_SEPARATOR . 'x402.php';

/**
 * x402 callback controller.
 */
class X402Callback extends X402
{
    /**
     * Handle the webhook callback from the x402 gateway.
     */
    public function index()
    {
        // Read the JSON payload
        $payload = json_decode(file_get_contents('php://input'), true);
        if (!is_array($payload)) {
            $payload = $this->post; // fallback to form-encoded
        }

        $paymentRef = $payload['reference'] ?? '';
        $status = $payload['status'] ?? '';
        $txHash = $payload['transaction_hash'] ?? '';
        $amount = $payload['amount'] ?? 0;

        // Extract invoice ID from the payment reference (pay_{invoiceId}_{nonce})
        if (!preg_match('/^pay_(\d+)_/', $paymentRef, $matches)) {
            $this->Input->setErrors(['reference' => ['invalid' => 'Invalid payment reference']]);
            $this->setMessage('error', 'Invalid payment reference');
            return false;
        }
        $invoiceId = (int)$matches[1];

        if (in_array($status, ['completed', 'confirmed'], true)) {
            // Mark the invoice as paid via Blesta's gateway log
            $this->Input->setErrors([]);
            $this->setMessage('success', 'Payment approved');
            return [
                'status' => 'approved',
                'reference_id' => $paymentRef,
                'transaction_id' => $txHash ?: $paymentRef,
                'amount' => $amount,
                'invoice_id' => $invoiceId,
            ];
        }

        if (in_array($status, ['failed', 'expired'], true)) {
            $this->setMessage('error', 'Payment ' . $status);
            return false;
        }

        // Pending — acknowledge
        return true;
    }
}
