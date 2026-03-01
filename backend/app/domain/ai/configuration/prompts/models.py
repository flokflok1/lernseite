"""
LernsystemX KI - Prompt Models

Pydantic models for centralized prompt template management.

Models:
- PromptMessage: Individual message in prompt (system/user/assistant)
- PromptVariable: Variable definition for template rendering
- PromptTemplate: Complete prompt template with metadata
- PromptContext: Runtime context for template rendering

Phase 24 - Developer Guide / KI-Prompts
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict, Any, List, Optional
from datetime import datetime


class PromptMessage(BaseModel):
    """
    Single message in a prompt template.

    Follows OpenAI/Anthropic chat message format with role and content.
    Content can contain template variables using {{variable_name}} syntax.

    Examples:
        system_msg = PromptMessage(
            role="system",
            content="Du bist ein KI-Tutor für {{course_title}}."
        )
    """
    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Message role: system (instructions), user (input), assistant (example)"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Message content with optional {{variable}} placeholders"
    )

    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Ensure content is not just whitespace"""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v


class PromptVariable(BaseModel):
    """
    Variable definition for prompt template.

    Defines a placeholder variable that must be provided when rendering
    the prompt template. Variables are referenced in message content using
    {{variable_name}} syntax.

    Examples:
        course_var = PromptVariable(
            name="course_title",
            description="Title of the course being taught",
            required=True
        )

        optional_var = PromptVariable(
            name="user_level",
            description="User's knowledge level",
            required=False,
            default="intermediate"
        )
    """
    name: str = Field(
        ...,
        min_length=1,
        pattern=r'^[a-z_][a-z0-9_]*$',
        description="Variable name (lowercase, underscores, no spaces)"
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Human-readable description of what this variable contains"
    )
    required: bool = Field(
        default=True,
        description="Whether this variable must be provided"
    )
    default: Optional[str] = Field(
        default=None,
        description="Default value if not provided (only for optional variables)"
    )

    @field_validator('default')
    @classmethod
    def default_only_if_optional(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure default is only set for optional variables"""
        # Note: In Pydantic v2, we use info.data to access other fields
        if v is not None and info.data.get('required', True):
            raise ValueError("Default value can only be set for optional variables (required=False)")
        return v


class PromptTemplate(BaseModel):
    """
    Complete prompt template definition.

    Central model for managing AI prompts across all learning methods.
    Templates are versioned, support multiple AI models, and can be
    customized per role or organisation.

    Template Rendering:
        1. Load template from registry: get_prompt_template("explain_concept")
        2. Provide context variables: {"course_title": "Python", ...}
        3. Render messages: replace {{variable}} with actual values
        4. Send to AI model specified in template.model

    Language Modes:
        - "source": Prompt in content's source language
        - "target": Prompt in user's target language
        - "mixed": Combination (e.g., translate from source to target)

    Examples:
        explain_template = PromptTemplate(
            code="explain_concept",
            title="Konzept Erklärung",
            description="Erklärt ein Konzept schrittweise mit Beispielen",
            tags=["learning", "explanation", "beginner-friendly"],
            messages=[
                PromptMessage(
                    role="system",
                    content="Du bist ein KI-Tutor für {{course_title}}. Dein Ziel ist es, Konzepte verständlich zu erklären."
                ),
                PromptMessage(
                    role="user",
                    content="Erkläre folgendes Konzept: {{concept_text}}"
                )
            ],
            variables=[
                PromptVariable(name="course_title", description="Kurstitel", required=True),
                PromptVariable(name="concept_text", description="Zu erklärender Text", required=True),
                PromptVariable(name="user_level", description="Wissenslevel", required=False, default="beginner")
            ],
            model="claude-3-sonnet-20240229",
            max_tokens=16000,
            temperature=0.7,
            language_mode="target",
            allowed_roles=["student", "teacher", "admin"]
        )
    """
    code: str = Field(
        ...,
        min_length=1,
        pattern=r'^[a-z_][a-z0-9_]*$',
        description="Unique identifier for this template (e.g., 'explain_concept', 'quiz_generator')"
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Human-readable title"
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed description of what this prompt does"
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Template version number (increment on changes)"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization (e.g., 'learning', 'quiz', 'translation')"
    )
    messages: List[PromptMessage] = Field(
        ...,
        min_length=1,
        description="Ordered list of messages (system, user, assistant)"
    )
    variables: List[PromptVariable] = Field(
        default_factory=list,
        description="Variables that must be provided when rendering"
    )

    # AI Model Configuration
    model: Optional[str] = Field(
        default=None,
        description="Preferred AI model (e.g., 'claude-3-sonnet-20240229', 'gpt-4-turbo')"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=128000,
        description="Maximum tokens for AI response"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Temperature for AI model (0.0 = deterministic, 2.0 = creative)"
    )

    # Internationalization
    language_mode: Literal["source", "target", "mixed"] = Field(
        default="target",
        description="How to handle language: source (content lang), target (user lang), mixed (both)"
    )

    # Access Control
    allowed_roles: List[str] = Field(
        default_factory=list,
        description="Roles allowed to use this template (empty = all roles)"
    )

    # Metadata
    created_at: Optional[datetime] = Field(
        default=None,
        description="Template creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )
    created_by: Optional[str] = Field(
        default=None,
        description="Creator identifier (user_id or 'system')"
    )

    @field_validator('messages')
    @classmethod
    def validate_message_roles(cls, v: List[PromptMessage]) -> List[PromptMessage]:
        """Ensure at least one system or user message exists"""
        if not v:
            raise ValueError("At least one message is required")

        roles = [msg.role for msg in v]
        if "system" not in roles and "user" not in roles:
            raise ValueError("Template must contain at least one 'system' or 'user' message")

        return v

    @field_validator('variables')
    @classmethod
    def validate_variables_unique(cls, v: List[PromptVariable]) -> List[PromptVariable]:
        """Ensure variable names are unique"""
        names = [var.name for var in v]
        if len(names) != len(set(names)):
            raise ValueError("Variable names must be unique")
        return v

    def get_required_variables(self) -> List[str]:
        """Get list of required variable names"""
        return [var.name for var in self.variables if var.required]

    def get_optional_variables(self) -> Dict[str, str]:
        """Get dict of optional variables with their defaults"""
        return {
            var.name: var.default or ""
            for var in self.variables
            if not var.required
        }

    def render(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Render template with provided context variables.

        Args:
            context: Dictionary mapping variable names to values

        Returns:
            List of rendered messages in format: [{"role": "...", "content": "..."}]

        Raises:
            ValueError: If required variables are missing

        Examples:
            template = get_prompt_template("explain_concept")
            messages = template.render({
                "course_title": "Python Basics",
                "concept_text": "What are list comprehensions?",
                "user_level": "beginner"
            })
        """
        # Check required variables
        required = set(self.get_required_variables())
        provided = set(context.keys())
        missing = required - provided

        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

        # Add optional variables with defaults
        full_context = {**self.get_optional_variables(), **context}

        # Render each message
        rendered_messages = []
        for message in self.messages:
            content = message.content

            # Replace {{variable}} placeholders
            for var_name, var_value in full_context.items():
                placeholder = f"{{{{{var_name}}}}}"
                content = content.replace(placeholder, str(var_value))

            rendered_messages.append({
                "role": message.role,
                "content": content
            })

        return rendered_messages

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return self.model_dump(mode='json')

    class Config:
        json_schema_extra = {
            "example": {
                "code": "explain_concept",
                "title": "Konzept Erklärung",
                "description": "Erklärt ein Konzept schrittweise mit Beispielen",
                "version": 1,
                "tags": ["learning", "explanation"],
                "messages": [
                    {
                        "role": "system",
                        "content": "Du bist ein KI-Tutor für {{course_title}}."
                    },
                    {
                        "role": "user",
                        "content": "Erkläre: {{concept_text}}"
                    }
                ],
                "variables": [
                    {
                        "name": "course_title",
                        "description": "Kurstitel",
                        "required": True
                    },
                    {
                        "name": "concept_text",
                        "description": "Zu erklärender Text",
                        "required": True
                    }
                ],
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 2000,
                "temperature": 0.7,
                "language_mode": "target",
                "allowed_roles": ["student", "teacher"]
            }
        }


class PromptContext(BaseModel):
    """
    Runtime context for rendering prompt templates.

    Optional helper model to validate context before rendering.
    Can be used to ensure all required data is present before
    making expensive AI API calls.

    Examples:
        context = PromptContext(
            course_title="Python Basics",
            lesson_title="List Comprehensions",
            lesson_content="...",
            user_level="intermediate",
            language="de"
        )

        messages = template.render(context.model_dump())
    """
    # Common context variables across all learning methods
    course_title: Optional[str] = Field(default=None, description="Course title")
    lesson_title: Optional[str] = Field(default=None, description="Lesson title")
    lesson_content: Optional[str] = Field(default=None, description="Lesson content text")
    user_level: Optional[str] = Field(default=None, description="User knowledge level")
    language: Optional[str] = Field(default=None, description="Target language code (e.g., 'de', 'en')")
    organisation_name: Optional[str] = Field(default=None, description="Organization name")

    # Learning method specific
    concept_text: Optional[str] = Field(default=None, description="Text to explain")
    num_flashcards: Optional[int] = Field(default=None, ge=1, description="Number of flashcards")
    num_questions: Optional[int] = Field(default=None, ge=1, description="Number of quiz questions")
    translation_source_lang: Optional[str] = Field(default=None, description="Source language for translation")
    translation_target_lang: Optional[str] = Field(default=None, description="Target language for translation")
    summary_length: Optional[str] = Field(default=None, description="Summary length (short/medium/long)")

    # Additional custom variables
    custom_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom variables"
    )

    def merge(self, **kwargs) -> 'PromptContext':
        """Merge additional variables into context"""
        data = self.model_dump()
        data['custom_variables'].update(kwargs)
        return PromptContext(**data)

    def to_render_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for template.render()"""
        data = self.model_dump(exclude_none=True, exclude={'custom_variables'})
        data.update(self.custom_variables)
        return data
