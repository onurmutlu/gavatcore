"""
Spam yönetim araçları modülü
"""

from pathlib import Path

SPAM_MANAGEMENT_DIR = Path(__file__).parent

def get_tool_path(tool_name: str) -> Path:
    """Spam yönetim aracının tam yolunu döndürür"""
    return SPAM_MANAGEMENT_DIR / f"{tool_name}.py" 