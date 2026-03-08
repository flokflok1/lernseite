"""
Curriculum Service

Orchestrates curriculum framework operations:
- AI-powered PDF import (parse exam framework documents)
- Automatic question-to-curriculum mapping via AI
- User curriculum performance profiles
- Exam relevance / coverage statistics

All DB access goes through CurriculumFrameworkRepository (G09).
No hardcoded AI providers or models (G07).
"""

import json
import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CurriculumService:
    """Application service for curriculum framework management."""

    # ── AI PDF Import ──────────────────────────────────────────────

    @staticmethod
    def parse_pdf_with_ai(
        pdf_text: str,
        provider: str = None,
        model: str = None,
    ) -> Dict[str, Any]:
        """Use AI to parse PDF text into a curriculum structure.

        Args:
            pdf_text: Extracted text content from a curriculum PDF.
            provider: Optional AI provider name (caller-selected).
            model: Optional model name. Falls back to provider default.

        Returns:
            Parsed curriculum dict with sections/positions/objectives.

        Raises:
            ValueError: If AI response cannot be parsed as valid JSON.
        """
        from app.infrastructure.ai.adapter import AIAdapter

        prompt = (
            "You are a curriculum structure parser. "
            "Analyze the following exam curriculum document and extract "
            "its hierarchical structure as JSON.\n\n"
            "Output MUST be valid JSON with this schema:\n"
            "{\n"
            '  "name": "Framework name",\n'
            '  "version": "1.0",\n'
            '  "sections": [\n'
            "    {\n"
            '      "code": "T1",\n'
            '      "title": "Section title",\n'
            '      "positions": [\n'
            "        {\n"
            '          "code": "T1.1",\n'
            '          "title": "Position title",\n'
            '          "objectives": [\n'
            '            {"code": "T1.1.1", "description": "..."}\n'
            "          ]\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Document text:\n"
            f"{pdf_text}"
        )

        ai_opts = {k: v for k, v in {'provider': provider, 'model': model}.items() if v}
        adapter = AIAdapter(**ai_opts)
        response = adapter.send_request(
            prompt=prompt,
            temperature=0.1,
            max_tokens=8000,
        )

        raw_text = response.get('output_text', '')
        raw_text = _strip_markdown_fences(raw_text)

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse AI curriculum response as JSON: %s",
                exc,
            )
            raise ValueError(
                f"AI response is not valid JSON: {exc}"
            ) from exc

        logger.info(
            "AI parsed curriculum: %s with %d sections",
            result.get('name', 'unknown'),
            len(result.get('sections', [])),
        )
        return result

    @staticmethod
    def import_from_ai_result(
        ai_result: dict,
        source_document: str = None,
    ) -> Dict[str, Any]:
        """Persist an AI-parsed framework structure to the database.

        Args:
            ai_result: Parsed curriculum dict from parse_pdf_with_ai.
            source_document: Optional source filename for metadata.

        Returns:
            Created framework dict with import_counts.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        if source_document:
            metadata = ai_result.get('metadata') or {}
            metadata['source_document'] = source_document
            ai_result['metadata'] = metadata

        framework = CurriculumFrameworkRepository.bulk_import_framework(
            ai_result,
        )

        logger.info(
            "Imported curriculum framework '%s' (id=%s), counts=%s",
            framework.get('name'),
            framework.get('framework_id'),
            framework.get('import_counts'),
        )
        return framework

    # ── AI Question Mapping ────────────────────────────────────────

    @staticmethod
    def auto_map_questions(
        exam_type_key: str,
        batch_size: int = 10,
    ) -> Dict[str, Any]:
        """AI-map unmapped questions to curriculum objectives.

        Finds all questions for the given exam type that have no
        curriculum tags, then uses AI to suggest objective mappings
        in batches.

        Args:
            exam_type_key: Exam type key (e.g. 'IHK_FISI').
            batch_size: Number of questions per AI batch call.

        Returns:
            Stats dict with mapped_count, skipped_count, error_count.

        Raises:
            ValueError: If no framework is linked to the exam type.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        repo = CurriculumFrameworkRepository

        framework = repo.find_framework_for_exam_type(exam_type_key)
        if not framework:
            raise ValueError(
                f"No curriculum framework linked to exam type "
                f"'{exam_type_key}'"
            )

        framework_id = framework['framework_id']
        objectives = repo.find_all_objectives_by_framework(framework_id)
        if not objectives:
            logger.warning(
                "Framework %s has no objectives, skipping mapping",
                framework_id,
            )
            return {'mapped_count': 0, 'skipped_count': 0, 'error_count': 0}

        obj_reference = _build_objective_reference(objectives)

        unmapped = repo.find_unmapped_questions(exam_type_key)
        if not unmapped:
            logger.info("No unmapped questions for %s", exam_type_key)
            return {'mapped_count': 0, 'skipped_count': 0, 'error_count': 0}

        stats = {'mapped_count': 0, 'skipped_count': 0, 'error_count': 0}

        for i in range(0, len(unmapped), batch_size):
            batch = unmapped[i:i + batch_size]
            CurriculumService._map_question_batch(
                batch, obj_reference, objectives, stats,
            )

        logger.info(
            "Auto-mapping complete for %s: %s", exam_type_key, stats,
        )
        return stats

    @staticmethod
    def _map_question_batch(
        questions: List[Dict],
        obj_reference: str,
        objectives: List[Dict],
        stats: Dict[str, int],
    ) -> None:
        """Map a batch of questions to objectives using AI.

        Args:
            questions: List of question dicts to map.
            obj_reference: Formatted objectives reference for AI prompt.
            objectives: Full objectives list for code lookup.
            stats: Mutable stats dict to update in-place.
        """
        from app.infrastructure.ai.adapter import AIAdapter
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        obj_by_code = {o['objective_code']: o for o in objectives}

        questions_text = "\n".join(
            f"- ID: {q['question_id']} | "
            f"Q{q.get('question_number', '?')}: "
            f"{(q.get('question_text') or '')[:200]}"
            for q in questions
        )

        prompt = (
            "Map each exam question to the most relevant curriculum "
            "objective code. Respond with a JSON array.\n\n"
            "Curriculum objectives:\n"
            f"{obj_reference}\n\n"
            "Questions:\n"
            f"{questions_text}\n\n"
            "Output format (JSON array):\n"
            '[{"question_id": "...", "objective_code": "...", '
            '"confidence": 0.0-1.0}]'
        )

        try:
            adapter = AIAdapter()
            response = adapter.send_request(
                prompt=prompt,
                temperature=0.1,
                max_tokens=4000,
            )

            raw = _strip_markdown_fences(
                response.get('output_text', ''),
            )
            mappings = json.loads(raw)

            for m in mappings:
                code = m.get('objective_code')
                qid = m.get('question_id')
                confidence = float(m.get('confidence', 0.8))

                if code not in obj_by_code or not qid:
                    stats['skipped_count'] += 1
                    continue

                CurriculumFrameworkRepository.tag_question(
                    question_id=qid,
                    objective_id=obj_by_code[code]['objective_id'],
                    confidence=confidence,
                    tagged_by='ai',
                )
                stats['mapped_count'] += 1

        except json.JSONDecodeError:
            logger.exception("Failed to parse AI mapping response")
            stats['error_count'] += len(questions)
        except Exception:
            logger.exception("Error in question batch mapping")
            stats['error_count'] += len(questions)

    # ── User Profile ───────────────────────────────────────────────

    @staticmethod
    def get_user_curriculum_profile(
        user_id: str,
        exam_type_key: str,
    ) -> List[Dict]:
        """Get user performance aggregated by curriculum position.

        Args:
            user_id: User UUID.
            exam_type_key: Exam type key.

        Returns:
            List of position dicts with accuracy and attempt stats.

        Raises:
            ValueError: If no framework is linked to the exam type.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        framework = CurriculumFrameworkRepository.find_framework_for_exam_type(
            exam_type_key,
        )
        if not framework:
            raise ValueError(
                f"No curriculum framework for '{exam_type_key}'"
            )

        return CurriculumFrameworkRepository.get_user_curriculum_profile(
            user_id, framework['framework_id'],
        )

    # ── Stats ──────────────────────────────────────────────────────

    @staticmethod
    def get_exam_relevance_weights(
        framework_id: int,
    ) -> List[Dict]:
        """Get coverage statistics for a curriculum framework.

        Delegates to the repository's coverage stats query.

        Args:
            framework_id: Curriculum framework ID.

        Returns:
            List of position-level stats with question counts.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        return CurriculumFrameworkRepository.get_curriculum_coverage_stats(
            framework_id,
        )


# ── Module-level helpers ───────────────────────────────────────────

def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences from AI output."""
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    return text.strip()


def _build_objective_reference(objectives: List[Dict]) -> str:
    """Build a compact text reference of objectives for AI prompts."""
    lines = []
    for obj in objectives:
        lines.append(
            f"{obj['objective_code']}: "
            f"{obj.get('description', '')[:120]}"
        )
    return "\n".join(lines)
