#!/usr/bin/env python
"""Build standalone .exe with PyInstaller.

Usage:
    python scripts/build_exe.py          # Build default
    python scripts/build_exe.py --clean  # Clean build
    python scripts/build_exe.py --debug  # Debug build (with console)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SPEC = ROOT / "nfe2pdf.spec"


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run command and return result."""
    print(f"[RUN] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd or ROOT, capture_output=False)


def clean() -> None:
    """Remove build artifacts."""
    for path in (DIST, BUILD, SPEC):
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"[CLEAN] Removed {path.relative_to(ROOT)}")


def build(clean_first: bool = False, debug: bool = False) -> int:
    """Build executable with PyInstaller."""
    if clean_first:
        clean()

    # Check dependencies
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("[ERROR] PyInstaller not installed. Run: pip install pyinstaller")
        return 1

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
    ]

    # Add paths for dependency analysis (conda DLLs)
    import os
    conda_prefix = os.environ.get("CONDA_PREFIX", r"C:\Users\Adriano\miniconda3")
    lib_bin = Path(conda_prefix) / "Library" / "bin"
    dll_dir = Path(conda_prefix) / "DLLs"
    if lib_bin.exists():
        cmd.extend(["--paths", str(lib_bin)])
    if dll_dir.exists():
        cmd.extend(["--paths", str(dll_dir)])

    # Explicitly add required DLLs from conda environment
    # Python DLLs from DLLs directory
    if dll_dir.exists():

        # Python DLLs from DLLs directory
        if dll_dir.exists():
            for dll_name in ["_ctypes.pyd", "_decimal.pyd", "_lzma.pyd", "_bz2.pyd", "pyexpat.pyd", "python313.dll"]:
                dll_path = dll_dir / dll_name
                if dll_path.exists():
                    cmd.extend(["--add-binary", f"{dll_path};."])

        # Dependency DLLs from Library/bin
        if lib_bin.exists():
            for dll_name in ["ffi.dll", "libexpat.dll", "libbz2.dll", "liblzma.dll", "libmpdec-4.dll", "libcrypto-3-x64.dll", "libssl-3-x64.dll"]:
                dll_path = lib_bin / dll_name
                if dll_path.exists():
                    cmd.extend(["--add-binary", f"{dll_path};."])

    # Hidden imports for common missing modules
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

    # Collect standard library binaries (for conda extension modules)
    cmd.extend(["--collect-binaries", "ctypes"])
    cmd.extend(["--collect-binaries", "lzma"])
    cmd.extend(["--collect-binaries", "bz2"])
    cmd.extend(["--collect-binaries", "pyexpat"])

    # Add icon if exists
    logo_path = SRC / "nfe2pdf" / "assets" / "logo.png"
    if logo_path.exists():
        cmd.extend(["--icon", str(logo_path)])

    # Debug mode: show console
    if not debug:
        cmd.append("--noconsole")

    # Add data files
    # Add config template
    config_template = ROOT / "config.yaml.example"
    if config_template.exists():
        cmd.extend(["--add-data", f"{config_template};."])

    # Add LGPL license
    lgpl_license = ROOT / "LGPL-3.0.txt"
    if lgpl_license.exists():
        cmd.extend(["--add-data", f"{lgpl_license};."])

    # Collect binaries for missing DLLs (conda environment)
    # Try to find and add required DLLs
    import os

    conda_dlls = os.environ.get("CONDA_PREFIX")
    if conda_dlls:
        dll_dir = Path(conda_dlls) / "DLLs"
        lib_bin_dir = Path(conda_dlls) / "Library" / "bin"
        if dll_dir.exists():
            for dll_name in ["_ctypes.pyd", "_decimal.pyd", "_lzma.pyd", "_bz2.pyd", "pyexpat.pyd"]:
                dll_path = dll_dir / dll_name
                if dll_path.exists():
                    cmd.extend(["--add-binary", f"{dll_path};."])
            # Also add dependency DLLs from Library/bin (ffi.dll, libexpat.dll, etc.)
            if lib_bin_dir.exists():
                for dll_name in [
                    "ffi.dll",
                    "libexpat.dll",
                    "libbz2.dll",
                    "liblzma.dll",
                    "libmpdec-4.dll",
                ]:
                    dll_path = lib_bin_dir / dll_name
                    if dll_path.exists():
                        cmd.extend(["--add-binary", f"{dll_path};."])

    # Runtime hook for DLL loading
    runtime_hook = ROOT / "scripts" / "runtime_hook_dlls.py"
    if runtime_hook.exists():
        cmd.extend(["--runtime-hook", str(runtime_hook)])

    # Main entry point
    cmd.append(str(SRC / "nfe2pdf" / "__main__.py"))

    # Run PyInstaller
    result = run(cmd)
    if result.returncode != 0:
        print("[ERROR] PyInstaller build failed")
        return result.returncode

    # Verify output
    exe_path = DIST / "nfe2pdf.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[SUCCESS] Built {exe_path.relative_to(ROOT)} ({size_mb:.1f} MB)")
    else:
        print("[ERROR] Executable not found at expected location")
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build nfe2pdf executable")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Build with console window (for debugging)",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Only clean, don't build",
    )
    args = parser.parse_args()

    if args.clean_only:
        clean()
        return 0

    return build(clean_first=args.clean, debug=args.debug)


if __name__ == "__main__":
    sys.exit(main())
