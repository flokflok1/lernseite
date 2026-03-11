"""
CurriculumFrameworkRepository — CRUD for curriculum frameworks and hierarchy.

Handles the curriculum structure:
  curriculum_frameworks -> curriculum_sections -> curriculum_positions -> curriculum_objectives

Split into two files for G01 compliance:
  - curriculum.py: Framework/Section/Position/Objective CRUD, bulk import, tree load
  - curriculum_part2.py: Topic mappings, question mappings, coverage stats
"""

import json
import logging
from typing import Dict, Any, Optional, List

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query, insert_returning
)
from app.infrastructure.persistence.repositories.exams.curriculum_part2 import (
    CurriculumMappingMixin,
)

logger = logging.getLogger(__name__)


class CurriculumFrameworkRepository(CurriculumMappingMixin):
    """Repository for assessments.curriculum_frameworks and child tables."""

    # ── Framework CRUD ──────────────────────────────────────────────

    @staticmethod
    def create_framework(data: dict) -> Dict[str, Any]:
        """Insert a new curriculum framework."""
        insert_data = {
            'name': data['name'],
            'framework_type': data.get('framework_type', 'custom'),
            'source_document': data.get('source_document'),
            'version': data.get('version', '1.0'),
            'metadata': json.dumps(data['metadata']) if data.get('metadata') else None,
        }
        # Remove None values so DB defaults apply
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        return insert_returning(
            'assessments.curriculum_frameworks',
            insert_data,
        )

    @staticmethod
    def find_all_frameworks() -> List[Dict[str, Any]]:
        """List all frameworks with section counts."""
        return fetch_all(
            """SELECT f.id AS framework_id, f.name, f.framework_type,
                      f.source_document, f.version, f.valid_from,
                      f.valid_until, f.metadata, f.created_at, f.updated_at,
                      COALESCE(sc.section_count, 0) AS section_count
               FROM assessments.curriculum_frameworks f
               LEFT JOIN LATERAL (
                   SELECT COUNT(*) AS section_count
                   FROM assessments.curriculum_sections s
                   WHERE s.framework_id = f.id
               ) sc ON TRUE
               ORDER BY f.created_at DESC""",
            [],
        )

    @staticmethod
    def find_framework_by_id(
        framework_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Find a single framework by ID."""
        row = fetch_one(
            "SELECT * FROM assessments.curriculum_frameworks WHERE id = %s",
            [framework_id],
        )
        if row:
            row['framework_id'] = row.pop('id', row.get('framework_id'))
        return row

    @staticmethod
    def delete_framework(framework_id: int) -> bool:
        """Delete a framework (cascades to sections/positions/objectives)."""
        result = fetch_one(
            """DELETE FROM assessments.curriculum_frameworks
               WHERE id = %s
               RETURNING id""",
            [framework_id],
        )
        return result is not None

    # ── Section CRUD ────────────────────────────────────────────────

    @staticmethod
    def create_section(
        framework_id: int, data: dict,
    ) -> Dict[str, Any]:
        """Insert a new curriculum section."""
        insert_data = {
            'framework_id': framework_id,
            'section_code': data.get('section_code') or data.get('code', ''),
            'display_name': json.dumps(data.get('title', '')) if isinstance(data.get('title'), str) else json.dumps(data.get('title', {})),
            'description': json.dumps(data.get('description', '')) if isinstance(data.get('description'), str) else json.dumps(data.get('description', {})),
            'order_index': data.get('order_index', 0),
        }
        applies_to = data.get('applies_to')
        if applies_to and isinstance(applies_to, list):
            insert_data['applies_to'] = applies_to
        return insert_returning(
            'assessments.curriculum_sections',
            insert_data,
        )

    @staticmethod
    def find_sections_by_framework(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """All sections for a framework, ordered by order_index."""
        return fetch_all(
            """SELECT id AS section_id,
                      section_code AS section_number,
                      display_name AS title,
                      framework_id, order_index, applies_to
               FROM assessments.curriculum_sections
               WHERE framework_id = %s
               ORDER BY order_index, id""",
            [framework_id],
        )

    # ── Position CRUD ───────────────────────────────────────────────

    @staticmethod
    def create_position(
        section_id: int, data: dict,
    ) -> Dict[str, Any]:
        """Insert a new curriculum position."""
        insert_data = {
            'section_id': section_id,
            'position_number': data.get('position_number') or data.get('code', ''),
            'display_name': json.dumps(data.get('title', '')) if isinstance(data.get('title'), str) else json.dumps(data.get('title', {})),
            'description': json.dumps(data.get('description', '')) if isinstance(data.get('description'), str) else json.dumps(data.get('description', {})),
            'order_index': data.get('order_index', 0),
        }
        training_period = data.get('training_period')
        if training_period:
            insert_data['training_period'] = training_period
        return insert_returning(
            'assessments.curriculum_positions',
            insert_data,
        )

    @staticmethod
    def find_positions_by_section(
        section_id: int,
    ) -> List[Dict[str, Any]]:
        """All positions for a section, ordered by order_index."""
        return fetch_all(
            """SELECT id AS position_id,
                      position_number,
                      display_name AS title,
                      section_id, order_index, training_period
               FROM assessments.curriculum_positions
               WHERE section_id = %s
               ORDER BY order_index, id""",
            [section_id],
        )

    # ── Objective CRUD ──────────────────────────────────────────────

    @staticmethod
    def create_objective(
        position_id: int, data: dict,
    ) -> Dict[str, Any]:
        """Insert a new curriculum objective."""
        insert_data = {
            'position_id': position_id,
            'objective_code': data.get('objective_code') or data.get('code', ''),
            'description': json.dumps(data.get('description', '')) if isinstance(data.get('description'), str) else json.dumps(data.get('description', {})),
            'competency_level': data.get('competency_level') or data.get('taxonomy_level'),
            'order_index': data.get('order_index', 0),
        }
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        return insert_returning(
            'assessments.curriculum_objectives',
            insert_data,
        )

    @staticmethod
    def find_objectives_by_position(
        position_id: int,
    ) -> List[Dict[str, Any]]:
        """All objectives for a position, ordered by order_index."""
        return fetch_all(
            """SELECT id AS objective_id,
                      objective_code AS code,
                      description AS description_text,
                      competency_level AS bloom_level,
                      position_id, order_index
               FROM assessments.curriculum_objectives
               WHERE position_id = %s
               ORDER BY order_index, id""",
            [position_id],
        )

    @staticmethod
    def find_all_objectives_by_framework(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """Flat list of all objectives with section/position context."""
        return fetch_all(
            """SELECT o.id AS objective_id, o.objective_code,
                      o.description, o.competency_level,
                      p.id AS position_id, p.position_number AS position_code,
                      p.display_name AS position_title,
                      s.id AS section_id, s.section_code,
                      s.display_name AS section_title
               FROM assessments.curriculum_objectives o
               JOIN assessments.curriculum_positions p
                   ON p.id = o.position_id
               JOIN assessments.curriculum_sections s
                   ON s.id = p.section_id
               WHERE s.framework_id = %s
               ORDER BY s.order_index, p.order_index, o.order_index""",
            [framework_id],
        )

    # ── Curriculum Course Generation ─────────────────────────────────

    @staticmethod
    def find_positions_with_question_stats(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """Load all positions with objective counts and mapped question IDs.

        Returns one row per position with:
        - position metadata (id, code, title, section info)
        - objectives_total: count of objectives in this position
        - objectives_with_questions: objectives with at least one tagged question
        - question_ids: array of distinct question IDs mapped to this position
        - total_points: sum of question points
        """
        return fetch_all(
            """SELECT p.id AS position_id,
                      p.position_number AS position_code,
                      p.display_name AS position_title,
                      s.id AS section_id,
                      s.section_code,
                      s.display_name AS section_title,
                      s.order_index AS section_order,
                      p.order_index AS position_order,
                      COUNT(DISTINCT o.id) AS objectives_total,
                      COUNT(DISTINCT o.id) FILTER (
                          WHERE ct.question_id IS NOT NULL
                      ) AS objectives_with_questions,
                      ARRAY_REMOVE(
                          ARRAY_AGG(DISTINCT ct.question_id), NULL
                      ) AS question_ids,
                      COALESCE((
                          SELECT SUM(sub_q.points)
                          FROM (
                              SELECT DISTINCT ct2.question_id, q2.points
                              FROM assessments.exam_question_curriculum_tags ct2
                              JOIN assessments.curriculum_objectives o2
                                  ON o2.id = ct2.curriculum_objective_id
                              JOIN assessments.exam_questions q2
                                  ON q2.question_id = ct2.question_id
                              WHERE o2.position_id = p.id
                          ) sub_q
                      ), 0) AS total_points
               FROM assessments.curriculum_sections s
               JOIN assessments.curriculum_positions p
                   ON p.section_id = s.id
               LEFT JOIN assessments.curriculum_objectives o
                   ON o.position_id = p.id
               LEFT JOIN assessments.exam_question_curriculum_tags ct
                   ON ct.curriculum_objective_id = o.id
               WHERE s.framework_id = %s
               GROUP BY p.id, p.position_number, p.display_name,
                        s.id, s.section_code, s.display_name,
                        s.order_index, p.order_index
               ORDER BY s.order_index, p.order_index""",
            [framework_id],
        )

    # ── Bulk Import ─────────────────────────────────────────────────

    @staticmethod
    def bulk_import_framework(data: dict) -> Dict[str, Any]:
        """Create entire hierarchy from nested dict.

        Expected shape:
        {
            "name": "...",
            "exam_type_key": "...",
            "version": "1.0",
            "metadata": {...},
            "sections": [
                {
                    "code": "T1", "title": "...", "order_index": 0,
                    "positions": [
                        {
                            "code": "T1.1", "title": "...",
                            "objectives": [
                                {"code": "T1.1.1", "description": "..."}
                            ]
                        }
                    ]
                }
            ]
        }
        """
        repo = CurriculumFrameworkRepository

        framework = repo.create_framework(data)
        framework_id = framework.get('id') or framework.get('framework_id')
        framework['framework_id'] = framework_id

        counts = {'sections': 0, 'positions': 0, 'objectives': 0}

        for s_idx, section_data in enumerate(data.get('sections', [])):
            section_data.setdefault('order_index', s_idx)
            section = repo.create_section(framework_id, section_data)
            counts['sections'] += 1

            for p_idx, pos_data in enumerate(
                section_data.get('positions', []),
            ):
                pos_data.setdefault('order_index', p_idx)
                position = repo.create_position(
                    section['id'], pos_data,
                )
                counts['positions'] += 1

                for o_idx, obj_data in enumerate(
                    pos_data.get('objectives', []),
                ):
                    obj_data.setdefault('order_index', o_idx)
                    repo.create_objective(
                        position['id'], obj_data,
                    )
                    counts['objectives'] += 1

        framework['import_counts'] = counts
        return framework

    # ── Full Tree Load ──────────────────────────────────────────────

    @staticmethod
    def load_framework_tree(
        framework_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Load framework with all nested children."""
        repo = CurriculumFrameworkRepository

        framework = repo.find_framework_by_id(framework_id)
        if not framework:
            return None

        sections = repo.find_sections_by_framework(framework_id)
        for section in sections:
            positions = repo.find_positions_by_section(
                section['section_id'],
            )
            for position in positions:
                position['objectives'] = repo.find_objectives_by_position(
                    position['position_id'],
                )
            section['positions'] = positions

        framework['sections'] = sections
        return framework

    # ── Exam Relevance Scores ──────────────────────────────────────

    @staticmethod
    def find_position_relevance_scores(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """Calculate exam relevance per curriculum position.

        Uses year-weighted scoring: newer exams count more.
        Weight = max(1.0 - (current_year - exam_year) * 0.1, 0.1)

        Also calculates trend by comparing recent (last 3 years)
        vs older appearance rates.

        Returns one row per position that has at least one tagged question.
        """
        return fetch_all(
            """WITH position_exam_data AS (
                   SELECT p.id AS position_id,
                          es.session_id,
                          es.year,
                          SUM(eq.points) AS exam_points
                   FROM assessments.curriculum_sections s
                   JOIN assessments.curriculum_positions p
                       ON p.section_id = s.id
                   JOIN assessments.curriculum_objectives o
                       ON o.position_id = p.id
                   JOIN assessments.exam_question_curriculum_tags ct
                       ON ct.curriculum_objective_id = o.id
                   JOIN assessments.exam_questions eq
                       ON eq.question_id = ct.question_id
                   JOIN assessments.exams e
                       ON e.exam_id = eq.exam_id
                   JOIN assessments.exam_sessions es
                       ON es.session_id = e.session_id
                   WHERE s.framework_id = %s
                     AND es.year IS NOT NULL
                   GROUP BY p.id, es.session_id, es.year
               ),
               total AS (
                   SELECT COUNT(DISTINCT session_id) AS total_exams,
                          MIN(year) AS min_year,
                          MAX(year) AS max_year
                   FROM position_exam_data
               )
               SELECT ped.position_id,
                      COUNT(DISTINCT ped.session_id) AS exam_count,
                      t.total_exams,
                      ROUND(
                          COUNT(DISTINCT ped.session_id)::numeric
                          / NULLIF(t.total_exams, 0), 2
                      ) AS appearance_rate,
                      ROUND(SUM(
                          ped.exam_points
                          * GREATEST(
                              1.0 - (t.max_year - ped.year) * 0.1,
                              0.1
                          )
                      )::numeric, 1) AS weighted_score,
                      ROUND(AVG(ped.exam_points)::numeric, 1)
                          AS avg_points_per_exam,
                      COUNT(DISTINCT ped.session_id) FILTER (
                          WHERE ped.year >= t.max_year - 2
                      ) AS recent_count,
                      COUNT(DISTINCT ped.session_id) FILTER (
                          WHERE ped.year < t.max_year - 2
                      ) AS older_count
               FROM position_exam_data ped
               CROSS JOIN total t
               GROUP BY ped.position_id, t.total_exams,
                        t.min_year, t.max_year
               ORDER BY weighted_score DESC""",
            [framework_id],
        )

    @staticmethod
    def find_position_exam_history(framework_id: int) -> List[Dict[str, Any]]:
        """Get exam appearance history per position for prognosis."""
        return fetch_all(
            """SELECT p.id AS position_id,
                      p.position_number AS position_code,
                      p.display_name AS position_title,
                      s.section_code,
                      ARRAY_AGG(DISTINCT e.year) FILTER (WHERE e.year IS NOT NULL) AS years,
                      ARRAY_AGG(DISTINCT e.semester) FILTER (WHERE e.semester IS NOT NULL) AS semesters,
                      COUNT(DISTINCT ct.question_id) AS total_questions
               FROM assessments.curriculum_sections s
               JOIN assessments.curriculum_positions p ON p.section_id = s.id
               LEFT JOIN assessments.curriculum_objectives o ON o.position_id = p.id
               LEFT JOIN assessments.exam_question_curriculum_tags ct ON ct.curriculum_objective_id = o.id
               LEFT JOIN assessments.exam_questions q ON q.question_id = ct.question_id
               LEFT JOIN assessments.exams e ON e.exam_id = q.exam_id
               WHERE s.framework_id = %s
               GROUP BY p.id, p.position_number, p.display_name, s.section_code
               ORDER BY s.order_index, p.order_index""",
            [framework_id],
        )
