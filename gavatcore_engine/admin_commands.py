"""
Admin Commands
=============

Admin command handlers for system management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from .config import get_settings
from .logger import LoggerMixin
from .redis_state import redis_state
from .scheduler_engine import scheduler_engine, ScheduledTask, TaskType


class AdminCommandHandler(LoggerMixin):
    """Admin command handler for system management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis = redis_state
        self.scheduler = scheduler_engine
    
    async def handle_command(self, command: str, args: Dict[str, Any], admin_user_id: int) -> Dict[str, Any]:
        """Handle admin command."""
        if admin_user_id not in self.settings.admin_user_ids:
            return {
                "success": False,
                "error": "Unauthorized: Admin access required",
            }
        
        self.log_event(
            "Admin command received",
            command=command,
            admin_user_id=admin_user_id,
            args=args,
        )
        
        # Route command to appropriate handler
        handlers = {
            "status": self._handle_status,
            "stats": self._handle_stats,
            "schedule_message": self._handle_schedule_message,
            "cancel_task": self._handle_cancel_task,
            "list_tasks": self._handle_list_tasks,
            "bot_status": self._handle_bot_status,
            "clear_queue": self._handle_clear_queue,
            "emergency_stop": self._handle_emergency_stop,
            "restart_scheduler": self._handle_restart_scheduler,
        }
        
        handler = handlers.get(command)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": list(handlers.keys()),
            }
        
        try:
            result = await handler(args)
            self.log_event("Admin command completed", command=command, success=True)
            return result
        except Exception as e:
            self.log_error(
                "Admin command failed",
                command=command,
                error=str(e),
            )
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _handle_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status command."""
        return {
            "success": True,
            "data": {
                "system_status": "healthy",
                "scheduler_running": self.scheduler.is_running,
                "redis_connected": self.redis.redis is not None,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    
    async def _handle_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stats command."""
        scheduler_stats = await self.scheduler.get_scheduler_stats()
        
        # Get Redis stats
        active_sessions = await self.redis.get_active_sessions()
        
        return {
            "success": True,
            "data": {
                "scheduler_stats": scheduler_stats,
                "active_sessions": len(active_sessions),
                "session_list": list(active_sessions),
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    
    async def _handle_schedule_message(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schedule message command."""
        required_fields = ["content", "bot_id", "scheduled_at"]
        
        for field in required_fields:
            if field not in args:
                return {
                    "success": False,
                    "error": f"Missing required field: {field}",
                }
        
        # Parse scheduled time
        try:
            scheduled_at = datetime.fromisoformat(args["scheduled_at"])
        except ValueError:
            return {
                "success": False,
                "error": "Invalid scheduled_at format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
            }
        
        # Create scheduled task
        task = ScheduledTask(
            type=TaskType.SCHEDULED_MESSAGE,
            scheduled_at=scheduled_at,
            task_data={
                "content": args["content"],
                "bot_id": args["bot_id"],
                "target_chat_id": args.get("target_chat_id"),
                "target_username": args.get("target_username"),
                "target_group_id": args.get("target_group_id"),
                "message_type": args.get("message_type", "dm"),
                "priority": args.get("priority", "normal"),
            },
        )
        
        task_id = await self.scheduler.schedule_task(task)
        
        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "scheduled_at": scheduled_at.isoformat(),
                "message": "Message scheduled successfully",
            },
        }
    
    async def _handle_cancel_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cancel task command."""
        if "task_id" not in args:
            return {
                "success": False,
                "error": "Missing required field: task_id",
            }
        
        success = await self.scheduler.cancel_task(args["task_id"])
        
        return {
            "success": success,
            "data": {
                "task_id": args["task_id"],
                "message": "Task cancelled successfully" if success else "Task not found",
            },
        }
    
    async def _handle_list_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list tasks command."""
        task_ids = await self.redis.smembers("scheduled_tasks")
        tasks = []
        
        for task_id in task_ids:
            task_data = await self.redis.hgetall(f"task:{task_id}")
            if task_data:
                tasks.append(task_data)
        
        return {
            "success": True,
            "data": {
                "total_tasks": len(tasks),
                "tasks": tasks,
            },
        }
    
    async def _handle_bot_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bot status command."""
        active_sessions = await self.redis.get_active_sessions()
        bot_statuses = {}
        
        for session_id in active_sessions:
            # Get bot state from Redis
            # This would need to be implemented based on how bot states are stored
            bot_statuses[session_id] = {
                "status": "active",
                "last_activity": "unknown",  # Would get from Redis
            }
        
        return {
            "success": True,
            "data": {
                "active_bots": len(active_sessions),
                "bot_statuses": bot_statuses,
            },
        }
    
    async def _handle_clear_queue(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle clear queue command."""
        queue_name = args.get("queue_name", "all")
        
        if queue_name == "all":
            # Clear all queues
            queues = ["urgent", "high", "normal", "low"]
            cleared_count = 0
            
            for queue in queues:
                queue_key = f"queue:{queue}"
                count = await self.redis.llen(queue_key)
                await self.redis.delete(queue_key)
                cleared_count += count
        else:
            # Clear specific queue
            queue_key = f"queue:{queue_name}"
            cleared_count = await self.redis.llen(queue_key)
            await self.redis.delete(queue_key)
        
        return {
            "success": True,
            "data": {
                "queue_name": queue_name,
                "cleared_messages": cleared_count,
                "message": f"Cleared {cleared_count} messages from queue(s)",
            },
        }
    
    async def _handle_emergency_stop(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency stop command."""
        # Stop scheduler
        await self.scheduler.stop()
        
        # Clear all queues
        queues = ["urgent", "high", "normal", "low"]
        total_cleared = 0
        
        for queue in queues:
            queue_key = f"queue:{queue}"
            count = await self.redis.llen(queue_key)
            await self.redis.delete(queue_key)
            total_cleared += count
        
        # Cancel all scheduled tasks
        task_ids = await self.redis.smembers("scheduled_tasks")
        for task_id in task_ids:
            await self.scheduler.cancel_task(task_id)
        
        return {
            "success": True,
            "data": {
                "scheduler_stopped": True,
                "queues_cleared": total_cleared,
                "tasks_cancelled": len(task_ids),
                "message": "Emergency stop executed successfully",
            },
        }
    
    async def _handle_restart_scheduler(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle restart scheduler command."""
        # Stop scheduler if running
        if self.scheduler.is_running:
            await self.scheduler.stop()
        
        # Start scheduler
        await self.scheduler.start()
        
        return {
            "success": True,
            "data": {
                "scheduler_restarted": True,
                "is_running": self.scheduler.is_running,
                "message": "Scheduler restarted successfully",
            },
        }


# Global admin command handler
admin_handler = AdminCommandHandler() 