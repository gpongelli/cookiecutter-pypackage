"""PyInstaller method to get working directory."""
import os
import sys
from pathlib import Path


def get_bundle_dir() -> Path:
    """Return bundle dir, different in case of binary file.

    Returns:
        folder as Path object.
    """
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = Path(sys._MEIPASS)  # type: ignore
    else:
        # we are running in a normal Python environment
        bundle_dir = Path.cwd()
        if 'PY_PKG_YEAR' in os.environ:
            # nox pass PY_PKG_YEAR env var, and its cwd is into docs/source
            bundle_dir = bundle_dir / '..' / '..'

    return bundle_dir
