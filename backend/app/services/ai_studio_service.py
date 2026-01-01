"""
LernsystemX AI Studio Service

Central service for AI generation in KI-Authoring-Studio.
Uses the prompt management system (prompt_registry) as the ONLY source for prompts.

Phase D4 - KI-Authoring-Studio
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from flask import current_app

from app.ki.prompt_registry import get_prompt_template, PromptRegistryError
from app.services.ai_adapter import AIAdapter, AIProviderError
from app.repositories.ai_studio_repository import (
    AIStudioRepository,
    AIStudioAnalyticsRepository,
    AIGenerationVariantRepository
)
from app.models.ai_studio import VariantType

logger = logging.getLogger(__name__)


# ==============================================================================
# STEP TO PROMPT MAPPING
# Maps content_type/step to prompt codes in the prompt registry
# ==============================================================================

AI_STUDIO_STEP_TO_PROMPT: Dict[str, str] = {
    # VariantType values -> prompt codes
    "theory": "ai_studio_theory",
    "lesson": "ai_studio_lessons",
    "method": "ai_studio_methods",
    "quiz": "ai_studio_methods",  # Quiz uses methods prompt for now
    "summary": "ai_studio_review",
    "full_chapter": "ai_studio_finalize",

    # Additional step mappings
    "source": "ai_studio_source",
    "review": "ai_studio_review",
    "finalize": "ai_studio_finalize",
}


class AiStudioServiceError(Exception):
    """Base exception for AI Studio service errors"""
    pass


class AiStudioService:
    """
    AI Studio Service for content generation.

    Uses the prompt management system (prompt_registry) as the ONLY source for prompts.
    Endpoints reference prompt codes, NOT prompt text.

    Usage:
        >>> service = AiStudioService()
        >>> result = service.generate_for_step(
        ...     step="theory",
        ...     session_id="uuid",
        ...     context={"target_audience": "Sek II", ...}
        ... )
    """

    def __init__(self, provider: str = "anthropic", model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize AI Studio Service.

        Args:
            provider: AI provider (default: anthropic)
            model: Model name (default: claude-3-5-sonnet-20241022)
        """
        self.provider = provider
        self.model = model

    def get_prompt_code(self, step: str) -> str:
        """
        Get the prompt code for a given step.

        Args:
            step: Step name (e.g., "theory", "lessons", "methods")

        Returns:
            Prompt code from AI_STUDIO_STEP_TO_PROMPT

        Raises:
            AiStudioServiceError: If step not found in mapping
        """
        if step not in AI_STUDIO_STEP_TO_PROMPT:
            raise AiStudioServiceError(
                f"Unknown step: {step}. "
                f"Valid steps: {', '.join(AI_STUDIO_STEP_TO_PROMPT.keys())}"
            )
        return AI_STUDIO_STEP_TO_PROMPT[step]

    def generate_for_step(
        self,
        step: str,
        session_id: str,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a wizard step.

        Loads the prompt from the prompt registry (NOT hardcoded)
        and sends it to the AI provider.

        Args:
            step: Wizard step (e.g., "source", "theory", "lessons")
            session_id: Session UUID
            context: Variables to render into the prompt template
            user_id: Optional user ID for analytics

        Returns:
            AI generation result with output_text, tokens, cost, etc.

        Raises:
            AiStudioServiceError: On prompt or generation errors
        """
        start_time = datetime.utcnow()

        try:
            # 1. Get prompt code from mapping
            prompt_code = self.get_prompt_code(step)
            logger.info(f"AI Studio generate: step={step}, prompt_code={prompt_code}")

            # 2. Load prompt template from registry (NOT hardcoded)
            try:
                template = get_prompt_template(prompt_code)
            except PromptRegistryError as e:
                raise AiStudioServiceError(f"Prompt not found: {str(e)}")

            # 3. Render prompt with context
            messages = template.render(context)

            # 4. Initialize AI adapter
            # Use explicitly passed model if provided, otherwise fall back to template model
            adapter = AIAdapter(
                provider=self.provider,
                model=self.model or template.model or "gpt-4-0613"
            )

            # 5. Send to AI
            result = adapter.send_messages(
                messages=messages,
                temperature=template.temperature or 0.7,
                max_tokens=template.max_tokens or 4000
            )

            # 6. Log analytics
            if user_id:
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                AIStudioAnalyticsRepository.log_event({
                    'session_id': session_id,
                    'user_id': user_id,
                    'event_type': 'generation_complete',
                    'event_data': {
                        'step': step,
                        'prompt_code': prompt_code,
                        'provider': self.provider,
                        'model': result.get('model'),
                        'input_tokens': result.get('input_tokens'),
                        'output_tokens': result.get('output_tokens'),
                        'cost_eur': result.get('cost_eur'),
                        'latency_ms': result.get('latency_ms')
                    },
                    'step_name': f'{step}_generation',
                    'tokens_used': result.get('total_tokens', 0),
                    'cost_eur': result.get('cost_eur', 0),
                    'duration_ms': duration_ms
                })

            logger.info(
                f"AI Studio generation complete: step={step}, "
                f"tokens={result.get('total_tokens')}, "
                f"cost={result.get('cost_eur')}€"
            )

            return {
                'success': True,
                'step': step,
                'prompt_code': prompt_code,
                'output_text': result.get('output_text'),
                'input_tokens': result.get('input_tokens'),
                'output_tokens': result.get('output_tokens'),
                'total_tokens': result.get('total_tokens'),
                'cost_eur': result.get('cost_eur'),
                'latency_ms': result.get('latency_ms'),
                'model': result.get('model'),
                'provider': result.get('provider')
            }

        except AIProviderError as e:
            logger.error(f"AI provider error for step {step}: {str(e)}")
            raise AiStudioServiceError(f"AI generation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in generate_for_step: {str(e)}")
            raise AiStudioServiceError(f"Generation failed: {str(e)}")

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
        # Get session for context
        session = AIStudioRepository.find_by_id(session_id)
        if not session:
            raise AiStudioServiceError(f"Session not found: {session_id}")

        source_data = session.get('source_data', {})

        context = {
            'target_audience': source_data.get('target_audience', 'Allgemein'),
            'difficulty': source_data.get('difficulty', 'mittel'),
            'target_language': source_data.get('target_language', 'de'),
            'learning_objectives': json.dumps(source_data.get('learning_objectives', [])),
            'max_theory_variants': str(max_variants),
            'pdf_analysis': json.dumps(pdf_analysis),
            'selected_didactic_angle': selected_didactic_angle or ''
        }

        return self.generate_for_step('theory', session_id, context, user_id)

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
        session = AIStudioRepository.find_by_id(session_id)
        if not session:
            raise AiStudioServiceError(f"Session not found: {session_id}")

        source_data = session.get('source_data', {})
        generated_content = session.get('generated_content', {})
        pdf_analysis = generated_content.get('pdf_analysis', source_data.get('pdf_analysis', {}))

        context = {
            'target_audience': source_data.get('target_audience', 'Allgemein'),
            'difficulty': source_data.get('difficulty', 'mittel'),
            'target_language': source_data.get('target_language', 'de'),
            'learning_objectives': json.dumps(source_data.get('learning_objectives', [])),
            'max_lessons': str(max_lessons),
            'pdf_analysis': json.dumps(pdf_analysis),
            'selected_theory_variant': json.dumps(selected_theory_variant)
        }

        return self.generate_for_step('lesson', session_id, context, user_id)

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
        session = AIStudioRepository.find_by_id(session_id)
        if not session:
            raise AiStudioServiceError(f"Session not found: {session_id}")

        source_data = session.get('source_data', {})

        context = {
            'target_audience': source_data.get('target_audience', 'Allgemein'),
            'difficulty': source_data.get('difficulty', 'mittel'),
            'target_language': source_data.get('target_language', 'de'),
            'method_preferences': json.dumps(method_preferences or []),
            'lessons': json.dumps(lessons)
        }

        return self.generate_for_step('method', session_id, context, user_id)

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
        session = AIStudioRepository.find_by_id(session_id)
        if not session:
            raise AiStudioServiceError(f"Session not found: {session_id}")

        source_data = session.get('source_data', {})

        context = {
            'target_audience': source_data.get('target_audience', 'Allgemein'),
            'difficulty': source_data.get('difficulty', 'mittel'),
            'learning_objectives': json.dumps(source_data.get('learning_objectives', [])),
            'selected_theory_variant': json.dumps(theory_variant),
            'lessons': json.dumps(lessons),
            'methods': json.dumps(methods)
        }

        return self.generate_for_step('review', session_id, context, user_id)

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
        session = AIStudioRepository.find_by_id(session_id)
        if not session:
            raise AiStudioServiceError(f"Session not found: {session_id}")

        source_data = session.get('source_data', {})

        context = {
            'target_audience': source_data.get('target_audience', 'Allgemein'),
            'difficulty': source_data.get('difficulty', 'mittel'),
            'target_language': source_data.get('target_language', 'de'),
            'learning_objectives': json.dumps(source_data.get('learning_objectives', [])),
            'selected_theory_variant': json.dumps(theory_variant),
            'lessons': json.dumps(lessons),
            'methods': json.dumps(methods),
            'review_results': json.dumps(review_results)
        }

        return self.generate_for_step('finalize', session_id, context, user_id)

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

        This method takes the generated content from an AI Studio session and
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
            AiStudioServiceError: On finalization errors
        """
        from app.repositories.chapter_repository import ChapterRepository
        from app.repositories.lesson_repository import LessonRepository
        from app.repositories.learning_method_instance_repository import LearningMethodInstanceRepository

        # Get session with all generated content
        session = AIStudioRepository.find_by_id(session_id)
        if not session:
            raise AiStudioServiceError(f"Session not found: {session_id}")

        course_id = session.get('course_id')
        if not course_id:
            raise AiStudioServiceError("Session has no course_id")

        # Parse JSON fields if needed
        generated_theory = session.get('generated_theory')
        generated_lessons = session.get('generated_lessons', [])
        generated_methods = session.get('generated_methods', [])

        if isinstance(generated_theory, str):
            generated_theory = json.loads(generated_theory) if generated_theory else {}
        if isinstance(generated_lessons, str):
            generated_lessons = json.loads(generated_lessons) if generated_lessons else []
        if isinstance(generated_methods, str):
            generated_methods = json.loads(generated_methods) if generated_methods else []

        result = {
            'chapter_id': None,
            'lesson_ids': [],
            'method_ids': [],
            'stats': {
                'chapters_created': 0,
                'lessons_created': 0,
                'methods_created': 0
            }
        }

        created_chapter = None

        # 1. Create Chapter
        if create_chapter:
            # Get chapter title from request, generated theory, or session name
            final_chapter_title = (
                chapter_title or
                generated_theory.get('title') or
                generated_theory.get('chapter_title') or
                session.get('session_name') or
                'KI-generiertes Kapitel'
            )

            chapter_description = (
                generated_theory.get('description') or
                generated_theory.get('summary') or
                None
            )

            chapter_data = {
                'course_id': course_id,
                'title': final_chapter_title,
                'description': chapter_description,
                'duration_minutes': generated_theory.get('estimated_duration', 0),
                'has_quiz': any(m.get('method_type') in [13, 22] for m in generated_methods),
                'has_exam': any(m.get('method_type') in [25] for m in generated_methods)
            }

            try:
                created_chapter = ChapterRepository.create(chapter_data)
                result['chapter_id'] = str(created_chapter['chapter_id'])
                result['stats']['chapters_created'] = 1

                # Update session with chapter_id
                AIStudioRepository.update_session(session_id, {'chapter_id': created_chapter['chapter_id']})

                logger.info(f"Created chapter: {created_chapter['chapter_id']} - {final_chapter_title}")
            except Exception as e:
                logger.error(f"Failed to create chapter: {str(e)}")
                raise AiStudioServiceError(f"Failed to create chapter: {str(e)}")

        # 2. Create Lessons
        if create_lessons and created_chapter:
            for idx, lesson_data in enumerate(generated_lessons):
                lesson_title = lesson_data.get('title', f'Lektion {idx + 1}')
                lesson_type = lesson_data.get('lesson_type', 'text')

                # Build content from generated data
                lesson_content = {
                    'description': lesson_data.get('description'),
                    'objectives': lesson_data.get('learning_objectives', []),
                    'content_text': lesson_data.get('content_text'),
                    'ai_generated': True,
                    'source_session_id': session_id
                }

                new_lesson_data = {
                    'chapter_id': created_chapter['chapter_id'],
                    'title': lesson_title,
                    'lesson_type': lesson_type,
                    'content': json.dumps(lesson_content),
                    'order_index': lesson_data.get('order_index', idx + 1),
                    'duration_minutes': lesson_data.get('duration_minutes', 10),
                    'published': publish_immediately,
                    'free_preview': lesson_data.get('is_preview', False)
                }

                try:
                    created_lesson = LessonRepository.create(new_lesson_data)
                    result['lesson_ids'].append(str(created_lesson['lesson_id']))
                    result['stats']['lessons_created'] += 1
                    logger.info(f"Created lesson: {created_lesson['lesson_id']} - {lesson_title}")
                except Exception as e:
                    logger.error(f"Failed to create lesson {lesson_title}: {str(e)}")
                    # Continue with other lessons

        # 3. Create Learning Methods
        if create_methods and created_chapter:
            for idx, method_data in enumerate(generated_methods):
                method_type = method_data.get('method_type', 0)
                method_title = method_data.get('title', f'Lernmethode {idx + 1}')

                # Build data JSONB for the learning method
                method_content = {
                    'instructions': method_data.get('instructions'),
                    'content': method_data.get('content', {}),
                    'ai_generated': True,
                    'source_session_id': session_id
                }

                # Merge with any additional data from generation
                if method_data.get('data'):
                    method_content.update(method_data['data'])

                new_method_data = {
                    'chapter_id': created_chapter['chapter_id'],
                    'method_type': method_type,
                    'title': method_title,
                    'instructions': method_data.get('instructions'),
                    'data': method_content,
                    'solution': method_data.get('solution'),
                    'tier': method_data.get('tier', 'basic'),
                    'duration_minutes': method_data.get('duration_minutes'),
                    'difficulty': method_data.get('difficulty', 'medium'),
                    'order_index': method_data.get('order_index', idx + 1),
                    'published': publish_immediately
                }

                try:
                    created_method = LearningMethodInstanceRepository.create(new_method_data)
                    result['method_ids'].append(str(created_method['method_id']))
                    result['stats']['methods_created'] += 1
                    logger.info(f"Created method: {created_method['method_id']} - {method_title} (LM{method_type:02d})")
                except Exception as e:
                    logger.error(f"Failed to create method {method_title}: {str(e)}")
                    # Continue with other methods

        # 4. Update session status
        AIStudioRepository.update_status(session_id, 'completed')

        # 5. Log analytics
        if user_id:
            AIStudioAnalyticsRepository.log_event({
                'session_id': session_id,
                'user_id': user_id,
                'event_type': 'session_finalized',
                'event_data': {
                    'chapter_id': result['chapter_id'],
                    'lessons_created': result['stats']['lessons_created'],
                    'methods_created': result['stats']['methods_created'],
                    'publish_immediately': publish_immediately
                },
                'step_name': 'finalize'
            })

        logger.info(
            f"Session {session_id} finalized: "
            f"{result['stats']['chapters_created']} chapters, "
            f"{result['stats']['lessons_created']} lessons, "
            f"{result['stats']['methods_created']} methods"
        )

        return result

    @staticmethod
    def get_available_steps() -> List[str]:
        """Get list of all available generation steps."""
        return list(AI_STUDIO_STEP_TO_PROMPT.keys())

    @staticmethod
    def get_prompt_code_for_step(step: str) -> Optional[str]:
        """Get prompt code for a step without raising an error."""
        return AI_STUDIO_STEP_TO_PROMPT.get(step)


# Convenience function for quick access
def get_ai_studio_service(
    provider: str = "anthropic",
    model: str = "claude-3-5-sonnet-20241022"
) -> AiStudioService:
    """
    Get an AI Studio service instance.

    Args:
        provider: AI provider
        model: Model name

    Returns:
        AiStudioService instance
    """
    return AiStudioService(provider=provider, model=model)
