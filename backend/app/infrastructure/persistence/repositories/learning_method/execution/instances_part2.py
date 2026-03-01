"""
LernsystemX - Learning Method Instance Repository (Part 2)

Statistics, runner session support, and helper methods for learning method instances.

Split from instances.py to comply with Quality Gate G01 (max 500 LOC per file).
"""

from typing import Dict, Any, Optional, List
from psycopg.rows import dict_row

from app.core.bootstrap import extensions
from app.infrastructure.persistence.repositories.learning_method.execution.instances import (
    LearningMethodInstanceRepository,
)


class LearningMethodInstanceStatisticsRepository(LearningMethodInstanceRepository):
    """
    Extended repository for learning method instance statistics,
    runner session support, and helper operations.

    Inherits core CRUD and bulk operations from LearningMethodInstanceRepository.
    """

    # =========================================================================
    # STATISTICS
    # =========================================================================

    @classmethod
    def get_statistics_by_chapter(cls, chapter_id: str) -> Dict[str, Any]:
        """
        Holt Statistiken für Learning Methods eines Kapitels.

        Args:
            chapter_id: UUID des Kapitels

        Returns:
            Statistik-Dict
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) as total_methods,
                        COUNT(*) FILTER (WHERE published = TRUE) as published_count,
                        COUNT(DISTINCT method_type) as unique_types,
                        COALESCE(SUM(duration_minutes), 0) as total_duration,
                        COUNT(*) FILTER (WHERE difficulty = 'easy') as easy_count,
                        COUNT(*) FILTER (WHERE difficulty = 'medium') as medium_count,
                        COUNT(*) FILTER (WHERE difficulty = 'hard') as hard_count,
                        COUNT(*) FILTER (WHERE tier = 'basic') as basic_count,
                        COUNT(*) FILTER (WHERE tier = 'premium') as premium_count,
                        COUNT(*) FILTER (WHERE tier = 'pro') as pro_count
                    FROM learning_methods
                    WHERE chapter_id = %s
                """, (chapter_id,))

                return cur.fetchone()

    @classmethod
    def get_method_type_distribution(cls, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Holt die Verteilung der Lernmethoden-Typen.

        Args:
            course_id: Optional - Filter auf einen Kurs

        Returns:
            Liste mit method_type und count
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if course_id:
                    cur.execute("""
                        SELECT
                            lm.method_type,
                            COUNT(*) as count
                        FROM learning_methods lm
                        JOIN courses.chapters ch ON lm.chapter_id = ch.chapter_id
                        WHERE ch.course_id = %s
                        GROUP BY lm.method_type
                        ORDER BY lm.method_type
                    """, (course_id,))
                else:
                    cur.execute("""
                        SELECT
                            method_type,
                            COUNT(*) as count
                        FROM learning_methods
                        GROUP BY method_type
                        ORDER BY method_type
                    """)

                return cur.fetchall()

    # =========================================================================
    # RUNNER SESSION SUPPORT
    # =========================================================================

    @classmethod
    def find_for_runner(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """
        Find learning method instance with runner-relevant data.

        Returns data needed for runner session initialization, including
        course context via lesson/chapter hierarchy.

        Args:
            method_id: UUID of the learning method instance

        Returns:
            Dict with method_id, lesson_id, method_type, default_mode_id,
            time_limit_seconds, config, chapter_id, course_id
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        lmi.method_id,
                        lmi.lesson_id,
                        lmi.method_type,
                        lmi.default_mode_id,
                        lmi.time_limit_seconds,
                        lmi.config,
                        l.chapter_id,
                        c.course_id
                    FROM learning_methods.learning_method_instances lmi
                    LEFT JOIN courses.lessons l ON lmi.lesson_id = l.lesson_id
                    LEFT JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
                    LEFT JOIN courses.courses c ON ch.course_id = c.course_id
                    WHERE lmi.method_id = %s
                """, (method_id,))
                return cur.fetchone()

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    @classmethod
    def publish(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Veröffentlicht eine Learning Method Instance."""
        return cls.update(method_id, {'published': True})

    @classmethod
    def unpublish(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Zieht die Veröffentlichung einer Learning Method Instance zurück."""
        return cls.update(method_id, {'published': False})

    @classmethod
    def copy_to_chapter(cls, method_id: str, target_chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Kopiert eine Learning Method Instance in ein anderes Kapitel.

        Args:
            method_id: UUID der zu kopierenden Instance
            target_chapter_id: UUID des Ziel-Kapitels

        Returns:
            Kopierte Instance oder None
        """
        original = cls.find_by_id(method_id)
        if not original:
            return None

        copy_data = {
            'chapter_id': target_chapter_id,
            'method_type': original['method_type'],
            'title': f"{original['title']} (Kopie)",
            'instructions': original.get('instructions'),
            'data': original.get('data', {}),
            'solution': original.get('solution'),
            'tier': original['tier'],
            'duration_minutes': original.get('duration_minutes'),
            'difficulty': original.get('difficulty'),
            'order_index': 0,  # Am Anfang einfügen
            'published': False  # Kopie ist nicht veröffentlicht
        }

        return cls.create(copy_data)
