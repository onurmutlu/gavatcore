"""
Session yönetim araçları modülü
"""

from pathlib import Path

SESSION_MANAGEMENT_DIR = Path(__file__).parent

def get_tool_path(tool_name: str) -> Path:
    """Session yönetim aracının tam yolunu döndürür"""
    return SESSION_MANAGEMENT_DIR / f"{tool_name}.py" 