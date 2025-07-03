"""
Bakım araçları modülü
"""

from pathlib import Path

MAINTENANCE_DIR = Path(__file__).parent

def get_tool_path(tool_name: str) -> Path:
    """Bakım aracının tam yolunu döndürür"""
    return MAINTENANCE_DIR / f"{tool_name}.py" 