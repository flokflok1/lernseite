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

from app.application.services.exams.curriculum_mapping_helpers import (
    extract_json_object,
    build_compound_code,
    build_objective_reference,
    build_mapping_prompt,
    detect_specialization,
    filter_sections_for_specialization,
)

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
            "You are an expert curriculum structure parser for German IHK "
            "(Industrie- und Handelskammer) vocational training frameworks "
            "(Ausbildungsrahmenplan). Analyze the document and extract the "
            "complete hierarchical structure as JSON.\n\n"
            "IMPORTANT extraction rules:\n"
            "- Detect the framework type: ihk_ausbildung, hochschule, "
            "zertifizierung, or custom\n"
            "- Extract the official section codes (e.g. 'A', 'B', 'C' or "
            "'Teil 1', 'Teil 2')\n"
            "- For each section, detect which specializations it applies to "
            "(e.g. 'Fachinformatiker Anwendungsentwicklung', "
            "'Fachinformatiker Systemintegration', etc.)\n"
            "- For each position, extract the training period if mentioned "
            "(e.g. '1.-15. Monat', '1.-36. Monat')\n"
            "- For each objective, detect the competency level from IHK "
            "taxonomy: 'kennen' (know), 'anwenden' (apply), or "
            "'beherrschen' (master). Look for cues like 'kennen', "
            "'beschreiben', 'anwenden', 'durchfuehren', 'beherrschen'.\n"
            "- Preserve the original German text for descriptions\n\n"
            "Output MUST be valid JSON with this schema:\n"
            "{\n"
            '  "name": "Official framework name",\n'
            '  "framework_type": "ihk_ausbildung",\n'
            '  "version": "1.0",\n'
            '  "sections": [\n'
            "    {\n"
            '      "code": "A",\n'
            '      "title": "Section title",\n'
            '      "description": "Optional section description",\n'
            '      "applies_to": ["Fachinformatiker Anwendungsentwicklung",'
            ' "Fachinformatiker Systemintegration"],\n'
            '      "positions": [\n'
            "        {\n"
            '          "code": "1",\n'
            '          "title": "Position title",\n'
            '          "description": "Optional position description",\n'
            '          "training_period": "1.-15. Monat",\n'
            '          "objectives": [\n'
            "            {\n"
            '              "code": "a",\n'
            '              "description": "Full objective text",\n'
            '              "competency_level": "anwenden"\n'
            "            }\n"
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
        adapter = AIAdapter(timeout=300, **ai_opts)
        response = adapter.send_request(
            prompt=prompt,
            temperature=0.1,
            max_tokens=65000,
        )

        raw_text = response.get('output_text', '')
        logger.info(
            "AI curriculum response: %d chars, %d input tokens, %d output tokens",
            len(raw_text),
            response.get('input_tokens', 0),
            response.get('output_tokens', 0),
        )

        if not raw_text.strip():
            raise ValueError(
                "AI returned empty response. The document may be too large "
                "or the model's safety filter blocked the output. "
                "Try a different model or smaller PDF."
            )

        raw_text = extract_json_object(raw_text)

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse AI curriculum response as JSON: %s\n"
                "First 500 chars: %s",
                exc, raw_text[:500],
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
        provider: str = None,
        model: str = None,
    ) -> Dict[str, Any]:
        """AI-map unmapped questions to curriculum objectives.

        Filters objectives by specialization (e.g. FISI → sections A,C,F)
        and passes exam part context (GA1/GA2/WK) for accurate mapping.

        Args:
            exam_type_key: Exam type key (e.g. 'IHK_FISI_AP1').
            batch_size: Number of questions per AI batch call.
            provider: Optional AI provider name.
            model: Optional model name.

        Returns:
            Stats dict with mapped, skipped, errors.

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

        framework_id = framework['id']
        specialization = detect_specialization(exam_type_key)
        all_objectives = repo.find_all_objectives_by_framework(framework_id)
        if not all_objectives:
            logger.warning(
                "Framework %s has no objectives, skipping mapping",
                framework_id,
            )
            return {'mapped': 0, 'skipped': 0, 'errors': 0}

        sections = repo.find_sections_by_framework(framework_id)
        allowed_sections = filter_sections_for_specialization(
            sections, specialization,
        )
        objectives = [
            o for o in all_objectives
            if o.get('section_code') in allowed_sections
        ]
        logger.info(
            "Filtered objectives: %d/%d (sections %s for %s)",
            len(objectives), len(all_objectives),
            allowed_sections, specialization,
        )

        obj_reference = build_objective_reference(objectives)

        unmapped = repo.find_unmapped_questions(exam_type_key)
        if not unmapped:
            logger.info("No unmapped questions for %s", exam_type_key)
            return {'mapped': 0, 'skipped': 0, 'errors': 0}

        stats = {'mapped': 0, 'skipped': 0, 'errors': 0}

        ai_kwargs = {k: v for k, v in
                     {'provider': provider, 'model': model}.items() if v}

        for i in range(0, len(unmapped), batch_size):
            batch = unmapped[i:i + batch_size]
            CurriculumService._map_question_batch(
                batch, obj_reference, objectives, stats, ai_kwargs,
                specialization,
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
        ai_kwargs: Dict[str, str] = None,
        specialization: str = None,
    ) -> None:
        """Map a batch of questions to objectives using AI.

        Args:
            questions: List of question dicts to map.
            obj_reference: Formatted objectives reference for AI prompt.
            objectives: Full objectives list for code lookup.
            stats: Mutable stats dict to update in-place.
            ai_kwargs: Optional dict with provider/model for AIAdapter.
            specialization: Detected specialization (e.g. 'FISI').
        """
        from app.infrastructure.ai.adapter import AIAdapter
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        obj_by_code = {build_compound_code(o): o for o in objectives}

        questions_text = "\n".join(
            f"- ID: {q['question_id']} | "
            f"Part: {q.get('exam_part') or 'unknown'} | "
            f"Q{q.get('question_number', '?')}: "
            f"{(q.get('question_text') or '')[:200]}"
            for q in questions
        )

        prompt = build_mapping_prompt(
            obj_reference, questions_text, specialization,
        )

        try:
            adapter = AIAdapter(**(ai_kwargs or {}))
            response = adapter.send_request(
                prompt=prompt,
                temperature=0.1,
                max_tokens=32000,
            )

            raw = extract_json_object(
                response.get('output_text', ''),
            )
            mappings = json.loads(raw)

            for m in mappings:
                code = m.get('objective_code')
                qid = m.get('question_id')
                confidence = float(m.get('confidence', 0.8))

                if code not in obj_by_code or not qid:
                    stats['skipped'] += 1
                    continue

                CurriculumFrameworkRepository.tag_question(
                    question_id=qid,
                    objective_id=obj_by_code[code]['objective_id'],
                    confidence=confidence,
                    tagged_by='ai',
                )
                stats['mapped'] += 1

        except json.JSONDecodeError:
            logger.exception("Failed to parse AI mapping response")
            stats['errors'] += len(questions)
        except Exception:
            logger.exception("Error in question batch mapping")
            stats['errors'] += len(questions)

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
        """Get exam-relevance scores per curriculum position.

        Returns year-weighted appearance rates, point scores,
        recent/older counts, and computed trend per position.

        Args:
            framework_id: Curriculum framework ID.

        Returns:
            List of dicts with position_id, exam_count, appearance_rate,
            weighted_score, recent_count, older_count, trend.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        rows = CurriculumFrameworkRepository.find_position_relevance_scores(
            framework_id,
        )
        for row in rows:
            row['trend'] = compute_trend(
                row.get('recent_count', 0),
                row.get('older_count', 0),
            )
        return rows

    @staticmethod
    def get_coverage_report(framework_id: int) -> Dict[str, Any]:
        """Combined coverage report: per-position gap detection + summary.

        Args:
            framework_id: Curriculum framework ID.

        Returns:
            Dict with 'summary' and 'positions' keys.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        coverage_rows = CurriculumFrameworkRepository.get_curriculum_coverage_stats(
            framework_id,
        )
        relevance_rows = CurriculumService.get_exam_relevance_weights(framework_id)
        relevance_by_id = {r['position_id']: r for r in relevance_rows}

        positions = []
        for row in coverage_rows:
            q_count = row.get('question_count', 0) or 0
            obj_count = row.get('objective_count', 0) or 0
            pos = dict(row)
            pos['has_questions'] = q_count > 0
            pos['gap'] = obj_count > 0 and q_count == 0
            pos['coverage_pct'] = min(100, round(q_count / obj_count * 100)) if obj_count > 0 else 0
            pos['relevance'] = relevance_by_id.get(row.get('position_id'))
            positions.append(pos)

        total_obj = sum(p.get('objective_count', 0) or 0 for p in positions)
        mapped_obj = sum(
            p.get('objective_count', 0) or 0 for p in positions if p['has_questions']
        )
        gap_count = sum(1 for p in positions if p['gap'])
        positions_with_q = sum(1 for p in positions if p['has_questions'])
        coverage_pct = round(mapped_obj / total_obj * 100) if total_obj else 0

        return {
            'summary': {
                'total_positions': len(positions),
                'positions_with_questions': positions_with_q,
                'gap_count': gap_count,
                'coverage_percent': coverage_pct,
                'total_objectives': total_obj,
                'mapped_objectives': mapped_obj,
            },
            'positions': positions,
        }


# ── Module-level helpers ───────────────────────────────────────────

def compute_trend(recent_count: int, older_count: int) -> str:
    """Determine trend from recent vs older exam appearances.

    Recent = last 3 years, older = everything before.
    Normalizes to per-year rate for fair comparison.

    Used by both the relevance API and the course generator.
    """
    if recent_count == 0 and older_count == 0:
        return 'stable'
    if older_count == 0:
        return 'rising'
    if recent_count == 0:
        return 'declining'
    recent_rate = recent_count / 3.0
    older_rate = older_count / 5.0
    if recent_rate > older_rate * 1.3:
        return 'rising'
    if recent_rate < older_rate * 0.7:
        return 'declining'
    return 'stable'


