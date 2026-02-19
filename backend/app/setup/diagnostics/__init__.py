"""
LernsystemX Setup - Diagnostics Package

Re-exports all diagnostics classes for backward-compatible imports.
"""

from app.setup.diagnostics.checks import (  # noqa: F401
    DiagnosticCheckResult,
    DiagnosticsReport,
)
from app.setup.diagnostics.checks_part2 import SystemDiagnostics  # noqa: F401
