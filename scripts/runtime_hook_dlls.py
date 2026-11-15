"""Runtime hook to ensure DLLs are found at runtime."""

import os
import sys

# When running in PyInstaller onefile mode, sys._MEIPASS points to the temp extraction dir
# The DLLs we added via --add-binary should be in this directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    meipass = sys._MEIPASS
    # Add the MEIPASS directory to the DLL search path
    os.add_dll_directory(meipass)
    # Also add it to PATH for good measure
    os.environ["PATH"] = meipass + os.pathsep + os.environ.get("PATH", "")
    # Add MEIPASS to sys.path so Python can find extension modules (.pyd files)
    if meipass not in sys.path:
        sys.path.insert(0, meipass)
    # Also add lib-dynload subdirectory if it exists
    lib_dynload = os.path.join(meipass, "lib-dynload")
    if os.path.isdir(lib_dynload) and lib_dynload not in sys.path:
        sys.path.insert(0, lib_dynload)
