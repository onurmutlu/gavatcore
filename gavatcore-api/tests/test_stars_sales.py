"""Isolated tests for the Stars payment state machine; no Telegram network calls."""
import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "app" / "routes" / "stars_sales.py"
spec = importlib.util.spec_from_file_location("stars_sales_under_test", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_only_matching_buyer_amount_and_currency_can_pay(tmp_path, monkeypatch):
    monkeypatch.setenv("GAVAT_STARS_DB", str(tmp_path / "payments.sqlite3"))
    order = module.new_order(123, 15)
    assert module.verify_checkout(123, order, "XTR", 15)
    assert not module.verify_checkout(124, order, "XTR", 15)
    assert not module.verify_checkout(123, order, "USD", 15)
    assert not module.verify_checkout(123, order, "XTR", 14)
    assert not module.verify_checkout(123, "not-an-order", "XTR", 15)


def test_payment_charge_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("GAVAT_STARS_DB", str(tmp_path / "payments.sqlite3"))
    order = module.new_order(123, 10)
    assert module.record_success(123, order, "XTR", 10, "charge-001")
    assert module.record_success(123, order, "XTR", 10, "charge-001")
    assert not module.record_success(123, order, "XTR", 10, "charge-002")
    assert not module.verify_checkout(123, order, "XTR", 10)
    assert module.lookup(order)[2] == "paid"


def test_forged_or_reused_charge_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("GAVAT_STARS_DB", str(tmp_path / "payments.sqlite3"))
    first = module.new_order(123, 5)
    second = module.new_order(123, 5)
    assert not module.record_success(124, first, "XTR", 5, "c1")
    assert not module.record_success(123, first, "XTR", 4, "c1")
    assert not module.record_success(123, first, "USD", 5, "c1")
    assert module.record_success(123, first, "XTR", 5, "c1")
    assert not module.record_success(123, second, "XTR", 5, "c1")
    assert module.lookup(second)[2] == "pending"
