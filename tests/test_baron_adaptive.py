import asyncio
import copy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from services.telegram.baron_campaign import Store, load_config, broadcast
from services.telegram.baron_adaptive import (
    AdaptiveEngine, Selection, classify_group, load_templates, recent_context,
    redact, scan_groups, validate_settings,
)


class AdaptiveTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.config = load_config()
        self.settings = self.config["adaptive"]
        self.engine = AdaptiveEngine(self.store, self.settings)
        self.context = ["Müzik konuşalım", "Son şarkı çok iyi", "Konser var mı?"]

    def tearDown(self):
        self.store.db.close()

    async def generate(self, context, topic):
        return "Bugün hangi konseri dinlemek isterdiniz?"

    def test_48_templates_unique_and_valid(self):
        self.assertEqual(len(load_templates(self.settings)), 48)
        validate_settings(self.settings)

    def test_candidates_are_not_generic_news_groups(self):
        result = classify_group("İstanbul Tanışma ve Arayış", [])
        self.assertTrue(result["candidate"])
        self.assertFalse(classify_group("Yazılım haberleri", ["merhaba", "yeni sürüm", "test sonucu"])["candidate"])
        self.assertFalse(classify_group("İş Arayışı", ["iş arıyorum"])["candidate"])

    def test_redacts_common_identifiers(self):
        result = redact("@foo https://example.com +90 532 555 55 55 test@example.com")
        for secret in ("@foo", "example.com", "532"):
            self.assertNotIn(secret, result)

    async def test_alternates_successful_sources_and_preserves_after_restart(self):
        sources = []
        for i in range(8):
            async def generate(context, topic):
                return f"Müzik hakkında {i} numaralı yeni bir soru."
            selected = await self.engine.choose(-123, self.context, generate)
            sources.append(selected.source)
            self.engine.record_sent(-123, i, selected)
            self.engine = AdaptiveEngine(self.store, self.settings)
        self.assertEqual(sources, ["template", "gpt"] * 4)

    async def test_new_groups_balance_sources_globally(self):
        first = await self.engine.choose(-1, self.context, self.generate)
        self.engine.record_sent(-1, 1, first)
        second = await self.engine.choose(-2, self.context, self.generate)
        self.assertEqual((first.source, second.source), ("template", "gpt"))

    async def test_gpt_failure_does_not_fall_back_or_advance(self):
        selected = await self.engine.choose(-123, self.context, self.generate)
        self.engine.record_sent(-123, 1, selected)
        async def unavailable(*args):
            return None
        self.assertIsNone(await self.engine.choose(-123, self.context, unavailable))
        self.assertEqual(self.engine.next_source(-123), "gpt")

    async def test_no_context_no_send(self):
        self.assertIsNone(await self.engine.choose(-123, [], self.generate))

    async def test_topic_relevance_and_duplicate_avoidance(self):
        selected = await self.engine.choose(-123, self.context, self.generate)
        self.assertTrue(selected.template_id.startswith("music_"))
        self.engine.record_sent(-123, 1, selected)
        generated = await self.engine.choose(-123, self.context, self.generate)
        self.engine.record_sent(-123, 2, generated)
        second = await self.engine.choose(-123, self.context, self.generate)
        self.assertNotEqual(selected.template_id, second.template_id)
        self.engine.record_sent(-123, 3, second)
        self.assertIsNone(await self.engine.choose(-123, self.context, self.generate))

    def test_feedback_deduplicates_and_isolates_groups(self):
        self.engine.record_sent(-123, 1, Selection("template", "hello", "music_01", "music"))
        self.engine.feedback(-123, 2, 1, "spam istemiyoruz")
        self.engine.feedback(-123, 2, 1, "spam istemiyoruz")
        self.engine.feedback(-456, 3, 1, "güzel")
        row = self.store.db.execute("SELECT replies,negative FROM adaptive_posts").fetchone()
        self.assertEqual(tuple(row), (0, 1))

    def test_retention_removes_feedback_but_keeps_ratio(self):
        self.engine.record_sent(-123, 1, Selection("template", "hello", "music_01"))
        self.engine.feedback(-123, 2, 1, "güzel")
        self.store.db.execute("UPDATE adaptive_posts SET sent=0")
        self.engine.prune()
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM adaptive_feedback").fetchone()[0], 0)
        self.assertEqual(self.engine.next_source(-123), "gpt")

    async def test_context_ignores_old_own_and_commands(self):
        now = datetime.now(timezone.utc)
        class Client:
            async def iter_messages(self, entity, limit):
                for raw, date, out in [("fresh", now, False), ("own", now, True), ("old", now-timedelta(days=4), False), ("/start", now, False)]:
                    yield SimpleNamespace(raw_text=raw, date=date, out=out)
        self.assertEqual(await recent_context(Client(), None, self.settings), ["fresh"])

    async def test_scan_never_sends_or_grants_permission(self):
        class Client:
            async def iter_dialogs(self):
                yield SimpleNamespace(is_group=False)
                yield SimpleNamespace(is_group=True, id=-123, title="Tanışma", entity=None)
            async def iter_messages(self, entity, limit):
                yield SimpleNamespace(raw_text="Merhaba", date=datetime.now(timezone.utc))
        report = await scan_groups(Client(), self.settings)
        self.assertTrue(report["complete"])
        self.assertEqual(len(report["groups"]), 1)
        self.assertFalse(report["groups"][0]["permission_confirmed"])
        self.assertFalse(report["groups"][0]["baron_is_admin"])

    async def test_broadcast_wires_context_and_records_success_only(self):
        self.config["broadcast"].update(enabled=True, groups=[{"id": -123, "permission_confirmed": True}])
        sent = []
        class Client:
            async def get_entity(self, chat):
                return SimpleNamespace(megagroup=True)
            async def iter_messages(self, entity, limit):
                for text in ["Müzik", "Şarkı", "Konser"]:
                    yield SimpleNamespace(raw_text=text, date=datetime.now(timezone.utc))
            async def send_message(self, entity, text):
                sent.append(text)
                return SimpleNamespace(id=len(sent))
        async def end(_):
            raise asyncio.CancelledError()
        self.store.db.execute("INSERT INTO schedule VALUES(-123,0,0)")
        for i in range(2):
            self.store.db.execute("UPDATE schedule SET next_at=0")
            self.store.db.execute("DELETE FROM state WHERE key='campaign_next_send'")
            with patch("services.telegram.baron_campaign.asyncio.sleep", end):
                with self.assertRaises(asyncio.CancelledError):
                    await broadcast(Client(), self.config, self.store, engine=self.engine, generate=self.generate)
        self.assertEqual(len(sent), 2)
        self.assertFalse(any("otomatik asistan" in text for text in sent))
        self.assertEqual(self.engine.next_source(-123), "template")

    async def test_group_generator_does_not_export_raw_context(self):
        from services.telegram import baron_bot_handler as handler
        captured = {}
        class Generator:
            client = True
            async def generate_reply(self, **kwargs):
                captured.update(kwargs)
                return "Günün şarkısı ne?"
        with patch.object(handler, "gpt_generator", Generator()):
            await handler.generate_baron_group_post(["özel metin 123"], "music")
        payload = captured["user_message"]
        self.assertNotIn("özel metin", payload)
        self.assertIn('"topic_hint": "music"', payload)

    async def test_dm_batch_coalesces_quick_messages(self):
        from services.telegram import baron_bot_handler as handler
        handler._dm_batches.clear()
        handler._dm_batch_lock = None
        first = asyncio.create_task(handler._collect_dm_batch("123", "birinci", delay=0.02))
        await asyncio.sleep(0)
        second = await handler._collect_dm_batch("123", "ikinci", delay=0.02)
        self.assertIsNone(second)
        self.assertEqual(await first, "birinci\nikinci")
        self.assertEqual(handler.humanizer.multi_message_chance, 0.0)

    async def test_dm_history_bootstrap_excludes_current_and_commands(self):
        from services.telegram import baron_bot_handler as handler
        class Client:
            async def iter_messages(self, peer, **options):
                self.options = options
                for text, out in [("önceki cevap", True), ("/start", False), ("önceki soru", False)]:
                    yield SimpleNamespace(raw_text=text, out=out, action=None)
        client = Client()
        history = await handler._load_recent_dm_history(client, 123, 99)
        self.assertEqual(client.options["max_id"], 99)
        self.assertEqual(
            history,
            [
                {"role": "user", "content": "önceki soru"},
                {"role": "assistant", "content": "önceki cevap"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
