#!/usr/bin/env python3
"""Baron — geriye dönük uyumluluk; final launcher'a yönlendirir."""

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "baron_bot_launcher.py"
    sys.argv[0] = str(target)
    if len(sys.argv) == 1:
        sys.argv.append("menu")
    runpy.run_path(str(target), run_name="__main__")
