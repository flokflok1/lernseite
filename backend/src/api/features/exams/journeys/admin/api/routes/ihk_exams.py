"""
Exam Systems - IHK Exams Routes (Admin Journey)

Endpoints for managing IHK exam templates.

Endpoints:
  POST   /admin/exams/ihk - Create IHK exam
  GET    /admin/exams/ihk - List IHK exams
  PUT    /admin/exams/ihk/:id - Update IHK exam

Phase: 5.3.2 - Exam Systems Domain
Reference: 02a_System-Features.md (ihk_exam_system)
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

from app.middleware.auth import admin_required
from src.api.exam_systems.core.domain.repositories import ExamRepository
from src.api.exam_systems.core.domain.factories import ExamFactory, ExamQuestionFactory


# Blueprint
ihk_exams_bp = Blueprint('exam_systems_ihk_exams', __name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class IHKExamCreate(BaseModel):
    """Request model for creating IHK exam"""
    title: str = Field(..., min_length=1, max_length=200, description="Exam title")
    description: Optional[str] = Field(None, description="Exam description")
    course_id: str = Field(..., description="Course UUID")
    chapter_id: Optional[str] = Field(None, description="Optional chapter UUID")
    time_limit_minutes: int = Field(60, ge=1, le=300, description="Time limit in minutes")
    passing_percentage: Decimal = Field(Decimal("50.0"), ge=0, le=100, description="Passing percentage")


class IHKExamUpdate(BaseModel):
    """Request model for updating IHK exam"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=300)
    passing_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class IHKQuestionCreate(BaseModel):
    """Request model for adding question to IHK exam"""
    question_text: str = Field(..., min_length=1, description="Question text")
    question_type: str = Field("multiple_choice", description="Question type")
    options: List[str] = Field(..., min_items=2, description="Answer options")
    correct_answers: List[int] = Field(..., min_items=1, description="Correct answer indices")
    points: int = Field(1, ge=1, description="Points for this question")
    explanation: Optional[str] = None
    order_index: int = Field(0, ge=0, description="Order in exam")


# ============================================================================
# Endpoints
# ============================================================================

@ihk_exams_bp.route('/admin/exams/ihk', methods=['POST'])
@jwt_required()
@admin_required
def create_ihk_exam():
    """
    Create a new IHK exam template.

    Request Body:
        {
            "title": "IHK FISI Abschlussprüfung 2024",
            "description": "Optional description",
            "course_id": "course-uuid",
            "chapter_id": "chapter-uuid",  // optional
            "time_limit_minutes": 60,
            "passing_percentage": 50
        }

    Response:
        201: Created
            {
                "success": true,
                "data": {
                    "exam_id": "uuid",
                    "exam_type": "ihk",
                    "title": "...",
                    ...
                }
            }
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
            exam_request = IHKExamCreate(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        # Create exam using factory
        exam_data = ExamFactory.create_ihk_exam(
            title=exam_request.title,
            course_id=exam_request.course_id,
            chapter_id=exam_request.chapter_id,
            description=exam_request.description,
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


@ihk_exams_bp.route('/admin/exams/ihk', methods=['GET'])
@jwt_required()
@admin_required
def list_ihk_exams():
    """
    List all IHK exams for a course.

    Query Parameters:
        course_id: UUID of the course (required)

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "exams": [
                        {
                            "exam_id": "uuid",
                            "exam_type": "ihk",
                            "title": "...",
                            "time_limit_minutes": 60,
                            "passing_percentage": 50,
                            "is_active": true
                        },
                        ...
                    ],
                    "total": 5
                }
            }
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

        # Get IHK exams for course
        exams = ExamRepository.get_exams_by_course(course_id, exam_type='ihk')

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


@ihk_exams_bp.route('/admin/exams/ihk/<exam_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_ihk_exam(exam_id: str):
    """
    Update an IHK exam.

    Args:
        exam_id: UUID of the exam

    Request Body:
        {
            "title": "Updated title",
            "description": "Updated description",
            "time_limit_minutes": 90,
            "passing_percentage": 60,
            "is_active": true
        }

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "exam_id": "uuid",
                    "exam_type": "ihk",
                    "title": "...",
                    ...
                }
            }
        400: Validation error
        404: Exam not found
        500: Internal server error
    """
    try:
        # Check if exam exists
        exam = ExamRepository.get_exam_by_id(exam_id)
        if not exam:
            return jsonify({
                "success": False,
                "error": {"code": "EXAM_NOT_FOUND", "message": f"Exam {exam_id} not found"}
            }), 404

        # Validate it's an IHK exam
        if exam['exam_type'] != 'ihk':
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_EXAM_TYPE", "message": "This is not an IHK exam"}
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_REQUEST", "message": "Request body required"}
            }), 400

        try:
            update_request = IHKExamUpdate(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        # Build update dict (only include non-None values)
        update_data = {}
        if update_request.title is not None:
            update_data['title'] = update_request.title
        if update_request.description is not None:
            update_data['description'] = update_request.description
        if update_request.time_limit_minutes is not None:
            update_data['time_limit_minutes'] = update_request.time_limit_minutes
        if update_request.passing_percentage is not None:
            update_data['passing_percentage'] = float(update_request.passing_percentage)
        if update_request.is_active is not None:
            update_data['is_active'] = update_request.is_active

        # Update exam
        updated_exam = ExamRepository.update_exam(exam_id, update_data)

        return jsonify({
            "success": True,
            "data": updated_exam
        }), 200

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "message": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "UPDATE_EXAM_ERROR", "message": str(e)}
        }), 500


__all__ = ['ihk_exams_bp']
