"""Repo-local shim for src-layout imports during direct execution.

This makes local commands such as `python3 -m eduflow_cli.main` and plain
`unittest` discovery work from the repository root without requiring an
editable install or explicit PYTHONPATH.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["__version__"]
__version__ = "0.1.0"

_SRC_PACKAGE_DIR = Path(__file__).resolve().parent.parent / "src" / "eduflow_cli"
if _SRC_PACKAGE_DIR.is_dir():
    __path__.append(str(_SRC_PACKAGE_DIR))
