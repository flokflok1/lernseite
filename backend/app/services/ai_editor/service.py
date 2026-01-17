"""
AI Editor Service

Central service for AI generation in KI-Authoring-Studio.
Orchestrates generation and finalization workflows.
"""

from typing import Dict, Any, Optional, List

from app.services.ai_editor.generation import AiEditorGenerator
from app.services.ai_editor.finalization import AiEditorFinalizer
from app.services.ai_editor.utils import (
    AiEditorServiceError,
    get_available_steps,
    get_prompt_code_for_step
)


class AiEditorService:
    """
    AI Editor Service for content generation.

    Uses the prompt management system (prompt_registry) as the ONLY source for prompts.
    Endpoints reference prompt codes, NOT prompt text.

    Combines generation and finalization workflows.

    Usage:
        >>> service = AiEditorService()
        >>> result = service.generate_for_step(
        ...     step="theory",
        ...     session_id="uuid",
        ...     context={"target_audience": "Sek II", ...}
        ... )
    """

    def __init__(self, provider: str = "anthropic", model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize AI Editor Service.

        Args:
            provider: AI provider (default: anthropic)
            model: Model name (default: claude-3-5-sonnet-20241022)
        """
        self._generator = AiEditorGenerator(provider=provider, model=model)
        self._finalizer = AiEditorFinalizer()

    def generate_for_step(
        self,
        step: str,
        session_id: str,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a wizard step.

        Args:
            step: Wizard step (e.g., "source", "theory", "lessons")
            session_id: Session UUID
            context: Variables to render into the prompt template
            user_id: Optional user ID for analytics

        Returns:
            AI generation result with output_text, tokens, cost, etc.

        Raises:
            AiEditorServiceError: On prompt or generation errors
        """
        return self._generator.generate_for_step(step, session_id, context, user_id)

    def generate_theory_variants(
        self,
        session_id: str,
        pdf_analysis: Dict[str, Any],
        selected_didactic_angle: Optional[str] = None,
        max_variants: int = 4,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate theory variants for a session.

        Args:
            session_id: Session UUID
            pdf_analysis: PDF analysis results
            selected_didactic_angle: Optional selected didactic approach
            max_variants: Maximum number of variants to generate
            user_id: Optional user ID for analytics

        Returns:
            Generation result with theory_variants
        """
        return self._generator.generate_theory_variants(
            session_id, pdf_analysis, selected_didactic_angle, max_variants, user_id
        )

    def generate_lessons(
        self,
        session_id: str,
        selected_theory_variant: Dict[str, Any],
        max_lessons: int = 5,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate lesson structure based on selected theory variant.

        Args:
            session_id: Session UUID
            selected_theory_variant: Chosen theory variant
            max_lessons: Maximum number of lessons
            user_id: Optional user ID for analytics

        Returns:
            Generation result with lessons
        """
        return self._generator.generate_lessons(
            session_id, selected_theory_variant, max_lessons, user_id
        )

    def generate_methods(
        self,
        session_id: str,
        lessons: List[Dict[str, Any]],
        method_preferences: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate method variants for each lesson.

        Args:
            session_id: Session UUID
            lessons: List of lessons to generate methods for
            method_preferences: Optional list of preferred method types
            user_id: Optional user ID for analytics

        Returns:
            Generation result with methods
        """
        return self._generator.generate_methods(session_id, lessons, method_preferences, user_id)

    def generate_review(
        self,
        session_id: str,
        theory_variant: Dict[str, Any],
        lessons: List[Dict[str, Any]],
        methods: List[Dict[str, Any]],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate consistency review for all content.

        Args:
            session_id: Session UUID
            theory_variant: Selected theory variant
            lessons: Generated lessons
            methods: Generated methods
            user_id: Optional user ID for analytics

        Returns:
            Generation result with review issues and suggestions
        """
        return self._generator.generate_review(
            session_id, theory_variant, lessons, methods, user_id
        )

    def generate_final_blueprint(
        self,
        session_id: str,
        theory_variant: Dict[str, Any],
        lessons: List[Dict[str, Any]],
        methods: List[Dict[str, Any]],
        review_results: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate final course blueprint.

        Args:
            session_id: Session UUID
            theory_variant: Selected theory variant
            lessons: Generated lessons
            methods: Generated methods
            review_results: Review results
            user_id: Optional user ID for analytics

        Returns:
            Generation result with final course_blueprint
        """
        return self._generator.generate_final_blueprint(
            session_id, theory_variant, lessons, methods, review_results, user_id
        )

    def finalize_session(
        self,
        session_id: str,
        create_chapter: bool = True,
        create_lessons: bool = True,
        create_methods: bool = True,
        chapter_title: Optional[str] = None,
        publish_immediately: bool = False,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Finalize session and create actual chapter, lessons, and learning methods.

        This method takes the generated content from an AI Editor session and
        creates the actual database records in courses/chapters/lessons.

        Args:
            session_id: Session UUID
            create_chapter: Create chapter from generated content
            create_lessons: Create lessons
            create_methods: Create learning methods
            chapter_title: Override chapter title (uses generated if None)
            publish_immediately: Publish chapter immediately
            user_id: User ID for analytics

        Returns:
            Result dict with created IDs

        Raises:
            AiEditorServiceError: On finalization errors
        """
        return self._finalizer.finalize_session(
            session_id=session_id,
            create_chapter=create_chapter,
            create_lessons=create_lessons,
            create_methods=create_methods,
            chapter_title=chapter_title,
            publish_immediately=publish_immediately,
            user_id=user_id
        )

    @staticmethod
    def get_available_steps() -> List[str]:
        """Get list of all available generation steps."""
        return get_available_steps()

    @staticmethod
    def get_prompt_code_for_step(step: str) -> Optional[str]:
        """Get prompt code for a step without raising an error."""
        return get_prompt_code_for_step(step)
