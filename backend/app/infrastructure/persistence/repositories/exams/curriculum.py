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
            """SELECT f.*,
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
        return fetch_one(
            "SELECT * FROM assessments.curriculum_frameworks WHERE id = %s",
            [framework_id],
        )

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
        return insert_returning(
            'assessments.curriculum_sections',
            {
                'framework_id': framework_id,
                'section_code': data.get('section_code') or data.get('code', ''),
                'display_name': json.dumps(data.get('title', '')) if isinstance(data.get('title'), str) else json.dumps(data.get('title', {})),
                'order_index': data.get('order_index', 0),
            },
        )

    @staticmethod
    def find_sections_by_framework(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """All sections for a framework, ordered by order_index."""
        return fetch_all(
            """SELECT * FROM assessments.curriculum_sections
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
        return insert_returning(
            'assessments.curriculum_positions',
            {
                'section_id': section_id,
                'position_number': data.get('position_number') or data.get('code', ''),
                'display_name': json.dumps(data.get('title', '')) if isinstance(data.get('title'), str) else json.dumps(data.get('title', {})),
                'order_index': data.get('order_index', 0),
            },
        )

    @staticmethod
    def find_positions_by_section(
        section_id: int,
    ) -> List[Dict[str, Any]]:
        """All positions for a section, ordered by order_index."""
        return fetch_all(
            """SELECT * FROM assessments.curriculum_positions
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
            """SELECT * FROM assessments.curriculum_objectives
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
        framework_id = framework['id']

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
                section['id'],
            )
            for position in positions:
                position['objectives'] = repo.find_objectives_by_position(
                    position['id'],
                )
            section['positions'] = positions

        framework['sections'] = sections
        return framework
