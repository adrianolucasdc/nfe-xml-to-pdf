#!/usr/bin/env python
"""Build standalone .exe with PyInstaller (stub - implementado no Commit 11)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    print("⚠️  Build script será implementado no Commit 11")
    print("    Por enquanto, use: pyinstaller --onefile -n nfe2pdf src/nfe2pdf/__main__.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())