"""
Scheduler Engine
===============

Advanced background task scheduler with dynamic spam protection and Redis state management.
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from croniter import croniter

from .config import get_settings
from .logger import LoggerMixin
from .redis_state import redis_state
from .message_pool import message_pool, Message, MessageType, MessagePriority


class TaskType(Enum):
    """Task types."""
    SCHEDULED_MESSAGE = "scheduled_message"
    GROUP_BROADCAST = "group_broadcast" 
    RECURRING_MESSAGE = "recurring_message"
    SPAM_PROTECTION = "spam_protection"
    COOLDOWN_RESET = "cooldown_reset"


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class GroupConfig:
    """Group-specific configuration."""
    group_id: int
    interval_min: int = 300  # 5 minutes default
    interval_max: int = 900  # 15 minutes default
    cooldown_min: int = 120  # 2 minutes default
    cooldown_max: int = 300  # 5 minutes default
    max_messages_per_hour: int = 12
    spam_protection_enabled: bool = True
    random_delay_enabled: bool = True
    priority_multiplier: float = 1.0
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroupConfig":
        return cls(**data)


@dataclass
class ScheduledTask:
    """Scheduled task definition."""
    id: str
    task_type: TaskType
    scheduled_at: datetime
    group_id: Optional[int] = None
    bot_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    
    # Recurring settings
    recurring: bool = False
    cron_expression: Optional[str] = None
    recurring_interval: Optional[int] = None  # seconds
    max_executions: Optional[int] = None
    execution_count: int = 0
    
    # Task data
    task_data: Dict[str, Any] = None
    
    # Timing
    created_at: datetime = None
    last_executed_at: Optional[datetime] = None
    next_execution_at: Optional[datetime] = None
    
    # Error handling
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.task_data is None:
            self.task_data = {}
        if isinstance(self.task_type, str):
            self.task_type = TaskType(self.task_type)
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
        if isinstance(self.scheduled_at, str):
            self.scheduled_at = datetime.fromisoformat(self.scheduled_at)
        if self.created_at and isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if self.last_executed_at and isinstance(self.last_executed_at, str):
            self.last_executed_at = datetime.fromisoformat(self.last_executed_at)
        if self.next_execution_at and isinstance(self.next_execution_at, str):
            self.next_execution_at = datetime.fromisoformat(self.next_execution_at)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['status'] = self.status.value
        data['scheduled_at'] = self.scheduled_at.isoformat()
        data['created_at'] = self.created_at.isoformat()
        if self.last_executed_at:
            data['last_executed_at'] = self.last_executed_at.isoformat()
        if self.next_execution_at:
            data['next_execution_at'] = self.next_execution_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScheduledTask":
        return cls(**data)
    
    def calculate_next_execution(self) -> Optional[datetime]:
        """Calculate next execution time for recurring tasks."""
        if not self.recurring:
            return None
        
        now = datetime.utcnow()
        
        if self.cron_expression:
            # Use cron expression
            try:
                cron = croniter(self.cron_expression, now)
                return cron.get_next(datetime)
            except Exception:
                return None
        elif self.recurring_interval:
            # Use interval
            base_time = self.last_executed_at or self.created_at
            return base_time + timedelta(seconds=self.recurring_interval)
        
        return None


class SpamProtection:
    """Dynamic spam protection system."""
    
    def __init__(self):
        self.group_states: Dict[int, Dict[str, Any]] = {}
        self.bot_states: Dict[str, Dict[str, Any]] = {}
    
    async def calculate_delay(
        self, 
        group_id: int, 
        bot_id: str, 
        config: GroupConfig
    ) -> float:
        """Calculate dynamic delay with spam protection."""
        
        # Get current states
        group_state = await self._get_group_state(group_id)
        bot_state = await self._get_bot_state(bot_id)
        
        # Base delay from config
        if config.random_delay_enabled:
            base_delay = random.uniform(config.interval_min, config.interval_max)
        else:
            base_delay = config.interval_min
        
        # Apply spam protection multipliers
        spam_multiplier = 1.0
        
        if config.spam_protection_enabled:
            # Check recent message frequency
            recent_messages = group_state.get('recent_messages', 0)
            if recent_messages > config.max_messages_per_hour:
                spam_multiplier *= 1.5  # Slow down if too many messages
            
            # Check if in cooldown
            cooldown_until = group_state.get('cooldown_until')
            if cooldown_until:
                cooldown_time = datetime.fromisoformat(cooldown_until)
                if datetime.utcnow() < cooldown_time:
                    remaining = (cooldown_time - datetime.utcnow()).total_seconds()
                    return max(base_delay, remaining)
            
            # Global bot rate limiting
            bot_message_count = bot_state.get('hourly_messages', 0)
            if bot_message_count > 20:  # Global limit
                spam_multiplier *= 2.0
        
        # Apply priority multiplier
        final_delay = base_delay * spam_multiplier * config.priority_multiplier
        
        # Add random jitter (±20%)
        jitter = random.uniform(0.8, 1.2)
        final_delay *= jitter
        
        return max(1.0, final_delay)  # Minimum 1 second
    
    async def apply_cooldown(
        self, 
        group_id: int, 
        config: GroupConfig
    ) -> None:
        """Apply cooldown to a group."""
        cooldown_duration = random.uniform(
            config.cooldown_min, 
            config.cooldown_max
        )
        
        cooldown_until = datetime.utcnow() + timedelta(seconds=cooldown_duration)
        
        await redis_state.hset(
            f"scheduler:group_state:{group_id}",
            "cooldown_until",
            cooldown_until.isoformat()
        )
        
        await redis_state.expire(f"scheduler:group_state:{group_id}", 3600)  # 1 hour
    
    async def increment_message_count(
        self, 
        group_id: int, 
        bot_id: str
    ) -> None:
        """Increment message counters."""
        
        # Group counter
        await redis_state.hincrby(f"scheduler:group_state:{group_id}", "recent_messages", 1)
        await redis_state.expire(f"scheduler:group_state:{group_id}", 3600)
        
        # Bot counter
        await redis_state.hincrby(f"scheduler:bot_state:{bot_id}", "hourly_messages", 1)
        await redis_state.expire(f"scheduler:bot_state:{bot_id}", 3600)
        
        # Store last message time
        now = datetime.utcnow().isoformat()
        await redis_state.hset(f"scheduler:group_state:{group_id}", "last_message_at", now)
        await redis_state.hset(f"scheduler:bot_state:{bot_id}", "last_message_at", now)
    
    async def _get_group_state(self, group_id: int) -> Dict[str, Any]:
        """Get group state from Redis."""
        state = await redis_state.hgetall(f"scheduler:group_state:{group_id}")
        return {k.decode() if isinstance(k, bytes) else k: 
                v.decode() if isinstance(v, bytes) else v 
                for k, v in state.items()} if state else {}
    
    async def _get_bot_state(self, bot_id: str) -> Dict[str, Any]:
        """Get bot state from Redis."""
        state = await redis_state.hgetall(f"scheduler:bot_state:{bot_id}")
        return {k.decode() if isinstance(k, bytes) else k: 
                v.decode() if isinstance(v, bytes) else v 
                for k, v in state.items()} if state else {}


class SchedulerEngine(LoggerMixin):
    """Advanced scheduler engine with spam protection."""
    
    def __init__(self):
        self.settings = get_settings()
        self.is_running = False
        self.tasks: Dict[str, ScheduledTask] = {}
        self.group_configs: Dict[int, GroupConfig] = {}
        self.spam_protection = SpamProtection()
        self.background_tasks: List[asyncio.Task] = []
        
        # Task handlers
        self.task_handlers: Dict[TaskType, Callable] = {
            TaskType.SCHEDULED_MESSAGE: self._handle_scheduled_message,
            TaskType.GROUP_BROADCAST: self._handle_group_broadcast,
            TaskType.RECURRING_MESSAGE: self._handle_recurring_message,
            TaskType.SPAM_PROTECTION: self._handle_spam_protection,
            TaskType.COOLDOWN_RESET: self._handle_cooldown_reset,
        }
    
    async def initialize(self) -> None:
        """Initialize scheduler engine."""
        self.log_event("Initializing scheduler engine")
        
        # Load tasks from Redis
        await self._load_tasks_from_redis()
        
        # Load group configurations
        await self._load_group_configs()
        
        self.log_event("Scheduler engine initialized", task_count=len(self.tasks))
    
    async def start(self) -> None:
        """Start the scheduler engine."""
        if self.is_running:
            return
        
        self.log_event("Starting scheduler engine")
        self.is_running = True
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._scheduler_loop()),
            asyncio.create_task(self._cleanup_loop()),
            asyncio.create_task(self._stats_update_loop()),
        ]
        
        self.log_event("Scheduler engine started")
    
    async def stop(self) -> None:
        """Stop the scheduler engine."""
        if not self.is_running:
            return
        
        self.log_event("Stopping scheduler engine")
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Save tasks to Redis
        await self._save_tasks_to_redis()
        
        self.log_event("Scheduler engine stopped")
    
    async def add_task(self, task: ScheduledTask) -> str:
        """Add a new scheduled task."""
        if isinstance(task, dict):
            task = ScheduledTask.from_dict(task)
        
        # Calculate next execution for recurring tasks
        if task.recurring:
            task.next_execution_at = task.calculate_next_execution()
        
        self.tasks[task.id] = task
        
        # Save to Redis
        await self._save_task_to_redis(task)
        
        self.log_event(
            "Task added",
            task_id=task.id,
            task_type=task.task_type.value,
            scheduled_at=task.scheduled_at.isoformat(),
            recurring=task.recurring,
        )
        
        return task.id
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.CANCELLED
        
        await self._save_task_to_redis(task)
        
        self.log_event("Task cancelled", task_id=task_id)
        return True
    
    async def pause_task(self, task_id: str) -> bool:
        """Pause a scheduled task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.PAUSED
        
        await self._save_task_to_redis(task)
        
        self.log_event("Task paused", task_id=task_id)
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status == TaskStatus.PAUSED:
            task.status = TaskStatus.PENDING
            await self._save_task_to_redis(task)
            
            self.log_event("Task resumed", task_id=task_id)
            return True
        
        return False
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        return [task.to_dict() for task in self.tasks.values()]
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task."""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None
    
    async def update_group_config(
        self, 
        group_id: int, 
        config: GroupConfig
    ) -> None:
        """Update group configuration."""
        self.group_configs[group_id] = config
        
        # Save to Redis
        await redis_state.hset(
            "scheduler:group_configs",
            str(group_id),
            json.dumps(config.to_dict())
        )
        
        self.log_event("Group config updated", group_id=group_id)
    
    async def get_group_config(self, group_id: int) -> GroupConfig:
        """Get group configuration."""
        if group_id not in self.group_configs:
            # Create default config
            config = GroupConfig(group_id=group_id)
            await self.update_group_config(group_id, config)
            return config
        
        return self.group_configs[group_id]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(
                1 for task in self.tasks.values() 
                if task.status == status
            )
        
        return {
            "is_running": self.is_running,
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "group_configs": len(self.group_configs),
            "background_tasks": len(self.background_tasks),
        }
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.is_running:
            try:
                await self._process_ready_tasks()
                await asyncio.sleep(1.0)  # Check every second
                
            except Exception as e:
                self.log_error("Scheduler loop error", error=str(e))
                await asyncio.sleep(5.0)  # Wait before retrying
    
    async def _process_ready_tasks(self) -> None:
        """Process tasks that are ready to run."""
        now = datetime.utcnow()
        
        ready_tasks = [
            task for task in self.tasks.values()
            if (task.status == TaskStatus.PENDING and 
                task.scheduled_at <= now)
        ]
        
        for task in ready_tasks:
            try:
                await self._execute_task(task)
            except Exception as e:
                self.log_error(
                    "Task execution error",
                    task_id=task.id,
                    error=str(e),
                )
                await self._handle_task_failure(task, str(e))
    
    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.execution_count += 1
        task.last_executed_at = datetime.utcnow()
        
        self.log_event(
            "Executing task",
            task_id=task.id,
            task_type=task.task_type.value,
            execution_count=task.execution_count,
        )
        
        try:
            # Get task handler
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.task_type}")
            
            # Execute task
            await handler(task)
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            
            # Handle recurring tasks
            if task.recurring:
                await self._handle_recurring_task(task)
            
            await self._save_task_to_redis(task)
            
            self.log_event(
                "Task completed",
                task_id=task.id,
                execution_count=task.execution_count,
            )
            
        except Exception as e:
            await self._handle_task_failure(task, str(e))
    
    async def _handle_task_failure(self, task: ScheduledTask, error: str) -> None:
        """Handle task execution failure."""
        task.status = TaskStatus.FAILED
        task.last_error = error
        task.retry_count += 1
        
        # Retry logic
        if task.retry_count < task.max_retries:
            # Schedule retry with exponential backoff
            retry_delay = (2 ** task.retry_count) * 60  # 2, 4, 8 minutes
            task.scheduled_at = datetime.utcnow() + timedelta(seconds=retry_delay)
            task.status = TaskStatus.PENDING
            
            self.log_event(
                "Task scheduled for retry",
                task_id=task.id,
                retry_count=task.retry_count,
                retry_delay=retry_delay,
            )
        else:
            self.log_error(
                "Task failed permanently",
                task_id=task.id,
                error=error,
                retry_count=task.retry_count,
            )
        
        await self._save_task_to_redis(task)
    
    async def _handle_recurring_task(self, task: ScheduledTask) -> None:
        """Handle recurring task completion."""
        if not task.recurring:
            return
        
        # Check max executions
        if task.max_executions and task.execution_count >= task.max_executions:
            task.status = TaskStatus.COMPLETED
            task.recurring = False
            return
        
        # Calculate next execution
        next_execution = task.calculate_next_execution()
        if next_execution:
            # Create new task for next execution
            new_task = ScheduledTask(
                id=str(uuid.uuid4()),
                task_type=task.task_type,
                scheduled_at=next_execution,
                group_id=task.group_id,
                bot_id=task.bot_id,
                recurring=task.recurring,
                cron_expression=task.cron_expression,
                recurring_interval=task.recurring_interval,
                max_executions=task.max_executions,
                task_data=task.task_data.copy(),
            )
            
            await self.add_task(new_task)
    
    async def _handle_scheduled_message(self, task: ScheduledTask) -> None:
        """Handle scheduled message task."""
        data = task.task_data
        
        # Apply spam protection delay if needed
        if task.group_id:
            config = await self.get_group_config(task.group_id)
            if config.spam_protection_enabled:
                delay = await self.spam_protection.calculate_delay(
                    task.group_id, 
                    task.bot_id or "default",
                    config
                )
                
                if delay > 1.0:
                    # Reschedule with delay
                    task.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
                    task.status = TaskStatus.PENDING
                    return
        
        # Create message
        message = Message(
            type=MessageType(data.get("message_type", "direct_message")),
            priority=MessagePriority(data.get("priority", "normal")),
            content=data["content"],
            target_chat_id=data.get("target_chat_id"),
            target_username=data.get("target_username"),
            bot_id=task.bot_id,
            context={
                "task_id": task.id,
                "scheduled_at": task.scheduled_at.isoformat(),
                "execution_count": task.execution_count,
            },
        )
        
        # Add to message pool
        message_id = await message_pool.add_message(message)
        
        # Update spam protection counters
        if task.group_id:
            await self.spam_protection.increment_message_count(
                task.group_id,
                task.bot_id or "default"
            )
        
        self.log_event(
            "Scheduled message queued",
            task_id=task.id,
            message_id=message_id,
            group_id=task.group_id,
        )
    
    async def _handle_group_broadcast(self, task: ScheduledTask) -> None:
        """Handle group broadcast task."""
        # Similar to scheduled message but for multiple groups
        await self._handle_scheduled_message(task)
    
    async def _handle_recurring_message(self, task: ScheduledTask) -> None:
        """Handle recurring message task."""
        await self._handle_scheduled_message(task)
    
    async def _handle_spam_protection(self, task: ScheduledTask) -> None:
        """Handle spam protection task."""
        # Reset message counters or apply cooldowns
        pass
    
    async def _handle_cooldown_reset(self, task: ScheduledTask) -> None:
        """Handle cooldown reset task."""
        if task.group_id:
            await redis_state.hdel(
                f"scheduler:group_state:{task.group_id}",
                "cooldown_until"
            )
    
    async def _cleanup_loop(self) -> None:
        """Cleanup completed and old tasks."""
        while self.is_running:
            try:
                await self._cleanup_tasks()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                self.log_error("Cleanup loop error", error=str(e))
                await asyncio.sleep(60)
    
    async def _cleanup_tasks(self) -> None:
        """Remove old completed tasks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        tasks_to_remove = [
            task_id for task_id, task in self.tasks.items()
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and
                task.last_executed_at and task.last_executed_at < cutoff_time)
        ]
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            await redis_state.hdel("scheduler:tasks", task_id)
        
        if tasks_to_remove:
            self.log_event("Cleaned up old tasks", count=len(tasks_to_remove))
    
    async def _stats_update_loop(self) -> None:
        """Update statistics periodically."""
        while self.is_running:
            try:
                stats = await self.get_stats()
                await redis_state.hset(
                    "scheduler:stats",
                    "current",
                    json.dumps(stats)
                )
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                self.log_error("Stats update error", error=str(e))
                await asyncio.sleep(60)
    
    async def _load_tasks_from_redis(self) -> None:
        """Load tasks from Redis."""
        try:
            tasks_data = await redis_state.hgetall("scheduler:tasks")
            
            for task_id, task_json in tasks_data.items():
                if isinstance(task_id, bytes):
                    task_id = task_id.decode()
                if isinstance(task_json, bytes):
                    task_json = task_json.decode()
                
                try:
                    task_dict = json.loads(task_json)
                    task = ScheduledTask.from_dict(task_dict)
                    self.tasks[task_id] = task
                except Exception as e:
                    self.log_error(
                        "Failed to load task from Redis",
                        task_id=task_id,
                        error=str(e),
                    )
            
            self.log_event("Tasks loaded from Redis", count=len(self.tasks))
            
        except Exception as e:
            self.log_error("Failed to load tasks from Redis", error=str(e))
    
    async def _save_tasks_to_redis(self) -> None:
        """Save all tasks to Redis."""
        try:
            tasks_data = {
                task_id: json.dumps(task.to_dict())
                for task_id, task in self.tasks.items()
            }
            
            if tasks_data:
                await redis_state.hmset("scheduler:tasks", tasks_data)
            
            self.log_event("Tasks saved to Redis", count=len(tasks_data))
            
        except Exception as e:
            self.log_error("Failed to save tasks to Redis", error=str(e))
    
    async def _save_task_to_redis(self, task: ScheduledTask) -> None:
        """Save single task to Redis."""
        try:
            await redis_state.hset(
                "scheduler:tasks",
                task.id,
                json.dumps(task.to_dict())
            )
        except Exception as e:
            self.log_error(
                "Failed to save task to Redis",
                task_id=task.id,
                error=str(e),
            )
    
    async def _load_group_configs(self) -> None:
        """Load group configurations from Redis."""
        try:
            configs_data = await redis_state.hgetall("scheduler:group_configs")
            
            for group_id, config_json in configs_data.items():
                if isinstance(group_id, bytes):
                    group_id = group_id.decode()
                if isinstance(config_json, bytes):
                    config_json = config_json.decode()
                
                try:
                    config_dict = json.loads(config_json)
                    config = GroupConfig.from_dict(config_dict)
                    self.group_configs[int(group_id)] = config
                except Exception as e:
                    self.log_error(
                        "Failed to load group config",
                        group_id=group_id,
                        error=str(e),
                    )
            
            self.log_event("Group configs loaded", count=len(self.group_configs))
            
        except Exception as e:
            self.log_error("Failed to load group configs", error=str(e))


# Global scheduler engine instance
scheduler_engine = SchedulerEngine()
