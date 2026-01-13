"""
Pydantic Models for Exam API.

Request/response validation models for the exam domain.
Enhanced with value objects for better type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any

from .value_objects import Difficulty, ExamMode


class ExamSimulationCreate(BaseModel):
    """Request model for creating an exam simulation."""

    mode: str = Field(default='smart', pattern='^(smart|manual)$')
    difficulty: str = Field(default='realistic', pattern='^(easy|realistic|hard)$')
    time_limit_minutes: int = Field(default=90, ge=15, le=180)
    focus_distribution: Optional[Dict[str, int]] = None
    extra_instructions: Optional[str] = None
    selected_files: Optional[List[str]] = None
    title: Optional[str] = None

    @validator('focus_distribution')
    def validate_focus_distribution(cls, v):
        """Validate that focus distribution sums to 100%."""
        if v is not None:
            total = sum(v.values())
            if total != 100:
                raise ValueError(f"Focus distribution must sum to 100%, got {total}%")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "smart",
                "difficulty": "realistic",
                "time_limit_minutes": 90,
                "focus_distribution": {
                    "Kalkulation": 35,
                    "Netzwerk": 30,
                    "SQL": 20,
                    "Projektmanagement": 15
                },
                "extra_instructions": "Fokus auf IHK-typische Aufgaben",
                "selected_files": ["file-uuid-1", "file-uuid-2"],
                "title": "FISI AP1 Simulation - Realistisch"
            }
        }


class ExamAttemptSubmit(BaseModel):
    """Request model for submitting exam attempt."""

    attempt_id: str = Field(description="Attempt UUID")
    answers: List[Dict[str, Any]] = Field(description="List of answers")
    time_spent_seconds: int = Field(ge=0, description="Time spent in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "550e8400-e29b-41d4-a716-446655440000",
                "answers": [
                    {"question_id": "q1", "answer": "A"},
                    {"question_id": "q2", "answer": "42"},
                    {"question_id": "q3", "answer": "true"}
                ],
                "time_spent_seconds": 3600
            }
        }


class UserExamProfileUpdate(BaseModel):
    """Request model for updating user exam profile."""

    profession: Optional[str] = Field(None, max_length=100)
    profession_detail: Optional[str] = Field(None, max_length=200)
    training_year: Optional[int] = Field(None, ge=1, le=4)
    target_exam: Optional[str] = Field(None, max_length=50)
    exam_date: Optional[str] = Field(None, description="ISO date string")
    region: Optional[str] = Field(None, max_length=100)
    ihk: Optional[str] = Field(None, max_length=200)
    ihk_code: Optional[str] = Field(None, max_length=20)
    preferred_difficulty: Optional[str] = Field(None, pattern='^(easy|realistic|hard)$')
    preferred_question_types: Optional[List[str]] = None
    daily_learning_goal_minutes: Optional[int] = Field(None, ge=0, le=480)

    class Config:
        json_schema_extra = {
            "example": {
                "profession": "FISI",
                "training_year": 2,
                "target_exam": "AP1",
                "exam_date": "2025-05-15",
                "region": "Baden-Württemberg",
                "ihk": "IHK Stuttgart",
                "preferred_difficulty": "realistic",
                "daily_learning_goal_minutes": 60
            }
        }


class ExamSimulationResponse(BaseModel):
    """Response model for exam simulation."""

    simulation_id: str
    course_id: str
    user_id: str
    title: str
    context: Dict[str, Any]
    config: Dict[str, Any]
    status: str
    error_message: Optional[str] = None
    attempt_count: int = 0
    best_score: Optional[float] = None
    avg_score: Optional[float] = None
    created_at: str
    updated_at: Optional[str] = None


class ExamAttemptResponse(BaseModel):
    """Response model for exam attempt."""

    attempt_id: str
    simulation_id: str
    started_at: str
    completed_at: Optional[str] = None
    time_spent_seconds: Optional[int] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    status: str


class ExamResultResponse(BaseModel):
    """Response model for exam result after submission."""

    attempt_id: str
    score: float
    max_score: float
    percentage: float
    passed: bool
    time_spent_seconds: int
    results_by_topic: Dict[str, Dict[str, Any]]
    answers: List[Dict[str, Any]]


class ExamContextResponse(BaseModel):
    """Response model for exam context."""

    profession: Optional[str] = None
    exam_level: Optional[str] = None
    region: Optional[str] = None
    ihk_standard: Optional[str] = None
    weak_topics: List[Dict[str, Any]] = []
    strong_topics: List[Dict[str, Any]] = []
    detected_topics: List[str] = []
    recommended_focus: Dict[str, int] = {}
    detected_files: List[Dict[str, Any]] = []
    confidence: float = 0.0
