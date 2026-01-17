"""Courses API Module"""
from app.api.v1.courses.core import core_bp
from app.api.v1.courses.crud import crud_bp
from app.api.v1.courses.enrollment import enrollment_bp
from app.api.v1.courses.publishing import publishing_bp
__all__ = ['core_bp', 'crud_bp', 'enrollment_bp', 'publishing_bp']
