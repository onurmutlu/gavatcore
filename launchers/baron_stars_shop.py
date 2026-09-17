#!/usr/bin/env python3
"""Separate BotFather bot for Baron's Stars payments; no user session needed."""
import asyncio
import logging
import os
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from services.telegram.baron_campaign import StarsShop, Store, load_config


async def main():
    load_dotenv(ROOT / ".env")
    config = load_config()
    token = os.getenv("BARON_SHOP_BOT_TOKEN")
    if not token:
        raise SystemExit(".env içinde BARON_SHOP_BOT_TOKEN gerekli")
    if not config["shop_username"]:
        raise SystemExit("config/baron_campaign.json içinde shop_username gerekli")
    store = Store()
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=40)) as session:
        async def api(method, **payload):
            async with session.post(f"https://api.telegram.org/bot{token}/{method}", json=payload) as response:
                result = await response.json()
            if not result.get("ok"):
                delay = result.get("parameters", {}).get("retry_after", 0)
                if delay:
                    await asyncio.sleep(delay)
                raise RuntimeError(f"Telegram {method} başarısız ({result.get('error_code')})")
            return result["result"]

        me = await api("getMe")
        if me["username"].lower() != config["shop_username"].lstrip("@").lower():
            raise SystemExit("Token, yapılandırılan mağaza botuna ait değil")
        webhook = await api("getWebhookInfo")
        if webhook.get("url"):
            raise SystemExit("Botta webhook etkin; mevcut entegrasyonu kaldırmadan polling başlatılamaz")
        shop = StarsShop(api, config, store)
        offset_row = store.db.execute("SELECT value FROM state WHERE key='offset'").fetchone()
        offset = offset_row[0] if offset_row else 0
        logging.info("Stars mağazası hazır: @%s (satış=%s)", me["username"], config["sales_enabled"])
        try:
            while True:
                try:
                    updates = await api("getUpdates", offset=offset, timeout=25,
                                        allowed_updates=["message", "pre_checkout_query"])
                    for update in updates:
                        await shop.update(update)
                        offset = update["update_id"] + 1
                        with store.db:
                            store.db.execute("INSERT OR REPLACE INTO state VALUES('offset',?)", (offset,))
                except Exception as exc:
                    # Never log request URLs: they contain the bot token.
                    logging.error("Stars işlemi tamamlanamadı: %s; kayıt yeniden denenecek", type(exc).__name__)
                    await asyncio.sleep(5)
        finally:
            store.db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
