from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
⚡ GAVATCore Advanced Async Task Manager
Enterprise-grade background task processing with priority queues and distributed execution

Features:
- Priority-based task queues
- Distributed task execution
- Task retry mechanisms
- Progress tracking
- Resource management
- Scheduler integration
- Result persistence
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import pickle
import heapq
import threading
from concurrent.futures import ProcessPoolExecutor
import structlog

logger = structlog.get_logger("gavatcore.async_task_manager")

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class TaskStatus(Enum):
    """Task status states."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

@dataclass
class TaskMetadata:
    """Task metadata and configuration."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    
    def __lt__(self, other):
        """Priority comparison for heap queue."""
        return self.priority.value < other.priority.value

@dataclass
class TaskResult:
    """Task execution result."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    progress: float = 0.0
    logs: List[str] = field(default_factory=list)

@dataclass
class TaskDefinition:
    """Complete task definition."""
    metadata: TaskMetadata
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """Priority comparison."""
        return self.metadata < other.metadata

class ProgressTracker:
    """Task progress tracking."""
    
    def __init__(self, task_id: str, total_steps: int = 100):
        self.task_id = task_id
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.messages: List[str] = []
        
    def update(self, step: int, message: str = ""):
        """Update progress."""
        self.current_step = step
        if message:
            self.messages.append(f"{datetime.now().isoformat()}: {message}")
        
        progress = min(step / self.total_steps * 100, 100)
        logger.debug("📊 Task progress updated",
                    task_id=self.task_id,
                    progress=f"{progress:.1f}%",
                    message=message)
    
    def complete(self, message: str = "Task completed"):
        """Mark as complete."""
        self.current_step = self.total_steps
        self.messages.append(f"{datetime.now().isoformat()}: {message}")
        logger.info("✅ Task completed",
                   task_id=self.task_id,
                   duration=time.time() - self.start_time)
    
    @property
    def progress_percent(self) -> float:
        """Get progress percentage."""
        return min(self.current_step / self.total_steps * 100, 100)

class TaskScheduler:
    """Advanced task scheduler with cron-like capabilities."""
    
    def __init__(self):
        self.scheduled_tasks: Dict[str, TaskDefinition] = {}
        self.recurring_tasks: Dict[str, Dict[str, Any]] = {}
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
    async def schedule_task(self, 
                          task_def: TaskDefinition, 
                          schedule_at: datetime):
        """Schedule a task for future execution."""
        task_def.metadata.scheduled_at = schedule_at
        self.scheduled_tasks[task_def.metadata.task_id] = task_def
        
        logger.info("⏰ Task scheduled",
                   task_id=task_def.metadata.task_id,
                   scheduled_at=schedule_at.isoformat())
    
    async def schedule_recurring(self,
                               task_def: TaskDefinition,
                               interval_seconds: int,
                               max_executions: Optional[int] = None):
        """Schedule recurring task."""
        self.recurring_tasks[task_def.metadata.task_id] = {
            'task_def': task_def,
            'interval': interval_seconds,
            'max_executions': max_executions,
            'execution_count': 0,
            'next_execution': datetime.now() + timedelta(seconds=interval_seconds)
        }
        
        logger.info("🔄 Recurring task scheduled",
                   task_id=task_def.metadata.task_id,
                   interval=interval_seconds)
    
    async def start_scheduler(self, task_manager):
        """Start the task scheduler."""
        self.scheduler_running = True
        self.scheduler_task = asyncio.create_task(
            self._scheduler_loop(task_manager)
        )
        logger.info("⏰ Task scheduler started")
    
    async def stop_scheduler(self):
        """Stop the task scheduler."""
        self.scheduler_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("⏰ Task scheduler stopped")
    
    async def _scheduler_loop(self, task_manager):
        """Main scheduler loop."""
        while self.scheduler_running:
            try:
                now = datetime.now()
                
                # Check scheduled tasks
                due_tasks = [
                    task_def for task_def in self.scheduled_tasks.values()
                    if task_def.metadata.scheduled_at and 
                       task_def.metadata.scheduled_at <= now
                ]
                
                for task_def in due_tasks:
                    await task_manager.submit_task(task_def)
                    del self.scheduled_tasks[task_def.metadata.task_id]
                
                # Check recurring tasks
                for task_id, recurring_info in list(self.recurring_tasks.items()):
                    if recurring_info['next_execution'] <= now:
                        # Check execution limit
                        if (recurring_info['max_executions'] is None or 
                            recurring_info['execution_count'] < recurring_info['max_executions']):
                            
                            # Create new task instance
                            task_def = recurring_info['task_def']
                            new_metadata = TaskMetadata(
                                task_type=task_def.metadata.task_type,
                                priority=task_def.metadata.priority,
                                max_retries=task_def.metadata.max_retries,
                                retry_delay=task_def.metadata.retry_delay,
                                timeout=task_def.metadata.timeout,
                                tags=task_def.metadata.tags.copy()
                            )
                            
                            new_task_def = TaskDefinition(
                                metadata=new_metadata,
                                func=task_def.func,
                                args=task_def.args,
                                kwargs=task_def.kwargs
                            )
                            
                            await task_manager.submit_task(new_task_def)
                            
                            # Update recurring info
                            recurring_info['execution_count'] += 1
                            recurring_info['next_execution'] = (
                                now + timedelta(seconds=recurring_info['interval'])
                            )
                        else:
                            # Remove completed recurring task
                            del self.recurring_tasks[task_id]
                            logger.info("🔄 Recurring task completed",
                                       task_id=task_id,
                                       executions=recurring_info['execution_count'])
                
                await asyncio.sleep(1)  # Check every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Scheduler error", error=str(e))
                await asyncio.sleep(5)

class ResourceManager:
    """Manage computational resources for tasks."""
    
    def __init__(self, 
                 max_concurrent_tasks: int = 10,
                 max_memory_mb: int = 1000,
                 max_cpu_percent: float = 80.0):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.current_tasks = 0
        self.resource_lock = asyncio.Lock()
        
    async def acquire_resources(self, 
                              estimated_memory_mb: int = 50,
                              estimated_cpu_percent: float = 10.0) -> bool:
        """Try to acquire resources for task execution."""
        async with self.resource_lock:
            # Check concurrent task limit
            if self.current_tasks >= self.max_concurrent_tasks:
                return False
            
            # Check memory availability (simplified check)
            try:
                import psutil
                memory_info = psutil.virtual_memory()
                available_memory_mb = memory_info.available / (1024 * 1024)
                
                if estimated_memory_mb > available_memory_mb * 0.8:
                    return False
                
                # Check CPU availability
                current_cpu = psutil.cpu_percent(interval=0.1)
                if current_cpu + estimated_cpu_percent > self.max_cpu_percent:
                    return False
                    
            except ImportError:
                # psutil not available, allow execution
                pass
            
            self.current_tasks += 1
            return True
    
    async def release_resources(self):
        """Release resources after task completion."""
        async with self.resource_lock:
            self.current_tasks = max(0, self.current_tasks - 1)
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource usage status."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            
            return {
                "concurrent_tasks": self.current_tasks,
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory_info.percent,
                "available_memory_gb": memory_info.available / (1024**3),
                "resource_pressure": (
                    self.current_tasks / self.max_concurrent_tasks * 100
                )
            }
        except ImportError:
            return {
                "concurrent_tasks": self.current_tasks,
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "resource_pressure": (
                    self.current_tasks / self.max_concurrent_tasks * 100
                )
            }

class AdvancedAsyncTaskManager:
    """
    ⚡ Advanced Async Task Manager
    Comprehensive task management with enterprise features.
    """
    
    def __init__(self, 
                 max_workers: int = 50,
                 max_concurrent_tasks: int = 20):
        self.max_workers = max_workers
        self.task_queue = []  # Priority heap queue
        self.active_tasks: Dict[str, TaskDefinition] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.progress_trackers: Dict[str, ProgressTracker] = {}
        
        # Components
        self.scheduler = TaskScheduler()
        self.resource_manager = ResourceManager(max_concurrent_tasks)
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.worker_stats = {
            'tasks_processed': 0,
            'tasks_failed': 0,
            'average_execution_time': 0.0
        }
        
        # Thread pool for CPU-intensive tasks
        self.process_executor = ProcessPoolExecutor(max_workers=4)
        
    async def start(self):
        """Start the task manager."""
        self.running = True
        
        # Start workers
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        
        # Start scheduler
        await self.scheduler.start_scheduler(self)
        
        logger.info("⚡ Advanced Task Manager started",
                   workers=self.max_workers,
                   max_concurrent=self.resource_manager.max_concurrent_tasks)
    
    async def stop(self):
        """Stop the task manager."""
        self.running = False
        
        # Stop scheduler
        await self.scheduler.stop_scheduler()
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Shutdown process executor
        self.process_executor.shutdown(wait=True)
        
        logger.info("⚡ Advanced Task Manager stopped")
    
    async def submit_task(self, 
                         task_def: Optional[TaskDefinition] = None,
                         func: Optional[Callable] = None,
                         *args,
                         task_type: str = "generic",
                         priority: TaskPriority = TaskPriority.NORMAL,
                         timeout: Optional[float] = None,
                         max_retries: int = 3,
                         tags: Optional[List[str]] = None,
                         **kwargs) -> str:
        """Submit task for async processing."""
        
        if task_def is None:
            if func is None:
                raise ValueError("Either task_def or func must be provided")
            
            metadata = TaskMetadata(
                task_type=task_type,
                priority=priority,
                timeout=timeout,
                max_retries=max_retries,
                tags=tags or []
            )
            
            task_def = TaskDefinition(
                metadata=metadata,
                func=func,
                args=args,
                kwargs=kwargs
            )
        
        # Create task result
        task_result = TaskResult(
            task_id=task_def.metadata.task_id,
            status=TaskStatus.QUEUED
        )
        self.task_results[task_def.metadata.task_id] = task_result
        
        # Add to priority queue
        heapq.heappush(self.task_queue, task_def)
        
        logger.info("📝 Task submitted",
                   task_id=task_def.metadata.task_id,
                   task_type=task_def.metadata.task_type,
                   priority=task_def.metadata.priority.name)
        
        return task_def.metadata.task_id
    
    async def get_task_result(self, 
                            task_id: str, 
                            timeout: Optional[float] = None) -> Optional[TaskResult]:
        """Get task result (blocking until complete or timeout)."""
        start_time = time.time()
        
        while True:
            if task_id in self.task_results:
                result = self.task_results[task_id]
                if result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    return result
            
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            await asyncio.sleep(0.1)
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get current task status."""
        return self.task_results.get(task_id)
    
    def get_task_progress(self, task_id: str) -> Optional[ProgressTracker]:
        """Get task progress tracker."""
        return self.progress_trackers.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        # Check if task is in queue
        for i, task_def in enumerate(self.task_queue):
            if task_def.metadata.task_id == task_id:
                del self.task_queue[i]
                heapq.heapify(self.task_queue)
                
                result = self.task_results.get(task_id)
                if result:
                    result.status = TaskStatus.CANCELLED
                
                logger.info("🚫 Task cancelled (queued)",
                           task_id=task_id)
                return True
        
        # Check if task is active
        if task_id in self.active_tasks:
            result = self.task_results.get(task_id)
            if result:
                result.status = TaskStatus.CANCELLED
                
            logger.info("🚫 Task cancelled (running)",
                       task_id=task_id)
            return True
        
        return False
    
    async def schedule_task(self, 
                          task_def: TaskDefinition,
                          schedule_at: datetime):
        """Schedule task for future execution."""
        await self.scheduler.schedule_task(task_def, schedule_at)
    
    async def schedule_recurring_task(self,
                                    task_def: TaskDefinition,
                                    interval_seconds: int,
                                    max_executions: Optional[int] = None):
        """Schedule recurring task."""
        await self.scheduler.schedule_recurring(
            task_def, interval_seconds, max_executions
        )
    
    def create_progress_tracker(self, 
                              task_id: str, 
                              total_steps: int = 100) -> ProgressTracker:
        """Create progress tracker for task."""
        tracker = ProgressTracker(task_id, total_steps)
        self.progress_trackers[task_id] = tracker
        return tracker
    
    async def _worker(self, worker_name: str):
        """Task worker coroutine."""
        logger.debug("👷 Worker started", worker_name=worker_name)
        
        while self.running:
            try:
                # Get task from priority queue
                if not self.task_queue:
                    await asyncio.sleep(0.1)
                    continue
                
                task_def = heapq.heappop(self.task_queue)
                
                # Check dependencies
                if not await self._check_dependencies(task_def):
                    # Re-queue task
                    heapq.heappush(self.task_queue, task_def)
                    await asyncio.sleep(1)
                    continue
                
                # Try to acquire resources
                if not await self.resource_manager.acquire_resources():
                    # Re-queue task
                    heapq.heappush(self.task_queue, task_def)
                    await asyncio.sleep(1)
                    continue
                
                # Process task
                await self._process_task(task_def, worker_name)
                
                # Release resources
                await self.resource_manager.release_resources()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Worker error",
                           worker_name=worker_name,
                           error=str(e))
                await asyncio.sleep(1)
        
        logger.debug("👷 Worker stopped", worker_name=worker_name)
    
    async def _check_dependencies(self, task_def: TaskDefinition) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_task_id in task_def.metadata.dependencies:
            dep_result = self.task_results.get(dep_task_id)
            if not dep_result or dep_result.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _process_task(self, task_def: TaskDefinition, worker_name: str):
        """Process individual task."""
        task_id = task_def.metadata.task_id
        result = self.task_results[task_id]
        
        logger.info("🔄 Processing task",
                   task_id=task_id,
                   worker_name=worker_name,
                   task_type=task_def.metadata.task_type)
        
        # Update status and timing
        result.status = TaskStatus.RUNNING
        result.started_at = datetime.now()
        
        # Add to active tasks
        self.active_tasks[task_id] = task_def
        
        try:
            # Setup timeout if specified
            if task_def.metadata.timeout:
                task_coro = asyncio.wait_for(
                    self._execute_task(task_def),
                    timeout=task_def.metadata.timeout
                )
            else:
                task_coro = self._execute_task(task_def)
            
            # Execute task
            task_result = await task_coro
            
            # Update result
            result.status = TaskStatus.COMPLETED
            result.result = task_result
            result.completed_at = datetime.now()
            result.execution_time = (
                result.completed_at - result.started_at
            ).total_seconds()
            
            # Update stats
            self.worker_stats['tasks_processed'] += 1
            current_avg = self.worker_stats['average_execution_time']
            task_count = self.worker_stats['tasks_processed']
            self.worker_stats['average_execution_time'] = (
                (current_avg * (task_count - 1) + result.execution_time) / task_count
            )
            
            logger.info("✅ Task completed",
                       task_id=task_id,
                       execution_time=result.execution_time,
                       worker_name=worker_name)
            
        except asyncio.TimeoutError:
            result.status = TaskStatus.FAILED
            result.error = "Task timeout"
            result.completed_at = datetime.now()
            
            logger.error("⏰ Task timeout",
                        task_id=task_id,
                        timeout=task_def.metadata.timeout)
            
            # Retry logic
            await self._handle_task_retry(task_def, result)
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()
            
            self.worker_stats['tasks_failed'] += 1
            
            logger.error("❌ Task failed",
                        task_id=task_id,
                        error=str(e),
                        worker_name=worker_name)
            
            # Retry logic
            await self._handle_task_retry(task_def, result)
        
        finally:
            # Remove from active tasks
            self.active_tasks.pop(task_id, None)
    
    async def _execute_task(self, task_def: TaskDefinition) -> Any:
        """Execute the actual task function."""
        func = task_def.func
        args = task_def.args
        kwargs = task_def.kwargs
        
        # Determine execution method
        if asyncio.iscoroutinefunction(func):
            # Async function
            return await func(*args, **kwargs)
        else:
            # Sync function - run in thread pool or process pool
            cpu_intensive_tasks = ['data_analysis', 'batch_processing', 'computation']
            
            if task_def.metadata.task_type in cpu_intensive_tasks:
                # Use process pool for CPU-intensive tasks
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    self.process_executor, func, *args
                )
            else:
                # Use thread pool for I/O tasks
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, func, *args)
    
    async def _handle_task_retry(self, task_def: TaskDefinition, result: TaskResult):
        """Handle task retry logic."""
        if result.retry_count < task_def.metadata.max_retries:
            result.retry_count += 1
            result.status = TaskStatus.RETRYING
            
            # Add delay before retry
            await asyncio.sleep(
                task_def.metadata.retry_delay * (2 ** result.retry_count)
            )
            
            # Re-queue task
            heapq.heappush(self.task_queue, task_def)
            
            logger.info("🔄 Task retry scheduled",
                       task_id=task_def.metadata.task_id,
                       retry_count=result.retry_count,
                       max_retries=task_def.metadata.max_retries)
    
    def get_manager_status(self) -> Dict[str, Any]:
        """Get comprehensive manager status."""
        return {
            "running": self.running,
            "active_workers": len(self.workers),
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len([
                r for r in self.task_results.values() 
                if r.status == TaskStatus.COMPLETED
            ]),
            "failed_tasks": len([
                r for r in self.task_results.values()
                if r.status == TaskStatus.FAILED
            ]),
            "worker_stats": self.worker_stats,
            "resource_status": self.resource_manager.get_resource_status(),
            "scheduled_tasks": len(self.scheduler.scheduled_tasks),
            "recurring_tasks": len(self.scheduler.recurring_tasks)
        }

# Global task manager instance
_global_task_manager: Optional[AdvancedAsyncTaskManager] = None

def get_task_manager() -> AdvancedAsyncTaskManager:
    """Get global task manager instance."""
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = AdvancedAsyncTaskManager()
    return _global_task_manager

async def initialize_task_manager() -> AdvancedAsyncTaskManager:
    """Initialize global task manager."""
    manager = get_task_manager()
    await manager.start()
    return manager

async def shutdown_task_manager():
    """Shutdown global task manager."""
    global _global_task_manager
    if _global_task_manager:
        await _global_task_manager.stop()
        _global_task_manager = None