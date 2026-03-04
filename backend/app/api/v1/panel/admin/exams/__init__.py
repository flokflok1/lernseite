"""
Exams Admin Module

Admin endpoints for exam archive management:
- Scan and import real IHK exam PDFs
- Queue AI analysis tasks
- List archive exams and questions
"""

from .archive import archive_bp

from app.api.v1 import api_v1

api_v1.register_blueprint(archive_bp)

__all__ = ['archive_bp']
