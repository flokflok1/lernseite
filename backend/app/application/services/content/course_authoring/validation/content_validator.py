"""
Content schema validation for AI-generated course content.

Thresholds come from QualityProfile, so 'schnell' is lenient
and 'maximum' is strict.
"""

import logging
from typing import Dict, List, Tuple

from app.application.services.content.course_authoring.quality_profile import (
    QualityProfile,
)

logger = logging.getLogger(__name__)


class ContentValidator:
    """Validates AI-generated content completeness."""

    @classmethod
    def validate(
        cls,
        structure: Dict,
        profile: QualityProfile
    ) -> Tuple[bool, List[Dict]]:
        """
        Validate draft structure using profile thresholds.

        Returns:
            (is_valid, issues) where each issue has level/path/message
        """
        if not profile.validate_content:
            return (True, [])

        issues: List[Dict] = []

        for ch_idx, ch in enumerate(structure.get('chapters', [])):
            ch_label = f"Kap. {ch_idx+1} \"{ch.get('title', '?')}\""

            if not ch.get('title', '').strip():
                issues.append({
                    'level': 'error', 'path': ch_label,
                    'message': 'Kein Titel'
                })

            for ls_idx, ls in enumerate(ch.get('lessons', [])):
                ls_label = (
                    f"{ch_label} -> Lek. {ls_idx+1} "
                    f"\"{ls.get('title', '?')}\""
                )
                cls._check_lesson(ls, ls_label, profile, issues)

                for mt in ls.get('methods', []):
                    mt_label = (
                        f"{ls_label} -> {mt.get('type', '?')} "
                        f"\"{mt.get('title', '?')}\""
                    )
                    cls._check_method(mt, mt_label, profile, issues)

        errors = [i for i in issues if i['level'] == 'error']
        return (len(errors) == 0, issues)

    @classmethod
    def _check_lesson(cls, lesson, path, profile, issues):
        content = lesson.get('content', {})
        raw_text = content.get('raw_text', '') if isinstance(content, dict) else ''

        if len(raw_text) < profile.min_raw_text_length:
            issues.append({
                'level': 'warning', 'path': path,
                'message': (
                    f'Theorieblatt zu kurz ({len(raw_text)} Zeichen, '
                    f'Minimum: {profile.min_raw_text_length})'
                )
            })

    @classmethod
    def _check_method(cls, method, path, profile, issues):
        mtype = method.get('type', '')
        content = method.get('content', {})

        if not isinstance(content, dict) or not content:
            issues.append({
                'level': 'error', 'path': path,
                'message': 'Leerer content'
            })
            return

        if mtype == 'quiz':
            qs = content.get('questions', [])
            if len(qs) < profile.min_quiz_questions:
                issues.append({
                    'level': 'error', 'path': path,
                    'message': (
                        f'{len(qs)} Fragen '
                        f'(Minimum: {profile.min_quiz_questions})'
                    )
                })
            for i, q in enumerate(qs):
                if not q.get('question'):
                    issues.append({
                        'level': 'error',
                        'path': f'{path}[{i}]',
                        'message': 'Frage ohne Text'
                    })
                if len(q.get('options', [])) < 2:
                    issues.append({
                        'level': 'error',
                        'path': f'{path}[{i}]',
                        'message': 'Weniger als 2 Optionen'
                    })
                if q.get('correct') is None:
                    issues.append({
                        'level': 'error',
                        'path': f'{path}[{i}]',
                        'message': 'Kein correct-Index'
                    })

        elif mtype == 'flashcards':
            cards = content.get('cards', [])
            if len(cards) < profile.min_flashcard_count:
                issues.append({
                    'level': 'error', 'path': path,
                    'message': (
                        f'{len(cards)} Karten '
                        f'(Minimum: {profile.min_flashcard_count})'
                    )
                })

        elif mtype == 'exercise':
            if not content.get('question') or len(content.get('question', '')) < 10:
                issues.append({
                    'level': 'error', 'path': path,
                    'message': 'Keine/zu kurze Frage'
                })
            solution = method.get('solution', {})
            if profile.require_exercise_solution and not solution.get('modelAnswer'):
                issues.append({
                    'level': 'warning', 'path': path,
                    'message': 'Keine Musterloesung'
                })
