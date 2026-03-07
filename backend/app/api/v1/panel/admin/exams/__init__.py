"""
Exams Admin Module

Admin endpoints for exam archive management:
- Scan and import real IHK exam PDFs
- Queue AI analysis tasks
- List archive exams and questions
- Auto-generate courses from exam questions
"""

from .archive import archive_bp
from .course_generator import course_gen_bp
from .intelligence import intelligence_bp

from app.api.v1 import api_v1

api_v1.register_blueprint(archive_bp)
api_v1.register_blueprint(course_gen_bp)
api_v1.register_blueprint(intelligence_bp)

__all__ = ['archive_bp', 'course_gen_bp', 'intelligence_bp']
