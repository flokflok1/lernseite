"""
Performance Stats Repository

Anonymized aggregate performance statistics for peer comparison.
Privacy: Only aggregates, never individual user data. Min 5 users per position.
"""

import logging
from typing import Dict, Any, List

from app.infrastructure.persistence.database.connection import fetch_all

logger = logging.getLogger(__name__)


class PerformanceStatsRepository:
    """Anonymized performance aggregates for peer comparison."""

    @staticmethod
    def get_position_aggregates(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """Get anonymized performance aggregates per position.

        Only includes positions where >=5 users have attempted questions.
        Returns AVG, median (P50), P25, P75 of accuracy.
        """
        return fetch_all(
            """SELECT p.id AS position_id,
                      p.position_number AS position_code,
                      COUNT(DISTINCT ua.user_id) AS user_count,
                      ROUND(AVG(
                          CASE WHEN ua.is_correct THEN 100.0 ELSE 0.0 END
                      ), 1) AS avg_accuracy,
                      ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
                          ORDER BY CASE WHEN ua.is_correct THEN 100.0 ELSE 0.0 END
                      ), 1) AS median_accuracy,
                      ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (
                          ORDER BY CASE WHEN ua.is_correct THEN 100.0 ELSE 0.0 END
                      ), 1) AS p25_accuracy,
                      ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (
                          ORDER BY CASE WHEN ua.is_correct THEN 100.0 ELSE 0.0 END
                      ), 1) AS p75_accuracy
               FROM assessments.curriculum_sections s
               JOIN assessments.curriculum_positions p ON p.section_id = s.id
               JOIN assessments.curriculum_objectives o ON o.position_id = p.id
               JOIN assessments.exam_question_curriculum_tags ct
                   ON ct.curriculum_objective_id = o.id
               JOIN assessments.user_exam_answers ua
                   ON ua.question_id = ct.question_id
               WHERE s.framework_id = %s
               GROUP BY p.id, p.position_number
               HAVING COUNT(DISTINCT ua.user_id) >= 5
               ORDER BY p.position_number""",
            [framework_id],
        )

    @staticmethod
    def get_user_percentile(
        user_id: str, framework_id: int,
    ) -> List[Dict[str, Any]]:
        """Get user's percentile rank per position.

        Uses PERCENT_RANK to compute where the user stands relative to peers.
        Only positions with >=5 users are included.
        """
        return fetch_all(
            """WITH position_scores AS (
                   SELECT ua.user_id,
                          p.id AS position_id,
                          ROUND(AVG(
                              CASE WHEN ua.is_correct THEN 100.0 ELSE 0.0 END
                          ), 1) AS user_accuracy
                   FROM assessments.curriculum_sections s
                   JOIN assessments.curriculum_positions p ON p.section_id = s.id
                   JOIN assessments.curriculum_objectives o ON o.position_id = p.id
                   JOIN assessments.exam_question_curriculum_tags ct
                       ON ct.curriculum_objective_id = o.id
                   JOIN assessments.user_exam_answers ua
                       ON ua.question_id = ct.question_id
                   WHERE s.framework_id = %s
                   GROUP BY ua.user_id, p.id
               ),
               ranked AS (
                   SELECT position_id,
                          user_id,
                          user_accuracy,
                          ROUND(PERCENT_RANK() OVER (
                              PARTITION BY position_id
                              ORDER BY user_accuracy
                          ) * 100, 0) AS percentile
                   FROM position_scores
               ),
               position_counts AS (
                   SELECT position_id, COUNT(*) AS user_count
                   FROM position_scores
                   GROUP BY position_id
                   HAVING COUNT(*) >= 5
               )
               SELECT r.position_id,
                      r.user_accuracy,
                      r.percentile
               FROM ranked r
               JOIN position_counts pc ON pc.position_id = r.position_id
               WHERE r.user_id = %s""",
            [framework_id, user_id],
        )
