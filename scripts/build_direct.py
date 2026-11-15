#!/usr/bin/env python
"""Build executable with proper environment setup for conda DLLs."""

import os
import subprocess
import sys
from pathlib import Path

# Set up PATH to include conda Library/bin so PyInstaller can find dependencies
conda_prefix = os.environ.get("CONDA_PREFIX", "")
lib_bin = Path(conda_prefix) / "Library" / "bin" if conda_prefix else Path()
dll_dir = Path(conda_prefix) / "DLLs" if conda_prefix else Path()

if lib_bin.exists():
    # Prepend to PATH so PyInstaller's dependency analysis finds DLLs
    os.environ["PATH"] = str(lib_bin) + os.pathsep + os.environ.get("PATH", "")
if dll_dir.exists():
    os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ.get("PATH", "")

ROOT = Path(__file__).parent.parent

# Check if icon exists
icon_path = ROOT / "src" / "nfe2pdf" / "assets" / "logo.png"
icon_arg = ["--icon", str(icon_path)] if icon_path.exists() else []

# Run PyInstaller directly with command line args
cmd = (
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "nfe2pdf",
        "--noconfirm",
        "--clean",
        "--noconsole",
        # Add paths for dependency analysis
        "--paths",
        str(lib_bin),
        "--paths",
        str(dll_dir),
        # Collect all binaries for problematic packages
        "--collect-all",
        "ctypes",
        "--collect-all",
        "lzma",
        "--collect-all",
        "bz2",
        "--collect-all",
        "pyexpat",
        "--collect-all",
        "_decimal",
        # Hidden imports
        "--hidden-import",
        "ctypes",
        "--hidden-import",
        "ctypes._ctypes",
        "--hidden-import",
        "ctypes.wintypes",
        "--hidden-import",
        "ctypes.util",
        "--hidden-import",
        "decimal",
        "--hidden-import",
        "lzma",
        "--hidden-import",
        "bz2",
        "--hidden-import",
        "pyexpat",
        "--hidden-import",
        "json",
        "--hidden-import",
        "yaml",
        "--hidden-import",
        "click",
        "--hidden-import",
        "loguru",
        "--hidden-import",
        "pydantic",
        "--hidden-import",
        "pydantic_settings",
        "--hidden-import",
        "lxml",
        "--hidden-import",
        "lxml.etree",
        "--hidden-import",
        "lxml._elementpath",
        "--hidden-import",
        "PIL",
        "--hidden-import",
        "PIL.Image",
        "--hidden-import",
        "PIL.ImageDraw",
        "--hidden-import",
        "PIL.ImageFont",
        "--hidden-import",
        "brazilfiscalreport",
        "--hidden-import",
        "brazilfiscalreport.danfe",
        "--hidden-import",
        "brazilfiscalreport.danfe.config",
        "--hidden-import",
        "charset_normalizer",
        # Data files
        "--add-data",
        f"{ROOT / 'config.yaml.example'};.",
        "--add-data",
        f"{ROOT / 'LGPL-3.0.txt'};.",
        # Runtime hook
        "--runtime-hook",
        f"{ROOT / 'scripts' / 'runtime_hook_dlls.py'}",
    ]
    + icon_arg
    + [
        # Main entry point
        str(ROOT / "src" / "nfe2pdf" / "__main__.py"),
    ]
)

# Filter out empty strings
cmd = [c for c in cmd if c]

print(f"[RUN] {' '.join(cmd)}")
result = subprocess.run(cmd, cwd=ROOT)
sys.exit(result.returncode)
