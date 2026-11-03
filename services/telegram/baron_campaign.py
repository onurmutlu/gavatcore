"""Explicitly configured Baron campaigns and persistent Stars orders."""
import asyncio
import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[2] / "config/baron_campaign.json"
DB = CONFIG.parent.parent / "data/baron_campaign.sqlite3"
log = logging.getLogger(__name__)


def load_config(path=CONFIG):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    profile_about = config.get("profile_about", "")
    if not isinstance(profile_about, str) or not 1 <= len(profile_about) <= 70:
        raise ValueError("Telegram profil açıklaması 1–70 karakter olmalı")
    if config.get("adaptive", {}).get("enabled"):
        from services.telegram.baron_adaptive import validate_settings
        validate_settings(config["adaptive"])
    campaign = config["broadcast"]
    if campaign["interval_seconds"] < 3600:
        raise ValueError("Grup paylaşım aralığı en az 3600 saniye olmalı")
    if not 0 <= campaign.get("initial_delay_seconds", 30) <= 3600:
        raise ValueError("İlk gönderim gecikmesi 0–3600 saniye olmalı")
    if campaign.get("send_gap_seconds", 90) < 60:
        raise ValueError("Gruplar arası gönderim aralığı en az 60 saniye olmalı")
    if campaign["enabled"] and (not campaign["groups"] or not campaign["messages"]):
        raise ValueError("İzinli grup listesi ve mesaj seti gerekli")
    for group in campaign["groups"]:
        if group.get("permission_confirmed") is not True:
            raise ValueError("Her grup için paylaşım izni doğrulanmalı")
        if not isinstance(group.get("id"), int) or group["id"] >= 0:
            raise ValueError("Grup ID negatif bir Telegram chat ID olmalı")
    for message in campaign["messages"]:
        if not isinstance(message, str) or not message.strip() or len(message) > 4096:
            raise ValueError("Grup mesajı 1–4096 karakter olmalı")
    for key, product in config["products"].items():
        if not key or not isinstance(product["stars"], int) or product["stars"] < 1:
            raise ValueError("Geçerli ürün ID ve Stars fiyatı gerekli")
        if not 1 <= len(product["title"]) <= 32 or not 1 <= len(product["description"]) <= 255:
            raise ValueError("Ürün başlığı veya açıklaması geçersiz")
        if not 1 <= len(product["content"]) <= 4096:
            raise ValueError("Teslim edilecek metin veya bağlantı gerekli (1–4096 karakter)")
        days = product.get("license_days")
        if "license_days" in product and (
            not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= 3650
        ):
            raise ValueError("license_days 1–3650 arasında tam sayı olmalı")
    if config["sales_enabled"] and (not config["products"] or not config["support"]):
        raise ValueError("Satış için ürün ve destek iletişimi gerekli")
    return config


class Store:
    def __init__(self, path=DB):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS schedule(chat INTEGER PRIMARY KEY, next_at REAL, cursor INTEGER);
            CREATE TABLE IF NOT EXISTS orders(
                id TEXT PRIMARY KEY, user INTEGER, stars INTEGER, content TEXT,
                created REAL, charge TEXT UNIQUE, delivered INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY, value INTEGER);
            CREATE TABLE IF NOT EXISTS dm_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                content TEXT NOT NULL,
                created REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS dm_history_user_id ON dm_history(user,id);
            CREATE TABLE IF NOT EXISTS payment_issues(
                charge TEXT PRIMARY KEY, user INTEGER, stars INTEGER, payload TEXT,
                reason TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS delivery_state(
                order_id TEXT PRIMARY KEY, attempts INTEGER DEFAULT 0, last_attempt REAL);
            CREATE TABLE IF NOT EXISTS refunds(charge TEXT PRIMARY KEY, created REAL);
            CREATE TABLE IF NOT EXISTS license_grants(
                charge TEXT PRIMARY KEY, user INTEGER, days INTEGER, created REAL);
        """)
        # Older databases predate paid licenses; add the column in place, keeping their orders.
        if "license_days" not in {row[1] for row in self.db.execute("PRAGMA table_info(orders)")}:
            with self.db:
                self.db.execute("ALTER TABLE orders ADD COLUMN license_days INTEGER")

    def record_issue(self, payment, user, reason):
        """Keep a payment the operator must look at (refund or manual delivery)."""
        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO payment_issues VALUES(?,?,?,?,?,?)",
                (payment.get("telegram_payment_charge_id"), user, payment.get("total_amount"),
                 payment.get("invoice_payload"), reason, time.time()),
            )

    def is_refunded(self, charge):
        return bool(charge) and self.db.execute("SELECT 1 FROM refunds WHERE charge=?", (charge,)).fetchone() is not None

    def order(self, user, product):
        payload = uuid.uuid4().hex
        with self.db:
            self.db.execute("INSERT INTO orders(id,user,stars,content,created,license_days) VALUES(?,?,?,?,?,?)",
                            (payload, user, product["stars"], product["content"], time.time(),
                             product.get("license_days")))
        return payload

    def validate(self, payment, user, checkout=False):
        row = self.db.execute("SELECT * FROM orders WHERE id=?", (payment["invoice_payload"],)).fetchone()
        if not row or row["user"] != user or payment["currency"] != "XTR" or payment["total_amount"] != row["stars"]:
            return None
        if checkout and (row["charge"] or time.time() - row["created"] > 3600):
            return None
        return row

    def dm_context(self, user, limit=24):
        rows = self.db.execute(
            "SELECT role,content FROM dm_history WHERE user=? ORDER BY id DESC LIMIT ?",
            (str(user), limit),
        ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def add_dm(self, user, role, content, retention_days=30, max_messages=40):
        if role not in ("user", "assistant"):
            raise ValueError("DM rolü user veya assistant olmalı")
        with self.db:
            self.db.execute(
                "INSERT INTO dm_history(user,role,content,created) VALUES(?,?,?,?)",
                (str(user), role, content[:4000], time.time()),
            )
            self.db.execute(
                "DELETE FROM dm_history WHERE created<?",
                (time.time() - retention_days * 86400,),
            )
            self.db.execute(
                "DELETE FROM dm_history WHERE user=? AND id NOT IN "
                "(SELECT id FROM dm_history WHERE user=? ORDER BY id DESC LIMIT ?)",
                (str(user), str(user), max_messages),
            )


async def broadcast(client, config, store, dry_run=False, engine=None, generate=None):
    from telethon.errors import FloodWaitError
    campaign = config["broadcast"]
    if not campaign["enabled"] or dry_run:
        return
    initial_delay = campaign.get("initial_delay_seconds", 30)
    send_gap = campaign.get("send_gap_seconds", 90)
    while True:
        now = time.time()
        with store.db:
            store.db.execute(
                "INSERT OR REPLACE INTO state VALUES('campaign_heartbeat',?)",
                (int(now),),
            )
        global_row = store.db.execute(
            "SELECT value FROM state WHERE key='campaign_next_send'"
        ).fetchone()
        if global_row and global_row["value"] > now:
            await asyncio.sleep(min(30, global_row["value"] - now))
            continue
        sent_this_pass = False
        for index, group in enumerate(campaign["groups"]):
            chat = group["id"]
            row = store.db.execute("SELECT * FROM schedule WHERE chat=?", (chat,)).fetchone()
            now = time.time()
            if row is None:
                # Stagger a new campaign so startup cannot blast every group at once.
                with store.db:
                    store.db.execute(
                        "INSERT INTO schedule VALUES(?,?,?)",
                        (chat, now + initial_delay + index * send_gap, 0),
                    )
                continue
            if row and row["next_at"] > now:
                continue
            cursor = row["cursor"] if row else 0
            # Reserve before sending: a restart or uncertain network result must not spam.
            with store.db:
                store.db.execute("INSERT OR REPLACE INTO schedule VALUES(?,?,?)",
                                 (chat, now + campaign["interval_seconds"], cursor))
            try:
                entity = await client.get_entity(chat)
                if not (getattr(entity, "megagroup", False) or entity.__class__.__name__ == "Chat"):
                    raise ValueError("Hedef bir grup değil")
                if config.get("adaptive", {}).get("enabled"):
                    from services.telegram.baron_adaptive import recent_context
                    if engine is None or generate is None:
                        raise ValueError("Adaptif motor veya GPT üreticisi eksik")
                    context = await recent_context(client, entity, config["adaptive"])
                    selection = await engine.choose(chat, context, generate)
                    if selection is None:
                        log.info("Baron paylaşımı atlandı: bağlam/üretim uygun değil, chat=%s", chat)
                        continue
                    sent = await client.send_message(entity, selection.text)
                    engine.record_sent(chat, sent.id, selection)
                else:
                    await client.send_message(entity, campaign["messages"][cursor % len(campaign["messages"])])
                with store.db:
                    store.db.execute("UPDATE schedule SET cursor=? WHERE chat=?", (cursor + 1, chat))
                    store.db.execute(
                        "INSERT OR REPLACE INTO state VALUES('campaign_next_send',?)",
                        (int(time.time() + send_gap),),
                    )
                sent_this_pass = True
            except FloodWaitError as exc:
                with store.db:
                    store.db.execute("UPDATE schedule SET next_at=MAX(next_at,?)", (time.time() + exc.seconds,))
                await asyncio.sleep(exc.seconds)
            except Exception as exc:
                log.warning("Baron grup gönderimi başarısız: chat=%s error=%s", chat, type(exc).__name__)
            if sent_this_pass:
                break
        await asyncio.sleep(30)


def campaign_report(config, store):
    campaign = config["broadcast"]
    source_rows = store.db.execute(
        "SELECT source, COUNT(*) count, COALESCE(SUM(replies),0) replies, "
        "COALESCE(SUM(negative),0) negative FROM adaptive_posts GROUP BY source"
    ).fetchall()
    schedules = store.db.execute(
        "SELECT COUNT(*) total, SUM(CASE WHEN cursor>0 THEN 1 ELSE 0 END) touched, "
        "MIN(next_at) next_at FROM schedule"
    ).fetchone()
    recent = store.db.execute(
        "SELECT chat,message,source,template_id,topic,sent,replies,negative "
        "FROM adaptive_posts ORDER BY sent DESC LIMIT 10"
    ).fetchall()
    heartbeat_row = store.db.execute(
        "SELECT value FROM state WHERE key='campaign_heartbeat'"
    ).fetchone()
    heartbeat = heartbeat_row["value"] if heartbeat_row else None
    dm_row = store.db.execute(
        "SELECT COUNT(*) messages, COUNT(DISTINCT user) users FROM dm_history"
    ).fetchone()
    return {
        "enabled": campaign["enabled"],
        "active": bool(campaign["enabled"] and heartbeat and time.time() - heartbeat < 90),
        "last_heartbeat_at": heartbeat,
        "configured_groups": len(campaign["groups"]),
        "interval_seconds": campaign["interval_seconds"],
        "send_gap_seconds": campaign.get("send_gap_seconds", 90),
        "scheduled_groups": schedules["total"] or 0,
        "groups_with_successful_posts": schedules["touched"] or 0,
        "next_scheduled_at": schedules["next_at"],
        "sources": {row["source"]: {"posts": row["count"], "replies": row["replies"], "negative": row["negative"]} for row in source_rows},
        "dm_memory": {"users": dm_row["users"], "messages": dm_row["messages"]},
        "recent_posts": [dict(row) for row in recent],
    }


class StarsShop:
    def __init__(self, api, config, store, licenses=None):
        """licenses: object with extend_license(user_id, days) / deactivate_license(user_id),
        normally core.license_checker.LicenseChecker. Required for products with license_days."""
        self.api, self.config, self.store, self.licenses = api, config, store, licenses
        if licenses is None and any("license_days" in p for p in config["products"].values()):
            raise ValueError("license_days olan ürünler için lisans yöneticisi gerekli")

    MAX_DELIVERY_ATTEMPTS = 5
    DELIVERY_RETRY_SECONDS = 300

    def grant_license(self, row):
        """Activate or extend the buyer's license once per paid charge (idempotent).

        Extends first and records the grant after: a crash in between can at worst give one
        extra period on replay, never a paid buyer without a license. Raises on failure so
        the caller counts it as a failed attempt and retries later."""
        days = row["license_days"]
        if not days or self.store.is_refunded(row["charge"]):
            return
        if self.store.db.execute("SELECT 1 FROM license_grants WHERE charge=?", (row["charge"],)).fetchone():
            return
        self.licenses.extend_license(row["user"], days)
        with self.store.db:
            self.store.db.execute("INSERT OR IGNORE INTO license_grants VALUES(?,?,?,?)",
                                  (row["charge"], row["user"], days, time.time()))
        log.info("Lisans etkinleştirildi: user=%s days=%s order=%s", row["user"], days, row["id"])

    async def deliver(self, row):
        if self.store.is_refunded(row["charge"]):
            return
        self.grant_license(row)
        if row["delivered"]:
            return
        await self.api("sendMessage", chat_id=row["user"], text=row["content"], protect_content=True)
        with self.store.db:
            self.store.db.execute("UPDATE orders SET delivered=1 WHERE id=?", (row["id"],))

    async def try_deliver(self, row):
        """Deliver without letting one unreachable buyer block the whole update queue.

        The paid charge is already stored, so a failure here is retried later by
        redeliver() or by the buyer's /orders command instead of raising."""
        try:
            await self.deliver(row)
        except Exception as exc:
            with self.store.db:
                self.store.db.execute(
                    "INSERT INTO delivery_state(order_id,attempts,last_attempt) VALUES(?,1,?) "
                    "ON CONFLICT(order_id) DO UPDATE SET attempts=attempts+1, last_attempt=excluded.last_attempt",
                    (row["id"], time.time()),
                )
            log.warning("Stars teslimatı başarısız: order=%s error=%s", row["id"], type(exc).__name__)

    async def redeliver(self, now=None):
        """Retry paid-but-undelivered orders; after too many failures hand them to the operator."""
        now = time.time() if now is None else now
        rows = self.store.db.execute(
            "SELECT o.* FROM orders o LEFT JOIN delivery_state d ON d.order_id=o.id "
            "WHERE o.charge IS NOT NULL "
            "AND (o.delivered=0 OR (o.license_days IS NOT NULL "
            "AND NOT EXISTS (SELECT 1 FROM license_grants g WHERE g.charge=o.charge))) "
            "AND NOT EXISTS (SELECT 1 FROM refunds r WHERE r.charge=o.charge) "
            "AND COALESCE(d.attempts,0)<? AND COALESCE(d.last_attempt,0)<=?",
            (self.MAX_DELIVERY_ATTEMPTS, now - self.DELIVERY_RETRY_SECONDS),
        ).fetchall()
        for row in rows:
            await self.try_deliver(row)
            state = self.store.db.execute(
                "SELECT attempts FROM delivery_state WHERE order_id=?", (row["id"],)
            ).fetchone()
            if state and state["attempts"] >= self.MAX_DELIVERY_ATTEMPTS:
                self.store.record_issue(
                    {"telegram_payment_charge_id": row["charge"], "total_amount": row["stars"],
                     "invoice_payload": row["id"]},
                    row["user"], "delivery_failed")
                log.error("Stars teslimatı %s denemede başarısız, operatör gerekli: order=%s",
                          self.MAX_DELIVERY_ATTEMPTS, row["id"])

    async def refund(self, charge):
        """Refund a Stars payment by charge id. Returns False if it was already refunded."""
        order = self.store.db.execute("SELECT user, license_days FROM orders WHERE charge=?", (charge,)).fetchone()
        issue = None if order else self.store.db.execute(
            "SELECT user FROM payment_issues WHERE charge=?", (charge,)).fetchone()
        owner = order or issue
        if not owner:
            raise ValueError("Bu ödeme kimliği için sipariş veya kayıtlı sorun yok")
        if self.store.is_refunded(charge):
            return False
        await self.api("refundStarPayment", user_id=owner["user"], telegram_payment_charge_id=charge)
        with self.store.db:
            self.store.db.execute("INSERT OR IGNORE INTO refunds VALUES(?,?)", (charge, time.time()))
        granted = order and order["license_days"] and self.licenses is not None and self.store.db.execute(
            "SELECT 1 FROM license_grants WHERE charge=?", (charge,)).fetchone()
        if granted:
            # The money is already back, so a failure here must not hide the refund; log it loudly.
            try:
                self.licenses.deactivate_license(order["user"])
            except Exception as exc:
                log.error("İade edildi ama lisans kapatılamadı: user=%s error=%s", order["user"], type(exc).__name__)
        return True

    def record_failed_update(self, update, exc):
        """Last resort for an update that kept failing: never lose a paid charge."""
        message = update.get("message", {})
        payment = message.get("successful_payment")
        if payment:
            self.store.record_issue(payment, message.get("from", {}).get("id"),
                                    f"update_failed:{type(exc).__name__}")
        log.error("Güncelleme %s atlandı (%s)%s", update.get("update_id"), type(exc).__name__,
                  "; ödeme kaydı payment_issues tablosuna alındı" if payment else "")

    async def update(self, update):
        query = update.get("pre_checkout_query")
        if query:
            valid = self.config["sales_enabled"] and self.store.validate(query, query["from"]["id"], checkout=True)
            await self.api("answerPreCheckoutQuery", pre_checkout_query_id=query["id"], ok=bool(valid),
                           **({} if valid else {"error_message": "Sipariş geçersiz veya süresi doldu. /shop ile yeniden dene."}))
            return
        message = update.get("message", {})
        if message.get("chat", {}).get("type") != "private" or message.get("from", {}).get("is_bot"):
            return
        user = message["from"]["id"]
        payment = message.get("successful_payment")
        if payment:
            # A payment that cannot be matched is recorded for the operator instead of
            # raising: raising would keep this update at the head of the queue forever.
            charge = payment["telegram_payment_charge_id"]
            row = self.store.validate(payment, user)
            if not row:
                self.store.record_issue(payment, user, "no_matching_order")
                log.error("Ödeme sipariş ile eşleşmiyor; operatör incelemesi gerekli: charge=%s", charge)
                return
            if row["charge"] and row["charge"] != charge:
                self.store.record_issue(payment, user, "order_has_other_charge")
                log.error("Siparişin farklı bir ödeme kaydı var: order=%s charge=%s", row["id"], charge)
                return
            taken = self.store.db.execute("SELECT id FROM orders WHERE charge=?", (charge,)).fetchone()
            if taken and taken["id"] != row["id"]:
                self.store.record_issue(payment, user, "charge_used_by_other_order")
                log.error("Ödeme kimliği başka siparişte kayıtlı: charge=%s", charge)
                return
            with self.store.db:
                self.store.db.execute("UPDATE orders SET charge=? WHERE id=?", (charge, row["id"]))
            row = self.store.db.execute("SELECT * FROM orders WHERE id=?", (row["id"],)).fetchone()
            await self.try_deliver(row)
            return
        text = message.get("text", "")
        command, _, argument = text.partition(" ")
        command = command.split("@")[0]
        if command == "/paysupport":
            reply = self.config["support"] or "Satış henüz açık değil."
        elif command == "/orders":
            rows = self.store.db.execute("SELECT * FROM orders WHERE user=? AND charge IS NOT NULL", (user,)).fetchall()
            for row in rows:
                await self.try_deliver(row)
            reply = "Ödenmiş siparişlerin kontrol edildi." if rows else "Ödenmiş siparişin bulunmuyor."
        elif command == "/buy" and self.config["sales_enabled"]:
            product = self.config["products"].get(argument.strip())
            if product:
                payload = self.store.order(user, product)
                await self.api("sendInvoice", chat_id=user, title=product["title"],
                               description=product["description"], payload=payload, currency="XTR",
                               prices=[{"label": product["title"], "amount": product["stars"]}],
                               start_parameter="shop")
                return
            reply = "Ürün bulunamadı. /shop ile kataloğa bakabilirsin."
        else:
            reply = "Baron içerik mağazası. Destek: /paysupport · Siparişler: /orders\n"
            reply += "\n".join(f"{p['title']} — {p['stars']} ⭐ · /buy {key}" for key, p in self.config["products"].items()) if self.config["sales_enabled"] else "Satış henüz açık değil."
        await self.api("sendMessage", chat_id=user, text=reply)


MAX_UPDATE_FAILURES = 3


async def process_update(shop, update, failures):
    """Run one Telegram update so a single bad update can never stall the queue.

    Returns when the polling offset may advance. While retries remain the original
    exception is re-raised (the caller sleeps and fetches the same update again);
    after MAX_UPDATE_FAILURES the update is recorded for the operator and skipped."""
    update_id = update["update_id"]
    try:
        await shop.update(update)
    except Exception as exc:
        failures[update_id] = failures.get(update_id, 0) + 1
        if failures[update_id] < MAX_UPDATE_FAILURES:
            raise
        failures.pop(update_id)
        shop.record_failed_update(update, exc)
    else:
        failures.pop(update_id, None)
