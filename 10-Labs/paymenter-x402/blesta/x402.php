<?php
/**
 * x402 Crypto Gateway for Blesta
 *
 * Accept gasless crypto payments (USDC/USDT/SOL/ETH) via the x402 protocol.
 * Powered by GenTech Labs. MIT License.
 *
 * Blesta gateway module structure:
 *   components/gateways/merchant/x402/x402.php
 *   components/gateways/merchant/x402/x402_pay.php   (payment page)
 *   components/gateways/merchant/x402/x402_callback.php (webhook)
 *   components/gateways/merchant/x402/config.json
 *
 * Install: copy the `x402` folder into Blesta `components/gateways/merchant/`,
 * then activate in Settings > Payment Gateways.
 */

require_once dirname(__FILE__) . DIRECTORY_SEPARATOR . 'x402_pay.php';

/**
 * x402 merchant gateway for Blesta.
 */
class X402 extends MerchantGateway
{
    /**
     * @var array An array of meta data for this gateway
     */
    private $meta;

    /**
     * Construct a new merchant gateway.
     */
    public function __construct()
    {
        $this->loadConfig(dirname(__FILE__) . DIRECTORY_SEPARATOR . 'config.json');

        // Load components required by this module
        Loader::loadComponents($this, ['Input']);

        // Load the language required by this module
        Language::loadLang('x402', null, dirname(__FILE__) . DIRECTORY_SEPARATOR . 'language' . DIRECTORY_SEPARATOR);
    }

    /**
     * Sets the meta data for this gateway.
     *
     * @param array $meta An array of meta data to set
     */
    public function setMeta(array $meta = null)
    {
        $this->meta = $meta;
    }

    /**
     * Returns all fields used when setting up a gateway.
     *
     * @return array An array of fields
     */
    public function getSettings(array $meta = null)
    {
        $this->view = $this->makeView('settings', 'default', str_replace(ROOTWEBDIR, '', dirname(__FILE__)));
        $this->view->setDefaultView(ROOTWEBDIR);

        // Load the helpers required for this view
        Loader::loadHelpers($this, ['Form', 'Html']);

        $this->view->set('meta', $meta);

        return $this->view->fetch();
    }

    /**
     * Validates the given meta data.
     *
     * @param array $meta An array of meta data to validate
     * @return array The meta data to be set
     */
    public function editSettings(array $meta)
    {
        $rules = [
            'x402_gateway_url' => [
                'valid' => [
                    'rule' => ['matches', '/^https?:\/\/.+/'],
                    'message' => Language::_('x402.!error.x402_gateway_url.valid', true),
                ],
            ],
            'x402_merchant_wallet' => [
                'empty' => [
                    'rule' => 'isEmpty',
                    'negate' => true,
                    'message' => Language::_('x402.!error.x402_merchant_wallet.empty', true),
                ],
            ],
        ];

        $this->Input->setRules($rules);

        $this->Input->validates($meta);
        return $meta;
    }

    /**
     * Returns the meta data for this gateway.
     *
     * @return array An array of meta data
     */
    public function getMeta()
    {
        return $this->meta;
    }

    /**
     * Build the x402 payment URL for a given invoice.
     *
     * @param array $contact_info An array of contact info
     * @param float $amount The amount to charge
     * @param array $invoice_amounts An array of invoice amounts
     * @param string $currency_iso The ISO 4217 currency code
     * @return string The x402 payment URL
     */
    private function buildPaymentUrl(array $contact_info, $amount, array $invoice_amounts, $currency_iso)
    {
        $gatewayUrl = $this->meta['x402_gateway_url'] ?? 'https://api.gentechlabs.net/x402';
        $merchantWallet = $this->meta['x402_merchant_wallet'] ?? '';
        $chain = $this->meta['x402_chain'] ?? 'solana';
        $token = $this->meta['x402_token'] ?? 'USDC';

        // Build a unique reference from the first invoice id
        $invoiceId = isset($invoice_amounts[0]['id']) ? $invoice_amounts[0]['id'] : 'inv';
        $paymentRef = 'pay_' . $invoiceId . '_' . uniqid();

        return rtrim($gatewayUrl, '/') . '/pay?' . http_build_query([
            'amount' => number_format((float)$amount, 2, '.', ''),
            'to' => $merchantWallet,
            'chain' => $chain,
            'token' => $token,
            'reference' => $paymentRef,
            'receipt' => 'true',
        ]);
    }

    /**
     * Charge a credit card (not supported — x402 is a wallet payment).
     *
     * @param array $card_info An array of card info
     * @param array $amounts An array of amounts
     * @param array $invoice_amounts An array of invoice amounts
     * @return array An array of transaction data
     */
    public function process(array $card_info, array $amounts, array $invoice_amounts = null)
    {
        // x402 is a wallet-based payment, not a card charge.
        // Return a redirect to the x402 payment page.
        $this->Input->setErrors($this->Input->errors());
        return [
            'status' => 'pending',
            'reference_id' => null,
            'transaction_id' => null,
            'message' => 'Redirecting to x402 payment',
        ];
    }

    /**
     * Validate a payment (used for off-site gateways).
     *
     * @param array $get The GET data
     * @param array $post The POST data
     * @param string $currency The currency code
     * @param int $amount The amount
     * @param array $invoice_amounts An array of invoice amounts
     * @return array An array of transaction data
     */
    public function validate(array $get, array $post, $currency, $amount, array $invoice_amounts = null)
    {
        $status = $post['status'] ?? ($get['status'] ?? '');
        $txHash = $post['transaction_hash'] ?? ($get['transaction_hash'] ?? '');
        $reference = $post['reference'] ?? ($get['reference'] ?? '');

        if (in_array($status, ['completed', 'confirmed'], true)) {
            return [
                'status' => 'approved',
                'reference_id' => $reference,
                'transaction_id' => $txHash ?: $reference,
                'message' => 'Payment approved',
            ];
        }

        return [
            'status' => 'declined',
            'reference_id' => $reference,
            'transaction_id' => null,
            'message' => 'Payment not completed',
        ];
    }

    /**
     * Refund a payment (not supported for x402 wallet payments).
     *
     * @param string $reference_id The reference ID for the previously authorized transaction
     * @param string $transaction_id The transaction ID for the previously authorized transaction
     * @param float $amount The amount to refund
     * @return array An array of transaction data
     */
    public function refund($reference_id, $transaction_id, $amount)
    {
        return [
            'status' => 'declined',
            'reference_id' => $reference_id,
            'transaction_id' => null,
            'message' => 'Refunds not supported for x402 wallet payments',
        ];
    }
}
