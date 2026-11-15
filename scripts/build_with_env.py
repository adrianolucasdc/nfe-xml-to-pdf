#!/usr/bin/env python
"""Build executable with proper environment setup for conda DLLs."""

import os
import subprocess
import sys
from pathlib import Path

# Set up PATH to include conda Library/bin so PyInstaller can find dependencies
conda_prefix = os.environ.get("CONDA_PREFIX", "")
if conda_prefix:
    lib_bin = Path(conda_prefix) / "Library" / "bin"
    if lib_bin.exists():
        # Prepend to PATH so PyInstaller's dependency analysis finds DLLs
        os.environ["PATH"] = str(lib_bin) + os.pathsep + os.environ.get("PATH", "")

ROOT = Path(__file__).parent.parent
SPEC = ROOT / "nfe2pdf.spec"

# Run PyInstaller with the modified environment
result = subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", str(SPEC)], cwd=ROOT)

sys.exit(result.returncode)
