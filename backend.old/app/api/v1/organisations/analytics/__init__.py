"""
Organisations Analytics Feature

Analytics and reporting functionality for organisations.

Files:
- stats.py: Organisation statistics (103 LOC)
- reports.py: Organisation reports (253 LOC)
- time_series.py: Time series analytics (273 LOC)

Total: 629 LOC

This is a TRUE FEATURE subdirectory - kept separate from role-based structure.
"""

from app.api.v1.organisations.analytics import (
    stats,
    reports,
    time_series
)

__all__ = ['stats', 'reports', 'time_series']
