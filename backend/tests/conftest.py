"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
import os

# Add backend/src to path for tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
