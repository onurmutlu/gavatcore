import datetime
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import license_checker as lc


class LicenseExpiryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        base = Path(self.directory.name)
        self.patches = [
            patch.object(lc, "DATA_DIR", str(base)),
            patch.object(lc, "LICENSE_FILE", str(base / "licenses.json")),
            patch.object(lc, "DEMO_ALERTS_FILE", str(base / "demo_alerts.json")),
            patch.object(lc, "log_event", lambda *args, **kwargs: None),
        ]
        for patcher in self.patches:
            patcher.start()
        self.checker = lc.LicenseChecker()

    def tearDown(self):
        for patcher in self.patches:
            patcher.stop()
        self.directory.cleanup()

    @staticmethod
    def iso(**delta):
        return (datetime.datetime.now() + datetime.timedelta(**delta)).isoformat()

    def expires(self, user):
        return datetime.datetime.fromisoformat(self.checker.load_licenses()[str(user)]["expires_at"])

    def test_expired_license_is_no_longer_valid(self):
        self.checker.save_licenses({"1": {"is_active": True, "expires_at": self.iso(days=-1)}})
        self.assertEqual(self.checker.get_license_status(1), "inactive")
        self.assertFalse(self.checker.is_license_valid(1, datetime.datetime.now()))

    def test_unexpired_license_stays_valid(self):
        self.checker.save_licenses({"1": {"is_active": True, "expires_at": self.iso(days=3)}})
        self.assertEqual(self.checker.get_license_status(1), "active")
        self.assertTrue(self.checker.is_license_valid(1, datetime.datetime.now()))

    def test_legacy_entries_without_expiry_stay_active(self):
        self.checker.save_licenses({"1": {"is_active": True, "activated_at": self.iso(days=-400)}})
        self.assertEqual(self.checker.get_license_status(1), "active")

    def test_unparsable_expiry_keeps_previous_behaviour(self):
        self.checker.save_licenses({"1": {"is_active": True, "expires_at": "not-a-date"}})
        self.assertEqual(self.checker.get_license_status(1), "active")

    def test_extend_starts_a_new_period_for_new_and_expired_users(self):
        before = datetime.datetime.now()
        self.checker.extend_license(1, 30)
        self.assertAlmostEqual((self.expires(1) - before).total_seconds(), 30 * 86400, delta=60)
        self.checker.save_licenses({"2": {"is_active": True, "expires_at": self.iso(days=-10)}})
        self.checker.extend_license(2, 7)
        self.assertAlmostEqual((self.expires(2) - before).total_seconds(), 7 * 86400, delta=60)
        self.assertEqual(self.checker.get_license_status(2), "active")

    def test_early_renewal_keeps_remaining_days(self):
        self.checker.extend_license(1, 30)
        first_expiry = self.expires(1)
        self.checker.extend_license(1, 30)
        self.assertEqual(self.expires(1), first_expiry + datetime.timedelta(days=30))
        self.assertEqual(self.checker.load_licenses()["1"]["license_days"], 60)

    def test_extend_reactivates_a_deactivated_license(self):
        self.checker.extend_license(1, 30)
        self.checker.deactivate_license(1)
        self.assertEqual(self.checker.get_license_status(1), "inactive")
        self.checker.extend_license(1, 30)
        self.assertEqual(self.checker.get_license_status(1), "active")
