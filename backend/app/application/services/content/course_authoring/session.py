"""
Course authoring session management and main service class.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.infrastructure.persistence.repositories.authoring.sessions import CourseAuthoringSessionRepository
from app.application.services.ai.adapter import AIAdapter, AIProviderError
from app.application.services.content.course_authoring.exceptions import CourseAuthoringError
from app.application.services.content.course_authoring.database import DatabaseOperations
from app.application.services.content.course_authoring.prompts import PromptGenerator
from app.application.services.content.course_authoring.helpers import DataHelpers, ActivityLogGenerator
from app.application.services.content.course_authoring.validation import OperationValidator
from app.application.services.content.course_authoring.operations import StructureOperations

logger = logging.getLogger(__name__)


class CourseAuthoringSession:
    """Represents a single course authoring session."""

    def __init__(self, session_data: Dict[str, Any]):
        """
        Initialize session from database data.

        Args:
            session_data: Session record from database
        """
        self.session_id = str(session_data['session_id'])
        self.course_id = str(session_data['course_id'])
        self.course_title = session_data.get('course_title', '')
        self.draft_structure = (
            session_data['draft_structure']
            if isinstance(session_data['draft_structure'], dict)
            else json.loads(session_data['draft_structure'])
        )
        self.chat_history = (
            session_data['chat_history']
            if isinstance(session_data['chat_history'], list)
            else json.loads(session_data['chat_history'] or '[]')
        )
        self.file_context = (
            session_data['file_context']
            if isinstance(session_data['file_context'], list)
            else json.loads(session_data['file_context'] or '[]')
        )
        self.status = session_data['status']
        self.total_tokens_used = session_data.get('total_tokens_used', 0)
        self.total_operations = session_data.get('total_operations', 0)
        self.model_profile = session_data.get('model_profile', '')
        self.created_at = session_data['created_at']
        self.updated_at = session_data['updated_at']

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'session_id': self.session_id,
            'course_id': self.course_id,
            'course_title': self.course_title,
            'draft_structure': self.draft_structure,
            'chat_history': self.chat_history,
            'file_context': self.file_context,
            'status': self.status,
            'total_tokens_used': self.total_tokens_used,
            'total_operations': self.total_operations,
            'model_profile': self.model_profile,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CourseAuthoringService:
    """
    Service für chat-basiertes Kurs-Authoring mit persistenten Sessions.

    Usage:
        >>> service = CourseAuthoringService()
        >>> session = service.create_session(user_id, course_id)
        >>> result = service.apply_chat_message(session['session_id'], user_id, "Erstelle 3 Kapitel")
        >>> service.finalize_session(session['session_id'], user_id)
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize course authoring service.

        Args:
            provider: AI provider name (resolved from DB default if None)
            model: AI model name (resolved from DB default if None)
        """
        if provider and model:
            self.provider = provider
            self.model = model
        else:
            self.provider, self.model = self._resolve_default_model()

    @staticmethod
    def get_available_models() -> List[Dict[str, Any]]:
        """Returns active providers (with API key) and their active chat models."""
        from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
        from app.infrastructure.persistence.repositories.ai_models.query import AIModelsQueryRepository

        providers = AIProviderRepository.get_all(include_inactive=False)
        models = AIModelsQueryRepository.get_by_category('chat', active_only=True)

        result = []
        for p in providers:
            if not p.get('has_api_key'):
                continue
            provider_models = [
                {
                    'model_id': m['model_id'],
                    'model_name': m['model_name'],
                    'display_name': m.get('display_name') or m['model_name'],
                    'is_default': m.get('is_default', False),
                    'context_window': m.get('context_window'),
                    'cost_level': m.get('cost_level'),
                }
                for m in models if m.get('provider_name') == p['name']
            ]
            if not provider_models:
                continue
            result.append({
                'provider_name': p['name'],
                'display_name': p['display_name'],
                'models': provider_models,
            })
        return result

    @staticmethod
    def validate_model_selection(provider_name: str, model_name: str) -> None:
        """Validates that a provider+model combination is active. Raises on invalid."""
        from app.infrastructure.persistence.repositories.ai_models.query import AIModelsQueryRepository

        model_record = AIModelsQueryRepository.get_by_name(model_name, provider_name)
        if not model_record or not model_record.get('active'):
            raise CourseAuthoringError(
                f"Model '{model_name}' for provider '{provider_name}' not found or inactive"
            )

    @staticmethod
    def _resolve_default_model() -> tuple:
        """Resolve default AI model from admin settings (G07 compliant)."""
        try:
            from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
            default = AIModelsRepository.get_default_model()
            if default:
                return (
                    default.get('provider_name', 'openai'),
                    default.get('model_name', 'gpt-4o-mini'),
                )
        except Exception:
            pass
        return ('openai', 'gpt-4o-mini')

    def create_session(
        self,
        user_id: str,
        course_id: str,
        model_profile: str = "anthropic-claude-sonnet"
    ) -> Dict[str, Any]:
        """
        Erstellt eine neue Authoring-Session für einen Kurs.

        Wenn der Kurs bereits Kapitel hat, werden diese in draft_structure übernommen.

        Args:
            user_id: User UUID
            course_id: Course UUID
            model_profile: KI-Modell-Profil

        Returns:
            Dict mit session_id und draft_structure
        """
        # Prüfe ob Kurs existiert und User Zugriff hat
        course = DatabaseOperations.get_course(course_id)
        if not course:
            raise CourseAuthoringError(f"Course not found: {course_id}")

        # Prüfe User-Berechtigung
        if not DatabaseOperations.check_user_access(user_id, course_id):
            raise CourseAuthoringError("User has no access to this course")

        # Lade bestehende Struktur aus DB
        draft_structure = DatabaseOperations.load_existing_structure(course_id, course)

        # Session erstellen
        session_id = str(uuid.uuid4())

        result = CourseAuthoringSessionRepository.create_session(
            session_id=session_id,
            course_id=course_id,
            user_id=user_id,
            model_profile=model_profile,
            draft_structure_json=json.dumps(draft_structure),
            chat_history_json=json.dumps([])
        )

        if not result:
            raise CourseAuthoringError("Failed to create session")

        logger.info(f"Created course authoring session {session_id} for course {course_id}")

        return {
            'session_id': str(result['session_id']),
            'course_id': str(result['course_id']),
            'draft_structure': draft_structure,
            'status': result['status'],
            'created_at': result['created_at'].isoformat() if result['created_at'] else None
        }

    def get_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Lädt eine bestehende Session.

        Args:
            session_id: Session UUID
            user_id: User UUID (für Zugriffsprüfung)

        Returns:
            Session-Daten mit draft_structure
        """
        result = CourseAuthoringSessionRepository.get_session_with_course(session_id)

        if not result:
            raise CourseAuthoringError(f"Session not found: {session_id}")

        # Prüfe Zugriff
        if str(result['created_by']) != user_id:
            if not DatabaseOperations.check_user_access(user_id, str(result['course_id'])):
                raise CourseAuthoringError("User has no access to this session")

        session = CourseAuthoringSession(result)
        return session.to_dict()

    def apply_chat_message(
        self,
        session_id: str,
        user_id: str,
        message: str,
        mode: Optional[str] = None,
        file_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet eine Chat-Nachricht und aktualisiert draft_structure.

        Args:
            session_id: Session UUID
            user_id: User UUID
            message: User-Nachricht
            mode: Optional - 'structure', 'lesson', 'method', 'exam'
            file_ids: Optional - Dateien für Kontext

        Returns:
            Dict mit assistant_message, updated draft_structure, operations_applied
        """
        # Session laden
        session = self.get_session(session_id, user_id)

        if session['status'] != 'active':
            raise CourseAuthoringError(f"Session is not active: {session['status']}")

        draft_structure = session['draft_structure']
        chat_history = session['chat_history']

        # File context laden falls angegeben
        file_context_text = ""
        if file_ids:
            # Validate file_ids belong to this session (prevent cross-session injection)
            from app.infrastructure.persistence.repositories.authoring.files import AuthoringFilesRepository
            session_files = AuthoringFilesRepository.get_files_by_session(session_id)
            valid_ids = {str(f['file_id']) for f in session_files}
            invalid = [fid for fid in file_ids if str(fid) not in valid_ids]
            if invalid:
                raise CourseAuthoringError("One or more file_ids do not belong to this session")
            file_context_text = DataHelpers.extract_file_context(file_ids)

        # Kurs-Info laden
        course_info = DatabaseOperations.get_course_info(session['course_id'])

        # Chat-History für Kontext (letzte 10 Nachrichten)
        history_context = DataHelpers.format_history_for_prompt(chat_history[-10:])

        # KI-Request bauen
        system_prompt = PromptGenerator.get_system_prompt(mode)
        user_prompt = PromptGenerator.build_user_prompt(
            course_info=course_info,
            draft_structure=draft_structure,
            user_message=message,
            file_context=file_context_text,
            history=history_context,
            mode=mode
        )

        # User-Message zur History
        chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.utcnow().isoformat()
        })

        try:
            # KI aufrufen
            adapter = AIAdapter(provider=self.provider, model=self.model)
            result = adapter.send_messages(
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            output_text = result.get('output_text', '')
            tokens_used = result.get('total_tokens', 0)

            # Response parsen
            assistant_message, structure_patch = DataHelpers.parse_ai_response(output_text)

            # Check for parse errors
            parse_error = None
            if structure_patch and '_parse_error' in structure_patch:
                parse_error = structure_patch['_parse_error']
                logger.warning(f"Session {session_id}: JSON parse error: {parse_error}")
                structure_patch = None

            # Patch validieren und anwenden
            operations_applied = []
            failed_ops = []
            validated_ops = []
            if structure_patch and structure_patch.get('operations'):
                operations = structure_patch['operations']
                validated_ops = OperationValidator.validate_operations(operations)
                draft_structure, operations_applied, failed_ops = StructureOperations.apply_operations(
                    draft_structure,
                    validated_ops
                )

            if failed_ops:
                logger.warning(
                    f"Session {session_id}: {len(failed_ops)} operations failed: "
                    f"{[f['op'] for f in failed_ops]}"
                )

            # Activity Log generieren
            if operations_applied:
                activity_entry = ActivityLogGenerator.generate_entry(
                    validated_ops,
                    draft_structure
                )
                if 'activity_log' not in draft_structure:
                    draft_structure['activity_log'] = []
                # Neuste Einträge am Anfang
                draft_structure['activity_log'].insert(0, activity_entry)
                # Max 50 Einträge behalten
                draft_structure['activity_log'] = draft_structure['activity_log'][:50]

            # Assistant-Message zur History
            chat_history.append({
                'role': 'assistant',
                'content': assistant_message,
                'timestamp': datetime.utcnow().isoformat(),
                'operations': operations_applied
            })

            # Session updaten
            DatabaseOperations.update_session(
                session_id,
                draft_structure=draft_structure,
                chat_history=chat_history,
                file_context=file_ids or session['file_context'],
                tokens_delta=tokens_used,
                operations_delta=len(operations_applied)
            )

            logger.info(f"Applied {len(operations_applied)} operations to session {session_id}")

            result = {
                'assistant_message': assistant_message,
                'draft_structure': draft_structure,
                'operations_applied': operations_applied,
                'tokens_used': tokens_used
            }
            if failed_ops:
                result['operations_failed'] = failed_ops
            if parse_error:
                result['parse_error'] = parse_error
            return result

        except AIProviderError as e:
            logger.error(f"AI provider error: {str(e)}")
            raise CourseAuthoringError("AI generation failed. Please try again.")

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

        created_chapters = []
        created_lessons = []
        created_methods = []

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
                        if lesson_draft.get('existing_id'):
                            DatabaseOperations.sync_methods_for_lesson(
                                lesson_draft['existing_id'],
                                lesson_draft.get('methods', []),
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
