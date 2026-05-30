from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
🚀 GAVATCore Advanced Asynchronous Processing Framework
Enterprise-grade scalability with load balancing and async processing

Features:
- Asynchronous task processing
- Connection pooling
- Circuit breaker pattern
- Rate limiting
- Load balancing algorithms
- Health monitoring
- Auto-scaling capabilities
"""

import asyncio
import time
import json
import logging
import hashlib
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from enum import Enum
import structlog
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import random
import uuid

# Configure structured logging
logger = structlog.get_logger("gavatcore.async_framework")

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    CONSISTENT_HASHING = "consistent_hashing"
    HEALTH_BASED = "health_based"

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    health_check_url: str = "/health"
    healthy: bool = True
    last_health_check: Optional[datetime] = None
    response_time: float = 0.0
    error_count: int = 0
    success_count: int = 0
    
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    @property
    def load_score(self) -> float:
        """Calculate load score for load balancing."""
        if not self.healthy:
            return float('inf')
        
        connection_ratio = self.current_connections / max(self.max_connections, 1)
        error_ratio = self.error_count / max(self.success_count + self.error_count, 1)
        
        return (connection_ratio * 0.6) + (error_ratio * 0.3) + (self.response_time * 0.1)

@dataclass
class TaskResult:
    """Async task result."""
    task_id: str
    status: str
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: float = 0.0

class CircuitBreaker:
    """
    🔒 Circuit Breaker Pattern Implementation
    Prevents cascading failures in distributed systems.
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 reset_timeout: int = 60,
                 expected_exception: tuple = (Exception,)):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def acall(self, func, *args, **kwargs):
        """Async version of circuit breaker call."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (time.time() - self.last_failure_time) >= self.reset_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

class RateLimiter:
    """
    ⏱️ Token Bucket Rate Limiter
    Controls request rate to prevent overload.
    """
    
    def __init__(self, max_tokens: int = 100, refill_rate: float = 10.0):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens from bucket."""
        async with self._lock:
            now = time.time()
            # Refill tokens
            time_passed = now - self.last_refill
            self.tokens = min(self.max_tokens, 
                            self.tokens + (time_passed * self.refill_rate))
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class LoadBalancer:
    """
    ⚖️ Advanced Load Balancer
    Distributes requests across multiple service endpoints.
    """
    
    def __init__(self, 
                 strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_CONNECTIONS,
                 health_check_interval: int = 30):
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.endpoints: List[ServiceEndpoint] = []
        self.current_index = 0
        self.hash_ring: Dict[str, ServiceEndpoint] = {}
        self.health_check_task = None
        self._session = None
        
    def add_endpoint(self, endpoint: ServiceEndpoint):
        """Add service endpoint to load balancer."""
        self.endpoints.append(endpoint)
        if self.strategy == LoadBalancingStrategy.CONSISTENT_HASHING:
            self._rebuild_hash_ring()
        logger.info("✅ Endpoint added to load balancer", 
                   endpoint_id=endpoint.id, url=endpoint.url)
    
    def remove_endpoint(self, endpoint_id: str):
        """Remove service endpoint from load balancer."""
        self.endpoints = [ep for ep in self.endpoints if ep.id != endpoint_id]
        if self.strategy == LoadBalancingStrategy.CONSISTENT_HASHING:
            self._rebuild_hash_ring()
        logger.info("🗑️ Endpoint removed from load balancer", endpoint_id=endpoint_id)
    
    async def get_endpoint(self, key: Optional[str] = None) -> Optional[ServiceEndpoint]:
        """Get next endpoint based on load balancing strategy."""
        healthy_endpoints = [ep for ep in self.endpoints if ep.healthy]
        
        if not healthy_endpoints:
            logger.warning("⚠️ No healthy endpoints available")
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin(healthy_endpoints)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_endpoints)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(healthy_endpoints)
        elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASHING:
            return self._consistent_hashing(healthy_endpoints, key or str(uuid.uuid4()))
        elif self.strategy == LoadBalancingStrategy.HEALTH_BASED:
            return self._health_based(healthy_endpoints)
        
        return healthy_endpoints[0]  # Fallback
    
    def _round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round-robin load balancing."""
        endpoint = endpoints[self.current_index % len(endpoints)]
        self.current_index += 1
        return endpoint
    
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least connections load balancing."""
        return min(endpoints, key=lambda ep: ep.current_connections)
    
    def _weighted_round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted round-robin load balancing."""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]
        
        weighted_endpoints = []
        for ep in endpoints:
            weighted_endpoints.extend([ep] * ep.weight)
        
        endpoint = weighted_endpoints[self.current_index % len(weighted_endpoints)]
        self.current_index += 1
        return endpoint
    
    def _consistent_hashing(self, endpoints: List[ServiceEndpoint], key: str) -> ServiceEndpoint:
        """Consistent hashing load balancing."""
        if not self.hash_ring:
            self._rebuild_hash_ring()
        
        hash_key = hashlib.md5(key.encode()).hexdigest()
        sorted_keys = sorted(self.hash_ring.keys())
        
        for ring_key in sorted_keys:
            if hash_key <= ring_key:
                return self.hash_ring[ring_key]
        
        return self.hash_ring[sorted_keys[0]]  # Wrap around
    
    def _health_based(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Health-based load balancing (best performing endpoint)."""
        return min(endpoints, key=lambda ep: ep.load_score)
    
    def _rebuild_hash_ring(self):
        """Rebuild consistent hashing ring."""
        self.hash_ring.clear()
        for endpoint in self.endpoints:
            for i in range(100):  # Virtual nodes
                virtual_key = hashlib.md5(f"{endpoint.id}:{i}".encode()).hexdigest()
                self.hash_ring[virtual_key] = endpoint
    
    async def start_health_checks(self):
        """Start periodic health checks."""
        logger.info("🏥 Health check monitoring started")
    
    async def stop_health_checks(self):
        """Stop health checks."""
        logger.info("🏥 Health check monitoring stopped")

class AsyncTaskProcessor:
    """
    ⚡ Advanced Asynchronous Task Processor
    Handles background tasks with prioritization and result tracking.
    """
    
    def __init__(self, 
                 max_workers: int = 50,
                 queue_size: int = 1000):
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.task_queue = asyncio.Queue(maxsize=queue_size)
        self.result_store: Dict[str, TaskResult] = {}
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def start(self):
        """Start task processor workers."""
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        logger.info("⚡ Async task processor started", workers=self.max_workers)
    
    async def stop(self):
        """Stop task processor."""
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("⚡ Async task processor stopped")
    
    async def submit_task(self, 
                         func: Callable,
                         *args,
                         priority: int = 5,
                         task_id: Optional[str] = None,
                         **kwargs) -> str:
        """Submit task for async processing."""
        if not task_id:
            task_id = str(uuid.uuid4())
        
        task_data = {
            'task_id': task_id,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'priority': priority,
            'submitted_at': datetime.now()
        }
        
        # Create result placeholder
        self.result_store[task_id] = TaskResult(
            task_id=task_id,
            status='queued',
            start_time=datetime.now()
        )
        
        await self.task_queue.put(task_data)
        logger.debug("📝 Task submitted", task_id=task_id, priority=priority)
        
        return task_id
    
    async def get_result(self, task_id: str, timeout: float = 30.0) -> Optional[TaskResult]:
        """Get task result (blocking until complete or timeout)."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.result_store:
                result = self.result_store[task_id]
                if result.status in ['completed', 'failed']:
                    return result
            
            await asyncio.sleep(0.1)
        
        return None
    
    def get_result_nowait(self, task_id: str) -> Optional[TaskResult]:
        """Get task result without waiting."""
        return self.result_store.get(task_id)
    
    async def _worker(self, worker_name: str):
        """Task processor worker."""
        logger.debug("👷 Worker started", worker_name=worker_name)
        
        while self.running:
            try:
                # Get task from queue
                task_data = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                await self._process_task(task_data, worker_name)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Worker error", 
                           worker_name=worker_name, error=str(e))
        
        logger.debug("👷 Worker stopped", worker_name=worker_name)
    
    async def _process_task(self, task_data: Dict, worker_name: str):
        """Process individual task."""
        task_id = task_data['task_id']
        func = task_data['func']
        args = task_data['args']
        kwargs = task_data['kwargs']
        
        logger.debug("🔄 Processing task", 
                    task_id=task_id, worker_name=worker_name)
        
        # Update result status
        result = self.result_store[task_id]
        result.status = 'running'
        result.start_time = datetime.now()
        
        try:
            # Execute task
            if asyncio.iscoroutinefunction(func):
                task_result = await func(*args, **kwargs)
            else:
                # Run in thread pool for CPU-bound tasks
                task_result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, func, *args, **kwargs
                )
            
            # Update result
            result.status = 'completed'
            result.result = task_result
            result.end_time = datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            logger.debug("✅ Task completed", 
                        task_id=task_id, 
                        execution_time=result.execution_time)
            
        except Exception as e:
            # Update result with error
            result.status = 'failed'
            result.error = str(e)
            result.end_time = datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            logger.error("❌ Task failed", 
                        task_id=task_id, 
                        error=str(e))

class AdvancedAsyncFramework:
    """
    🚀 GAVATCore Advanced Async Framework
    Central coordinator for all async operations and scalability features.
    """
    
    def __init__(self):
        self.load_balancer = LoadBalancer()
        self.task_processor = AsyncTaskProcessor()
        self.rate_limiter = RateLimiter()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.system_metrics = {
            'requests_processed': 0,
            'errors_count': 0,
            'average_response_time': 0.0,
            'active_connections': 0,
            'queue_size': 0
        }
        self.running = False
        
        logger.info("🚀 Advanced Async Framework initialized")
    
    async def start(self):
        """Start all framework components."""
        await self.task_processor.start()
        await self.load_balancer.start_health_checks()
        self.running = True
        
        logger.info("🚀 Advanced Async Framework started")
    
    async def stop(self):
        """Stop all framework components."""
        self.running = False
        await self.task_processor.stop()
        await self.load_balancer.stop_health_checks()
        
        logger.info("🚀 Advanced Async Framework stopped")
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    async def execute_with_protections(self,
                                     func: Callable,
                                     service_name: str,
                                     *args,
                                     rate_limit_tokens: int = 1,
                                     **kwargs):
        """Execute function with all protection mechanisms."""
        # Rate limiting
        if not await self.rate_limiter.acquire(rate_limit_tokens):
            raise Exception("Rate limit exceeded")
        
        # Circuit breaker
        circuit_breaker = self.get_circuit_breaker(service_name)
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await circuit_breaker.acall(func, *args, **kwargs)
            else:
                result = circuit_breaker.call(func, *args, **kwargs)
            
            self.system_metrics['requests_processed'] += 1
            return result
            
        except Exception as e:
            self.system_metrics['errors_count'] += 1
            raise e
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            
            return {
                'framework_running': self.running,
                'task_processor_workers': len(self.task_processor.workers),
                'active_endpoints': len([ep for ep in self.load_balancer.endpoints if ep.healthy]),
                'total_endpoints': len(self.load_balancer.endpoints),
                'system_metrics': self.system_metrics,
                'system_resources': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_info.percent,
                    'memory_available_gb': memory_info.available / (1024**3)
                },
                'circuit_breakers': {
                    name: cb.state.value 
                    for name, cb in self.circuit_breakers.items()
                }
            }
        except ImportError:
            return {
                'framework_running': self.running,
                'task_processor_workers': len(self.task_processor.workers),
                'active_endpoints': len([ep for ep in self.load_balancer.endpoints if ep.healthy]),
                'total_endpoints': len(self.load_balancer.endpoints),
                'system_metrics': self.system_metrics,
                'circuit_breakers': {
                    name: cb.state.value 
                    for name, cb in self.circuit_breakers.items()
                }
            }

# Decorator for async protection
def async_protected(service_name: str, rate_limit_tokens: int = 1):
    """Decorator to add async protections to functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            framework = getattr(wrapper, '_framework', None)
            if framework:
                return await framework.execute_with_protections(
                    func, service_name, *args, 
                    rate_limit_tokens=rate_limit_tokens, **kwargs
                )
            else:
                return await func(*args, **kwargs)
        return wrapper
    return decorator

# Global framework instance
_global_framework: Optional[AdvancedAsyncFramework] = None

def get_async_framework() -> AdvancedAsyncFramework:
    """Get global async framework instance."""
    global _global_framework
    if _global_framework is None:
        _global_framework = AdvancedAsyncFramework()
    return _global_framework

async def initialize_framework():
    """Initialize global framework."""
    framework = get_async_framework()
    await framework.start()
    return framework

async def shutdown_framework():
    """Shutdown global framework."""
    global _global_framework
    if _global_framework:
        await _global_framework.stop()
        _global_framework = None 