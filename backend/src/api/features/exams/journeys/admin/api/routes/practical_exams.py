"""
Exam Systems - Practical Exams Routes (Admin Journey)

Endpoints for managing Practical exam templates.

Endpoints:
  POST   /admin/exams/practical - Create Practical exam
  GET    /admin/exams/practical - List Practical exams

Phase: 5.3.2 - Exam Systems Domain
Reference: 02a_System-Features.md (practical_exam_engine)
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
practical_exams_bp = Blueprint('exam_systems_practical_exams', __name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class PracticalExamCreate(BaseModel):
    """Request model for creating Practical exam"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    course_id: str = Field(...)
    chapter_id: Optional[str] = None
    min_steps: int = Field(3, ge=1, le=20, description="Minimum practical steps")
    time_limit_minutes: int = Field(90, ge=1, le=300)
    passing_percentage: Decimal = Field(Decimal("60.0"), ge=0, le=100)


# ============================================================================
# Endpoints
# ============================================================================

@practical_exams_bp.route('/admin/exams/practical', methods=['POST'])
@jwt_required()
@admin_required
def create_practical_exam():
    """
    Create a new Practical exam template.

    Request Body:
        {
            "title": "Netzwerk-Konfiguration Praxisprüfung",
            "description": "Optional",
            "course_id": "uuid",
            "chapter_id": "uuid",  // optional
            "min_steps": 3,
            "time_limit_minutes": 90,
            "passing_percentage": 60
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
            exam_request = PracticalExamCreate(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        # Create exam using factory
        exam_data = ExamFactory.create_practical_exam(
            title=exam_request.title,
            course_id=exam_request.course_id,
            chapter_id=exam_request.chapter_id,
            description=exam_request.description,
            min_steps=exam_request.min_steps,
            time_limit_minutes=exam_request.time_limit_minutes,
            passing_percentage=exam_request.passing_percentage
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


@practical_exams_bp.route('/admin/exams/practical', methods=['GET'])
@jwt_required()
@admin_required
def list_practical_exams():
    """
    List all Practical exams for a course.

    Query Parameters:
        course_id: UUID (required)

    Response:
        200: Success
        400: Missing course_id
        500: Internal server error
    """
    try:
        course_id = request.args.get('course_id')
        if not course_id:
            return jsonify({
                "success": False,
                "error": {"code": "MISSING_PARAMETER", "message": "course_id is required"}
            }), 400

        exams = ExamRepository.get_exams_by_course(course_id, exam_type='practical')

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


__all__ = ['practical_exams_bp']
