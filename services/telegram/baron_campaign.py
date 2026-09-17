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
        """)

    def order(self, user, product):
        payload = uuid.uuid4().hex
        with self.db:
            self.db.execute("INSERT INTO orders(id,user,stars,content,created) VALUES(?,?,?,?,?)",
                            (payload, user, product["stars"], product["content"], time.time()))
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
    def __init__(self, api, config, store):
        self.api, self.config, self.store = api, config, store

    async def deliver(self, row):
        if row["delivered"]:
            return
        await self.api("sendMessage", chat_id=row["user"], text=row["content"], protect_content=True)
        with self.store.db:
            self.store.db.execute("UPDATE orders SET delivered=1 WHERE id=?", (row["id"],))

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
            row = self.store.validate(payment, user)
            if not row:
                raise ValueError("Ödeme sipariş ile eşleşmiyor; operatör incelemesi gerekli")
            charge = payment["telegram_payment_charge_id"]
            if row["charge"] and row["charge"] != charge:
                raise ValueError("Siparişin farklı bir ödeme kaydı var")
            with self.store.db:
                self.store.db.execute("UPDATE orders SET charge=? WHERE id=?", (charge, row["id"]))
            await self.deliver(row)
            return
        text = message.get("text", "")
        command, _, argument = text.partition(" ")
        command = command.split("@")[0]
        if command == "/paysupport":
            reply = self.config["support"] or "Satış henüz açık değil."
        elif command == "/orders":
            rows = self.store.db.execute("SELECT * FROM orders WHERE user=? AND charge IS NOT NULL", (user,)).fetchall()
            for row in rows:
                await self.deliver(row)
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
