"""
Migrasyon araçları modülü
"""

from pathlib import Path

MIGRATION_DIR = Path(__file__).parent

def get_tool_path(tool_name: str) -> Path:
    """Migrasyon aracının tam yolunu döndürür"""
    return MIGRATION_DIR / f"{tool_name}.py" 