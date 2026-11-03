#!/usr/bin/env python3
"""Operator tool for the Stars shop: list problem payments and refund by charge id.

    python launchers/baron_stars_refund.py --issues
    python launchers/baron_stars_refund.py <telegram_payment_charge_id> [--yes]
"""
import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from launchers.baron_stars_shop import make_api
from services.telegram.baron_campaign import StarsShop, Store, load_config


def print_issues(store):
    rows = store.db.execute(
        "SELECT i.* FROM payment_issues i "
        "WHERE NOT EXISTS (SELECT 1 FROM refunds r WHERE r.charge=i.charge) ORDER BY i.created"
    ).fetchall()
    if not rows:
        print("Açık ödeme sorunu yok.")
    for row in rows:
        when = datetime.fromtimestamp(row["created"]).strftime("%Y-%m-%d %H:%M")
        print(f"{when}  charge={row['charge']}  user={row['user']}  stars={row['stars']}  neden={row['reason']}")


async def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("charge", nargs="?", help="telegram_payment_charge_id")
    parser.add_argument("--issues", action="store_true", help="iade/teslimat bekleyen sorunları listele")
    parser.add_argument("--yes", action="store_true", help="onay sormadan iade et")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    store = Store()
    try:
        if args.issues:
            print_issues(store)
            return
        if not args.charge:
            parser.error("charge kimliği veya --issues gerekli")
        token = os.getenv("BARON_SHOP_BOT_TOKEN")
        if not token:
            raise SystemExit(".env içinde BARON_SHOP_BOT_TOKEN gerekli")
        if not args.yes and input(f"{args.charge} ödemesi iade edilsin mi? [e/H] ").strip().lower() != "e":
            raise SystemExit("İptal edildi")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=40)) as session:
            shop = StarsShop(make_api(session, token), load_config(), store)
            try:
                refunded = await shop.refund(args.charge)
            except (ValueError, RuntimeError) as exc:
                raise SystemExit(f"İade yapılamadı: {exc}")
        print("İade edildi." if refunded else "Bu ödeme zaten iade edilmişti.")
    finally:
        store.db.close()


if __name__ == "__main__":
    asyncio.run(main())
