"""Exercise production classes with external DB/Telegram dependencies isolated."""
import ast
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[2]


def load_class(path, name, globals_):
    # Execute the actual class, replacing only unavailable external dependencies.
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    code = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), node], type_ignores=[])
    exec(compile(ast.fix_missing_locations(code), str(path), "exec"), globals_)
    return globals_[name]


class LifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = types.SimpleNamespace(
            SESSION_STORAGE_PATH=self.temp.name, TELEGRAM_API_ID="123",
            TELEGRAM_API_HASH="test-hash", OPENAI_API_KEY="test-key", OPENAI_MODEL="test",
        )
        self.supervisor = types.SimpleNamespace(children={}, start=AsyncMock(), stop=AsyncMock())
        self.fresh_db = types.SimpleNamespace(get=AsyncMock(), commit=AsyncMock())
        self.context = types.SimpleNamespace()
        context = AsyncMock()
        context.__aenter__.return_value = self.fresh_db
        self.factory = Mock(return_value=context)
        source = ROOT / "gavatcore-api/app/services/bot_launcher_service.py"
        globals_ = dict(
            __file__=str(source), Path=Path, settings=self.settings, os=os, sys=sys,
            json=json, asyncio=asyncio, supervisor=self.supervisor,
            async_session_factory=self.factory, BotInstance=object,
            BotInstanceError=RuntimeError, logger=Mock(),
        )
        cls = load_class(source, "BotLauncherService", globals_)
        self.service = cls()
        self.bot = types.SimpleNamespace(
            id=42, bot_name="test_bot", personality="yayincilara", reply_mode="manual",
            phone_number=None, user_id=1, session_file_path=str(Path(self.temp.name)/"test.session"),
            triggers="[]", config="{}", is_active=False, is_online=False,
            start_bot=Mock(), stop_bot=Mock(), log_error=Mock(),
        )
        self.db = types.SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock(), get=AsyncMock(return_value=self.bot))

    async def asyncTearDown(self):
        self.temp.cleanup()

    async def test_start_uses_absolute_runner_and_exit_gets_its_own_db_session(self):
        await self.service._start_bot_process(self.bot, self.db)
        args, kwargs = self.supervisor.start.call_args
        self.assertEqual(args[0], 42)
        self.assertEqual(args[1][:2], [sys.executable, str(ROOT / "userbot_session.py")])
        self.assertEqual(kwargs["cwd"], str(ROOT))
        self.db.commit.assert_not_awaited()  # No active flag before readiness.
        await kwargs["on_started"]()
        self.db.commit.assert_awaited_once()
        self.bot.start_bot.assert_called_once()
        self.fresh_db.get.return_value = self.bot
        await kwargs["on_exit"](7)
        self.factory.assert_called_once()
        self.fresh_db.get.assert_awaited_once_with(object, 42)
        self.fresh_db.commit.assert_awaited_once()
        self.bot.log_error.assert_called_once_with("Bot process exited with code 7")
        self.assertEqual(self.db.commit.await_count, 1)

    async def test_generated_config_has_explicit_session_and_no_credentials(self):
        path = await self.service._create_bot_config(self.bot)
        config = json.loads(path.read_text())
        self.assertEqual(config["session_file"], self.bot.session_file_path)
        self.assertTrue(config["non_interactive"])
        self.assertEqual(config["handlers"], ["gpt_handler", "common_handler"])
        self.assertNotIn("test-key", path.read_text())
        self.assertNotIn("test-hash", path.read_text())
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    async def test_spawn_error_is_not_returned_as_success(self):
        self.supervisor.start.side_effect = RuntimeError("spawn failed")
        with self.assertRaisesRegex(RuntimeError, "failed to become ready"):
            await self.service._start_bot_process(self.bot, self.db)
        self.db.rollback.assert_awaited_once()
        self.bot.start_bot.assert_not_called()
        self.bot.stop_bot.assert_called_once()
        self.bot.log_error.assert_called_once()

    async def test_stop_only_persists_after_supervisor_confirmation(self):
        await self.service.stop_bot_instance(self.bot, self.db)
        self.bot.stop_bot.assert_not_called()
        await self.supervisor.stop.call_args.kwargs["on_stopped"]()
        self.bot.stop_bot.assert_called_once()
        self.db.commit.assert_awaited_once()

    async def test_restart_waits_for_stop_before_start(self):
        order = []
        async def stop(*args):
            order.append("stopped")
        async def start(*args):
            self.assertEqual(order, ["stopped"])
            order.append("started")
        self.service.stop_bot_instance = stop
        self.service._start_bot_process = start
        await self.service.restart_bot_instance(self.bot, self.db)
        self.assertEqual(order, ["stopped", "started"])

    async def test_noninteractive_session_rejects_unauthorized_client(self):
        cls = load_class(ROOT / "userbot_session.py", "UserbotSession", dict(
            Path=Path, os=os, asyncio=asyncio, logger=Mock(),
        ))
        session = cls("test", {"session_file": str(Path(self.temp.name)/"test.session"), "non_interactive": True}, None)
        session.client = types.SimpleNamespace(
            connect=AsyncMock(), is_user_authorized=AsyncMock(return_value=False), start=AsyncMock(),
        )
        with patch("builtins.print") as output:
            with self.assertRaisesRegex(RuntimeError, "not authorized"):
                await session.start()
        session.client.start.assert_not_awaited()
        output.assert_not_called()

    async def test_ready_only_after_authorization_and_handler_setup(self):
        cls = load_class(ROOT / "userbot_session.py", "UserbotSession", dict(
            Path=Path, os=os, asyncio=asyncio, logger=Mock(),
        ))
        session = cls("test", {"session_file": str(Path(self.temp.name)/"test.session"), "non_interactive": True}, None)
        session.client = types.SimpleNamespace(
            connect=AsyncMock(), is_user_authorized=AsyncMock(return_value=True), start=AsyncMock(),
        )
        session._setup_handlers = Mock()
        session._keep_alive = AsyncMock()
        with patch("builtins.print") as output:
            await session.start()
        session._setup_handlers.assert_called_once()
        output.assert_called_once_with("GAVATCORE_SESSION_READY", flush=True)
        session._setup_handlers.side_effect = RuntimeError("handler failed")
        with patch("builtins.print") as output:
            with self.assertRaisesRegex(RuntimeError, "handler failed"):
                await session.start()
        output.assert_not_called()


if __name__ == "__main__":
    unittest.main()
