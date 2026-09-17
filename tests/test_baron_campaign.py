import asyncio
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("baron_campaign", Path(__file__).resolve().parents[1] / "services/telegram/baron_campaign.py")
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


class ShopTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = campaign.Store(":memory:")
        self.calls = []
        self.config = campaign.load_config()
        self.config["adaptive"]["enabled"] = False
        self.config.update(sales_enabled=True, support="@support")
        self.product = {"title": "Rehber", "description": "Sohbet rehberi", "stars": 25, "content": "Satın alınan içerik"}
        self.config["products"] = {"guide": self.product}

        async def api(method, **kwargs):
            self.calls.append((method, kwargs))

        self.shop = campaign.StarsShop(api, self.config, self.store)
        self.payload = self.store.order(123, self.product)
        self.payment = {"invoice_payload": self.payload, "currency": "XTR", "total_amount": 25, "telegram_payment_charge_id": "charge1"}

    def tearDown(self):
        self.store.db.close()

    def paid_update(self):
        return {"message": {"chat": {"type": "private"}, "from": {"id": 123}, "successful_payment": self.payment}}

    async def test_checkout_does_not_deliver(self):
        await self.shop.update({"pre_checkout_query": {**self.payment, "id": "q", "from": {"id": 123}}})
        self.assertEqual(self.calls, [("answerPreCheckoutQuery", {"pre_checkout_query_id": "q", "ok": True})])

    async def test_duplicate_payment_delivers_once(self):
        await self.shop.update(self.paid_update())
        await self.shop.update(self.paid_update())
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][1]["text"], self.product["content"])

    async def test_failed_delivery_can_retry(self):
        original = self.shop.api
        async def fail(*args, **kwargs):
            raise RuntimeError("offline")
        self.shop.api = fail
        with self.assertRaises(RuntimeError):
            await self.shop.update(self.paid_update())
        self.shop.api = original
        await self.shop.update(self.paid_update())
        self.assertEqual(len(self.calls), 1)

    def test_wrong_user_amount_currency_and_expired_order(self):
        self.assertIsNone(self.store.validate(self.payment, 456))
        for field, value in (("currency", "USD"), ("total_amount", 1), ("invoice_payload", "unknown")):
            self.assertIsNone(self.store.validate({**self.payment, field: value}, 123))
        self.store.db.execute("UPDATE orders SET created=0")
        self.assertIsNone(self.store.validate(self.payment, 123, checkout=True))
        self.assertIsNotNone(self.store.validate(self.payment, 123))

    async def test_paid_order_rejects_checkout(self):
        await self.shop.update(self.paid_update())
        self.assertIsNone(self.store.validate(self.payment, 123, checkout=True))

    async def test_invoice_is_xtr_and_user_bound(self):
        await self.shop.update({"message": {"chat": {"type": "private"}, "from": {"id": 123}, "text": "/buy guide"}})
        method, invoice = self.calls[0]
        self.assertEqual(method, "sendInvoice")
        self.assertEqual(invoice["currency"], "XTR")
        self.assertEqual(invoice["prices"][0]["amount"], 25)

    def test_dm_history_persists_and_is_user_scoped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dm.sqlite3"
            first = campaign.Store(path)
            first.add_dm("123", "user", "önceki konuşma")
            first.add_dm("123", "assistant", "hatırlıyorum")
            first.add_dm("456", "user", "başka kullanıcı")
            first.db.close()
            second = campaign.Store(path)
            try:
                self.assertEqual(
                    second.dm_context("123"),
                    [
                        {"role": "user", "content": "önceki konuşma"},
                        {"role": "assistant", "content": "hatırlıyorum"},
                    ],
                )
            finally:
                second.db.close()

    def test_permission_and_interval_validation(self):
        for mutate in (
            lambda c: c["broadcast"].update(interval_seconds=1),
            lambda c: c["broadcast"].update(groups=[{"id": -123, "permission_confirmed": False}]),
            lambda c: c["broadcast"].update(enabled=True, groups=[]),
        ):
            config = copy.deepcopy(self.config)
            mutate(config)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "config.json"
                path.write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    campaign.load_config(path)

    async def test_broadcast_rotation_restart_cooldown_and_dry_run(self):
        self.config["broadcast"].update(enabled=True, groups=[{"id": -123, "permission_confirmed": True}], messages=["one", "two"])
        sent = []
        class Client:
            async def get_entity(self, chat):
                return type("Chat", (), {})()
            async def send_message(self, entity, text):
                sent.append(text)
        async def end_cycle(_):
            raise asyncio.CancelledError()
        async def cycle():
            with patch.object(campaign.asyncio, "sleep", end_cycle):
                with self.assertRaises(asyncio.CancelledError):
                    await campaign.broadcast(Client(), self.config, self.store)
        await campaign.broadcast(Client(), self.config, self.store, dry_run=True)
        self.assertEqual(sent, [])
        self.store.db.execute("INSERT INTO schedule VALUES(-123,0,0)")
        await cycle()
        await cycle()
        self.assertEqual(sent, ["one"])
        self.store.db.execute("UPDATE schedule SET next_at=0")
        self.store.db.execute("DELETE FROM state WHERE key='campaign_next_send'")
        await cycle()
        self.assertEqual(sent, ["one", "two"])


if __name__ == "__main__":
    unittest.main()
