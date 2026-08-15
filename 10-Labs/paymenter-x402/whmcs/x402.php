<?php
/**
 * x402 Crypto Gateway for WHMCS
 *
 * Accept gasless crypto payments (USDC/USDT/SOL/ETH) via the x402 protocol.
 * Powered by GenTech Labs. MIT License.
 *
 * WHMCS gateway module structure:
 *   modules/gateways/x402/x402.php          - module definition + config
 *   modules/gateways/x402/x402create.php    - payment page (redirect to x402)
 *   modules/gateways/x402/x402callback.php  - webhook callback (marks invoice paid)
 *   modules/gateways/x402/x402whmcs.php     - client area redirect helper
 *
 * Install: copy the `x402` folder into WHMCS `modules/gateways/`, then
 * activate in Setup > Payments > Payment Gateways.
 */

if (!defined('WHMCS')) {
    die('This file cannot be accessed directly');
}

/**
 * Define the gateway module metadata.
 */
function x402_config()
{
    return [
        'FriendlyName' => [
            'Type' => 'System',
            'Value' => 'x402 Crypto Gateway',
        ],
        'x402GatewayUrl' => [
            'FriendlyName' => 'x402 Gateway URL',
            'Type' => 'text',
            'Size' => '50',
            'Default' => 'https://api.gentechlabs.net/x402',
            'Description' => 'Your x402 gateway endpoint (default: GenTech public gateway)',
        ],
        'x402MerchantWallet' => [
            'FriendlyName' => 'Merchant Wallet Address',
            'Type' => 'text',
            'Size' => '60',
            'Description' => 'Wallet where payments settle (Solana or EVM address)',
        ],
        'x402Chain' => [
            'FriendlyName' => 'Blockchain Network',
            'Type' => 'dropdown',
            'Options' => 'solana,base,ethereum,polygon',
            'Description' => 'Which chain to settle on',
        ],
        'x402Token' => [
            'FriendlyName' => 'Accepted Token',
            'Type' => 'dropdown',
            'Options' => 'USDC,USDT,SOL,ETH',
            'Description' => 'Which token to accept',
        ],
        'x402ApiKey' => [
            'FriendlyName' => 'x402 API Key',
            'Type' => 'text',
            'Size' => '50',
            'Description' => 'Optional API key for private gateways',
        ],
    ];
}

/**
 * Client area payment page — build the x402 payment URL and redirect.
 *
 * @param array $params Gateway configuration params
 * @return string HTML (auto-submit form) or redirect
 */
function x402_link($params)
{
    $gatewayUrl = $params['x402GatewayUrl'] ?: 'https://api.gentechlabs.net/x402';
    $merchantWallet = $params['x402MerchantWallet'];
    $chain = $params['x402Chain'] ?: 'solana';
    $token = $params['x402Token'] ?: 'USDC';

    // WHMCS invoice details
    $invoiceId = $params['invoiceid'];
    $amount = $params['amount'];
    $currency = $params['currency'];

    // Unique payment reference
    $paymentRef = 'pay_' . $invoiceId . '_' . uniqid();

    // Build x402 payment URL
    $paymentUrl = rtrim($gatewayUrl, '/') . '/pay?' . http_build_query([
        'amount' => number_format((float)$amount, 2, '.', ''),
        'to' => $merchantWallet,
        'chain' => $chain,
        'token' => $token,
        'reference' => $paymentRef,
        'redirect' => $params['systemurl'] . 'viewinvoice.php?id=' . $invoiceId . '&paymentsuccess=true',
        'receipt' => 'true',
    ]);

    // Auto-submit form that redirects the customer to the x402 payment page
    $code = '<form method="post" action="' . htmlspecialchars($paymentUrl) . '" id="x402-pay-form">';
    $code .= '<input type="submit" value="Pay with Crypto (x402)" class="btn btn-primary" />';
    $code .= '</form>';
    $code .= '<script>document.getElementById("x402-pay-form").submit();</script>';

    return $code;
}
