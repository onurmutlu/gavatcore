"""Isolated Telegram Stars Bot API checkout for a single approved digital product.
Disabled by default. Does not use Telethon or trust client-reported payments.
"""
import os
import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

import httpx
from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter()
DB_PATH = lambda: os.environ.get("GAVAT_STARS_DB", "stars_orders.sqlite3")


def enabled():
    return os.environ.get("GAVAT_STARS_ENABLED") == "true"


def product():
    price = int(os.environ.get("GAVAT_STARS_PRICE", "0"))
    title = os.environ.get("GAVAT_STARS_TITLE", "")
    description = os.environ.get("GAVAT_STARS_DESCRIPTION", "")
    if not 1 <= price <= 100000 or not 1 <= len(title) <= 32 or not 1 <= len(description) <= 255:
        raise ValueError("Configure approved product title, description and positive integer Stars price")
    return title, description, price


def config():
    if not enabled():
        raise HTTPException(503, "Stars checkout disabled")
    token = os.environ.get("GAVAT_STARS_BOT_TOKEN", "")
    secret = os.environ.get("GAVAT_STARS_WEBHOOK_SECRET", "")
    if not token or len(secret) < 32 or not all(32 <= ord(c) < 127 for c in secret):
        raise HTTPException(503, "Stars credentials not configured")
    try:
        product()
    except ValueError:
        raise HTTPException(503, "Stars product not configured")
    return token, secret


@contextmanager
def database():
    path = Path(DB_PATH())
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    try:
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("""CREATE TABLE IF NOT EXISTS stars_orders (
          order_id TEXT PRIMARY KEY,
          telegram_user_id INTEGER NOT NULL,
          amount INTEGER NOT NULL CHECK(amount > 0),
          state TEXT NOT NULL CHECK(state IN ('pending','paid')),
          telegram_charge_id TEXT UNIQUE,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          paid_at TEXT
        )""")
        yield db
    finally:
        db.close()


def new_order(user_id, amount):
    order_id = uuid.uuid4().hex
    with database() as db:
        db.execute("INSERT INTO stars_orders(order_id,telegram_user_id,amount,state) VALUES (?,?,?,'pending')",
                   (order_id, user_id, amount))
    return order_id


def lookup(order_id):
    with database() as db:
        return db.execute("SELECT telegram_user_id,amount,state,telegram_charge_id FROM stars_orders WHERE order_id=?",
                          (order_id,)).fetchone()


def verify_checkout(user_id, payload, currency, amount):
    record = lookup(payload) if isinstance(payload, str) else None
    return bool(record and record[0] == user_id and record[1] == amount and
                record[2] == "pending" and currency == "XTR")


def record_success(user_id, payload, currency, amount, charge_id):
    if not isinstance(charge_id, str) or not charge_id:
        return False
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        record = db.execute("SELECT telegram_user_id,amount,state,telegram_charge_id FROM stars_orders WHERE order_id=?",
                            (payload,)).fetchone()
        if not record or record[0] != user_id or record[1] != amount or currency != "XTR":
            db.rollback()
            return False
        if record[2] == "paid":
            db.rollback()
            return record[3] == charge_id
        try:
            db.execute("""UPDATE stars_orders SET state='paid', telegram_charge_id=?, paid_at=CURRENT_TIMESTAMP
                          WHERE order_id=? AND state='pending'""", (charge_id, payload))
            db.commit()
            return True
        except sqlite3.IntegrityError:
            db.rollback()
            return False


async def telegram_api(token, method, payload):
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.post(f"https://api.telegram.org/bot{token}/{method}", json=payload)
        response.raise_for_status()
        body = response.json()
        if not body.get("ok"):
            raise RuntimeError("Telegram API failed")
        return body["result"]


@router.post("/webhook")
async def stars_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    token, secret = config()
    if not x_telegram_bot_api_secret_token or not secrets.compare_digest(x_telegram_bot_api_secret_token, secret):
        raise HTTPException(403, "Invalid Telegram webhook secret")
    update = await request.json()

    message = update.get("message", {})
    user = message.get("from", {})
    user_id = user.get("id")
    chat_id = message.get("chat", {}).get("id")

    if message.get("text") == "/start" and isinstance(user_id, int) and chat_id == user_id:
        title, description, price = product()
        order_id = new_order(user_id, price)
        await telegram_api(token, "sendInvoice", {
            "chat_id": chat_id, "title": title, "description": description,
            "payload": order_id, "provider_token": "", "currency": "XTR",
            "prices": [{"label": title, "amount": price}],
            "start_parameter": f"order_{order_id}"
        })
        return {"ok": True}

    checkout = update.get("pre_checkout_query")
    if checkout:
        buyer_id = checkout.get("from", {}).get("id")
        ok = verify_checkout(buyer_id, checkout.get("invoice_payload"),
                             checkout.get("currency"), checkout.get("total_amount"))
        await telegram_api(token, "answerPreCheckoutQuery", {
            "pre_checkout_query_id": checkout["id"], "ok": ok,
            **({} if ok else {"error_message": "Order unavailable or price mismatch"})
        })
        return {"ok": True}

    successful = message.get("successful_payment")
    if successful and isinstance(user_id, int):
        accepted = record_success(user_id, successful.get("invoice_payload"),
                                  successful.get("currency"), successful.get("total_amount"),
                                  successful.get("telegram_payment_charge_id"))
        if not accepted:
            raise HTTPException(409, "Payment does not match a pending order")
        # DO NOT fulfill here. Payment is persisted; fulfillment needs a retry-safe outbox.
        return {"ok": True, "payment_recorded": True, "fulfillment": "pending"}
    return {"ok": True}
