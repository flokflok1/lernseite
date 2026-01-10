"""
Exam Systems - Chapter Completion Routes (Admin Journey)

Endpoints for managing Chapter Completion exam templates.

Endpoints:
  POST   /admin/exams/chapter-completion - Create Chapter Completion exam
  GET    /admin/exams/chapter-completion - List Chapter Completion exams

Phase: 5.3.2 - Exam Systems Domain
Reference: 02a_System-Features.md (chapter_completion_system)
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

from app.middleware.auth import admin_required
from src.api.exam_systems.core.domain.repositories import ExamRepository
from src.api.exam_systems.core.domain.factories import ExamFactory


# Blueprint
chapter_completion_exams_bp = Blueprint('exam_systems_chapter_completion_exams', __name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class ChapterCompletionExamCreate(BaseModel):
    """Request model for creating Chapter Completion exam"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    course_id: str = Field(...)
    chapter_id: str = Field(..., description="Chapter UUID (required)")
    time_limit_minutes: int = Field(90, ge=1, le=300)
    passing_percentage: Decimal = Field(Decimal("70.0"), ge=0, le=100)
    unlock_next_chapter: bool = Field(True, description="Unlock next chapter on pass")


# ============================================================================
# Endpoints
# ============================================================================

@chapter_completion_exams_bp.route('/admin/exams/chapter-completion', methods=['POST'])
@jwt_required()
@admin_required
def create_chapter_completion_exam():
    """
    Create a new Chapter Completion exam template.

    Request Body:
        {
            "title": "Kapitel 3 Abschlussprüfung",
            "description": "Optional",
            "course_id": "uuid",
            "chapter_id": "uuid",  // REQUIRED
            "time_limit_minutes": 90,
            "passing_percentage": 70,
            "unlock_next_chapter": true
        }

    Response:
        201: Created
        400: Validation error
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_REQUEST", "message": "Request body required"}
            }), 400

        try:
            exam_request = ChapterCompletionExamCreate(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        # Create exam using factory
        exam_data = ExamFactory.create_chapter_completion_exam(
            title=exam_request.title,
            course_id=exam_request.course_id,
            chapter_id=exam_request.chapter_id,
            description=exam_request.description,
            time_limit_minutes=exam_request.time_limit_minutes,
            passing_percentage=exam_request.passing_percentage,
            unlock_next_chapter=exam_request.unlock_next_chapter
        )

        # Save to database
        exam = ExamRepository.create_exam(exam_data)

        return jsonify({
            "success": True,
            "data": exam
        }), 201

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "message": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "CREATE_EXAM_ERROR", "message": str(e)}
        }), 500


@chapter_completion_exams_bp.route('/admin/exams/chapter-completion', methods=['GET'])
@jwt_required()
@admin_required
def list_chapter_completion_exams():
    """
    List all Chapter Completion exams.

    Query Parameters:
        course_id: UUID (optional, filter by course)
        chapter_id: UUID (optional, filter by chapter)

    Response:
        200: Success
        500: Internal server error
    """
    try:
        course_id = request.args.get('course_id')
        chapter_id = request.args.get('chapter_id')

        if chapter_id:
            # Get by chapter
            exams = ExamRepository.get_exams_by_chapter(chapter_id)
            exams = [e for e in exams if e['exam_type'] == 'chapter_completion']
        elif course_id:
            # Get by course
            exams = ExamRepository.get_exams_by_course(course_id, exam_type='chapter_completion')
        else:
            return jsonify({
                "success": False,
                "error": {"code": "MISSING_PARAMETER", "message": "course_id or chapter_id is required"}
            }), 400

        return jsonify({
            "success": True,
            "data": {
                "exams": exams,
                "total": len(exams)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "LIST_EXAMS_ERROR", "message": str(e)}
        }), 500


__all__ = ['chapter_completion_exams_bp']
