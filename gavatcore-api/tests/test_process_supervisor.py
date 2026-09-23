"""Real subprocess tests: no Telegram, credentials, or network required."""
import asyncio
import importlib.util
import os
from pathlib import Path
import signal
import sys
import unittest
from unittest.mock import AsyncMock

SOURCE = Path(__file__).resolve().parents[1] / "app/services/process_supervisor.py"
spec = importlib.util.spec_from_file_location("process_supervisor", SOURCE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class SupervisorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.supervisor = module.ProcessSupervisor(startup_timeout=2, stop_timeout=0.1)
        self.started = AsyncMock()
        self.exited = AsyncMock()

    async def asyncTearDown(self):
        await self.supervisor.close(AsyncMock())

    async def start(self, code, key=1):
        return await self.supervisor.start(
            key, [sys.executable, "-u", "-c", code], cwd=str(SOURCE.parent),
            env=os.environ.copy(), on_started=self.started, on_exit=self.exited,
        )

    async def test_start_returns_while_child_is_alive_and_stop_reaps_before_persist(self):
        await asyncio.wait_for(self.start(
            "import time; print('GAVATCORE_SESSION_READY'); time.sleep(60)"
        ), 3)
        child = self.supervisor.children[1]
        self.assertIsNone(child.process.returncode)
        self.started.assert_awaited_once()

        async def persist():
            self.assertIsNotNone(child.process.returncode)

        await self.supervisor.stop(1, on_stopped=persist)
        self.assertNotIn(1, self.supervisor.children)
        self.exited.assert_not_awaited()

    async def test_concurrent_start_is_idempotent(self):
        code = "import time; print('GAVATCORE_SESSION_READY'); time.sleep(60)"
        results = await asyncio.gather(self.start(code), self.start(code))
        self.assertEqual(sorted(results), [False, True])
        self.started.assert_awaited_once()

    async def test_early_exit_does_not_mark_active(self):
        with self.assertRaises(RuntimeError):
            await self.start("raise SystemExit(7)")
        self.started.assert_not_awaited()
        self.assertFalse(self.supervisor.children)

    async def test_readiness_timeout_reaps_child(self):
        self.supervisor.startup_timeout = 0.1
        with self.assertRaises(asyncio.TimeoutError):
            await self.start("import time; time.sleep(60)")
        self.assertFalse(self.supervisor.children)
        self.started.assert_not_awaited()

    async def test_exit_after_readiness_is_reconciled(self):
        await self.start("import time; print('GAVATCORE_SESSION_READY'); time.sleep(.1); raise SystemExit(7)")
        child = self.supervisor.children[1]
        await asyncio.wait_for(child.monitor, 3)
        self.exited.assert_awaited_once_with(7)
        self.assertFalse(self.supervisor.children)

    async def test_unknown_active_child_cannot_report_stopped(self):
        stopped = AsyncMock()
        with self.assertRaisesRegex(RuntimeError, "not owned"):
            await self.supervisor.stop(1, on_stopped=stopped, require_owned=True)
        stopped.assert_not_awaited()

    @unittest.skipIf(sys.platform == "win32", "POSIX signal behavior")
    async def test_terminate_timeout_escalates_to_kill(self):
        await self.start(
            "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            "print('GAVATCORE_SESSION_READY'); time.sleep(60)"
        )
        child = self.supervisor.children[1]
        await self.supervisor.stop(1, on_stopped=AsyncMock())
        self.assertEqual(child.process.returncode, -signal.SIGKILL)

    async def test_persistence_failure_during_start_reaps_child(self):
        self.started.side_effect = RuntimeError("DB unavailable")
        with self.assertRaisesRegex(RuntimeError, "DB unavailable"):
            await self.start("import time; print('GAVATCORE_SESSION_READY'); time.sleep(60)")
        self.assertFalse(self.supervisor.children)

    async def test_noisy_child_does_not_block_on_full_pipe(self):
        await self.start(
            "import time; print('GAVATCORE_SESSION_READY'); "
            "[print('x'*1024) for _ in range(2048)]; time.sleep(.1)"
        )
        await asyncio.wait_for(self.supervisor.children[1].monitor, 5)
        self.exited.assert_awaited_once_with(0)

    async def test_shutdown_reaps_all_and_rejects_new_starts(self):
        code = "import time; print('GAVATCORE_SESSION_READY'); time.sleep(60)"
        await self.start(code, 1)
        await self.start(code, 2)
        children = list(self.supervisor.children.values())
        await self.supervisor.close(AsyncMock())
        self.assertTrue(all(c.process.returncode is not None for c in children))
        with self.assertRaisesRegex(RuntimeError, "shutting down"):
            await self.start(code)

    async def test_stop_persistence_can_be_retried_after_reap(self):
        await self.start("import time; print('GAVATCORE_SESSION_READY'); time.sleep(60)")
        with self.assertRaisesRegex(RuntimeError, "DB offline"):
            await self.supervisor.stop(1, on_stopped=AsyncMock(side_effect=RuntimeError("DB offline")))
        persisted = AsyncMock()
        await self.supervisor.stop(1, on_stopped=persisted, require_owned=True)
        persisted.assert_awaited_once()

    async def test_shutdown_still_stops_other_children_when_db_fails(self):
        code = "import time; print('GAVATCORE_SESSION_READY'); time.sleep(60)"
        await self.start(code, 1)
        await self.start(code, 2)
        children = list(self.supervisor.children.values())
        with self.assertRaisesRegex(RuntimeError, "persist"):
            await self.supervisor.close(AsyncMock(side_effect=RuntimeError("DB offline")))
        self.assertTrue(all(c.process.returncode is not None for c in children))
        self.assertFalse(self.supervisor.children)


if __name__ == "__main__":
    unittest.main()
