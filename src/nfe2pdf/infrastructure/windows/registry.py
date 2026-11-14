"""Windows Registry manager for file associations."""
from __future__ import annotations

import contextlib
import sys

from nfe2pdf.domain.exceptions import FileAssociationError


class WindowsRegistryManager:
    """Manages Windows file associations via Registry.

    Uses HKEY_CURRENT_USER for non-admin installation.
    """

    def __init__(self) -> None:
        self._exe_path = self._get_exe_path()
        self._prog_id = "nfe2pdf.xml"
        self._description = "NF-e XML Document"

    def _get_exe_path(self) -> str:
        """Get the executable path for registry registration."""
        if getattr(sys, "frozen", False):
            # Running as PyInstaller executable
            return sys.executable
        # Running from source - use python -m nfe2pdf (direct file arg, no subcommand)
        return f'"{sys.executable}" -m nfe2pdf'

    def is_associated(self, extension: str = ".xml") -> bool:
        """Check if extension is associated with this application."""
        if sys.platform != "win32":
            return False

        try:
            import winreg

            # Check HKEY_CURRENT_USER\Software\Classes
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes") as key:
                try:
                    with winreg.OpenKey(key, extension) as ext_key:
                        prog_id, _ = winreg.QueryValueEx(ext_key, "")
                        return prog_id == self._prog_id
                except FileNotFoundError:
                    return False

        except Exception:
            return False

    def associate(self, extension: str = ".xml", description: str = "NF-e XML Document") -> None:
        """Associate extension with this application.

        Creates:
        - HKCU\\Software\\Classes\\.xml -> nfe2pdf.xml
        - HKCU\\Software\\Classes\\nfe2pdf.xml -> description
        - HKCU\\Software\\Classes\\nfe2pdf.xml\\shell\\open\\command -> exe path
        - HKCU\\Software\\Classes\\nfe2pdf.xml\\DefaultIcon -> exe path,0
        """
        if sys.platform != "win32":
            raise FileAssociationError("Associação de arquivo só suportada no Windows")

        try:
            import winreg

            # Ensure extension starts with dot
            if not extension.startswith("."):
                extension = f".{extension}"

            # Create extension key
            ext_path = rf"Software\Classes\{extension}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, ext_path) as ext_key:
                winreg.SetValueEx(ext_key, "", 0, winreg.REG_SZ, self._prog_id)

            # Create ProgID key
            prog_id_path = rf"Software\Classes\{self._prog_id}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, prog_id_path) as prog_key:
                winreg.SetValueEx(prog_key, "", 0, winreg.REG_SZ, description)

                # DefaultIcon
                with winreg.CreateKey(prog_key, "DefaultIcon") as icon_key:
                    if '"' in self._exe_path:
                        icon_path = self._exe_path.split('"')[1]
                    else:
                        icon_path = self._exe_path
                    if icon_path.endswith(".exe"):
                        winreg.SetValueEx(icon_key, "", 0, winreg.REG_SZ, f"{icon_path},0")
                    else:
                        winreg.SetValueEx(icon_key, "", 0, winreg.REG_SZ, icon_path)

                # shell\open\command
                with winreg.CreateKey(prog_key, r"shell\open\command") as cmd_key:
                    cmd = f'{self._exe_path} "%1"'
                    winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, cmd)

            # Notify Windows of change
            self._notify_shell()

        except PermissionError as e:
            raise FileAssociationError(
                "Permissao negada para modificar Registro. Execute como admin.",
                original_error=e,
            ) from e
        except Exception as e:
            raise FileAssociationError(
                f"Erro ao criar associacao no Registro: {e}",
                original_error=e,
            ) from e

    def unassociate(self, extension: str = ".xml") -> None:
        """Remove association for extension."""
        if sys.platform != "win32":
            return

        try:
            import winreg

            if not extension.startswith("."):
                extension = f".{extension}"

            # Delete extension key
            with contextlib.suppress(FileNotFoundError):
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{extension}")

            # Delete ProgID key
            with contextlib.suppress(FileNotFoundError):
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{self._prog_id}")

            self._notify_shell()

        except Exception as e:
            raise FileAssociationError(
                f"Erro ao remover associacao: {e}",
                original_error=e,
            ) from e

    def _notify_shell(self) -> None:
        """Notify Windows Shell of association change."""
        try:
            import ctypes
            # SHChangeNotify with SHCNE_ASSOCCHANGED
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        except Exception:
            pass  # Best effort


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"