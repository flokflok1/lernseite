"""
Exam Context Repository

Database access for exam context detection:
- User profile loading (profession, region, target exam)
- Course metadata loading (profession_tag, exam_level, detected_topics)
- Exam-relevant course files
- User learning analytics (topic scores, strengths, weaknesses)
"""

from typing import Dict, Optional, List

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class ExamContextRepository:
    """Repository for exam context detection queries."""

    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict]:
        """
        Load user profile with exam-relevant fields.

        Args:
            user_id: User UUID

        Returns:
            User profile row or empty dict-like None
        """
        query = """
            SELECT
                up.profession,
                up.profession_detail,
                up.training_year,
                up.target_exam,
                up.exam_date,
                up.region,
                up.ihk,
                up.detected_profession,
                up.detected_level,
                up.detection_confidence,
                up.preferred_difficulty,
                u.display_name,
                u.email
            FROM user_profiles up
            RIGHT JOIN users u ON u.user_id = up.user_id
            WHERE u.user_id = %s
        """
        return fetch_one(query, (user_id,))

    @staticmethod
    def get_course_metadata(course_id: str) -> Optional[Dict]:
        """
        Load course metadata for exam context detection.

        Args:
            course_id: Course UUID

        Returns:
            Course row or None
        """
        query = """
            SELECT
                course_id,
                title,
                description,
                profession_tag,
                exam_level,
                exam_region,
                ihk_standard,
                detected_exam_type,
                detected_topics,
                exam_metadata,
                tags
            FROM courses
            WHERE course_id = %s
        """
        return fetch_one(query, (course_id,))

    @staticmethod
    def get_exam_relevant_files(course_id: str) -> List[Dict]:
        """
        Load exam-relevant files for a course.

        Args:
            course_id: Course UUID

        Returns:
            List of file rows (max 20)
        """
        query = """
            SELECT
                file_id,
                original_filename,
                file_type,
                file_size,
                is_exam_relevant,
                exam_topics,
                content_summary,
                analyzed_at,
                created_at
            FROM course_files
            WHERE course_id = %s
              AND (
                  is_exam_relevant = TRUE
                  OR file_type IN ('application/pdf', 'text/plain')
                  OR original_filename ILIKE '%%prüfung%%'
                  OR original_filename ILIKE '%%exam%%'
                  OR original_filename ILIKE '%%ap1%%'
                  OR original_filename ILIKE '%%ap2%%'
              )
            ORDER BY is_exam_relevant DESC, created_at DESC
            LIMIT 20
        """
        return fetch_all(query, (course_id,))

    @staticmethod
    def get_learning_analytics(
        user_id: str,
        course_id: str
    ) -> List[Dict]:
        """
        Load learning analytics for a user in a course.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            List of analytics rows ordered by attempts
        """
        query = """
            SELECT
                topic,
                topic_category,
                score_avg,
                score_best,
                score_trend,
                attempts,
                correct_count,
                incorrect_count,
                common_mistakes,
                weak_subtopics,
                strong_subtopics,
                last_attempt
            FROM user_learning_analytics
            WHERE user_id = %s
              AND (course_id = %s OR course_id IS NULL)
            ORDER BY attempts DESC
        """
        return fetch_all(query, (user_id, course_id))
