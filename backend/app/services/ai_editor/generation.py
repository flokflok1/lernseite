"""
AI Editor Generation Module

Handles content generation for AI Editor wizard steps.
Uses the prompt management system as the ONLY source for prompts.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.domain.ai.configuration.prompt_registry import get_prompt_template, PromptRegistryError
from app.services.ai_adapter import AIAdapter, AIProviderError
from app.infrastructure.persistence.repositories.ai.editor import (
    AIEditorRepository,
    AIEditorAnalyticsRepository
)
from app.services.ai_editor.utils import (
    AiEditorServiceError,
    get_prompt_code
)

logger = logging.getLogger(__name__)


class AiEditorGenerator:
    """
    AI content generator for wizard steps.

    Uses the prompt management system (prompt_registry) as the ONLY source for prompts.
    """

    def __init__(self, provider: str = "anthropic", model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize AI Editor Generator.

        Args:
            provider: AI provider (default: anthropic)
            model: Model name (default: claude-3-5-sonnet-20241022)
        """
        self.provider = provider
        self.model = model

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
            AiEditorServiceError: On prompt or generation errors
        """
        start_time = datetime.utcnow()

        try:
            # 1. Get prompt code from mapping
            prompt_code = get_prompt_code(step)
            logger.info(f"AI Editor generate: step={step}, prompt_code={prompt_code}")

            # 2. Load prompt template from registry (NOT hardcoded)
            try:
                template = get_prompt_template(prompt_code)
            except PromptRegistryError as e:
                raise AiEditorServiceError(f"Prompt not found: {str(e)}")

            # 3. Render prompt with context
            messages = template.render(context)

            # 4. Initialize AI adapter
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
                AIEditorAnalyticsRepository.log_event({
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
                f"AI Editor generation complete: step={step}, "
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
            raise AiEditorServiceError(f"AI generation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in generate_for_step: {str(e)}")
            raise AiEditorServiceError(f"Generation failed: {str(e)}")

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
        session = AIEditorRepository.find_by_id(session_id)
        if not session:
            raise AiEditorServiceError(f"Session not found: {session_id}")

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
        session = AIEditorRepository.find_by_id(session_id)
        if not session:
            raise AiEditorServiceError(f"Session not found: {session_id}")

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
        session = AIEditorRepository.find_by_id(session_id)
        if not session:
            raise AiEditorServiceError(f"Session not found: {session_id}")

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
        session = AIEditorRepository.find_by_id(session_id)
        if not session:
            raise AiEditorServiceError(f"Session not found: {session_id}")

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
        session = AIEditorRepository.find_by_id(session_id)
        if not session:
            raise AiEditorServiceError(f"Session not found: {session_id}")

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
