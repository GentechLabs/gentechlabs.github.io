<?php
/**
 * Test harness for the x402 WHMCS/Blesta gateway port.
 *
 * Validates the core payment-URL generation logic shared by both modules
 * without requiring a full WHMCS/Blesta install. Extracts the URL-building
 * logic and asserts the generated x402 payment URLs are well-formed.
 */

$failures = 0;
$passes = 0;

function check($name, $cond, $detail = '')
{
    global $failures, $passes;
    if ($cond) {
        $passes++;
        echo "  PASS  $name\n";
    } else {
        $failures++;
        echo "  FAIL  $name  $detail\n";
    }
}

/**
 * Replicates the x402 payment URL builder (identical logic in both modules).
 */
function build_x402_url($gatewayUrl, $merchantWallet, $chain, $token, $amount, $invoiceId, $redirect)
{
    $paymentRef = 'pay_' . $invoiceId . '_' . uniqid();
    return rtrim($gatewayUrl, '/') . '/pay?' . http_build_query([
        'amount' => number_format((float)$amount, 2, '.', ''),
        'to' => $merchantWallet,
        'chain' => $chain,
        'token' => $token,
        'reference' => $paymentRef,
        'redirect' => $redirect,
        'receipt' => 'true',
    ]);
}

echo "x402 WHMCS/Blesta port — payment URL generation tests\n";
echo "======================================================\n";

// Test 1: default gateway URL, Solana USDC
$url = build_x402_url('https://api.gentechlabs.net/x402', '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU', 'solana', 'USDC', 25.00, 42, 'https://whmcs.example/viewinvoice.php?id=42');
check('default gateway URL', strpos($url, 'https://api.gentechlabs.net/x402/pay?') === 0, $url);
check('amount formatted 2dp', strpos($url, 'amount=25.00') !== false, $url);
check('merchant wallet present', strpos($url, 'to=7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU') !== false, $url);
check('chain=solana', strpos($url, 'chain=solana') !== false, $url);
check('token=USDC', strpos($url, 'token=USDC') !== false, $url);
check('receipt enabled', strpos($url, 'receipt=true') !== false, $url);
check('reference prefix pay_42_', preg_match('/reference=pay_42_[0-9a-f]+/', $url) === 1, $url);
check('redirect preserved', strpos($url, 'redirect=https%3A%2F%2Fwhmcs.example%2Fviewinvoice.php%3Fid%3D42') !== false, $url);

// Test 2: trailing slash on gateway URL is stripped
$url2 = build_x402_url('https://api.gentechlabs.net/x402/', '0x3d11...eCb', 'base', 'USDC', 9.99, 7, 'https://blesta.example/');
check('trailing slash stripped', strpos($url2, 'x402/pay?') !== false && strpos($url2, 'x402//pay') === false, $url2);
check('base chain', strpos($url2, 'chain=base') !== false, $url2);

// Test 3: EVM wallet + ETH token
$url3 = build_x402_url('https://api.gentechlabs.net/x402', '0x3d11...eCb', 'ethereum', 'ETH', 0.5, 99, 'https://whmcs.example/');
check('ethereum chain', strpos($url3, 'chain=ethereum') !== false, $url3);
check('ETH token', strpos($url3, 'token=ETH') !== false, $url3);
check('decimal amount 0.50', strpos($url3, 'amount=0.50') !== false, $url3);

// Test 4: integer amount
$url4 = build_x402_url('https://api.gentechlabs.net/x402', 'wallet', 'polygon', 'USDT', 100, 1, 'https://whmcs.example/');
check('integer amount 100.00', strpos($url4, 'amount=100.00') !== false, $url4);
check('polygon chain', strpos($url4, 'chain=polygon') !== false, $url4);
check('USDT token', strpos($url4, 'token=USDT') !== false, $url4);

// Test 5: reference regex used by both callbacks to extract invoice id
$ref = 'pay_42_abc123';
check('callback regex extracts invoice 42', preg_match('/^pay_(\d+)_/', $ref, $m) === 1 && $m[1] === '42', json_encode($m));
$refBad = 'not_a_payment';
check('callback regex rejects bad ref', preg_match('/^pay_(\d+)_/', $refBad) === 0, $refBad);

// Test 6: config.json is valid JSON with required settings
$config = json_decode(file_get_contents(__DIR__ . '/blesta/config.json'), true);
check('blesta config.json valid', is_array($config), json_last_error_msg());
check('blesta config has 4 settings', isset($config['settings']) && count($config['settings']) === 4, json_encode($config['settings'] ?? []));
$keys = array_column($config['settings'] ?? [], 'key');
check('has x402_gateway_url', in_array('x402_gateway_url', $keys), json_encode($keys));
check('has x402_merchant_wallet', in_array('x402_merchant_wallet', $keys), json_encode($keys));
check('has x402_chain', in_array('x402_chain', $keys), json_encode($keys));
check('has x402_token', in_array('x402_token', $keys), json_encode($keys));

echo "\n======================================================\n";
echo "RESULT: $passes passed, $failures failed\n";
exit($failures === 0 ? 0 : 1);
