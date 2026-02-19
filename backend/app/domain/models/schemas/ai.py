"""
LernsystemX Admin AI Models

Pydantic models for AI job management:
- AI job creation request
- AI job response
- AI job finalize request

Phase B24-05 - ISO 9001:2015 compliant
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class AIJobCreateRequest(BaseModel):
    """
    AI job creation request model

    Example:
        >>> request = AIJobCreateRequest(
        ...     type="course_from_pdf",
        ...     file_name="python_basics.pdf",
        ...     prompt="Create a beginner Python course"
        ... )
    """
    type: str = Field(..., description="Job type (course_from_pdf, module_autogen, lesson_autogen)")
    file_name: Optional[str] = Field(None, max_length=255, description="Input file name")
    prompt: Optional[str] = Field(None, max_length=5000, description="User prompt for AI guidance")
    course_id: Optional[str] = Field(None, description="Course UUID (for module/lesson generation)")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate job type"""
        valid_types = ['course_from_pdf', 'module_autogen', 'lesson_autogen']
        if v not in valid_types:
            raise ValueError(f'Type must be one of: {", ".join(valid_types)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class AIJobResponse(BaseModel):
    """
    AI job response model

    Example:
        >>> job = AIJobResponse(
        ...     id="uuid",
        ...     user_id="uuid",
        ...     type="course_from_pdf",
        ...     status="processing",
        ...     progress=50,
        ...     created_at=datetime.now()
        ... )
    """
    id: str = Field(..., description="Job UUID")
    user_id: str = Field(..., description="User UUID")
    course_id: Optional[str] = Field(None, description="Course UUID")
    type: str = Field(..., description="Job type")
    status: str = Field(..., description="Job status (pending, processing, completed, failed, cancelled)")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    input_file: Optional[str] = Field(None, description="Input file name")
    input_prompt: Optional[str] = Field(None, description="User prompt")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Generated output data (JSONB)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Optional joined fields
    user_email: Optional[str] = Field(None, description="User email (from join)")
    course_title: Optional[str] = Field(None, description="Course title (from join)")

    model_config = ConfigDict(from_attributes=True)


class AIJobFinalizeRequest(BaseModel):
    """
    AI job finalize request model

    Used to create actual course/modules/lessons from AI output

    Example:
        >>> request = AIJobFinalizeRequest(
        ...     create_course=True,
        ...     create_modules=True,
        ...     create_lessons=True
        ... )
    """
    create_course: bool = Field(default=True, description="Create course from AI output")
    create_modules: bool = Field(default=True, description="Create modules from AI output")
    create_lessons: bool = Field(default=True, description="Create lessons from AI output")
    override_existing: bool = Field(default=False, description="Override existing content if course_id exists")

    model_config = ConfigDict(from_attributes=True)
