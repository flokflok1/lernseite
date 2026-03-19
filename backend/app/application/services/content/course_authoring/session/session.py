"""
Course authoring session management and main service class.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.infrastructure.persistence.repositories.authoring.sessions.sessions import CourseAuthoringSessionRepository
from app.application.services.ai.adapter import AIAdapter, AIProviderError
from app.application.services.content.course_authoring.exceptions import CourseAuthoringError
from app.application.services.content.course_authoring.database import DatabaseOperations
from app.application.services.content.course_authoring.generation.prompts import PromptGenerator
from app.application.services.content.course_authoring.helpers import DataHelpers, ActivityLogGenerator
from app.application.services.content.course_authoring.validation.validation import OperationValidator
from app.application.services.content.course_authoring.operations import StructureOperations
from app.application.services.content.course_authoring.generation.tool_processor import ToolCallProcessor
from app.application.services.content.course_authoring.validation.scope_guard import ScopeGuard
from app.domain.ai.tool_definitions import AUTHORING_TOOLS
from app.domain.ai.scope import OperationScope
from app.application.services.content.course_authoring.session.session_finalize import FinalizeMixin

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


class CourseAuthoringService(FinalizeMixin):
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
        from app.infrastructure.persistence.repositories.ai.config.providers import AIProviderRepository
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
        """Resolve default AI model from task defaults (G07 compliant)."""
        from app.infrastructure.ai.task_model_resolver import resolve_model_for_task
        return resolve_model_for_task('content')

    def create_session(
        self,
        user_id: str,
        course_id: str,
        model_profile: str = "anthropic-claude-sonnet",
        initial_chat_history: Optional[List] = None
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
            chat_history_json=json.dumps(initial_chat_history or [])
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
        file_ids: Optional[List[str]] = None,
        focus_chapter_id: Optional[str] = None,
        focus_lesson_id: Optional[str] = None,
        prompt_code: Optional[str] = None,
        quality_level: str = 'standard'
    ) -> Dict[str, Any]:
        """
        Verarbeitet eine Chat-Nachricht und aktualisiert draft_structure.

        Uses Tool Calling (Level 2) for structured AI responses when supported.
        Falls back to text-based JSON parsing for providers without tool calling.

        Args:
            session_id: Session UUID
            user_id: User UUID
            message: User-Nachricht
            mode: Optional - 'structure', 'lesson', 'method', 'exam'
            file_ids: Optional - Dateien für Kontext
            focus_chapter_id: Optional - Fokussiertes Kapitel (Scope Guard)
            focus_lesson_id: Optional - Fokussierte Lektion (Scope Guard)

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
            from app.infrastructure.persistence.repositories.authoring.files import AuthoringFilesRepository
            session_files = AuthoringFilesRepository.get_files_by_session(session_id)
            valid_ids = {str(f['file_id']) for f in session_files}
            invalid = [fid for fid in file_ids if str(fid) not in valid_ids]
            if invalid:
                raise CourseAuthoringError("One or more file_ids do not belong to this session")
            file_context_text = DataHelpers.extract_file_context(file_ids)

        # Kurs-Info laden
        course_info = DatabaseOperations.get_course_info(session['course_id'])

        # Quality Profile laden
        from app.application.services.content.course_authoring.quality_profile import (
            get_quality_profile,
        )
        from app.application.services.content.course_authoring.token_budget import TokenBudget
        from app.application.services.content.course_authoring.content_validator import ContentValidator
        from app.application.services.content.course_authoring.pipeline import GenerationPipeline

        profile = get_quality_profile(quality_level)

        # Chat-History für Kontext (profile-driven limits)
        history_context = DataHelpers.format_history_for_prompt(
            chat_history[-profile.history_message_limit:],
            max_chars=profile.history_char_limit,
            message_char_limit=profile.history_message_char_limit
        )

        # KI-Request bauen (DB-Template mit Fallback auf hardcoded)
        system_prompt = self._resolve_system_prompt(prompt_code, mode)
        user_prompt = PromptGenerator.build_user_prompt(
            course_info=course_info,
            draft_structure=draft_structure,
            user_message=message,
            file_context=file_context_text,
            history=history_context,
            mode=mode
        )

        # Scope bestimmen (Security)
        scope = self._build_scope(
            session['course_id'], focus_chapter_id, focus_lesson_id
        )

        # User-Message zur History
        chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.utcnow().isoformat()
        })

        try:
            adapter = AIAdapter(provider=self.provider, model=self.model)

            # Dynamic token budget (no artificial cap — model limit is ceiling)
            max_tokens = TokenBudget.compute(
                self.provider, self.model, system_prompt, user_prompt, profile
            )

            # Temperature based on mode and quality level
            temperature = profile.temperature_default
            if mode and 'structure' in mode:
                temperature = profile.temperature_structure
            elif mode and ('lesson' in mode or 'content' in mode):
                temperature = profile.temperature_content
            elif mode and 'method' in mode:
                temperature = profile.temperature_methods

            # Pipeline step injection (for multi-step generation)
            if mode and mode.startswith('pipeline_'):
                step = mode.replace('pipeline_', '')
                step_suffix = GenerationPipeline.get_step_prompt(step)
                if step_suffix:
                    system_prompt += step_suffix

            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]

            # Try Tool Calling first, fallback to text parsing
            tool_calls = []
            output_text = ''
            parse_error = None

            try:
                result = adapter.send_messages_with_tools(
                    messages=messages,
                    tools=AUTHORING_TOOLS,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                output_text = result.get('output_text', '')
                tool_calls = result.get('tool_calls', [])
                tokens_used = result.get('total_tokens', 0)
            except Exception as e:
                # Fallback: Provider doesn't support tool calling
                logger.info(f"Tool calling not available, falling back to text: {e}")
                result = adapter.send_messages(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                output_text = result.get('output_text', '')
                tokens_used = result.get('total_tokens', 0)

            # Operations aus Tool Calls oder Text-Parsing extrahieren
            if tool_calls:
                # Level 2: Structured tool calls
                assistant_message = output_text or 'Änderungen werden angewendet...'
                validated_ops = ToolCallProcessor.to_operations(tool_calls)
                logger.info(
                    f"Session {session_id}: Tool calling → "
                    f"{len(validated_ops)} operations from {len(tool_calls)} calls"
                )
            else:
                # Fallback: Text-based JSON parsing (Level 1)
                assistant_message, structure_patch = DataHelpers.parse_ai_response(output_text)

                if structure_patch and '_parse_error' in structure_patch:
                    parse_error = structure_patch['_parse_error']
                    logger.warning(f"Session {session_id}: JSON parse error: {parse_error}")
                    structure_patch = None

                validated_ops = []
                if structure_patch and structure_patch.get('operations'):
                    validated_ops = OperationValidator.validate_operations(
                        structure_patch['operations']
                    )

            # Scope Guard: Nur erlaubte Operationen durchlassen
            blocked_ops = []
            if validated_ops and scope:
                validated_ops, blocked_ops = ScopeGuard.check(
                    validated_ops, scope, draft_structure
                )
                if blocked_ops:
                    logger.warning(
                        f"Session {session_id}: ScopeGuard blocked "
                        f"{len(blocked_ops)} operations: "
                        f"{[op.get('op') for op in blocked_ops]}"
                    )

            # Operationen anwenden
            operations_applied = []
            failed_ops = []
            if validated_ops:
                draft_structure, operations_applied, failed_ops = (
                    StructureOperations.apply_operations(draft_structure, validated_ops)
                )

            if failed_ops:
                logger.warning(
                    f"Session {session_id}: {len(failed_ops)} operations failed: "
                    f"{[f['op'] for f in failed_ops]}"
                )

            # Content validation (profile-driven thresholds)
            validation_result = None
            if profile.validate_content and operations_applied:
                is_valid, validation_issues = ContentValidator.validate(
                    draft_structure, profile
                )
                if validation_issues:
                    validation_result = {
                        'valid': is_valid,
                        'errors': [i for i in validation_issues if i['level'] == 'error'],
                        'warnings': [i for i in validation_issues if i['level'] == 'warning'],
                    }

            # Intelligent retry (profile-driven attempts)
            retry_count = 0
            while (
                retry_count < profile.max_retries
                and validation_result
                and validation_result.get('errors')
            ):
                retry_count += 1
                retry_temp = max(
                    0.2, temperature - profile.retry_temperature_drop * retry_count
                )
                logger.info(
                    f"Session {session_id}: Retry {retry_count}/{profile.max_retries} "
                    f"for {len(validation_result['errors'])} errors (temp={retry_temp})"
                )

                fix_prompt = self._build_fix_prompt(
                    failed_ops, validation_result['errors'], draft_structure
                )
                if not fix_prompt:
                    break

                try:
                    fix_result = adapter.send_messages_with_tools(
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': fix_prompt}
                        ],
                        tools=AUTHORING_TOOLS,
                        temperature=retry_temp,
                        max_tokens=max_tokens // 2
                    )
                    fix_calls = fix_result.get('tool_calls', [])
                    if fix_calls:
                        fix_ops = ToolCallProcessor.to_operations(fix_calls)
                        draft_structure, fix_applied, fix_failed = (
                            StructureOperations.apply_operations(draft_structure, fix_ops)
                        )
                        operations_applied.extend(fix_applied)
                        tokens_used += fix_result.get('total_tokens', 0)

                    # Re-validate
                    is_valid, validation_issues = ContentValidator.validate(
                        draft_structure, profile
                    )
                    validation_result = {
                        'valid': is_valid,
                        'errors': [i for i in validation_issues if i['level'] == 'error'],
                        'warnings': [i for i in validation_issues if i['level'] == 'warning'],
                    }
                except Exception as retry_err:
                    logger.warning(f"Retry {retry_count} failed: {retry_err}")
                    break

            # Activity Log generieren
            if operations_applied:
                activity_entry = ActivityLogGenerator.generate_entry(
                    validated_ops,
                    draft_structure
                )
                if 'activity_log' not in draft_structure:
                    draft_structure['activity_log'] = []
                draft_structure['activity_log'].insert(0, activity_entry)
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
                'tokens_used': tokens_used,
                'quality_level': profile.level,
                'max_tokens_used': max_tokens,
                '_chat_history': chat_history,
            }
            if failed_ops:
                result['operations_failed'] = failed_ops
            if blocked_ops:
                result['operations_blocked'] = [op.get('op') for op in blocked_ops]
            if parse_error:
                result['parse_error'] = parse_error
            if validation_result:
                result['content_validation'] = validation_result
            return result

        except AIProviderError as e:
            logger.error(f"AI provider error: {str(e)}")
            raise CourseAuthoringError("AI generation failed. Please try again.")

    @staticmethod
    def _build_scope(
        course_id: str,
        focus_chapter_id: Optional[str] = None,
        focus_lesson_id: Optional[str] = None
    ) -> Optional[OperationScope]:
        """Baut OperationScope basierend auf Frontend-Kontext."""
        if focus_lesson_id:
            return OperationScope.for_lesson(
                course_id=course_id,
                lesson_id=focus_lesson_id,
                chapter_id=focus_chapter_id or ''
            )
        if focus_chapter_id:
            return OperationScope.for_chapter(
                course_id=course_id,
                chapter_id=focus_chapter_id
            )
        # Kein Fokus → Kurs-Scope (alles erlaubt)
        return OperationScope.for_course(course_id=course_id)

    @staticmethod
    def _build_fix_prompt(
        failed_ops: List[Dict],
        errors: List[Dict],
        draft_structure: Dict
    ) -> Optional[str]:
        """Build targeted prompt to fix validation errors."""
        issues = []
        for op in failed_ops:
            issues.append(f"- Operation '{op.get('op')}' fehler: {op.get('error')}")
        for err in errors:
            issues.append(f"- {err['path']}: {err['message']}")
        if not issues:
            return None

        structure_summary = PromptGenerator._summarize_structure(draft_structure)
        return (
            f"FEHLER-KORREKTUR:\n"
            f"Folgende Probleme muessen behoben werden:\n"
            + "\n".join(issues)
            + f"\n\nAKTUELLE STRUKTUR:\n{structure_summary}\n\n"
            f"Korrigiere NUR die genannten Probleme mit den passenden Tools."
        )

    @staticmethod
    def _resolve_system_prompt(
        prompt_code: Optional[str] = None,
        mode: Optional[str] = None
    ) -> str:
        """
        Löst System-Prompt auf: DB-Template → Fallback auf hardcoded.

        Args:
            prompt_code: Optional template code (z.B. 'ai_editor_freitext')
            mode: Optional mode für hardcoded Fallback

        Returns:
            System prompt string
        """
        if prompt_code:
            try:
                from app.infrastructure.persistence.repositories.prompts.templates import (
                    PromptTemplateRepository,
                )
                template = PromptTemplateRepository.find_by_code(prompt_code)
                if template and template.get('system_prompt'):
                    logger.info(f"Using DB prompt template: {prompt_code}")
                    return template['system_prompt']
                logger.warning(
                    f"Prompt template '{prompt_code}' not found, using default"
                )
            except Exception as e:
                logger.warning(f"Error loading prompt template: {e}")

        return PromptGenerator.get_system_prompt(mode)

    @staticmethod
    def list_available_prompts() -> List[Dict[str, Any]]:
        """
        Listet verfügbare Prompt-Templates für den AI Editor.

        Returns:
            Liste der Templates mit code, title, description, style
        """
        try:
            from app.infrastructure.persistence.repositories.prompts.templates import (
                PromptTemplateRepository,
            )
            templates = PromptTemplateRepository.list_by_category('ai_editor')
            return [
                {
                    'code': t['code'],
                    'title': t['title'],
                    'description': t.get('description', ''),
                    'style': t['style'],
                    'icon': t.get('icon', ''),
                    'is_default': t.get('is_default', False),
                }
                for t in templates
            ]
        except Exception as e:
            logger.warning(f"Error listing prompt templates: {e}")
            return []

    # finalize_session is inherited from FinalizeMixin (session_finalize.py)
