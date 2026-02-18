"""
PDF Service Exceptions

Custom exception classes for PDF extraction and validation.
"""


class PDFExtractionError(Exception):
    """Base exception for PDF extraction errors"""
    pass


class PDFPasswordProtectedError(PDFExtractionError):
    """Raised when PDF is password protected"""
    pass


class PDFCorruptedError(PDFExtractionError):
    """Raised when PDF is corrupted or unreadable"""
    pass
