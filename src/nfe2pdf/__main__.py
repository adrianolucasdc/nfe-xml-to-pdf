"""Entry point: python -m nfe2pdf"""

from __future__ import annotations

import sys
from pathlib import Path

from nfe2pdf.cli import main

if __name__ == "__main__":
    # Check for direct file execution (Windows "Abrir com...")
    # This runs before Click parses arguments
    # We check if the first argument (after script name) looks like an XML file
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
        # Not an option, not a known subcommand, and looks like an XML file
        if not arg.startswith("-") and arg not in (
            "generate",
            "config",
            "install",
            "--help",
            "--version",
            "-h",
            "-V",
        ):
            xml_path = Path(arg)
            if xml_path.exists() and xml_path.suffix.lower() == ".xml":
                # Direct execution: invoke generate logic directly
                sys.argv = [sys.argv[0], "generate"] + sys.argv[1:]

    try:
        main()
    except Exception as exc:  # noqa: BLE001
        # Em modo --noconsole não há terminal: mostra alerta nativo
        if sys.stderr is None and sys.platform == "win32":
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, f"Erro fatal: {exc}", "nfe2pdf", 0x10)
        raise
