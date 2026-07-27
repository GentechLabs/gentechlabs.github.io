<?php

namespace Paymenter\Extensions\Gateways\X402;

use App\Attributes\ExtensionMeta;
use App\Classes\Extension\Gateway;
use App\Models\Invoice;
use App\Models\Extension;
use App\Helpers\ExtensionHelper;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\View;
use Illuminate\Support\Facades\Log;

#[ExtensionMeta(
    name: 'x402 Crypto Gateway',
    description: 'Accept crypto payments via x402 — agent-to-agent, gasless, instant settlement. Powered by GenTech Labs.',
    version: '1.0.0',
    author: 'GenTech Labs',
    url: 'https://gentechlabs.net',
    icon: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiI+PHJlY3Qgd2lkdGg9IjUxMiIgaGVpZ2h0PSI1MTIiIGZpbGw9IiMwMDBhMjAiLz48cGF0aCBkPSJNMjU2IDQ4QzE0MCA0OCA0OCAxNDAgNDggMjU2czkyIDIwOCAyMDggMjA4IDIwOC05MiAyMDgtMjA4UzM3MiA0OCAyNTYgNDh6bTAgMzg0Yy05NyAwLTE3Ni03OS0xNzYtMTc2UzE1OSA4MCAyNTYgODBzMTc2IDc5IDE3NiAxNzYtNzkgMTc2LTE3NiAxNzZ6IiBmaWxsPSIjMDBmMGZmIi8+PHBhdGggZD0iTTI1NiAxMjhsLTU2IDE0MCA1NiA2MCA1Ni02MC01Ni0xNDB6bTAgODBjMTEuMCAwIDIwIDkgMjAgMjBzLTkgMjAtMjAgMjAtMjAtOS0yMC0yMCA5LTIwIDIwLTIweiIgZmlsbD0iIzAwZjBmZiIvPjwvc3ZnPg=='
)]
class X402 extends Gateway
{
    /**
     * Boot the extension — register routes and views.
     */
    public function boot()
    {
        require __DIR__ . '/routes.php';
        View::addNamespace('gateways.x402', __DIR__ . '/resources/views');
    }

    /**
     * Configuration fields for the admin panel.
     */
    public function getConfig($values = [])
    {
        return [
            [
                'name' => 'x402_gateway_url',
                'label' => 'x402 Gateway URL',
                'type' => 'text',
                'default' => 'https://api.gentechlabs.net/x402',
                'description' => 'Your x402 gateway endpoint (e.g. https://api.gentechlabs.net/x402 or self-hosted)',
                'required' => true,
            ],
            [
                'name' => 'x402_api_key',
                'label' => 'x402 API Key',
                'type' => 'text',
                'description' => 'API key for the x402 gateway (optional for public gateways)',
                'required' => false,
            ],
            [
                'name' => 'x402_merchant_wallet',
                'label' => 'Merchant Wallet Address',
                'type' => 'text',
                'description' => 'Your wallet address where payments are sent (Solana or EVM)',
                'required' => true,
            ],
            [
                'name' => 'x402_chain',
                'label' => 'Blockchain Network',
                'type' => 'select',
                'default' => 'solana',
                'description' => 'Which chain to settle payments on',
                'options' => [
                    'solana' => 'Solana (USDC)',
                    'base' => 'Base (USDC)',
                    'ethereum' => 'Ethereum (USDC)',
                    'polygon' => 'Polygon (USDC)',
                ],
                'required' => true,
            ],
            [
                'name' => 'x402_accepted_tokens',
                'label' => 'Accepted Tokens',
                'type' => 'select',
                'default' => 'USDC',
                'description' => 'Which token to accept for payments',
                'options' => [
                    'USDC' => 'USDC',
                    'USDT' => 'USDT',
                    'SOL' => 'SOL (Solana only)',
                    'ETH' => 'ETH (EVM chains only)',
                ],
                'required' => true,
            ],
        ];
    }

    /**
     * Check if this gateway can be used for a given transaction.
     */
    public function canUseGateway($total, $currency, $type, $items = [])
    {
        // x402 works with any amount, any currency (converted at settlement)
        // Only available for invoices (not cart checkout)
        if ($type === 'cart') {
            return false;
        }
        return true;
    }

    /**
     * Process payment — generate an x402 payment request with Q402 Trust Receipt.
     */
    public function pay(Invoice $invoice, $total)
    {
        $config = $this->getConfigValues();
        $gatewayUrl = $config['x402_gateway_url'] ?? 'https://api.gentechlabs.net/x402';
        $merchantWallet = $config['x402_merchant_wallet'] ?? '';
        $chain = $config['x402_chain'] ?? 'solana';
        $token = $config['x402_accepted_tokens'] ?? 'USDC';

        // Generate a unique payment reference
        $paymentRef = 'pay_' . $invoice->id . '_' . uniqid();

        // Build the x402 payment URL with receipt support
        // The Q402 gateway returns a rct_ receipt ID on completion
        $paymentUrl = rtrim($gatewayUrl, '/') . '/pay?' . http_build_query([
            'amount' => number_format((float)$total, 2, '.', ''),
            'to' => $merchantWallet,
            'chain' => $chain,
            'token' => $token,
            'reference' => $paymentRef,
            'redirect' => route('invoices.show', $invoice) . '?receipt={receipt_id}',
            'receipt' => 'true',  // Enable Q402 Trust Receipt
        ]);

        // Store the payment reference on the invoice
        $invoice->update([
            'transaction_id' => $paymentRef,
        ]);

        return view('gateways.x402::pay', [
            'invoice' => $invoice,
            'total' => $total,
            'paymentUrl' => $paymentUrl,
            'paymentRef' => $paymentRef,
            'chain' => $chain,
            'token' => $token,
            'merchantWallet' => $merchantWallet,
        ]);
    }

    /**
     * Handle webhook callback from the x402 gateway.
     */
    public function handleWebhook(Request $request)
    {
        $payload = $request->all();
        $paymentRef = $payload['reference'] ?? '';
        $status = $payload['status'] ?? '';
        $txHash = $payload['transaction_hash'] ?? '';

        Log::info('x402 webhook received', [
            'reference' => $paymentRef,
            'status' => $status,
            'tx_hash' => $txHash,
        ]);

        // Extract invoice ID from payment reference
        if (!preg_match('/^pay_(\d+)_/', $paymentRef, $matches)) {
            return response()->json(['error' => 'Invalid reference'], 400);
        }

        $invoiceId = $matches[1];
        $invoice = Invoice::find($invoiceId);

        if (!$invoice) {
            return response()->json(['error' => 'Invoice not found'], 404);
        }

        if ($status === 'completed' || $status === 'confirmed') {
            // Mark invoice as paid
            ExtensionHelper::addPayment(
                $invoice,
                $txHash ?: $paymentRef,
                $payload['amount'] ?? $invoice->total,
                null,
                $payload
            );

            Log::info('x402 payment completed', [
                'invoice_id' => $invoiceId,
                'tx_hash' => $txHash,
            ]);

            return response()->json(['success' => true]);
        }

        if ($status === 'failed' || $status === 'expired') {
            Log::warning('x402 payment failed', [
                'invoice_id' => $invoiceId,
                'status' => $status,
            ]);
            return response()->json(['success' => true, 'status' => $status]);
        }

        return response()->json(['success' => true, 'status' => 'pending']);
    }
}
