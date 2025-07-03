#!/usr/bin/env python3
"""
🔧 GavatCore Core Module 🔧

Bu modül GavatCore'un ana sistemlerini içerir.

Enhanced Features:
- Lazy loading ve error handling
- Type annotations ve comprehensive logging  
- Graceful fallbacks for missing dependencies
- Performance monitoring ve health checks
"""

import logging
from typing import Optional, Dict, Any, Type, Union
import warnings
from pathlib import Path

# Configure logging for core module
logger = logging.getLogger("gavatcore.core")

# Version information
__version__ = "1.0.0"
__author__ = "Onur SiyahKare"
__description__ = "GavatCore Core System Module"

# Global registry for lazy-loaded modules
_module_registry: Dict[str, Any] = {}
_failed_imports: Dict[str, Exception] = {}

def _safe_import(module_name: str, class_name: str, description: str = "") -> Optional[Type]:
    """
    Safely import a module with comprehensive error handling.
    
    Args:
        module_name: Name of the module to import (e.g., 'database_manager')
        class_name: Name of the class/object to import
        description: Human-readable description for logging
        
    Returns:
        Optional[Type]: The imported class/object, or None if import failed
    """
    try:
        # Check if already cached
        cache_key = f"{module_name}.{class_name}"
        if cache_key in _module_registry:
            return _module_registry[cache_key]
        
        # Check if previously failed
        if cache_key in _failed_imports:
            logger.debug(f"⚠️ Skipping previously failed import: {cache_key}")
            return None
        
        # Attempt import
        logger.debug(f"🔄 Importing {cache_key}: {description}")
        
        if module_name.startswith('.'):
            # Relative import
            from importlib import import_module
            module = import_module(module_name, package=__name__)
        else:
            # Absolute import
            module = __import__(f"core.{module_name}", fromlist=[class_name])
        
        imported_item = getattr(module, class_name)
        
        # Cache successful import
        _module_registry[cache_key] = imported_item
        logger.debug(f"✅ Successfully imported {cache_key}")
        
        return imported_item
        
    except ImportError as e:
        logger.warning(f"⚠️ Import failed for {module_name}.{class_name}: {e}")
        _failed_imports[cache_key] = e
        return None
    except AttributeError as e:
        logger.warning(f"⚠️ Attribute not found {module_name}.{class_name}: {e}")
        _failed_imports[cache_key] = e
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected import error {module_name}.{class_name}: {e}")
        _failed_imports[cache_key] = e
        return None

def get_import_status() -> Dict[str, Dict[str, Any]]:
    """
    Get status of all attempted imports.
    
    Returns:
        Dict with successful and failed imports
    """
    return {
        "successful": {
            name: {"type": type(obj).__name__, "module": getattr(obj, "__module__", "unknown")}
            for name, obj in _module_registry.items()
        },
        "failed": {
            name: {"error": str(error), "type": type(error).__name__}
            for name, error in _failed_imports.items()
        },
        "stats": {
            "total_attempts": len(_module_registry) + len(_failed_imports),
            "successful_count": len(_module_registry),
            "failed_count": len(_failed_imports),
            "success_rate": len(_module_registry) / max(len(_module_registry) + len(_failed_imports), 1)
        }
    }

# Database managers - with safe imports and fallbacks
database_manager = _safe_import(
    "database_manager", "database_manager", 
    "Main database management system"
)

babagavat_redis_manager = _safe_import(
    "redis_manager", "babagavat_redis_manager", 
    "Redis cache and session management"
)

babagavat_mongo_manager = _safe_import(
    "mongodb_manager", "babagavat_mongo_manager", 
    "MongoDB document store management"
)

BabaGAVATPostgreSQLManager = _safe_import(
    "postgresql_manager", "BabaGAVATPostgreSQLManager", 
    "PostgreSQL relational database management"
)

# Core services - with graceful degradation
babagavat_coin_service = _safe_import(
    "coin_service", "babagavat_coin_service", 
    "Cryptocurrency and token management system"
)

babagavat_user_analyzer = _safe_import(
    "user_analyzer", "babagavat_user_analyzer", 
    "AI-powered user behavior analysis"
)

babagavat_erko_analyzer = _safe_import(
    "erko_analyzer", "babagavat_erko_analyzer", 
    "Street-smart user risk assessment"
)

# Session & Profile Management
SessionManager = _safe_import(
    "session_manager", "SessionManager", 
    "Telegram session lifecycle management"
)

analytics_logger = _safe_import(
    "analytics_logger", "analytics_logger", 
    "Analytics data collection and logging"
)

# Advanced AI Services (optional components)
advanced_ai_manager = _safe_import(
    "advanced_ai_manager", "AdvancedAIManager", 
    "Multi-model AI orchestration system"
)

ai_voice_engine = _safe_import(
    "ai_voice_engine", "ai_voice_engine", 
    "Text-to-speech and voice processing"
)

social_gaming_engine = _safe_import(
    "social_gaming_engine", "social_gaming_engine", 
    "Gamification and engagement system"
)

# Performance and Monitoring
metrics_collector = _safe_import(
    "metrics_collector", "metrics_collector", 
    "System performance metrics collection"
)

error_tracker = _safe_import(
    "error_tracker", "error_tracker", 
    "Error monitoring and reporting system"
)

# Utility functions for core module management
def validate_core_dependencies() -> Dict[str, Any]:
    """
    Validate that critical core dependencies are available.
    
    Returns:
        Dict with validation results and recommendations
    """
    critical_components = [
        ("database_manager", database_manager, "Database operations will fail"),
        ("redis_manager", babagavat_redis_manager, "Cache and sessions limited"),
        ("user_analyzer", babagavat_user_analyzer, "User analysis unavailable"),
    ]
    
    optional_components = [
        ("mongo_manager", babagavat_mongo_manager, "Document storage limited"),
        ("coin_service", babagavat_coin_service, "Token features unavailable"),
        ("ai_voice_engine", ai_voice_engine, "Voice features disabled"),
    ]
    
    results = {
        "critical": {},
        "optional": {},
        "overall_status": "healthy",
        "recommendations": []
    }
    
    # Check critical components
    critical_failures = 0
    for name, component, impact in critical_components:
        if component is None:
            results["critical"][name] = {"status": "failed", "impact": impact}
            critical_failures += 1
        else:
            results["critical"][name] = {"status": "available", "impact": None}
    
    # Check optional components
    for name, component, impact in optional_components:
        if component is None:
            results["optional"][name] = {"status": "failed", "impact": impact}
        else:
            results["optional"][name] = {"status": "available", "impact": None}
    
    # Determine overall status
    if critical_failures > 0:
        results["overall_status"] = "critical"
        results["recommendations"].append("Fix critical component imports immediately")
    elif len(_failed_imports) > len(_module_registry):
        results["overall_status"] = "degraded"
        results["recommendations"].append("Review optional component configurations")
    
    # Add specific recommendations
    if database_manager is None:
        results["recommendations"].append("Install database dependencies: pip install aiosqlite asyncpg motor")
    
    if babagavat_redis_manager is None:
        results["recommendations"].append("Install Redis dependencies: pip install redis[hiredis]")
    
    return results

def get_available_services() -> Dict[str, bool]:
    """
    Get a simple dict of available services for runtime checks.
    
    Returns:
        Dict mapping service names to availability
    """
    return {
        "database": database_manager is not None,
        "redis": babagavat_redis_manager is not None,
        "mongodb": babagavat_mongo_manager is not None,
        "postgresql": BabaGAVATPostgreSQLManager is not None,
        "coin_service": babagavat_coin_service is not None,
        "user_analyzer": babagavat_user_analyzer is not None,
        "erko_analyzer": babagavat_erko_analyzer is not None,
        "session_manager": SessionManager is not None,
        "analytics": analytics_logger is not None,
        "ai_voice": ai_voice_engine is not None,
        "social_gaming": social_gaming_engine is not None,
        "metrics": metrics_collector is not None,
        "error_tracking": error_tracker is not None,
    }

def print_core_status() -> None:
    """Print a human-readable status of core module."""
    print("\n🔧 GavatCore Core Module Status 🔧")
    print("=" * 50)
    
    available_services = get_available_services()
    validation_results = validate_core_dependencies()
    
    # Print service availability
    print("\n📋 Service Availability:")
    for service, available in available_services.items():
        status = "✅" if available else "❌"
        print(f"  {status} {service}")
    
    # Print overall status
    status_emoji = {
        "healthy": "✅",
        "degraded": "⚠️", 
        "critical": "❌"
    }
    overall_status = validation_results["overall_status"]
    print(f"\n🎯 Overall Status: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
    
    # Print recommendations if any
    if validation_results["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in validation_results["recommendations"]:
            print(f"  • {rec}")
    
    # Print import statistics
    import_stats = get_import_status()["stats"]
    print(f"\n📊 Import Statistics:")
    print(f"  • Success Rate: {import_stats['success_rate']:.1%}")
    print(f"  • Successful: {import_stats['successful_count']}")
    print(f"  • Failed: {import_stats['failed_count']}")

# Export configuration
__all__ = [
    # Database managers
    "database_manager",
    "babagavat_redis_manager", 
    "babagavat_mongo_manager",
    "BabaGAVATPostgreSQLManager",
    
    # Core services
    "babagavat_coin_service",
    "babagavat_user_analyzer",
    "babagavat_erko_analyzer",
    
    # Session Management
    "SessionManager",
    "analytics_logger",
    
    # Advanced Services (may be None)
    "advanced_ai_manager",
    "ai_voice_engine", 
    "social_gaming_engine",
    "metrics_collector",
    "error_tracker",
    
    # Utility functions
    "validate_core_dependencies",
    "get_available_services",
    "get_import_status",
    "print_core_status",
    
    # Metadata
    "__version__",
    "__author__",
    "__description__",
]

# Log core module initialization
logger.info(f"🔧 GavatCore Core Module v{__version__} initialized")

# Validate dependencies on import (non-blocking)
try:
    validation_results = validate_core_dependencies()
    if validation_results["overall_status"] != "healthy":
        warnings.warn(
            f"Core module status: {validation_results['overall_status']}. "
            f"Some features may be limited. Use core.print_core_status() for details.",
            UserWarning
        )
    logger.info(f"✅ Core module validation complete: {validation_results['overall_status']}")
except Exception as e:
    logger.warning(f"⚠️ Core module validation failed: {e}")

# Auto-print status in debug mode
if logger.getEffectiveLevel() <= logging.DEBUG:
    print_core_status() 