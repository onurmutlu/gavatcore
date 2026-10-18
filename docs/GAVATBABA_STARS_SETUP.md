# Telegram Stars checkout (initial implementation)

Branch: `claude/gavatbaba-sales-engine-v2`

This is an **isolated Bot API module**, not the existing Telethon userbot. It is **disabled by default**. Do not enable public sales until product eligibility, webhook routing, fulfillment and refund handling are tested and approved.

## Required environment variables (never commit values)

- `GAVAT_STARS_ENABLED=true` only after readiness checklist
- `GAVAT_STARS_BOT_TOKEN` BotFather-issued token for a **Bot API** bot
- `GAVAT_STARS_WEBHOOK_SECRET` unpredictable ASCII string (>=32 chars)
- `GAVAT_STARS_DB` persistent writable disk location; SQLite is intended for initial single-instance testing only
- `GAVAT_STARS_TITLE` approved digital product title (1–32 characters)
- `GAVAT_STARS_DESCRIPTION` approved product description (1–255 characters)
- `GAVAT_STARS_PRICE` positive integer Telegram Stars amount

HTTPS POST `/api/stars/webhook` receives Bot API updates. Register the webhook via Telegram's `setWebhook` with `secret_token` set to the configured secret, and `allowed_updates=["message","pre_checkout_query"]`. Never place token or webhook secret in source, CLI history or logs.

Workflow:
1. Buyer voluntarily starts the Bot API bot via `/start` in their private chat.
2. A pending order is stored, then an XTR invoice is sent.
3. Telegram's pre-checkout query is accepted only for matching user, order and Stars amount.
4. Only `message.successful_payment`, received via the secret-protected webhook, records payment. Charge ID is unique. Duplicate successful events are idempotent.
5. **Fulfillment is deliberately not active.** The API response explicitly reports fulfillment pending.

## Readiness blockers

- Confirm BotFather token ownership, HTTPS webhook delivery, secrets rotation and real payment testing in Telegram's test environment.
- Introduce database-backed fulfillment outbox, idempotent delivery and refunds; reconcile abandoned orders.
- Move SQLite order storage to a migrated production datastore before multiple workers/containers.
- Ensure only owner-approved, legal, platform-permitted content is offered. No prohibited matchmaking or sexual services.
- Implement buyer support and `/paysupport` before public launch.
- Remove or disable legacy digital-product IBAN/Stripe DM prompts.
- Run `pytest gavatcore-api/tests/test_stars_sales.py -q` in the project environment.
- No live production payment was attempted or verified during implementation.

The existing `/api/payment/stars/invoice` remains a legacy stub; do not use it. The new Bot API webhook is `/api/stars/webhook`.
