from infrastructure.config.loader import config_path

"""
Configuration loader for centralized config directory.
"""
from pathlib import Path

# Base directory for config files
BASE_DIR = Path(__file__).parent

def config_path(filename: str) -> Path:
    """Return the full Path to a config file under infrastructure/config."""
    return BASE_DIR / filename
