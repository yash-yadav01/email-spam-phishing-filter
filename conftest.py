"""
conftest.py
===========
Pytest configuration — adds the project root to sys.path so that
`from src.xxx import ...` works when running tests from the project root.
"""
import sys
from pathlib import Path

# Insert project root at the front of sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
