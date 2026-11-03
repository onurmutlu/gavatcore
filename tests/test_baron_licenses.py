import copy
import importlib.util
import json
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "baron_campaign_licenses", Path(__file__).resolve().parents[1] / "services/telegram/baron_campaign.py"
)
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


class FakeLicenses:
    def __init__(self):
        self.extended, self.deactivated, self.fail = [], [], False

    def extend_license(self, user_id, days):
        if self.fail:
            raise RuntimeError("license store offline")
        self.extended.append((user_id, days))

    def deactivate_license(self, user_id):
        self.deactivated.append(user_id)


class LicenseSaleTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = campaign.Store(":memory:")
        self.calls = []
        self.licenses = FakeLicenses()
        self.config = campaign.load_config()
        self.config["adaptive"]["enabled"] = False
        self.product = {"title": "Pro lisans", "description": "30 günlük lisans", "stars": 100,
                        "content": "Lisansın etkin", "license_days": 30}
        self.config.update(sales_enabled=True, support="@support", products={"pro": self.product})

        async def api(method, **kwargs):
            self.calls.append((method, kwargs))

        self.api = api
        self.shop = campaign.StarsShop(api, self.config, self.store, self.licenses)
        self.payload = self.store.order(123, self.product)
        self.payment = {"invoice_payload": self.payload, "currency": "XTR", "total_amount": 100,
                        "telegram_payment_charge_id": "chargeL"}

    def tearDown(self):
        self.store.db.close()

    def paid_update(self, payment=None):
        return {"message": {"chat": {"type": "private"}, "from": {"id": 123},
                            "successful_payment": payment or self.payment}}

    def later(self):
        return time.time() + self.shop.DELIVERY_RETRY_SECONDS + 1

    async def test_paid_license_is_activated_once_and_content_delivered(self):
        await self.shop.update(self.paid_update())
        await self.shop.update(self.paid_update())  # Telegram redelivering the same update
        self.assertEqual(self.licenses.extended, [(123, 30)])
        self.assertEqual([call[0] for call in self.calls], ["sendMessage"])
        self.assertEqual(self.calls[0][1]["text"], "Lisansın etkin")

    async def test_license_failure_does_not_raise_and_is_retried(self):
        self.licenses.fail = True
        await self.shop.update(self.paid_update())  # must not block the queue
        row = self.store.db.execute("SELECT charge, delivered FROM orders").fetchone()
        self.assertEqual((row["charge"], row["delivered"]), ("chargeL", 0))
        self.assertEqual(self.calls, [])
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM license_grants").fetchone()[0], 0)
        self.licenses.fail = False
        await self.shop.redeliver(now=self.later())
        self.assertEqual(self.licenses.extended, [(123, 30)])
        self.assertEqual(len(self.calls), 1)

    async def test_license_is_granted_even_if_content_was_already_delivered(self):
        # Order delivered before the license column existed / granted: sweep must still grant it.
        await self.shop.update(self.paid_update())
        with self.store.db:
            self.store.db.execute("DELETE FROM license_grants")
        self.licenses.extended.clear()
        await self.shop.redeliver(now=self.later())
        self.assertEqual(self.licenses.extended, [(123, 30)])
        self.assertEqual(len(self.calls), 1)  # content is not sent a second time

    async def test_plain_product_never_touches_licenses(self):
        plain = {"title": "Rehber", "description": "d", "stars": 25, "content": "metin"}
        payload = self.store.order(123, plain)
        payment = {"invoice_payload": payload, "currency": "XTR", "total_amount": 25,
                   "telegram_payment_charge_id": "chargeP"}
        await self.shop.update(self.paid_update(payment))
        self.assertEqual(self.licenses.extended, [])
        self.assertEqual(len(self.calls), 1)

    async def test_refund_revokes_a_granted_license(self):
        await self.shop.update(self.paid_update())
        self.assertTrue(await self.shop.refund("chargeL"))
        self.assertEqual(self.licenses.deactivated, [123])

    async def test_refund_before_grant_never_grants_or_revokes(self):
        self.licenses.fail = True
        await self.shop.update(self.paid_update())
        self.assertTrue(await self.shop.refund("chargeL"))
        self.assertEqual(self.licenses.deactivated, [])  # nothing was ever granted
        self.licenses.fail = False
        await self.shop.redeliver(now=self.later())
        self.assertEqual(self.licenses.extended, [])  # a refunded charge is not fulfilled
        self.assertEqual(self.calls[-1][0], "refundStarPayment")

    def test_license_days_validation(self):
        for bad in (0, -5, "30", True, 3651, 1.5):
            config = copy.deepcopy(self.config)
            config["products"]["pro"]["license_days"] = bad
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "config.json"
                path.write_text(json.dumps(config))
                with self.assertRaises(ValueError, msg=f"license_days={bad!r}"):
                    campaign.load_config(path)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(self.config))
            self.assertEqual(campaign.load_config(path)["products"]["pro"]["license_days"], 30)

    def test_license_product_requires_a_license_manager(self):
        with self.assertRaises(ValueError):
            campaign.StarsShop(self.api, self.config, self.store)

    def test_order_remembers_license_days_at_purchase_time(self):
        self.product["license_days"] = 365  # price/terms are fixed when the invoice is created
        row = self.store.db.execute("SELECT license_days FROM orders WHERE id=?", (self.payload,)).fetchone()
        self.assertEqual(row["license_days"], 30)

    def test_legacy_orders_table_gains_license_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.sqlite3"
            legacy = sqlite3.connect(path)
            legacy.executescript(
                "CREATE TABLE orders(id TEXT PRIMARY KEY, user INTEGER, stars INTEGER, content TEXT,"
                " created REAL, charge TEXT UNIQUE, delivered INTEGER DEFAULT 0);"
                "INSERT INTO orders VALUES('old',9,5,'x',1.0,'legacy-charge',1);"
            )
            legacy.commit()
            legacy.close()
            store = campaign.Store(path)
            try:
                row = store.db.execute("SELECT user, charge, delivered, license_days FROM orders").fetchone()
                self.assertEqual(tuple(row), (9, "legacy-charge", 1, None))
                store.order(9, self.product)  # new orders work on the migrated table
            finally:
                store.db.close()
