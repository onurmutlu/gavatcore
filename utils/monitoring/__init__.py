"""
İzleme araçları modülü
"""

from pathlib import Path

MONITORING_DIR = Path(__file__).parent

def get_tool_path(tool_name: str) -> Path:
    """İzleme aracının tam yolunu döndürür"""
    return MONITORING_DIR / f"{tool_name}.py" 