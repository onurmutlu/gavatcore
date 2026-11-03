import asyncio
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import time
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

    async def fail_api(self, *args, **kwargs):
        raise RuntimeError("offline")

    async def test_failed_delivery_does_not_raise_and_retries_later(self):
        original = self.shop.api
        self.shop.api = self.fail_api
        await self.shop.update(self.paid_update())  # must not raise: the charge is stored
        row = self.store.db.execute("SELECT charge, delivered FROM orders").fetchone()
        self.assertEqual((row["charge"], row["delivered"]), ("charge1", 0))
        self.shop.api = original
        await self.shop.redeliver()  # too soon: retry delay has not passed
        self.assertEqual(self.calls, [])
        await self.shop.redeliver(now=time.time() + self.shop.DELIVERY_RETRY_SECONDS + 1)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.store.db.execute("SELECT delivered FROM orders").fetchone()[0], 1)

    async def test_buyer_command_retries_failed_delivery(self):
        original = self.shop.api
        self.shop.api = self.fail_api
        await self.shop.update(self.paid_update())
        self.shop.api = original
        await self.shop.update({"message": {"chat": {"type": "private"}, "from": {"id": 123}, "text": "/orders"}})
        self.assertEqual([call[0] for call in self.calls], ["sendMessage", "sendMessage"])
        self.assertEqual(self.calls[0][1]["text"], self.product["content"])

    async def test_redelivery_gives_up_and_hands_over_to_operator(self):
        self.shop.api = self.fail_api
        await self.shop.update(self.paid_update())
        later = time.time()
        for _ in range(self.shop.MAX_DELIVERY_ATTEMPTS + 2):
            later += self.shop.DELIVERY_RETRY_SECONDS + 1
            await self.shop.redeliver(now=later)
        attempts = self.store.db.execute("SELECT attempts FROM delivery_state").fetchone()[0]
        self.assertEqual(attempts, self.shop.MAX_DELIVERY_ATTEMPTS)
        issue = self.store.db.execute("SELECT charge, reason FROM payment_issues").fetchone()
        self.assertEqual((issue["charge"], issue["reason"]), ("charge1", "delivery_failed"))

    async def test_unmatched_payment_is_recorded_not_raised(self):
        unknown = {**self.payment, "invoice_payload": "unknown", "telegram_payment_charge_id": "orphan"}
        await self.shop.update({"message": {"chat": {"type": "private"}, "from": {"id": 123}, "successful_payment": unknown}})
        issue = self.store.db.execute("SELECT charge, user, reason FROM payment_issues").fetchone()
        self.assertEqual((issue["charge"], issue["user"], issue["reason"]), ("orphan", 123, "no_matching_order"))
        self.assertEqual(self.calls, [])

    async def test_charge_used_by_another_order_is_recorded_not_raised(self):
        await self.shop.update(self.paid_update())
        second = self.store.order(123, self.product)
        replay = {**self.payment, "invoice_payload": second}
        await self.shop.update({"message": {"chat": {"type": "private"}, "from": {"id": 123}, "successful_payment": replay}})
        issue = self.store.db.execute("SELECT reason FROM payment_issues").fetchone()
        self.assertEqual(issue["reason"], "charge_used_by_other_order")

    async def test_bad_update_cannot_block_the_queue(self):
        poison = {"update_id": 1, "message": {"chat": {"type": "private"}, "from": {"id": 123},
                                              "successful_payment": {**self.payment, "currency": None}}}
        good = {"update_id": 2, **self.paid_update()}
        original = self.shop.update

        async def update(update):
            if update["update_id"] == 1:
                raise KeyError("broken update")
            await original(update)

        self.shop.update = update
        failures = {}
        for _ in range(campaign.MAX_UPDATE_FAILURES - 1):
            with self.assertRaises(KeyError):
                await campaign.process_update(self.shop, poison, failures)
        await campaign.process_update(self.shop, poison, failures)  # last failure: skipped, offset may advance
        self.assertEqual(failures, {})
        issue = self.store.db.execute("SELECT charge, reason FROM payment_issues").fetchone()
        self.assertEqual((issue["charge"], issue["reason"]), ("charge1", "update_failed:KeyError"))
        await campaign.process_update(self.shop, good, failures)  # the buyer behind it is served
        self.assertEqual(len(self.calls), 1)

    async def test_refund_calls_bot_api_once_and_stops_delivery(self):
        await self.shop.update(self.paid_update())
        self.calls.clear()
        self.assertTrue(await self.shop.refund("charge1"))
        self.assertFalse(await self.shop.refund("charge1"))
        self.assertEqual(self.calls, [("refundStarPayment", {"user_id": 123, "telegram_payment_charge_id": "charge1"})])
        self.store.db.execute("UPDATE orders SET delivered=0")
        await self.shop.redeliver(now=time.time() + self.shop.DELIVERY_RETRY_SECONDS + 1)
        self.assertEqual(len(self.calls), 1)  # nothing is delivered for a refunded charge

    async def test_refund_unmatched_payment_and_unknown_charge(self):
        unknown = {**self.payment, "invoice_payload": "unknown", "telegram_payment_charge_id": "orphan"}
        await self.shop.update({"message": {"chat": {"type": "private"}, "from": {"id": 123}, "successful_payment": unknown}})
        self.assertTrue(await self.shop.refund("orphan"))
        self.assertEqual(self.calls[-1], ("refundStarPayment", {"user_id": 123, "telegram_payment_charge_id": "orphan"}))
        with self.assertRaises(ValueError):
            await self.shop.refund("never-seen")

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
