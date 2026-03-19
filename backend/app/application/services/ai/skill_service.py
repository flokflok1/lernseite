"""
Skill Execution Service

Orchestrates AI skill execution for the Unified AI Editor.
Uses PromptResolver for prompts, LMModelResolver for model routing,
AIAdapter for AI calls, and repositories for persistence.
"""

from typing import Dict, Any, Optional, List
import json
import logging
import uuid

from app.domain.ai.configuration.skills import (
    get_skill, get_all_skills, get_course_skills, get_skills_by_category, SkillDefinition
)
from app.application.services.ai.prompts.resolver import PromptResolver
from app.application.services.content.lm.model_resolver import LMModelResolver
from app.infrastructure.ai.adapter import AIAdapter
from app.infrastructure.persistence.repositories.ai.tracking.generation_log import GenerationLogRepository
from app.infrastructure.persistence.repositories.features.repository import FeatureRepository

logger = logging.getLogger(__name__)


class SkillExecutionService:
    """Orchestrates single and batch skill execution."""

    @staticmethod
    def get_catalog() -> List[Dict[str, Any]]:
        """
        Return the AI Editor skill catalog.

        Filters applied:
        1. Only course-scoped skills (session/user-level excluded)
        2. Skills with required_feature_code only if that SF is active
        """
        skills = get_course_skills()
        return _filter_by_active_features(skills)

    @staticmethod
    def get_catalog_by_category(category: str) -> List[Dict[str, Any]]:
        """Return skills filtered by category (course-scoped only)."""
        skills = [s for s in get_course_skills() if s.category == category]
        return _filter_by_active_features(skills)

    @staticmethod
    def get_skill_detail(code: str) -> Optional[Dict[str, Any]]:
        """Return a single skill definition."""
        skill = get_skill(code)
        if not skill:
            return None
        return _serialize_skill(skill)

    @staticmethod
    def execute(
        skill_code: str,
        course_id: str,
        user_id: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        prompt_override: Optional[str] = None,
        plan_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a single skill.

        Returns:
            GenerationResult dict with content, tokens, model info.
        """
        skill = get_skill(skill_code)
        if not skill:
            raise ValueError(f'Unknown skill: {skill_code}')

        params = parameters or {}
        language = params.get('language', 'de')

        # Resolve model
        provider_name, model_name = _resolve_model(skill, course_id, target_id)

        # Resolve and render prompt
        messages = _resolve_prompt(
            skill, course_id, language, params, prompt_override
        )

        # Call AI
        adapter = AIAdapter(provider=provider_name, model=model_name)
        response = adapter.send_messages(
            messages=messages,
            temperature=params.get('temperature', 0.7),
            max_tokens=params.get('max_tokens', skill.estimated_tokens * 2),
        )

        # Parse output
        output_content = _parse_output(response.get('output_text', ''))

        # Log generation
        log_entry = GenerationLogRepository.create({
            'plan_id': plan_id,
            'skill_code': skill_code,
            'course_id': course_id,
            'target_type': target_type,
            'target_id': target_id,
            'input_prompt': json.dumps(messages),
            'output_content': output_content,
            'tokens_input': response.get('input_tokens', 0),
            'tokens_output': response.get('output_tokens', 0),
            'model_name': model_name,
            'provider_name': provider_name,
            'status': 'completed',
        })

        generation_id = log_entry['generation_id'] if log_entry else str(uuid.uuid4())

        return {
            'generation_id': generation_id,
            'skill_code': skill_code,
            'content': output_content,
            'tokens_input': response.get('input_tokens', 0),
            'tokens_output': response.get('output_tokens', 0),
            'model_name': model_name,
            'provider_name': provider_name,
            'status': 'completed',
        }

    @staticmethod
    def execute_batch(
        plan_id: str,
        steps: List[Dict[str, Any]],
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple skills sequentially (for plan execution).

        Returns:
            List of GenerationResult dicts.
        """
        results = []
        for step in steps:
            try:
                result = SkillExecutionService.execute(
                    skill_code=step['skill_code'],
                    course_id=step['course_id'],
                    user_id=user_id,
                    target_type=step.get('target_type'),
                    target_id=step.get('target_id'),
                    parameters=step.get('parameters'),
                    plan_id=plan_id,
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Skill execution failed for {step.get('skill_code')}: {e}")
                results.append({
                    'generation_id': None,
                    'skill_code': step.get('skill_code', 'unknown'),
                    'content': {},
                    'tokens_input': 0,
                    'tokens_output': 0,
                    'model_name': '',
                    'provider_name': '',
                    'status': 'failed',
                    'error': str(e),
                })
        return results


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _resolve_model(
    skill: SkillDefinition, course_id: str, target_id: Optional[str]
) -> tuple[str, str]:
    """Resolve provider and model for a skill."""
    if skill.learning_method_id is not None:
        try:
            resolved = LMModelResolver.resolve(
                learning_method_id=skill.learning_method_id,
                course_id=course_id,
                chapter_id=target_id,
                allow_fallback=True,
            )
            if resolved:
                return resolved.provider_name, resolved.model_name
        except Exception as e:
            logger.warning(f"LMModelResolver failed for {skill.code}: {e}")

    # Fallback to system default via task defaults
    from app.infrastructure.ai.task_model_resolver import resolve_model_for_task
    return resolve_model_for_task('default')


def _resolve_prompt(
    skill: SkillDefinition,
    course_id: str,
    language: str,
    params: Dict[str, Any],
    prompt_override: Optional[str],
) -> list[Dict[str, str]]:
    """Resolve and render the prompt messages for a skill."""
    if prompt_override:
        return [
            {'role': 'system', 'content': 'You are an expert educational content creator.'},
            {'role': 'user', 'content': prompt_override},
        ]

    scope = skill.prompt_template_code
    context = {
        'language': language,
        'difficulty': params.get('difficulty', 'medium'),
        'count': params.get('count', 5),
        'skill_code': skill.code,
        'learning_method_id': skill.learning_method_id,
        'topic': params.get('topic', ''),
        'chapter_title': params.get('chapter_title', ''),
        'course_title': params.get('course_title', ''),
    }

    try:
        messages = PromptResolver.resolve_and_render(
            course_id=course_id,
            scope=scope,
            context=context,
            language=language,
        )
        if messages:
            return messages
    except Exception as e:
        logger.warning(f"PromptResolver failed for {skill.code}: {e}")

    # Hardcoded fallback with topic context
    topic = params.get('topic', '')
    chapter_title = params.get('chapter_title', '')
    course_title = params.get('course_title', '')

    topic_context = ''
    if course_title:
        topic_context += f'Kurs: {course_title}\n'
    if chapter_title:
        topic_context += f'Kapitel: {chapter_title}\n'
    if topic:
        topic_context += f'Lektion: {topic}\n'

    skill_instructions = _get_skill_instructions(skill.code, language)

    return [
        {
            'role': 'system',
            'content': (
                'Du bist ein erfahrener Lehrplanentwickler und Content-Creator. '
                'Erstelle hochwertige Lerninhalte in der angegebenen Sprache. '
                'Antworte NUR mit dem Lerninhalt, ohne Meta-Kommentare.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f'{topic_context}\n'
                f'{skill_instructions}\n\n'
                f'Sprache: {language}\n'
                f'Erstelle den Inhalt passend zum Thema der Lektion.'
            ),
        },
    ]


def _get_skill_instructions(skill_code: str, language: str) -> str:
    """Return skill-specific generation instructions."""
    lang_label = 'Deutsch' if language == 'de' else 'English' if language == 'en' else language

    instructions = {
        'generate_theory_sheet': (
            f'Erstelle ein ausführliches Theorie-Arbeitsblatt auf {lang_label}. '
            'Strukturiere es mit Überschriften, Erklärungen, Beispielen und '
            'einer Zusammenfassung. Verwende Markdown-Formatierung.'
        ),
        'generate_deep_explanation': (
            f'Erstelle eine tiefgehende Erklärung auf {lang_label}. '
            'Erkläre das Thema ausführlich mit Analogien, Beispielen und '
            'Hintergrundwissen. Verwende Markdown-Formatierung.'
        ),
        'generate_step_by_step': (
            f'Erstelle eine Schritt-für-Schritt-Anleitung auf {lang_label}. '
            'Nummeriere jeden Schritt und erkläre ihn verständlich.'
        ),
        'generate_example_scenario': (
            f'Erstelle ein praxisnahes Beispiel-Szenario auf {lang_label}. '
            'Beschreibe eine realistische Situation und zeige die Anwendung.'
        ),
        'generate_diagram': (
            f'Erstelle eine textuelle Beschreibung eines Diagramms auf {lang_label}. '
            'Beschreibe die Elemente, Verbindungen und Zusammenhänge.'
        ),
        'generate_quiz': (
            f'Erstelle ein Quiz mit 5-10 Multiple-Choice-Fragen auf {lang_label}. '
            'Gib als JSON zurück: {{"questions": [{{"question": "...", '
            '"options": ["A", "B", "C", "D"], "correct": 0, '
            '"explanation": "..."}}]}}'
        ),
        'generate_flashcards': (
            f'Erstelle 10-15 Lernkarten auf {lang_label}. '
            'Gib als JSON zurück: {{"cards": [{{"front": "...", "back": "..."}}]}}'
        ),
        'generate_drag_and_drop': (
            f'Erstelle eine Zuordnungsaufgabe auf {lang_label}. '
            'Gib als JSON zurück: {{"pairs": [{{"term": "...", "definition": "..."}}]}}'
        ),
        'generate_cloze_test': (
            f'Erstelle einen Lückentext auf {lang_label}. '
            'Gib als JSON zurück: {{"text": "Der {{{{1}}}} ist...", '
            '"gaps": [{{"id": 1, "answer": "...", "alternatives": ["..."]}}]}}'
        ),
        'generate_true_false': (
            f'Erstelle 8-12 Wahr/Falsch-Aussagen auf {lang_label}. '
            'Gib als JSON zurück: {{"statements": [{{"statement": "...", '
            '"correct": true, "explanation": "..."}}]}}'
        ),
        'generate_free_text': (
            f'Erstelle 3-5 offene Fragen auf {lang_label}. '
            'Gib als JSON zurück: {{"questions": [{{"question": "...", '
            '"sample_answer": "...", "keywords": ["..."]}}]}}'
        ),
        'generate_ihk_tasks': (
            f'Erstelle prüfungsähnliche Aufgaben im IHK-Stil auf {lang_label}. '
            'Gib als JSON zurück: {{"tasks": [{{"task": "...", '
            '"points": 10, "solution": "..."}}]}}'
        ),
        'generate_multi_step': (
            f'Erstelle eine mehrstufige praktische Aufgabe auf {lang_label}. '
            'Gib als JSON zurück: {{"steps": [{{"instruction": "...", '
            '"expected_result": "...", "hints": ["..."]}}]}}'
        ),
        'generate_math_interactive': (
            f'Erstelle interaktive Rechenaufgaben auf {lang_label}. '
            'Gib als JSON zurück: {{"exercises": [{{"problem": "...", '
            '"solution": "...", "steps": ["..."]}}]}}'
        ),
        'generate_hands_on_lab': (
            f'Erstelle eine praktische Laborübung auf {lang_label}. '
            'Beschreibe Ziel, Materialien, Schritte und erwartete Ergebnisse.'
        ),
        'generate_whiteboard': (
            f'Erstelle eine Whiteboard-Übung auf {lang_label}. '
            'Beschreibe Konzepte die visuell erarbeitet werden sollen.'
        ),
    }

    return instructions.get(skill_code, f'Erstelle Lerninhalt auf {lang_label}.')


def _parse_output(output_text: str) -> Dict[str, Any]:
    """Parse AI output text, attempting JSON extraction."""
    try:
        return json.loads(output_text)
    except (json.JSONDecodeError, TypeError):
        return {'raw_text': output_text}


def _filter_by_active_features(skills: List[SkillDefinition]) -> List[Dict[str, Any]]:
    """
    Filter skills by active System Features.

    Skills without required_feature_code pass through.
    Skills with required_feature_code are only included if that SF is active.
    """
    # Collect which feature codes we need to check
    needed_codes = {s.required_feature_code for s in skills if s.required_feature_code}

    if not needed_codes:
        return [_serialize_skill(s) for s in skills]

    # Query active features once
    try:
        active_features = FeatureRepository.list_all_features(active_only=True)
        active_codes = {f['feature_code'] for f in active_features}
    except Exception as e:
        logger.warning(f"Could not query active features, showing all course skills: {e}")
        active_codes = needed_codes  # Fail open: show all on DB error

    return [
        _serialize_skill(s) for s in skills
        if not s.required_feature_code or s.required_feature_code in active_codes
    ]


def _serialize_skill(skill: SkillDefinition) -> Dict[str, Any]:
    """Convert a SkillDefinition to a serializable dict."""
    return {
        'code': skill.code,
        'name_i18n_key': skill.name_i18n_key,
        'description_i18n_key': skill.description_i18n_key,
        'icon': skill.icon,
        'category': skill.category,
        'learning_method_id': skill.learning_method_id,
        'prompt_template_code': skill.prompt_template_code,
        'required_context': list(skill.required_context),
        'parameters': [
            {
                'key': p.key,
                'label_i18n_key': p.label_i18n_key,
                'type': p.param_type,
                'default_value': p.default_value,
                'options': [{'value': v, 'label_i18n_key': l} for v, l in p.options],
                'required': p.required,
            }
            for p in skill.parameters
        ],
        'supports_variants': skill.supports_variants,
        'estimated_tokens': skill.estimated_tokens,
        'content_scope': skill.content_scope,
        'required_feature_code': skill.required_feature_code,
    }
