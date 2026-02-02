"""
Authoring Service Package

Universal chat-based content creation service for KI-Authoring-Studio:
- Chat-based AI interaction
- Chapter, lesson, task, learning method creation
- File context integration
- Preview generation

Version: D4 - Universal KI-Authoring-System
"""

from .exceptions import AuthoringServiceError
from .session_manager import SessionManager
from .chat_processor import ChatProcessor
from .preview_generator import PreviewGenerator
from .content_saver import ContentSaver
from .authoring_service import AuthoringService, get_authoring_service

__all__ = [
    'AuthoringServiceError',
    'SessionManager',
    'ChatProcessor',
    'PreviewGenerator',
    'ContentSaver',
    'AuthoringService',
    'get_authoring_service'
]
