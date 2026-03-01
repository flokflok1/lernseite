"""
Course authoring session finalization.

Split from session.py to stay under 500 LOC (Quality Gate G01).
"""

import logging
from typing import Dict, Any, List

from app.application.services.content.course_authoring.exceptions import CourseAuthoringError
from app.application.services.content.course_authoring.database import DatabaseOperations

logger = logging.getLogger(__name__)


class FinalizeMixin:
    """Finalization logic for CourseAuthoringService."""

    def finalize_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Finalisiert eine Session und erstellt echte DB-Entities.

        All DB writes run in a single transaction — on any error,
        all changes are rolled back (no orphaned chapters/lessons).

        Args:
            session_id: Session UUID
            user_id: User UUID

        Returns:
            Dict mit created IDs und Stats
        """
        from app.infrastructure.persistence.database.connection import get_connection
        from psycopg.rows import dict_row

        session = self.get_session(session_id, user_id)

        if session['status'] != 'active':
            raise CourseAuthoringError(f"Session is not active: {session['status']}")

        draft_structure = session['draft_structure']
        course_id = session['course_id']

        created_chapters: List[str] = []
        created_lessons: List[str] = []
        created_methods: List[str] = []

        try:
            with get_connection() as conn:
                # Atomic CAS: claim the session for finalization.
                # Prevents double-finalize race condition.
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("""
                        UPDATE courses.course_authoring_sessions
                        SET status = 'finalizing'
                        WHERE session_id = %s AND status = 'active'
                        RETURNING session_id
                    """, (session_id,))
                    if cur.fetchone() is None:
                        raise CourseAuthoringError(
                            "Session was already finalized or is no longer active"
                        )

                # Kapitel erstellen/updaten
                for chapter_draft in draft_structure.get('chapters', []):
                    chapter_id = DatabaseOperations.create_or_update_chapter(
                        course_id,
                        chapter_draft,
                        user_id,
                        conn=conn
                    )
                    created_chapters.append(chapter_id)

                    # Lektionen erstellen/updaten
                    for lesson_draft in chapter_draft.get('lessons', []):
                        lesson_id = DatabaseOperations.create_or_update_lesson(
                            chapter_id,
                            lesson_draft,
                            user_id,
                            conn=conn
                        )
                        created_lessons.append(lesson_id)

                        # Für bestehende Lektionen: alte Methoden löschen
                        # die nicht mehr im Draft stehen (KI hat sie entfernt)
                        # WICHTIG: Nur synchronisieren wenn der Draft explizit
                        # Methoden enthält. Leere methods=[] bei reinen Text-Updates
                        # darf NICHT alle bestehenden Methoden löschen.
                        draft_methods = lesson_draft.get('methods', [])
                        if lesson_draft.get('existing_id') and draft_methods:
                            DatabaseOperations.sync_methods_for_lesson(
                                lesson_draft['existing_id'],
                                draft_methods,
                                conn=conn
                            )

                        # Neue Methoden erstellen (nur die im Draft)
                        for method_draft in lesson_draft.get('methods', []):
                            # Methoden mit existing_id überspringen —
                            # die existieren bereits in der DB
                            if method_draft.get('existing_id'):
                                continue
                            method_id = DatabaseOperations.create_method(
                                lesson_id,
                                chapter_id,
                                method_draft,
                                user_id,
                                conn=conn
                            )
                            created_methods.append(method_id)

                # Mark as finalized (same transaction — commits together)
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("""
                        UPDATE courses.course_authoring_sessions
                        SET status = 'finalized', finalized_at = NOW()
                        WHERE session_id = %s
                    """, (session_id,))

            logger.info(
                f"Finalized session {session_id}: {len(created_chapters)} chapters, "
                f"{len(created_lessons)} lessons, {len(created_methods)} methods"
            )

            return {
                'status': 'ok',
                'created_chapter_ids': created_chapters,
                'created_lesson_ids': created_lessons,
                'created_method_ids': created_methods,
                'stats': {
                    'chapters': len(created_chapters),
                    'lessons': len(created_lessons),
                    'methods': len(created_methods)
                }
            }

        except CourseAuthoringError:
            raise
        except Exception as e:
            logger.error(f"Error finalizing session: {str(e)}", exc_info=True)
            raise CourseAuthoringError("Finalize failed due to an internal error")
