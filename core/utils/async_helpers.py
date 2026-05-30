#!/usr/bin/env python3
"""
Async Helper Utilities
Replace blocking operations with async alternatives
"""

import asyncio
import subprocess
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger("gavatcore.async_helpers")


async def run_subprocess_async(
    command: List[str], timeout: Optional[float] = None, capture_output: bool = True
) -> Tuple[int, str, str]:
    """
    Run subprocess asynchronously instead of blocking subprocess.run()

    Args:
        command: Command and arguments as list
        timeout: Optional timeout in seconds
        capture_output: Whether to capture stdout/stderr

    Returns:
        (return_code, stdout, stderr)
    """
    try:
        if capture_output:
            process = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
        else:
            process = await asyncio.create_subprocess_exec(*command)

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

            stdout_str = stdout.decode("utf-8") if stdout else ""
            stderr_str = stderr.decode("utf-8") if stderr else ""

            return process.returncode, stdout_str, stderr_str

        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise asyncio.TimeoutError(f"Command timed out after {timeout}s")

    except Exception as e:
        logger.error(f"Subprocess execution failed: {e}")
        raise


async def sleep_async(seconds: float) -> None:
    """
    Async sleep replacement for time.sleep()

    Args:
        seconds: Sleep duration in seconds
    """
    await asyncio.sleep(seconds)


class AsyncTaskManager:
    """Manager for async tasks to replace threading patterns"""

    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}
        self._task_results: Dict[str, Any] = {}

    async def run_task(self, name: str, coro, timeout: Optional[float] = None) -> Any:
        """
        Run async task with optional timeout

        Args:
            name: Task identifier
            coro: Coroutine to run
            timeout: Optional timeout in seconds

        Returns:
            Task result
        """
        try:
            if timeout:
                result = await asyncio.wait_for(coro, timeout=timeout)
            else:
                result = await coro

            self._task_results[name] = result
            return result

        except asyncio.TimeoutError:
            logger.warning(f"Task {name} timed out after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"Task {name} failed: {e}")
            raise

    async def run_background_task(self, name: str, coro) -> asyncio.Task:
        """
        Run task in background (replacement for threading.Thread)

        Args:
            name: Task identifier
            coro: Coroutine to run

        Returns:
            Task object
        """
        if name in self._tasks and not self._tasks[name].done():
            logger.warning(f"Task {name} already running")
            return self._tasks[name]

        task = asyncio.create_task(coro)
        self._tasks[name] = task

        # Add done callback for cleanup
        task.add_done_callback(lambda t: self._on_task_done(name, t))

        logger.info(f"Background task started: {name}")
        return task

    def _on_task_done(self, name: str, task: asyncio.Task) -> None:
        """Handle task completion"""
        try:
            # Check cancelled first - calling exception() on cancelled task raises CancelledError
            if task.cancelled():
                logger.info(f"Background task {name} was cancelled")
                return

            exc = task.exception()
            if exc is not None:
                logger.error(f"Background task {name} failed: {exc}")
            else:
                result = task.result()
                self._task_results[name] = result
                logger.info(f"Background task {name} completed successfully")
        except asyncio.CancelledError:
            logger.info(f"Background task {name} was cancelled")
        except Exception as e:
            logger.error(f"Error handling task completion for {name}: {e}")

    async def wait_for_task(self, name: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for background task to complete

        Args:
            name: Task identifier
            timeout: Optional timeout in seconds

        Returns:
            Task result
        """
        if name not in self._tasks:
            raise ValueError(f"Task {name} not found")

        task = self._tasks[name]

        if timeout:
            result = await asyncio.wait_for(task, timeout=timeout)
        else:
            result = await task

        # Store the result and return it directly
        self._task_results[name] = result
        return result

    async def cancel_task(self, name: str) -> bool:
        """
        Cancel background task

        Args:
            name: Task identifier

        Returns:
            True if task was cancelled
        """
        if name not in self._tasks:
            return False

        task = self._tasks[name]
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            logger.info(f"Task cancelled: {name}")
            return True

        return False

    async def cancel_all_tasks(self) -> None:
        """Cancel all running tasks"""
        cancelled_tasks = []

        for name, task in self._tasks.items():
            if not task.done():
                task.cancel()
                cancelled_tasks.append(task)

        if cancelled_tasks:
            await asyncio.gather(*cancelled_tasks, return_exceptions=True)
            logger.info(f"Cancelled {len(cancelled_tasks)} background tasks")

    def get_task_status(self) -> Dict[str, str]:
        """Get status of all tasks"""
        status = {}

        for name, task in self._tasks.items():
            if task.done():
                if task.cancelled():
                    status[name] = "cancelled"
                elif task.exception():
                    status[name] = f"failed: {task.exception()}"
                else:
                    status[name] = "completed"
            else:
                status[name] = "running"

        return status


# Global task manager
_task_manager: Optional[AsyncTaskManager] = None


def get_task_manager() -> AsyncTaskManager:
    """Get global task manager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager()
    return _task_manager
