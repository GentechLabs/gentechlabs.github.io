<?php

use Illuminate\Support\Facades\Route;
use Paymenter\Extensions\Gateways\X402\X402;

/*
|--------------------------------------------------------------------------
| x402 Gateway Routes
|--------------------------------------------------------------------------
|
| Webhook endpoint for the x402 gateway to notify Paymenter of payment
| status changes (completed, failed, expired).
|
*/

Route::post('/gateways/x402/webhook', [X402::class, 'handleWebhook'])
    ->name('gateways.x402.webhook');
