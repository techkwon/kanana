"""Ensure local src/ layout is importable in ad-hoc CLI and unittest runs.

This keeps `python3 -m unittest discover -s tests` working from the repo root
without requiring callers to export PYTHONPATH manually.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if SRC.is_dir():
    src_str = str(SRC)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
