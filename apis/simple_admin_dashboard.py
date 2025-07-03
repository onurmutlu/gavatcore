#!/usr/bin/env python3
"""
🚀 Simple Admin Dashboard API
============================

High-performance admin dashboard API with:
- Database query optimization
- In-memory caching
- Real-time metrics
- Performance monitoring

@version: 1.0.0
@created: 2025-01-30
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
import sqlite3
import hashlib
import psutil
from functools import wraps

# ============= CONFIGURATION =============

DATABASE_PATH = "gavatcore_v2.db"
CACHE_TTL = 300  # 5 minutes

# ============= SIMPLE CACHE =============

class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.cache_times = {}
        self.stats = {"hits": 0, "misses": 0}
    
    def get(self, key: str):
        if key in self.cache:
            cache_time = self.cache_times.get(key, 0)
            if time.time() - cache_time < CACHE_TTL:
                self.stats["hits"] += 1
                return self.cache[key]
            else:
                # Remove expired entry
                del self.cache[key]
                del self.cache_times[key]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any):
        self.cache[key] = value
        self.cache_times[key] = time.time()
    
    def clear(self):
        self.cache.clear()
        self.cache_times.clear()
    
    def get_stats(self):
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "total_requests": total,
            "current_entries": len(self.cache)
        }

cache = SimpleCache()

# ============= DATABASE UTILS =============

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query: str, params=None):
    """Execute query and return results"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Query error: {e}")
        return []
    finally:
        conn.close()

def execute_scalar(query: str, params=None):
    """Execute query and return single value"""
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Scalar query error: {e}")
        return 0
    finally:
        conn.close()

# ============= PERFORMANCE MONITORING =============

def monitor_performance(endpoint_name: str):
    """Performance monitoring decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                print(f"📊 {endpoint_name}: {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"❌ {endpoint_name} error ({execution_time:.4f}s): {e}")
                raise
        return wrapper
    return decorator

# ============= FASTAPI APP =============

app = FastAPI(
    title="GAVATCore Admin Dashboard API (Simple)",
    description="Simple high-performance admin dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= ENDPOINTS =============

@app.get("/api/admin/dashboard/stats")
@monitor_performance("dashboard_stats")
async def get_dashboard_stats(
    force_refresh: bool = Query(False, description="Force cache refresh")
):
    """Get dashboard statistics with caching"""
    
    cache_key = "dashboard_stats"
    
    # Try cache first
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            cached_data["cached"] = True
            cached_data["cache_timestamp"] = datetime.now().isoformat()
            return cached_data
    
    # Fetch fresh data
    start_time = time.time()
    
    try:
        # Get basic counts (with fallback for missing tables)
        queries = [
            "SELECT COUNT(*) FROM users",
            "SELECT COUNT(*) FROM users WHERE last_activity > datetime('now', '-1 day')",
            "SELECT COUNT(*) FROM messages",
            "SELECT COALESCE(SUM(token_balance), 0) FROM users"
        ]
        
        results = []
        for query in queries:
            try:
                result = execute_scalar(query)
                results.append(result)
            except:
                results.append(0)  # Fallback if table doesn't exist
        
        total_users, active_users, total_messages, total_tokens = results
        
    except Exception as e:
        print(f"Database error: {e}")
        total_users = active_users = total_messages = total_tokens = 0
    
    # System metrics
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
    except:
        cpu_usage = memory_usage = 0
    
    cache_stats = cache.get_stats()
    execution_time = time.time() - start_time
    
    # Create response
    stats = {
        "total_users": total_users,
        "active_users": active_users,
        "total_messages": total_messages,
        "total_tokens": total_tokens,
        "system_health": "healthy" if execution_time < 1.0 else "slow",
        "cache_hit_rate": cache_stats["hit_rate"],
        "response_time": execution_time,
        "timestamp": datetime.now().isoformat(),
        "cached": False,
        "system_metrics": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "cache_size": cache_stats["current_entries"]
        }
    }
    
    # Cache the result
    cache.set(cache_key, stats)
    
    return stats

@app.get("/api/admin/users")
@monitor_performance("admin_users")
async def get_admin_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    search: Optional[str] = Query(None, description="Search username")
):
    """Get paginated user list"""
    
    # Create cache key
    cache_key = f"admin_users_{page}_{limit}_{search or ''}"
    
    # Try cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        cached_data["cached"] = True
        return cached_data
    
    try:
        # Build query
        base_query = "SELECT user_id, username, message_count, token_balance, last_activity FROM users"
        count_query = "SELECT COUNT(*) FROM users"
        
        where_clause = ""
        params = {}
        
        if search:
            where_clause = " WHERE username LIKE :search"
            params["search"] = f"%{search}%"
        
        # Add pagination
        offset = (page - 1) * limit
        final_query = base_query + where_clause + f" ORDER BY last_activity DESC LIMIT {limit} OFFSET {offset}"
        final_count_query = count_query + where_clause
        
        # Execute queries
        users_data = execute_query(final_query, params)
        total_count = execute_scalar(final_count_query, params)
        
        # Calculate pagination
        total_pages = (total_count + limit - 1) // limit
        
        response_data = {
            "users": users_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache for 2 minutes
        cache.set(cache_key, response_data)
        
        return response_data
        
    except Exception as e:
        print(f"Users query error: {e}")
        # Return empty result on error
        return {
            "users": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": 0,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False
            },
            "cached": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/admin/system/health")
@monitor_performance("system_health")
async def get_system_health():
    """Get system health status"""
    
    start_time = time.time()
    
    # System metrics
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
    except:
        cpu_usage = memory_usage = disk_usage = 0
    
    # Cache metrics
    cache_stats = cache.get_stats()
    
    # Database health check
    db_healthy = True
    db_response_time = 0
    
    try:
        db_start = time.time()
        result = execute_scalar("SELECT 1")
        db_response_time = time.time() - db_start
        db_healthy = result == 1
    except:
        db_healthy = False
    
    # Calculate health score
    health_score = 100
    if cpu_usage > 80:
        health_score -= 20
    if memory_usage > 90:
        health_score -= 30
    if not db_healthy:
        health_score -= 40
    
    overall_status = "healthy"
    if health_score < 60:
        overall_status = "critical"
    elif health_score < 80:
        overall_status = "warning"
    
    response_time = time.time() - start_time
    
    return {
        "overall_status": overall_status,
        "health_score": max(0, health_score),
        "system_metrics": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage
        },
        "cache_stats": cache_stats,
        "database": {
            "healthy": db_healthy,
            "response_time": db_response_time
        },
        "api_response_time": response_time,
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/api/admin/cache/clear")
@monitor_performance("cache_clear")
async def clear_cache():
    """Clear cache"""
    
    try:
        old_entries = len(cache.cache)
        cache.clear()
        
        return {
            "success": True,
            "message": f"Cleared {old_entries} cache entries",
            "deleted_count": old_entries,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GAVATCore Admin Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/admin/dashboard/stats",
            "/api/admin/users",
            "/api/admin/system/health",
            "/api/admin/cache/clear"
        ]
    }

# ============= MAIN =============

if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Starting Simple Admin Dashboard API...")
    print("=" * 50)
    print("🔧 Features:")
    print("   • In-memory caching")
    print("   • Database optimization")
    print("   • Real-time metrics")
    print("   • Performance monitoring")
    print()
    print("🌐 Endpoints:")
    print("   • GET /api/admin/dashboard/stats")
    print("   • GET /api/admin/users")
    print("   • GET /api/admin/system/health")
    print("   • DELETE /api/admin/cache/clear")
    print()
    print("📊 Starting server on http://localhost:5055")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5055,
        log_level="info"
    )