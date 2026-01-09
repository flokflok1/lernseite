"""
DEPRECATED: PDF Service Legacy Bridge

This module is deprecated. Use the new modular pdf package instead:

    from app.services.pdf import PDFService

This bridge maintains backward compatibility with the old import path.
"""

import warnings

# Show deprecation warning
warnings.warn(
    "pdf_service module is deprecated. "
    "Use 'from app.services.pdf import PDFService' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new package for backward compatibility
from app.services.pdf import (
    PDFService,
    PDFExtractor,
    PDFAnalyzer,
    PDFValidator,
    PDFExtractionError,
    PDFPasswordProtectedError,
    PDFCorruptedError
)

__all__ = [
    'PDFService',
    'PDFExtractor',
    'PDFAnalyzer',
    'PDFValidator',
    'PDFExtractionError',
    'PDFPasswordProtectedError',
    'PDFCorruptedError'
]

__doc__ = """
LEGACY MODULE - Use the new pdf package instead:
    from app.services.pdf import PDFService

This module provides backward compatibility only.
All new code should import from the new pdf package.
"""
