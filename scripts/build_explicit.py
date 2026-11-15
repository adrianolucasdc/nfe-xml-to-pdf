#!/usr/bin/env python
"""Build executable with explicit DLL bundling for conda."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Conda paths
conda_prefix = os.environ.get("CONDA_PREFIX", "")
lib_bin = Path(conda_prefix) / "Library" / "bin"
dll_dir = Path(conda_prefix) / "DLLs"

# Explicit DLLs to add
explicit_binaries = []

# Python DLLs from DLLs directory
if dll_dir.exists():
    for dll_name in [
        "_ctypes.pyd",
        "_decimal.pyd",
        "_lzma.pyd",
        "_bz2.pyd",
        "pyexpat.pyd",
        "python313.dll",
    ]:
        dll_path = dll_dir / dll_name
        if dll_path.exists():
            explicit_binaries.append((str(dll_path), "."))

# Dependency DLLs from Library/bin
if lib_bin.exists():
    for dll_name in ["ffi.dll", "libexpat.dll", "libbz2.dll", "liblzma.dll", "libmpdec-4.dll"]:
        dll_path = lib_bin / dll_name
        if dll_path.exists():
            explicit_binaries.append((str(dll_path), "."))

# Build command
cmd = [
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
]

# Add explicit binaries
for src, dest in explicit_binaries:
    cmd.extend(["--add-binary", f"{src};{dest}"])

# Hidden imports
hidden_imports = [
    "ctypes",
    "ctypes._ctypes",
    "ctypes.wintypes",
    "ctypes.util",
    "decimal",
    "lzma",
    "bz2",
    "pyexpat",
    "json",
    "yaml",
    "click",
    "loguru",
    "pydantic",
    "pydantic_settings",
    "lxml",
    "lxml.etree",
    "lxml._elementpath",
    "PIL",
    "PIL.Image",
    "PIL.ImageDraw",
    "PIL.ImageFont",
    "brazilfiscalreport",
    "brazilfiscalreport.danfe",
    "brazilfiscalreport.danfe.config",
    "charset_normalizer",
]
for hi in hidden_imports:
    cmd.extend(["--hidden-import", hi])

# Data files
cmd.extend(["--add-data", f"{ROOT / 'config.yaml.example'};."])
cmd.extend(["--add-data", f"{ROOT / 'LGPL-3.0.txt'};."])

# Runtime hook
cmd.extend(["--runtime-hook", f"{ROOT / 'scripts' / 'runtime_hook_dlls.py'}"])

# Icon
icon_path = ROOT / "src" / "nfe2pdf" / "assets" / "logo.png"
if icon_path.exists():
    cmd.extend(["--icon", str(icon_path)])

# Main entry point
cmd.append(str(ROOT / "src" / "nfe2pdf" / "__main__.py"))

print(f"[RUN] {' '.join(cmd)}")
result = subprocess.run(cmd, cwd=ROOT)
sys.exit(result.returncode)
