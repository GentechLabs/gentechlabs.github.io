<div class="max-w-lg mx-auto mt-8 p-6 bg-gray-900 rounded-lg border border-gray-700">
    <div class="text-center mb-6">
        <div class="text-2xl font-bold text-white mb-2">Pay with Crypto</div>
        <div class="text-sm text-gray-400">
            Powered by <span class="text-cyan-400 font-semibold">x402</span>
            <span class="text-gray-500"> // </span>
            <span class="text-pink-400 font-semibold">GenTech</span>
        </div>
    </div>

    <div class="bg-gray-800 rounded-lg p-4 mb-6">
        <div class="flex justify-between text-sm mb-2">
            <span class="text-gray-400">Invoice #{{ $invoice->id }}</span>
            <span class="text-white font-bold">{{ number_format($total, 2) }} USD</span>
        </div>
        <div class="flex justify-between text-sm">
            <span class="text-gray-400">Network</span>
            <span class="text-cyan-400 font-medium">{{ strtoupper($chain) }}</span>
        </div>
        <div class="flex justify-between text-sm">
            <span class="text-gray-400">Token</span>
            <span class="text-yellow-400 font-medium">{{ $token }}</span>
        </div>
        <div class="flex justify-between text-sm mt-2 pt-2 border-t border-gray-700">
            <span class="text-gray-400">Merchant</span>
            <span class="text-gray-300 text-xs font-mono truncate max-w-[200px]">{{ $merchantWallet }}</span>
        </div>
    </div>

    <div id="x402-payment-container" class="mb-4">
        <div id="x402-loading" class="text-center py-8">
            <div class="inline-block w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-2"></div>
            <div class="text-gray-400 text-sm">Preparing payment request...</div>
        </div>
        <div id="x402-qr" class="hidden text-center py-4">
            <div class="text-gray-300 text-sm mb-4">Scan with your wallet app or click to pay</div>
            <div id="x402-qr-code" class="inline-block bg-white p-4 rounded-lg mb-4"></div>
            <div class="text-gray-400 text-xs font-mono break-all px-4" id="x402-payment-url"></div>
        </div>
        <div id="x402-error" class="hidden text-center py-8">
            <div class="text-red-400 text-lg mb-2">⚠️ Payment Error</div>
            <div class="text-gray-400 text-sm" id="x402-error-message">Could not create payment request.</div>
            <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 text-sm">
                Try Again
            </button>
        </div>
    </div>

    <div class="text-center">
        <a href="{{ route('invoices.show', $invoice) }}"
           class="text-sm text-gray-500 hover:text-gray-300 transition-colors">
            ← Back to Invoice
        </a>
    </div>

    <div class="mt-6 pt-4 border-t border-gray-700 text-center">
        <div class="text-xs text-gray-500">
            <span class="text-cyan-400">x402</span> — gasless, instant, agent-to-agent payments.
            <a href="https://gentechlabs.net" target="_blank" class="text-pink-400 hover:underline">GenTech Labs</a>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<script>
(function() {
    const paymentUrl = "{{ $paymentUrl }}";
    const loadingEl = document.getElementById('x402-loading');
    const qrEl = document.getElementById('x402-qr');
    const errorEl = document.getElementById('x402-error');
    const qrCodeEl = document.getElementById('x402-qr-code');
    const urlEl = document.getElementById('x402-payment-url');

    if (!paymentUrl) {
        loadingEl.classList.add('hidden');
        errorEl.classList.remove('hidden');
        document.getElementById('x402-error-message').textContent = 'No payment URL generated.';
        return;
    }

    // Generate QR code
    try {
        new QRCode(qrCodeEl, {
            text: paymentUrl,
            width: 200,
            height: 200,
            colorDark: '#000000',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.H
        });
        urlEl.textContent = paymentUrl;
        loadingEl.classList.add('hidden');
        qrEl.classList.remove('hidden');
    } catch (e) {
        loadingEl.classList.add('hidden');
        errorEl.classList.remove('hidden');
        document.getElementById('x402-error-message').textContent = 'Failed to generate QR code.';
    }

    // Poll for payment status
    let pollCount = 0;
    const maxPolls = 120; // 10 minutes at 5s intervals
    const pollInterval = setInterval(function() {
        pollCount++;
        if (pollCount > maxPolls) {
            clearInterval(pollInterval);
            return;
        }
        fetch('{{ route("invoices.show", $invoice) }}?checkPayment=true')
            .then(r => r.text())
            .then(html => {
                if (html.includes('paid') || html.includes('Paid') || html.includes('PAID')) {
                    clearInterval(pollInterval);
                    window.location.reload();
                }
            })
            .catch(() => {});
    }, 5000);
})();
</script>
