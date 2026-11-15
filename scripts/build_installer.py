#!/usr/bin/env python
"""Build Windows installer with Inno Setup.

Usage:
    python scripts/build_installer.py          # Build installer
    python scripts/build_installer.py --clean  # Clean output first
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
INSTALLER_OUTPUT = ROOT / "installer_output"
SCRIPT = ROOT / "scripts" / "build_installer.iss"


def clean() -> None:
    """Remove installer output."""
    if INSTALLER_OUTPUT.exists():
        shutil.rmtree(INSTALLER_OUTPUT)
        print(f"[CLEAN] Removed {INSTALLER_OUTPUT.relative_to(ROOT)}")


def build(clean_first: bool = False) -> int:
    """Build installer with Inno Setup."""
    if clean_first:
        clean()

    # Check if executable exists
    exe_path = DIST / "nfe2pdf.exe"
    if not exe_path.exists():
        print("[ERROR] Executable not found. Run 'python scripts/build_exe.py' first.")
        return 1

    # Check Inno Setup compiler
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    iscc = None
    for path in iscc_paths:
        if Path(path).exists():
            iscc = path
            break

    if not iscc:
        print("[ERROR] Inno Setup compiler (ISCC.exe) not found.")
        print("Install Inno Setup 6 from https://jrsoftware.org/isinfo.php")
        return 1

    # Ensure output directory exists
    INSTALLER_OUTPUT.mkdir(parents=True, exist_ok=True)

    # Run Inno Setup compiler
    cmd = [iscc, str(SCRIPT)]
    print(f"[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)

    if result.returncode != 0:
        print("[ERROR] Inno Setup compilation failed")
        return result.returncode

    # Find and report output
    setup_files = list(INSTALLER_OUTPUT.glob("*.exe"))
    if setup_files:
        for setup_file in setup_files:
            size_mb = setup_file.stat().st_size / (1024 * 1024)
            print(f"[SUCCESS] Built installer: {setup_file.relative_to(ROOT)} ({size_mb:.1f} MB)")
    else:
        print("[WARNING] No installer executable found in output directory")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build nfe2pdf Windows installer")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean installer output before building",
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

    return build(clean_first=args.clean)


if __name__ == "__main__":
    sys.exit(main())
