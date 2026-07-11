/**
 * GenTech Email Agent — Cloudflare Email Worker
 * 
 * Handles inbound email routing:
 * 1. Parses incoming email (from, to, subject, body, attachments)
 * 2. Stores in KV for MCP server to read
 * 3. Stores attachments in R2
 * 4. Routes based on recipient (support@, hello@, etc.)
 */

export default {
  async email(message, env, ctx) {
    const from = message.from;
    const to = message.to;
    const subject = message.subject || '(no subject)';
    const text = message.rawText || '';
    const html = message.rawHtml || '';
    const now = Date.now();
    const emailId = `inbox:${now}`;

    // Parse recipient for routing
    const recipient = to.split('@')[0].toLowerCase();
    const timestamp = new Date(now).toISOString();

    // Build email record
    const record = {
      id: emailId,
      from,
      to,
      subject,
      text: text.substring(0, 10000), // cap at 10KB
      html: html.substring(0, 50000), // cap at 50KB
      recipient,
      timestamp,
      attachments: [],
      read: false,
    };

    // Store in KV (7 day TTL)
    await env.EMAIL_KV.put(emailId, JSON.stringify(record), {
      expirationTtl: 86400 * 7,
    });

    // Update inbox index
    const inboxIndex = JSON.parse(
      (await env.EMAIL_KV.get('inbox:index')) || '[]'
    );
    inboxIndex.unshift(emailId);
    // Keep last 100 emails in index
    if (inboxIndex.length > 100) inboxIndex.length = 100;
    await env.EMAIL_KV.put('inbox:index', JSON.stringify(inboxIndex));

    // Route based on recipient
    switch (recipient) {
      case 'support':
        await routeSupport(env, record);
        break;
      case 'hello':
        await routeHello(env, record);
        break;
      case 'billing':
        await routeBilling(env, record);
        break;
      default:
        // Catch-all: just store for Forge to read
        break;
    }

    console.log(`[Email] Received from ${from} to ${to} — ${subject}`);
  },
};

/**
 * Route support emails — flag as high priority
 */
async function routeSupport(env, record) {
  await env.EMAIL_KV.put(
    `priority:support:${record.id}`,
    JSON.stringify(record),
    { expirationTtl: 86400 * 3 }
  );
}

/**
 * Route hello/inquiries — general inbox
 */
async function routeHello(env, record) {
  // Just stored in main inbox, no special routing needed
}

/**
 * Route billing inquiries
 */
async function routeBilling(env, record) {
  await env.EMAIL_KV.put(
    `priority:billing:${record.id}`,
    JSON.stringify(record),
    { expirationTtl: 86400 * 7 }
  );
}
