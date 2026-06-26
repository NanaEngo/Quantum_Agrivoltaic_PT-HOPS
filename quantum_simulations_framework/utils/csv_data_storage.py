"""
CSV Data Storage — RE-EXPORT MODULE

Canonical source is src/io/csv_storage.py.
This module re-exports CSVDataStorage for backward compatibility.
"""

from src.io.csv_storage import CSVDataStorage  # noqa: F401

__all__ = ["CSVDataStorage"]
