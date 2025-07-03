"""
Gavatcore utility araçları
"""

from pathlib import Path
import importlib

UTILS_DIR = Path(__file__).parent

def find_and_run_tool(tool_type: str, tool_name: str, *args, **kwargs):
    """
    Utility aracını bulur ve çalıştırır
    
    Args:
        tool_type: Araç tipi ('maintenance', 'migration', 'monitoring', 'session_management', 'spam_management')
        tool_name: Araç adı
        *args, **kwargs: Araca geçirilecek parametreler
    
    Returns:
        Aracın çalışma sonucu
    """
    type_map = {
        'maintenance': ['cleanup', 'fix', 'reset'],
        'migration': ['migrate'],
        'monitoring': ['monitor', 'check'],
        'session_management': ['session'],
        'spam_management': ['spam', 'activate']
    }
    
    if tool_type not in type_map:
        raise ValueError(f"Geçersiz araç tipi: {tool_type}")
    
    # Modülü import et
    try:
        module = importlib.import_module(f"utils.{tool_type}")
        tool_path = module.get_tool_path(tool_name)
        
        if not tool_path.exists():
            raise FileNotFoundError(f"Araç bulunamadı: {tool_path}")
        
        # Aracı çalıştır
        spec = importlib.util.spec_from_file_location(tool_name, tool_path)
        tool_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_module)
        
        if hasattr(tool_module, 'main'):
            return tool_module.main(*args, **kwargs)
        else:
            raise AttributeError(f"Araçta main() fonksiyonu bulunamadı: {tool_name}")
            
    except Exception as e:
        raise Exception(f"Araç çalıştırma hatası: {str(e)}")

def list_available_tools():
    """Mevcut araçları listeler"""
    tools = {}
    for category in ['maintenance', 'migration', 'monitoring', 'session_management', 'spam_management']:
        category_dir = UTILS_DIR / category
        if category_dir.exists():
            tools[category] = [
                p.stem for p in category_dir.glob("*.py") 
                if p.stem != "__init__"
            ]
    return tools 