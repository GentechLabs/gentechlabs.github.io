<?php
/**
 * x402 Crypto Gateway for Blesta — Payment Page
 *
 * Renders the "Pay with Crypto (x402)" button and redirects the customer
 * to the x402 payment page.
 */

/**
 * x402 payment page class.
 */
class X402Pay extends MerchantGateway
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
        Loader::loadComponents($this, ['Input']);
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
     * Returns the meta data for this gateway.
     *
     * @return array An array of meta data
     */
    public function getMeta()
    {
        return $this->meta;
    }

    /**
     * Build the x402 payment URL.
     *
     * @param array $contact_info An array of contact info
     * @param float $amount The amount to charge
     * @param array $invoice_amounts An array of invoice amounts
     * @param string $currency_iso The ISO 4217 currency code
     * @return string The x402 payment URL
     */
    public function buildPaymentUrl(array $contact_info, $amount, array $invoice_amounts, $currency_iso)
    {
        $gatewayUrl = $this->meta['x402_gateway_url'] ?? 'https://api.gentechlabs.net/x402';
        $merchantWallet = $this->meta['x402_merchant_wallet'] ?? '';
        $chain = $this->meta['x402_chain'] ?? 'solana';
        $token = $this->meta['x402_token'] ?? 'USDC';

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
}
