"""
Backend i18n System
Error codes instead of hardcoded strings - Frontend handles translation
"""
from .error_codes import ErrorCode, error_response, success_response
from .message_codes import MessageCode

__all__ = ['ErrorCode', 'MessageCode', 'error_response', 'success_response']
