"""
Prompt Resolver Service (Phase C1.4)

Resolves AI prompts with the following resolution chain:
1. Course-Specific Prompt (from course_prompts table)
2. Global Prompt (from PROMPT_REGISTRY)
3. Hardcoded Fallback (basic default prompts)

This service is used by AI generation endpoints to get the appropriate
prompt for a specific course and operation.

Phase: C1.4 - Prompt-System für Kurs/Modul/Prüfung
Date: 2025-01-23
"""

from typing import Optional, Dict, Any, List
import logging
from app.infrastructure.persistence.repositories.course_prompt import CoursePromptRepository
from app.domain.ai.configuration.prompts.registry_bridge import get_prompt_template, PROMPT_REGISTRY
from app.domain.ai.configuration.prompts.models import PromptTemplate

# Initialize logger
logger = logging.getLogger(__name__)


class PromptResolver:
    """
    Service for resolving AI prompts with course-specific overrides.

    Resolution Chain:
    1. **Course-Specific Prompt** (from DB): If a course has a custom prompt for
       the requested scope and language, use it.
    2. **Global Prompt** (from PROMPT_REGISTRY): If no course-specific prompt exists,
       use the global default from the prompt registry.
    3. **Hardcoded Fallback** (basic default): If no global prompt exists,
       use a basic hardcoded fallback.

    Example:
        resolver = PromptResolver()
        resolved = resolver.resolve(
            course_id="abc123",
            scope="module_generation",
            language="de"
        )
        # resolved = {
        #     "source": "course_specific",
        #     "prompt_system": "Du bist ein IHK-Ausbilder...",
        #     "prompt_user_template": "Erstelle ein Modul über {{topic}}",
        #     "metadata": {"temperature": 0.7}
        # }
    """

    # Mapping of scopes to global prompt codes in PROMPT_REGISTRY
    SCOPE_TO_GLOBAL_CODE_MAP = {
        'course_generation': None,  # No global prompt for courses (custom only)
        'module_generation': None,  # No global prompt for modules (custom only)
        'exam_generation': 'quiz_generator',  # Maps to quiz_generator global prompt
        'lesson_generation': 'explain_concept',  # Maps to explain_concept global prompt
        'quiz_generation': 'quiz_generator'  # Maps to quiz_generator global prompt
    }

    # Hardcoded fallback prompts (used if no DB or global prompt exists)
    HARDCODED_FALLBACKS = {
        'course_generation': {
            'prompt_system': (
                "You are an expert educational content creator. "
                "Your goal is to create comprehensive, engaging, and well-structured courses."
            ),
            'prompt_user_template': (
                "Generate a detailed course outline for: {{course_title}}\n\n"
                "Description: {{description}}\n\n"
                "Target audience: {{target_audience}}\n"
                "Difficulty level: {{difficulty}}"
            ),
            'metadata': {'temperature': 0.7, 'max_tokens': 3000}
        },
        'module_generation': {
            'prompt_system': (
                "You are an expert educational content creator. "
                "Your goal is to create comprehensive, engaging, and well-structured learning modules."
            ),
            'prompt_user_template': (
                "Generate a detailed module for the course: {{course_title}}\n\n"
                "Module topic: {{topic}}\n"
                "Module description: {{description}}\n\n"
                "The module should include clear learning objectives, structured content, and practical examples."
            ),
            'metadata': {'temperature': 0.7, 'max_tokens': 4000}
        },
        'exam_generation': {
            'prompt_system': (
                "You are an expert educational assessment creator. "
                "Your goal is to create fair, comprehensive, and well-structured exams."
            ),
            'prompt_user_template': (
                "Generate an exam for the course: {{course_title}}\n\n"
                "Exam title: {{exam_title}}\n"
                "Standard: {{exam_standard}}\n"
                "Difficulty: {{difficulty}}\n"
                "Number of questions: {{question_count}}\n\n"
                "Create questions that accurately assess understanding of the material."
            ),
            'metadata': {'temperature': 0.5, 'max_tokens': 6000}
        },
        'lesson_generation': {
            'prompt_system': (
                "You are an expert educational content creator. "
                "Your goal is to create clear, engaging, and effective lesson content."
            ),
            'prompt_user_template': (
                "Generate a lesson for the module: {{module_title}}\n\n"
                "Lesson topic: {{topic}}\n"
                "Lesson type: {{lesson_type}}\n\n"
                "Create content that is easy to understand and engaging for learners."
            ),
            'metadata': {'temperature': 0.7, 'max_tokens': 3000}
        },
        'quiz_generation': {
            'prompt_system': (
                "You are an expert educational assessment creator. "
                "Your goal is to create effective quiz questions that test understanding."
            ),
            'prompt_user_template': (
                "Generate quiz questions for: {{topic}}\n\n"
                "Number of questions: {{question_count}}\n"
                "Question types: {{question_types}}\n"
                "Difficulty: {{difficulty}}\n\n"
                "Create questions with clear, unambiguous answers."
            ),
            'metadata': {'temperature': 0.5, 'max_tokens': 2000}
        }
    }

    @staticmethod
    def resolve(
        course_id: str,
        scope: str,
        language: Optional[str] = None,
        fallback_to_global: bool = True,
        fallback_to_hardcoded: bool = True
    ) -> Dict[str, Any]:
        """
        Resolve a prompt for a specific course, scope, and language.

        Resolution Chain:
        1. Course-Specific → 2. Global → 3. Hardcoded Fallback

        Args:
            course_id: UUID of the course
            scope: Scope of the prompt (e.g., 'module_generation')
            language: Optional language code (e.g., 'de'). If None, uses default language.
            fallback_to_global: If True, falls back to global prompts if no course-specific prompt
            fallback_to_hardcoded: If True, falls back to hardcoded prompts if no global prompt

        Returns:
            Dict with resolved prompt data:
            {
                "source": "course_specific" | "global" | "hardcoded_fallback",
                "scope": str,
                "language": str | None,
                "prompt_system": str | None,
                "prompt_user_template": str | None,
                "metadata": dict
            }

        Example:
            resolved = PromptResolver.resolve(
                course_id="abc123",
                scope="module_generation",
                language="de"
            )
        """
        # STEP 1: Try course-specific prompt (DB)
        course_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )

        if course_prompt:
            logger.info(
                f"✓ Resolved COURSE-SPECIFIC prompt: course={course_id[:8]}..., "
                f"scope={scope}, language={language or 'default'}"
            )
            return {
                "source": "course_specific",
                "scope": scope,
                "language": course_prompt.get('language'),
                "prompt_system": course_prompt.get('prompt_system'),
                "prompt_user_template": course_prompt.get('prompt_user_template'),
                "metadata": course_prompt.get('metadata', {})
            }

        # STEP 2: Try global prompt (PROMPT_REGISTRY)
        if fallback_to_global:
            global_code = PromptResolver.SCOPE_TO_GLOBAL_CODE_MAP.get(scope)
            if global_code:
                global_prompt = get_prompt_template(global_code)
                if global_prompt:
                    logger.info(
                        f"✓ Resolved GLOBAL prompt: scope={scope}, "
                        f"global_code={global_code}, language={language or 'default'}"
                    )
                    # Convert PromptTemplate to dict format
                    return {
                        "source": "global",
                        "scope": scope,
                        "language": language,  # Keep requested language
                        "prompt_system": PromptResolver._extract_system_message(global_prompt),
                        "prompt_user_template": PromptResolver._extract_user_template(global_prompt),
                        "metadata": global_prompt.metadata or {}
                    }

        # STEP 3: Use hardcoded fallback
        if fallback_to_hardcoded:
            fallback = PromptResolver.HARDCODED_FALLBACKS.get(scope)
            if fallback:
                logger.info(
                    f"✓ Resolved HARDCODED FALLBACK: scope={scope}, language={language or 'default'}"
                )
                return {
                    "source": "hardcoded_fallback",
                    "scope": scope,
                    "language": language,
                    **fallback  # Unpack prompt_system, prompt_user_template, metadata
                }

        # STEP 4: No prompt found (should never happen with fallback enabled)
        logger.error(
            f"✗ Failed to resolve prompt: scope={scope}, course_id={course_id}, "
            f"language={language}, fallback_to_global={fallback_to_global}, "
            f"fallback_to_hardcoded={fallback_to_hardcoded}"
        )
        raise ValueError(
            f"No prompt found for scope '{scope}' (course_id={course_id}, language={language}). "
            f"Enable fallbacks or register a global prompt."
        )

    @staticmethod
    def resolve_and_render(
        course_id: str,
        scope: str,
        context: Dict[str, Any],
        language: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Resolve a prompt and immediately render it with context variables.

        This is a convenience method that combines resolve() + template rendering.

        Args:
            course_id: UUID of the course
            scope: Scope of the prompt
            context: Context variables for template rendering (e.g., {"topic": "Networking"})
            language: Optional language code

        Returns:
            List of rendered messages ready for AI API:
            [
                {"role": "system", "content": "You are an expert..."},
                {"role": "user", "content": "Generate a module about Networking..."}
            ]

        Example:
            messages = PromptResolver.resolve_and_render(
                course_id="abc123",
                scope="module_generation",
                context={"course_title": "FISI AP1", "topic": "Networking"},
                language="de"
            )
            # Send messages to AI API
            ai_adapter.send_messages(messages)
        """
        # Resolve prompt
        resolved = PromptResolver.resolve(
            course_id=course_id,
            scope=scope,
            language=language
        )

        # Build messages list
        messages = []

        # Add system message if present
        if resolved.get('prompt_system'):
            # Render system message (in case it has variables)
            system_content = PromptResolver._render_template(
                resolved['prompt_system'],
                context
            )
            messages.append({
                "role": "system",
                "content": system_content
            })

        # Add user message if present
        if resolved.get('prompt_user_template'):
            user_content = PromptResolver._render_template(
                resolved['prompt_user_template'],
                context
            )
            messages.append({
                "role": "user",
                "content": user_content
            })

        return messages

    @staticmethod
    def get_available_scopes() -> List[str]:
        """
        Get list of all available prompt scopes.

        Returns:
            List of scope strings
        """
        return list(PromptResolver.HARDCODED_FALLBACKS.keys())

    @staticmethod
    def has_course_specific_prompt(
        course_id: str,
        scope: str,
        language: Optional[str] = None
    ) -> bool:
        """
        Check if a course has a custom prompt for a specific scope.

        Args:
            course_id: UUID of the course
            scope: Scope to check
            language: Optional language code

        Returns:
            True if course has a custom prompt, False otherwise
        """
        course_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )
        return course_prompt is not None

    # ========================================================================
    # PRIVATE Helper Methods
    # ========================================================================

    @staticmethod
    def _extract_system_message(prompt_template: PromptTemplate) -> Optional[str]:
        """
        Extract system message content from a PromptTemplate.

        Args:
            prompt_template: PromptTemplate object

        Returns:
            System message content, or None if no system message
        """
        for message in prompt_template.messages:
            if message.role == 'system':
                return message.content
        return None

    @staticmethod
    def _extract_user_template(prompt_template: PromptTemplate) -> Optional[str]:
        """
        Extract user message template from a PromptTemplate.

        Args:
            prompt_template: PromptTemplate object

        Returns:
            User message template, or None if no user message
        """
        for message in prompt_template.messages:
            if message.role == 'user':
                return message.content
        return None

    @staticmethod
    def _render_template(template: str, context: Dict[str, Any]) -> str:
        """
        Simple template rendering (replaces {{variable}} placeholders).

        Args:
            template: Template string with {{variable}} placeholders
            context: Dict of variable values

        Returns:
            Rendered string with placeholders replaced

        Example:
            _render_template("Hello {{name}}", {"name": "Alice"})
            # Returns: "Hello Alice"
        """
        rendered = template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered
