"""Single-process child ownership. Run the API with ONE worker and no reload.

No PID-based signalling: unknown children are never claimed or killed.
"""
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

READY = b"GAVATCORE_SESSION_READY\n"


@dataclass
class Child:
    process: asyncio.subprocess.Process
    reader: asyncio.Task
    monitor: Optional[asyncio.Task] = None


class ProcessSupervisor:
    def __init__(self, startup_timeout=45, stop_timeout=10):
        self.startup_timeout = startup_timeout
        self.stop_timeout = stop_timeout
        self.children = {}
        self.reaped = set()
        self.locks = {}
        self.closing = False

    def _lock(self, key):
        return self.locks.setdefault(key, asyncio.Lock())

    async def _read(self, process, ready):
        # Drain continuously; do not accumulate logs/secrets in RAM or API errors.
        try:
            pending = b""
            while chunk := await process.stdout.read(65536):
                data = pending + chunk
                if (data.startswith(READY) or b"\n" + READY in data) and not ready.done():
                    ready.set_result(None)
                pending = data[-len(READY):]
        finally:
            if not ready.done():
                ready.set_exception(RuntimeError("Bot exited before readiness"))

    async def _terminate(self, child):
        process = child.process
        if process.returncode is None:
            try:
                process.terminate()
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(process.wait(), self.stop_timeout)
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                await process.wait()
        await asyncio.gather(child.reader, return_exceptions=True)

    async def start(self, key, command, *, cwd, env, on_started, on_exit):
        async with self._lock(key):
            if self.closing:
                raise RuntimeError("Bot supervisor is shutting down")
            existing = self.children.get(key)
            if existing:
                if existing.process.returncode is None:
                    return False
                raise RuntimeError("Previous bot exit is still being reconciled; retry")
            process = await asyncio.create_subprocess_exec(
                *command, cwd=cwd, env=env,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
                limit=1024 * 1024,
            )
            ready = asyncio.get_running_loop().create_future()
            child = Child(process, asyncio.create_task(self._read(process, ready)))
            self.children[key] = child
            self.reaped.discard(key)
            try:
                await asyncio.wait_for(ready, self.startup_timeout)
                if process.returncode is not None:
                    raise RuntimeError("Bot exited during startup")
                await on_started()
            except BaseException:
                ready.cancel()
                await self._terminate(child)
                self.children.pop(key, None)
                self.reaped.add(key)
                raise
            child.monitor = asyncio.create_task(self._monitor(key, child, on_exit))
            return True

    async def _monitor(self, key, child, on_exit):
        code = await child.process.wait()
        await asyncio.gather(child.reader, return_exceptions=True)
        async with self._lock(key):
            if self.children.get(key) is child:
                try:
                    await on_exit(code)
                except Exception:
                    logging.getLogger(__name__).exception("Could not persist bot exit: %s", key)
                finally:
                    self.children.pop(key, None)
                    self.reaped.add(key)

    async def stop(self, key, *, on_stopped, require_owned=False):
        async with self._lock(key):
            child = self.children.get(key)
            if child is None and require_owned and key not in self.reaped:
                raise RuntimeError("Bot process is not owned by this API worker; refusing a false stop")
            if child:
                await self._terminate(child)
                if child.monitor:
                    child.monitor.cancel()
                    await asyncio.gather(child.monitor, return_exceptions=True)
                self.children.pop(key, None)
                self.reaped.add(key)
            # Persist stopped only AFTER the OS confirms child exit.
            await on_stopped()

    async def close(self, on_exit):
        self.closing = True
        errors = []
        for key in list(self.children):
            async def stopped(key=key):
                await on_exit(key)
            try:
                await self.stop(key, on_stopped=stopped)
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise RuntimeError("Failed to persist one or more bot shutdowns") from errors[0]


supervisor = ProcessSupervisor()
