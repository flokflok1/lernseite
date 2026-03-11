"""
CurriculumFrameworkRepository Part 2 — Mappings and coverage stats.

Continuation of CurriculumFrameworkRepository (curriculum.py).
Contains topic mappings, question tagging, coverage stats, and exam type linking.

Split from curriculum.py to comply with Quality Gate G01 (max 500 lines per file).
"""

import logging
from typing import Dict, Any, Optional, List

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query
)

logger = logging.getLogger(__name__)


class CurriculumMappingMixin:
    """Mixin providing mapping and stats operations for CurriculumFrameworkRepository."""

    # ── Curriculum <-> Topic Mapping ────────────────────────────────

    @staticmethod
    def create_topic_mapping(
        objective_id: int,
        topic_id: str,
        confidence: float = 1.0,
        mapped_by: str = 'manual',
    ) -> Dict[str, Any]:
        """Upsert a mapping between objective and topic.

        topic_id is UUID from exam_topic_taxonomy.
        """
        return fetch_one(
            """INSERT INTO assessments.curriculum_topic_mapping
                   (curriculum_objective_id, topic_id, confidence, mapped_by)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (curriculum_objective_id, topic_id)
               DO UPDATE SET confidence = EXCLUDED.confidence,
                             mapped_by = EXCLUDED.mapped_by
               RETURNING *""",
            [objective_id, topic_id, confidence, mapped_by],
        )

    @staticmethod
    def find_topics_by_objective(
        objective_id: int,
    ) -> List[Dict[str, Any]]:
        """All topics mapped to an objective, joined with taxonomy."""
        return fetch_all(
            """SELECT m.id AS mapping_id,
                      m.curriculum_objective_id,
                      m.topic_id,
                      m.confidence, m.mapped_by,
                      t.topic_name, t.parent_topic_id
               FROM assessments.curriculum_topic_mapping m
               JOIN assessments.exam_topic_taxonomy t
                   ON t.topic_id = m.topic_id
               WHERE m.curriculum_objective_id = %s
               ORDER BY m.confidence DESC""",
            [objective_id],
        )

    # ── Question <-> Curriculum Tagging ─────────────────────────────

    @staticmethod
    def tag_question(
        question_id: str,
        objective_id: int,
        confidence: float = 1.0,
        tagged_by: str = 'manual',
    ) -> Dict[str, Any]:
        """Upsert a tag linking a question to a curriculum objective.

        question_id is UUID from exam_questions.
        """
        return fetch_one(
            """INSERT INTO assessments.exam_question_curriculum_tags
                   (question_id, curriculum_objective_id, confidence,
                    tagged_by)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (question_id, curriculum_objective_id)
               DO UPDATE SET confidence = EXCLUDED.confidence,
                             tagged_by = EXCLUDED.tagged_by
               RETURNING *""",
            [question_id, objective_id, confidence, tagged_by],
        )

    @staticmethod
    def find_tags_by_question(
        question_id: str,
    ) -> List[Dict[str, Any]]:
        """All curriculum tags for a question with full hierarchy context."""
        return fetch_all(
            """SELECT ct.id AS tag_id, ct.question_id,
                      ct.curriculum_objective_id,
                      ct.confidence, ct.tagged_by,
                      o.objective_code, o.description,
                      p.id AS position_id,
                      p.position_number AS position_code,
                      p.display_name AS position_title,
                      s.id AS section_id,
                      s.section_code,
                      s.display_name AS section_title,
                      s.framework_id
               FROM assessments.exam_question_curriculum_tags ct
               JOIN assessments.curriculum_objectives o
                   ON o.id = ct.curriculum_objective_id
               JOIN assessments.curriculum_positions p
                   ON p.id = o.position_id
               JOIN assessments.curriculum_sections s
                   ON s.id = p.section_id
               WHERE ct.question_id = %s
               ORDER BY s.order_index, p.order_index, o.order_index""",
            [question_id],
        )

    @staticmethod
    def find_questions_by_objective(
        objective_id: int,
    ) -> List[Dict[str, Any]]:
        """All questions tagged with a specific objective."""
        return fetch_all(
            """SELECT ct.id AS tag_id, ct.confidence, ct.tagged_by,
                      q.question_id, q.question_number,
                      q.question_text, q.points, q.difficulty,
                      q.exam_id
               FROM assessments.exam_question_curriculum_tags ct
               JOIN assessments.exam_questions q
                   ON q.question_id = ct.question_id
               WHERE ct.curriculum_objective_id = %s
               ORDER BY ct.confidence DESC""",
            [objective_id],
        )

    @staticmethod
    def remove_question_tag(
        question_id: str, objective_id: int,
    ) -> bool:
        """Remove a question-objective tag."""
        result = fetch_one(
            """DELETE FROM assessments.exam_question_curriculum_tags
               WHERE question_id = %s
                 AND curriculum_objective_id = %s
               RETURNING id""",
            [question_id, objective_id],
        )
        return result is not None

    # ── Coverage Stats ──────────────────────────────────────────────

    @staticmethod
    def get_curriculum_coverage_stats(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """Count questions per position for a framework."""
        return fetch_all(
            """SELECT s.id AS section_id,
                      s.section_code,
                      s.display_name AS section_title,
                      p.id AS position_id,
                      p.position_number AS position_code,
                      p.display_name AS position_title,
                      COUNT(DISTINCT ct.question_id) AS question_count,
                      COUNT(DISTINCT o.id) AS objective_count,
                      COUNT(DISTINCT ct.question_id) FILTER (
                          WHERE ct.tagged_by = 'ai'
                      ) AS ai_tagged_count
               FROM assessments.curriculum_sections s
               JOIN assessments.curriculum_positions p
                   ON p.section_id = s.id
               LEFT JOIN assessments.curriculum_objectives o
                   ON o.position_id = p.id
               LEFT JOIN assessments.exam_question_curriculum_tags ct
                   ON ct.curriculum_objective_id = o.id
               WHERE s.framework_id = %s
               GROUP BY s.id, s.section_code, s.display_name,
                        p.id, p.position_number, p.display_name
               ORDER BY s.order_index, p.order_index""",
            [framework_id],
        )

    # ── Exam Type Linking ───────────────────────────────────────────

    @staticmethod
    def link_framework_to_exam_type(
        framework_id: int, exam_type_key: str,
    ) -> bool:
        """Link a framework to an exam type in the registry."""
        row = fetch_one(
            """UPDATE assessments.exam_type_registry
               SET framework_id = %s, updated_at = NOW()
               WHERE exam_type = %s
               RETURNING exam_type""",
            [framework_id, exam_type_key],
        )
        if not row:
            raise ValueError(
                f'Exam type "{exam_type_key}" not found in registry'
            )
        return True

    @staticmethod
    def find_framework_for_exam_type(
        exam_type_key: str,
    ) -> Optional[Dict[str, Any]]:
        """Find the curriculum framework linked to an exam type."""
        return fetch_one(
            """SELECT f.*
               FROM assessments.curriculum_frameworks f
               JOIN assessments.exam_type_registry r
                   ON r.framework_id = f.id
               WHERE r.exam_type = %s""",
            [exam_type_key],
        )

    # ── Unmapped Questions ─────────────────────────────────────────

    @staticmethod
    def find_unmapped_questions(
        exam_type_key: str,
    ) -> List[Dict[str, Any]]:
        """Find questions for an exam type that have no curriculum tags."""
        return fetch_all(
            """SELECT q.question_id, q.question_number,
                      q.question_text, q.points, q.difficulty,
                      q.exam_id
               FROM assessments.exam_questions q
               JOIN assessments.exams e ON e.exam_id = q.exam_id
               WHERE e.exam_type_key = %s
                 AND NOT EXISTS (
                     SELECT 1
                     FROM assessments.exam_question_curriculum_tags ct
                     WHERE ct.question_id = q.question_id
                 )
               ORDER BY e.year DESC NULLS LAST, q.question_number""",
            [exam_type_key],
        )

    # ── User Curriculum Profile ────────────────────────────────────

    @staticmethod
    def get_user_curriculum_profile(
        user_id: str, framework_id: int,
    ) -> List[Dict[str, Any]]:
        """User performance aggregated by curriculum position.

        Joins question tags with user answer history to compute
        per-position accuracy and attempt counts.
        """
        return fetch_all(
            """SELECT p.id AS position_id,
                      p.position_number AS position_code,
                      p.display_name AS position_title,
                      s.section_code,
                      s.display_name AS section_title,
                      COUNT(DISTINCT ct.question_id) AS question_count,
                      COUNT(DISTINCT ua.id) AS attempt_count,
                      ROUND(AVG(
                          CASE WHEN ua.is_correct THEN 100.0 ELSE 0.0 END
                      ), 1) AS accuracy_pct
               FROM assessments.curriculum_sections s
               JOIN assessments.curriculum_positions p
                   ON p.section_id = s.id
               LEFT JOIN assessments.curriculum_objectives o
                   ON o.position_id = p.id
               LEFT JOIN assessments.exam_question_curriculum_tags ct
                   ON ct.curriculum_objective_id = o.id
               LEFT JOIN assessments.user_exam_answers ua
                   ON ua.question_id = ct.question_id
                   AND ua.user_id = %s
               WHERE s.framework_id = %s
               GROUP BY p.id, p.position_number, p.display_name,
                        s.section_code, s.display_name
               ORDER BY s.section_code, p.position_number""",
            [user_id, framework_id],
        )
