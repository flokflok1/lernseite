"""
Prognosis Service

Orchestrates exam prognosis predictions using domain logic and repository data.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PrognosisService:
    """Application service for exam prognosis predictions."""

    @staticmethod
    def predict_all(framework_id: int) -> List[Dict[str, Any]]:
        """Predict probability of positions appearing in next exam.

        Args:
            framework_id: Curriculum framework ID.

        Returns:
            List of position predictions sorted by probability desc.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )
        from app.domain.services.exam_prognosis import predict_all_positions

        history = CurriculumFrameworkRepository.find_position_exam_history(
            framework_id,
        )

        # Transform DB rows to domain input format
        positions_history = []
        for row in history:
            years = row.get('years') or []
            semesters = row.get('semesters') or []
            positions_history.append({
                'position_id': row['position_id'],
                'position_code': f"{row.get('section_code', '?')}.{row['position_code']}",
                'position_title': row.get('position_title', ''),
                'years': [int(y) for y in years if y],
                'semesters': [str(s) for s in semesters if s],
                'total_questions': row.get('total_questions', 0),
            })

        results = predict_all_positions(positions_history)
        logger.info(
            "Prognosis for framework %d: %d positions predicted",
            framework_id, len(results),
        )
        return results

    @staticmethod
    def predict_for_position(
        framework_id: int, position_id: int,
    ) -> Dict[str, Any]:
        """Predict probability for a single position.

        Args:
            framework_id: Curriculum framework ID.
            position_id: Position ID.

        Returns:
            Prediction dict for the position.

        Raises:
            ValueError: If position not found.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )
        from app.domain.services.exam_prognosis import predict_next_exam

        history = CurriculumFrameworkRepository.find_position_exam_history(
            framework_id,
        )
        row = next(
            (r for r in history if r['position_id'] == position_id),
            None,
        )
        if not row:
            raise ValueError(
                f"Position {position_id} not found in framework {framework_id}",
            )

        years = row.get('years') or []
        semesters = row.get('semesters') or []
        pos = {
            'position_id': row['position_id'],
            'position_code': f"{row.get('section_code', '?')}.{row['position_code']}",
            'position_title': row.get('position_title', ''),
            'years': [int(y) for y in years if y],
            'semesters': [str(s) for s in semesters if s],
            'total_questions': row.get('total_questions', 0),
        }

        prediction = predict_next_exam(pos)
        prediction.update({
            'position_id': pos['position_id'],
            'position_code': pos['position_code'],
            'position_title': pos['position_title'],
            'total_questions': pos['total_questions'],
        })
        return prediction
