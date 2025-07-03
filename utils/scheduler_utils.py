#!/usr/bin/env python3
"""
⏰ GAVATCORE SCHEDULER UTILS
Scheduled message and task management
"""

import asyncio
import random
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger("gavatcore.scheduler")

class SchedulerTask:
    """Individual scheduler task"""
    
    def __init__(self, task_id: str, interval: int, callback: Callable, **kwargs):
        self.task_id = task_id
        self.interval = interval  # seconds
        self.callback = callback
        self.kwargs = kwargs
        self.created_at = datetime.now()
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self.is_running = False
        self.task_handle: Optional[Any] = None

class SchedulerUtils:
    """Scheduler utility for periodic tasks"""
    
    def __init__(self, bot_name: str, config: Dict[str, Any]):
        self.bot_name = bot_name
        self.config = config
        self.tasks = {}
        self.is_running = False
        
        # Default scheduler settings
        self.default_messages = self._load_default_messages()
        
    def _load_default_messages(self) -> Dict[str, List[str]]:
        """Load default scheduled messages for each bot"""
        return {
            'yayincilara': [
                "Привет всем! 🎮 Кто сегодня играет?",
                "Yayın zamanı geldi mi? 📺 Stream açalım!",
                "Gaming mood активирован! 💪 Hangi oyun?",
                "Twitch'te buluşalım mı bu akşam? 🔥",
                "Сегодня будет эпик stream! 🚀",
            ],
            'xxxgeisha': [
                "İyi akşamlar güzeller... 🌸 Nasıl geçiyor gününüz?",
                "Bugün kendinize zaman ayırdınız mı? ✨",
                "Güzellik içten gelir derler... 💋 Siz ne düşünüyorsunuz?",
                "Akşam saatleri en sevdiğim... 🌙 Sizin için?",
                "Zarafet bir yaşam tarzıdır 💫",
            ],
            'gawatbaba': [
                "Lan moruklar, nasıl gidiyor işler? 💪",
                "Evlatlar, bugün ne kadar para kazandık? 💰",
                "Kankalar, motivasyon zamanı! 🔥",
                "Abi tavsiyesi: Çok çalışın ama dinlenmeyi de unutmayın 😎",
                "Oğlum, hayatta en önemli şey disiplin! ⚡",
            ]
        }
    
    async def start_scheduler(self):
        """Start the scheduler system"""
        if self.is_running:
            logger.warning(f"🔄 Scheduler already running for {self.bot_name}")
            return
        
        self.is_running = True
        
        # Setup default scheduled messages if enabled
        if self.config.get('scheduler_enabled', False):
            await self._setup_default_tasks()
        
        logger.info(f"⏰ Scheduler started for {self.bot_name}")
    
    async def stop_scheduler(self):
        """Stop all scheduled tasks"""
        self.is_running = False
        
        # Cancel all running tasks
        for task in self.tasks.values():
            if task.task_handle and not task.task_handle.done():
                task.task_handle.cancel()
        
        self.tasks.clear()
        logger.info(f"🛑 Scheduler stopped for {self.bot_name}")
    
    async def _setup_default_tasks(self):
        """Setup default scheduled message tasks"""
        try:
            interval = self.config.get('scheduler_interval', 300)  # 5 minutes default
            
            # Add scheduled messages task
            await self.add_task(
                task_id="scheduled_messages",
                interval=interval,
                callback=self._send_scheduled_message
            )
            
            logger.info(f"📅 Default scheduled tasks setup", 
                       bot=self.bot_name,
                       interval=interval)
            
        except Exception as e:
            logger.error(f"❌ Default task setup error: {e}")
    
    async def add_task(self, task_id: str, interval: int, callback: Callable, **kwargs) -> bool:
        """Add a new scheduled task"""
        try:
            if task_id in self.tasks:
                logger.warning(f"⚠️ Task {task_id} already exists")
                return False
            
            task = SchedulerTask(task_id, interval, callback, **kwargs)
            self.tasks[task_id] = task
            
            # Start the task
            task.task_handle = asyncio.create_task(
                self._run_task(task),
                name=f"scheduler_{self.bot_name}_{task_id}"
            )
            
            logger.info(f"✅ Task added", 
                       task_id=task_id,
                       interval=interval,
                       bot=self.bot_name)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Add task error: {e}")
            return False
    
    async def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Cancel the task
        if task.task_handle and not task.task_handle.done():
            task.task_handle.cancel()
        
        del self.tasks[task_id]
        
        logger.info(f"🗑️ Task removed", task_id=task_id, bot=self.bot_name)
        return True
    
    async def _run_task(self, task: SchedulerTask):
        """Run a scheduled task"""
        while self.is_running:
            try:
                # Wait for interval
                await asyncio.sleep(task.interval)
                
                if not self.is_running:
                    break
                
                # Execute task
                task.is_running = True
                await task.callback(**task.kwargs)
                
                # Update stats
                task.last_run = datetime.now()
                task.run_count += 1
                task.is_running = False
                
                logger.debug(f"⚡ Task executed", 
                           task_id=task.task_id,
                           run_count=task.run_count)
                
            except asyncio.CancelledError:
                logger.info(f"🛑 Task cancelled: {task.task_id}")
                break
            except Exception as e:
                logger.error(f"❌ Task execution error: {e}")
                task.is_running = False
                # Continue running despite errors
    
    async def _send_scheduled_message(self, **kwargs):
        """Send a scheduled message"""
        try:
            # Get client from kwargs or config
            client = kwargs.get('client')
            if not client:
                logger.warning("📭 No client provided for scheduled message")
                return
            
            # Get target chats (groups to send messages to)
            target_chats = kwargs.get('target_chats', [])
            if not target_chats:
                logger.debug("📭 No target chats for scheduled messages")
                return
            
            # Get messages for this bot
            messages = self.default_messages.get(self.bot_name, [])
            if not messages:
                logger.warning(f"📭 No messages configured for {self.bot_name}")
                return
            
            # Select random message
            message = random.choice(messages)
            
            # Add some randomization to make it more natural
            if random.random() < 0.1:  # 10% chance to skip
                logger.debug("🎲 Scheduled message skipped (randomization)")
                return
            
            # Send to random target chat
            target_chat = random.choice(target_chats)
            
            try:
                await client.send_message(target_chat, message)
                
                logger.info(f"📨 Scheduled message sent", 
                           bot=self.bot_name,
                           target=target_chat,
                           message_preview=message[:30])
                
            except Exception as send_error:
                logger.error(f"❌ Message send error: {send_error}")
                
        except Exception as e:
            logger.error(f"❌ Scheduled message error: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        return {
            'task_id': task.task_id,
            'interval': task.interval,
            'created_at': task.created_at.isoformat(),
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'run_count': task.run_count,
            'is_running': task.is_running,
            'is_cancelled': task.task_handle.cancelled() if task.task_handle else False
        }
    
    def get_all_tasks_status(self) -> Dict[str, Any]:
        """Get status of all tasks"""
        return {
            'bot_name': self.bot_name,
            'scheduler_running': self.is_running,
            'total_tasks': len(self.tasks),
            'tasks': {
                task_id: self.get_task_status(task_id)
                for task_id in self.tasks.keys()
            }
        }
    
    async def update_task_interval(self, task_id: str, new_interval: int) -> bool:
        """Update task interval"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Cancel current task
        if task.task_handle and not task.task_handle.done():
            task.task_handle.cancel()
        
        # Update interval
        task.interval = new_interval
        
        # Restart task
        task.task_handle = asyncio.create_task(
            self._run_task(task),
            name=f"scheduler_{self.bot_name}_{task_id}"
        )
        
        logger.info(f"🔄 Task interval updated", 
                   task_id=task_id,
                   new_interval=new_interval)
        
        return True 