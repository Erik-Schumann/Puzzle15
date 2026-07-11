"""Pytest configuration: make project-root modules importable from tests/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
