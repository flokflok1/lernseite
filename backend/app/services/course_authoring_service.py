"""
LernsystemX Course Authoring Service

Chat-basiertes Kurs-Authoring mit persistenten Sessions.
Ermöglicht:
- Kursstruktur über Chat erstellen/bearbeiten
- Kapitel, Lektionen, Lernmethoden generieren
- Draft-Structure mit Patch-Operationen
- Finalize um echte DB-Entities zu erstellen

Integration:
- Nutzt AIAdapter für KI-Calls
- Nutzt bestehenden AuthoringService für Content-Generation
- Speichert Sessions in course_authoring_sessions Tabelle

Lernmethoden-Typen:
- calculator_tutorial: Taschenrechner-Anleitungen
- tool_tutorial: Software/CLI-Tutorials
- step_by_step: Prozess-Anleitungen
- theory: Theorieblätter
- quiz: Quizze/Prüfungsfragen
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.database.connection import fetch_one, fetch_all, execute_query
from app.services.ai_adapter import AIAdapter, AIProviderError

logger = logging.getLogger(__name__)


class CourseAuthoringError(Exception):
    """Base exception for course authoring errors"""
    pass


class CourseAuthoringService:
    """
    Service für chat-basiertes Kurs-Authoring mit persistenten Sessions.

    Usage:
        >>> service = CourseAuthoringService()
        >>> session = service.create_session(user_id, course_id)
        >>> result = service.apply_chat_message(session['session_id'], user_id, "Erstelle 3 Kapitel")
        >>> service.finalize_session(session['session_id'], user_id)
    """

    # Erlaubte Patch-Operationen
    VALID_OPERATIONS = {
        'add_chapter', 'update_chapter', 'delete_chapter',
        'add_lesson', 'update_lesson', 'delete_lesson',
        'add_method', 'update_method', 'delete_method',
        'reorder_chapters', 'reorder_lessons',
        'set_meta'
    }

    # Erlaubte Lernmethoden-Typen
    VALID_METHOD_TYPES = {
        'calculator_tutorial',  # Taschenrechner-Anleitung
        'tool_tutorial',        # Software/CLI-Tutorial
        'step_by_step',         # Prozess-Anleitung
        'theory',               # Theorieblatt
        'quiz',                 # Quiz
        'flashcards',           # Karteikarten
        'exam',                 # Prüfungssimulation
        'exercise',             # Übungsaufgabe
        'video',                # Video-Lektion
        'interactive'           # Interaktive Übung
    }

    def __init__(self, provider: str = "anthropic", model: str = "claude-sonnet-4-20250514"):
        """Initialize course authoring service."""
        self.provider = provider
        self.model = model

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
        course = self._get_course(course_id)
        if not course:
            raise CourseAuthoringError(f"Course not found: {course_id}")

        # Prüfe User-Berechtigung
        if not self._check_user_access(user_id, course_id):
            raise CourseAuthoringError("User has no access to this course")

        # Lade bestehende Struktur aus DB
        draft_structure = self._load_existing_structure(course_id, course)

        # Session erstellen
        session_id = str(uuid.uuid4())

        query = """
            INSERT INTO course_authoring_sessions (
                session_id, course_id, created_by, model_profile,
                draft_structure, chat_history, status
            ) VALUES (%s, %s, %s, %s, %s, %s, 'active')
            RETURNING session_id, course_id, created_by, draft_structure,
                      status, created_at
        """

        result = fetch_one(query, (
            session_id,
            course_id,
            user_id,
            model_profile,
            json.dumps(draft_structure),
            json.dumps([])
        ))

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
        query = """
            SELECT s.*, c.title as course_title
            FROM course_authoring_sessions s
            JOIN courses c ON c.course_id = s.course_id
            WHERE s.session_id = %s
        """

        result = fetch_one(query, (session_id,))

        if not result:
            raise CourseAuthoringError(f"Session not found: {session_id}")

        # Prüfe Zugriff
        if str(result['created_by']) != user_id:
            if not self._check_user_access(user_id, str(result['course_id'])):
                raise CourseAuthoringError("User has no access to this session")

        return {
            'session_id': str(result['session_id']),
            'course_id': str(result['course_id']),
            'course_title': result['course_title'],
            'draft_structure': result['draft_structure'] if isinstance(result['draft_structure'], dict) else json.loads(result['draft_structure']),
            'chat_history': result['chat_history'] if isinstance(result['chat_history'], list) else json.loads(result['chat_history'] or '[]'),
            'file_context': result['file_context'] if isinstance(result['file_context'], list) else json.loads(result['file_context'] or '[]'),
            'status': result['status'],
            'total_tokens_used': result['total_tokens_used'],
            'total_operations': result['total_operations'],
            'model_profile': result['model_profile'],
            'created_at': result['created_at'].isoformat() if result['created_at'] else None,
            'updated_at': result['updated_at'].isoformat() if result['updated_at'] else None
        }

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
            file_context_text = self._extract_file_context(file_ids)

        # Kurs-Info laden
        course_info = self._get_course_info(session['course_id'])

        # Chat-History für Kontext (letzte 10 Nachrichten)
        history_context = self._format_history_for_prompt(chat_history[-10:])

        # KI-Request bauen
        system_prompt = self._get_system_prompt(mode)
        user_prompt = self._build_user_prompt(
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
            assistant_message, structure_patch = self._parse_ai_response(output_text)

            # Patch validieren und anwenden
            operations_applied = []
            validated_ops = []
            if structure_patch and structure_patch.get('operations'):
                operations = structure_patch['operations']
                validated_ops = self._validate_operations(operations)
                draft_structure = self._apply_operations(draft_structure, validated_ops)
                operations_applied = [op.get('op') for op in validated_ops]

            # Activity Log generieren
            if operations_applied:
                activity_entry = self._generate_activity_log_entry(
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
            self._update_session(
                session_id,
                draft_structure=draft_structure,
                chat_history=chat_history,
                file_context=file_ids or session['file_context'],
                tokens_delta=tokens_used,
                operations_delta=len(operations_applied)
            )

            logger.info(f"Applied {len(operations_applied)} operations to session {session_id}")

            return {
                'assistant_message': assistant_message,
                'draft_structure': draft_structure,
                'operations_applied': operations_applied,
                'tokens_used': tokens_used
            }

        except AIProviderError as e:
            logger.error(f"AI provider error: {str(e)}")
            raise CourseAuthoringError(f"AI generation failed: {str(e)}")

    def finalize_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Finalisiert eine Session und erstellt echte DB-Entities.

        Args:
            session_id: Session UUID
            user_id: User UUID

        Returns:
            Dict mit created IDs und Stats
        """
        session = self.get_session(session_id, user_id)

        if session['status'] != 'active':
            raise CourseAuthoringError(f"Session is not active: {session['status']}")

        draft_structure = session['draft_structure']
        course_id = session['course_id']

        created_chapters = []
        created_lessons = []
        created_methods = []

        try:
            # Kapitel erstellen/updaten
            for chapter_draft in draft_structure.get('chapters', []):
                chapter_id = self._create_or_update_chapter(course_id, chapter_draft, user_id)
                created_chapters.append(chapter_id)

                # Lektionen erstellen
                for lesson_draft in chapter_draft.get('lessons', []):
                    lesson_id = self._create_or_update_lesson(chapter_id, lesson_draft, user_id)
                    created_lessons.append(lesson_id)

                    # Methoden erstellen
                    for method_draft in lesson_draft.get('methods', []):
                        method_id = self._create_method(lesson_id, chapter_id, method_draft, user_id)
                        created_methods.append(method_id)

            # Session als finalized markieren
            update_query = """
                UPDATE course_authoring_sessions
                SET status = 'finalized', finalized_at = NOW()
                WHERE session_id = %s
            """
            execute_query(update_query, (session_id,))

            logger.info(f"Finalized session {session_id}: {len(created_chapters)} chapters, "
                       f"{len(created_lessons)} lessons, {len(created_methods)} methods")

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

        except Exception as e:
            logger.error(f"Error finalizing session: {str(e)}")
            raise CourseAuthoringError(f"Finalize failed: {str(e)}")

    # === Private Methods ===

    def _get_course(self, course_id: str) -> Optional[Dict]:
        """Lädt Kurs aus DB."""
        query = "SELECT * FROM courses WHERE course_id = %s"
        return fetch_one(query, (course_id,))

    def _check_user_access(self, user_id: str, course_id: str) -> bool:
        """Prüft ob User Zugriff auf Kurs hat."""
        # Admin/Teacher/Creator haben Zugriff
        query = """
            SELECT r.role_name
            FROM users u
            JOIN roles r ON r.role_id = u.role_id
            WHERE u.user_id = %s
        """
        result = fetch_one(query, (user_id,))
        if result and result['role_name'] in ('admin', 'teacher', 'creator', 'school', 'company'):
            return True

        # Oder Kurs-Owner
        query = "SELECT created_by FROM courses WHERE course_id = %s"
        course = fetch_one(query, (course_id,))
        return course and str(course['created_by']) == user_id

    def _load_existing_structure(self, course_id: str, course: Dict) -> Dict:
        """Lädt bestehende Kursstruktur in draft_structure Format."""
        structure = {
            'course_id': course_id,
            'course_title': course.get('title', ''),
            'course_description': course.get('description', ''),
            'chapters': [],
            'meta': {
                'version': 1,
                'source': 'existing',
                'last_operation': None
            }
        }

        # Kapitel laden
        chapters_query = """
            SELECT * FROM chapters
            WHERE course_id = %s
            ORDER BY sort_order, created_at
        """
        chapters = fetch_all(chapters_query, (course_id,))

        for chapter in chapters:
            chapter_id = str(chapter['chapter_id'])
            chapter_draft = {
                'id': chapter_id,
                'existing_id': chapter_id,
                'title': chapter.get('title', ''),
                'description': chapter.get('description', ''),
                'lessons': []
            }

            # Lektionen laden
            lessons_query = """
                SELECT * FROM lessons
                WHERE chapter_id = %s
                ORDER BY sort_order, created_at
            """
            lessons = fetch_all(lessons_query, (chapter_id,))

            for lesson in lessons:
                lesson_id = str(lesson['lesson_id'])
                lesson_draft = {
                    'id': lesson_id,
                    'existing_id': lesson_id,
                    'title': lesson.get('title', ''),
                    'type': lesson.get('lesson_type', 'text'),
                    'lm_type': lesson.get('lm_type', 'LM00'),
                    'methods': []
                }
                chapter_draft['lessons'].append(lesson_draft)

            structure['chapters'].append(chapter_draft)

        return structure

    def _get_course_info(self, course_id: str) -> Dict:
        """Lädt Kurs-Info für Prompt."""
        query = """
            SELECT c.*, cat.name as category_name
            FROM courses c
            LEFT JOIN course_categories cat ON cat.category_id = c.category_id
            WHERE c.course_id = %s
        """
        result = fetch_one(query, (course_id,))
        if result:
            return {
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'category': result.get('category_name', ''),
                'target_audience': result.get('target_audience', ''),
                'difficulty': result.get('difficulty_level', 'intermediate')
            }
        return {}

    def _extract_file_context(self, file_ids: List[str]) -> str:
        """Extrahiert Text-Kontext aus Dateien."""
        try:
            from app.services.file_context_service import FileContextService
            return FileContextService.extract_for_ai_context(file_ids, 'course')
        except Exception as e:
            logger.warning(f"Could not extract file context: {e}")
            return ""

    def _format_history_for_prompt(self, history: List[Dict]) -> str:
        """Formatiert Chat-History für Prompt."""
        if not history:
            return "Keine vorherigen Nachrichten."

        lines = []
        for msg in history:
            role = "Benutzer" if msg['role'] == 'user' else "Assistent"
            content = msg['content'][:300] + "..." if len(msg['content']) > 300 else msg['content']
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def _get_system_prompt(self, mode: Optional[str] = None) -> str:
        """Returns system prompt for course authoring."""
        base_prompt = """Du bist der LSX-Kursarchitekt, ein Experte für die Erstellung von Lernmaterialien.

Du hilfst beim Aufbau von Kursen für das LernsystemX. Du kennst:
- IHK-Prüfungsformate (AP1, AP2 für Fachinformatiker)
- Kaufmännische Berufsausbildungen
- Didaktische Best Practices

WICHTIG: Du antwortest IMMER im folgenden JSON-Format:
{
  "assistant_message": "Deine erklärende Antwort an den Benutzer",
  "structure_patch": {
    "operations": [
      {
        "op": "add_chapter|update_chapter|delete_chapter|add_lesson|update_lesson|delete_lesson|add_method|update_method|delete_method",
        "chapter_id": "id oder null",
        "lesson_id": "id oder null",
        "data": { ... }
      }
    ]
  }
}

Verfügbare Lernmethoden-Typen:
- calculator_tutorial: Taschenrechner-Anleitungen (z.B. "So rechne Prozent auf dem Casio fx-991")
- tool_tutorial: Software/CLI-Tutorials (z.B. "pfSense IPsec konfigurieren")
- step_by_step: Prozess-Anleitungen (z.B. "Handelskalkulation Schritt für Schritt")
- theory: Theorieblätter mit Kernkonzepten
- quiz: Quiz-Fragen
- flashcards: Karteikarten
- exercise: Übungsaufgaben

Operationen:
- add_chapter: Neues Kapitel { "id": "temp-uuid", "title": "...", "description": "..." }
- add_lesson: Neue Lektion { "chapter_id": "...", "id": "temp-uuid", "title": "...", "type": "text" }
- add_method: Neue Lernmethode { "lesson_id": "...", "id": "temp-uuid", "type": "calculator_tutorial", "title": "...", "content": {...} }
- update_*: Aktualisiert bestehende Elemente
- delete_*: Löscht Elemente

Wenn keine Strukturänderung nötig ist, setze "operations": []."""

        if mode == 'exam':
            base_prompt += """

MODUS: Prüfungsgenerierung
Fokussiere auf die Erstellung von Prüfungsfragen im IHK-Stil.
Nutze method_type "quiz" oder "exam" für Prüfungsinhalte."""

        elif mode == 'calculator':
            base_prompt += """

MODUS: Taschenrechner-Tutorial
Erstelle detaillierte Schritt-für-Schritt-Anleitungen für Taschenrechner.
Nutze method_type "calculator_tutorial" mit:
- calculator_model: "Casio fx-991" oder "TI-30"
- steps: Array mit Tasteneingaben und Erklärungen"""

        return base_prompt

    def _build_user_prompt(
        self,
        course_info: Dict,
        draft_structure: Dict,
        user_message: str,
        file_context: str,
        history: str,
        mode: Optional[str]
    ) -> str:
        """Baut User-Prompt für KI."""
        # Struktur kompakt formatieren
        structure_summary = self._summarize_structure(draft_structure)

        prompt = f"""KURS-INFO:
Titel: {course_info.get('title', 'Unbekannt')}
Beschreibung: {course_info.get('description', '-')}
Kategorie: {course_info.get('category', '-')}
Zielgruppe: {course_info.get('target_audience', '-')}

AKTUELLE STRUKTUR:
{structure_summary}

"""
        if file_context:
            prompt += f"""DATEI-KONTEXT (Kursmaterial):
{file_context[:3000]}

"""

        if history and history != "Keine vorherigen Nachrichten.":
            prompt += f"""CHAT-VERLAUF:
{history}

"""

        prompt += f"""BENUTZER-NACHRICHT:
{user_message}

Antworte im JSON-Format mit assistant_message und structure_patch."""

        return prompt

    def _summarize_structure(self, structure: Dict) -> str:
        """Fasst Struktur kompakt zusammen."""
        chapters = structure.get('chapters', [])
        if not chapters:
            return "Keine Kapitel vorhanden."

        lines = []
        for i, ch in enumerate(chapters, 1):
            lines.append(f"{i}. {ch.get('title', 'Kapitel')} (ID: {ch.get('id', '?')})")
            for j, lesson in enumerate(ch.get('lessons', []), 1):
                methods = lesson.get('methods', [])
                method_types = [m.get('type', '?') for m in methods]
                methods_str = f" [{', '.join(method_types)}]" if methods else ""
                lines.append(f"   {i}.{j} {lesson.get('title', 'Lektion')}{methods_str}")

        return "\n".join(lines)

    def _parse_ai_response(self, output: str) -> tuple:
        """Parst KI-Response in message und patch."""
        assistant_message = output
        structure_patch = None

        try:
            # Versuche JSON zu extrahieren
            if '```json' in output:
                start = output.find('```json') + 7
                end = output.find('```', start)
                if end > start:
                    json_str = output[start:end].strip()
                    data = json.loads(json_str)
                    assistant_message = data.get('assistant_message', output[:500])
                    structure_patch = data.get('structure_patch')
            elif output.strip().startswith('{'):
                data = json.loads(output)
                assistant_message = data.get('assistant_message', '')
                structure_patch = data.get('structure_patch')
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse AI response as JSON: {e}")

        return assistant_message, structure_patch

    def _generate_activity_log_entry(
        self,
        operations: List[Dict],
        draft_structure: Dict
    ) -> Dict[str, Any]:
        """
        Generiert einen Activity-Log-Eintrag aus den angewandten Operationen.

        Args:
            operations: Liste der angewandten Operationen
            draft_structure: Aktuelle Draft-Struktur

        Returns:
            Activity-Log-Entry mit timestamp, summary, operations
        """
        from datetime import datetime

        op_summaries = []
        op_types = []

        for op in operations:
            op_type = op.get('op', '')
            data = op.get('data', {})
            op_types.append(op_type)

            # Zusammenfassung basierend auf Operation generieren
            if op_type == 'add_chapter':
                title = data.get('title', 'Unbenanntes Kapitel')
                lessons_count = len(data.get('lessons', []))
                if lessons_count:
                    op_summaries.append(f"Kapitel '{title}' erstellt ({lessons_count} Lektionen)")
                else:
                    op_summaries.append(f"Kapitel '{title}' erstellt")

            elif op_type == 'update_chapter':
                title = data.get('title', '')
                op_summaries.append(f"Kapitel '{title}' aktualisiert")

            elif op_type == 'delete_chapter':
                op_summaries.append("Kapitel gelöscht")

            elif op_type == 'add_lesson':
                title = data.get('title', 'Unbenannte Lektion')
                op_summaries.append(f"Lektion '{title}' hinzugefügt")

            elif op_type == 'update_lesson':
                title = data.get('title', '')
                op_summaries.append(f"Lektion '{title}' aktualisiert")

            elif op_type == 'delete_lesson':
                op_summaries.append("Lektion gelöscht")

            elif op_type == 'add_method':
                method_type = data.get('type', 'unknown')
                method_labels = {
                    'calculator_tutorial': 'Taschenrechner-Tutorial',
                    'tool_tutorial': 'Tool-Tutorial',
                    'step_by_step': 'Prozess-Anleitung',
                    'theory': 'Theorieblatt',
                    'quiz': 'Quiz',
                    'flashcards': 'Karteikarten',
                    'exercise': 'Übungsaufgabe',
                    'exam': 'Prüfungssimulation'
                }
                label = method_labels.get(method_type, method_type)
                op_summaries.append(f"{label} hinzugefügt")

            elif op_type == 'update_method':
                op_summaries.append("Lernmethode aktualisiert")

            elif op_type == 'delete_method':
                op_summaries.append("Lernmethode gelöscht")

        # Zusammenfassung kombinieren
        if len(op_summaries) == 1:
            summary = op_summaries[0]
        elif len(op_summaries) <= 3:
            summary = "; ".join(op_summaries)
        else:
            summary = f"{len(op_summaries)} Änderungen durchgeführt"

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': summary,
            'operations': op_types,
            'details': op_summaries
        }

    def _validate_operations(self, operations: List[Dict]) -> List[Dict]:
        """Validiert Patch-Operationen."""
        validated = []
        for op in operations:
            op_type = op.get('op')
            if op_type not in self.VALID_OPERATIONS:
                logger.warning(f"Invalid operation type: {op_type}")
                continue

            # Methoden-Typ validieren falls vorhanden
            if 'method' in op_type and op.get('data', {}).get('type'):
                method_type = op['data']['type']
                if method_type not in self.VALID_METHOD_TYPES:
                    logger.warning(f"Invalid method type: {method_type}")
                    continue

            validated.append(op)

        return validated

    def _apply_operations(self, structure: Dict, operations: List[Dict]) -> Dict:
        """Wendet Operationen auf draft_structure an."""
        for op in operations:
            op_type = op.get('op')
            data = op.get('data', {})

            try:
                if op_type == 'add_chapter':
                    chapter = {
                        'id': data.get('id', str(uuid.uuid4())),
                        'title': data.get('title', 'Neues Kapitel'),
                        'description': data.get('description', ''),
                        'existing_id': None,
                        'lessons': []
                    }
                    structure['chapters'].append(chapter)

                elif op_type == 'update_chapter':
                    chapter_id = op.get('chapter_id') or data.get('id')
                    for ch in structure['chapters']:
                        if ch['id'] == chapter_id:
                            ch.update({k: v for k, v in data.items() if k != 'id'})
                            break

                elif op_type == 'delete_chapter':
                    chapter_id = op.get('chapter_id') or data.get('id')
                    structure['chapters'] = [
                        ch for ch in structure['chapters'] if ch['id'] != chapter_id
                    ]

                elif op_type == 'add_lesson':
                    chapter_id = op.get('chapter_id') or data.get('chapter_id')
                    lesson = {
                        'id': data.get('id', str(uuid.uuid4())),
                        'title': data.get('title', 'Neue Lektion'),
                        'type': data.get('type', 'text'),
                        'existing_id': None,
                        'methods': []
                    }
                    for ch in structure['chapters']:
                        if ch['id'] == chapter_id:
                            ch['lessons'].append(lesson)
                            break

                elif op_type == 'update_lesson':
                    lesson_id = op.get('lesson_id') or data.get('id')
                    for ch in structure['chapters']:
                        for lesson in ch['lessons']:
                            if lesson['id'] == lesson_id:
                                lesson.update({k: v for k, v in data.items() if k != 'id'})
                                break

                elif op_type == 'delete_lesson':
                    lesson_id = op.get('lesson_id') or data.get('id')
                    for ch in structure['chapters']:
                        ch['lessons'] = [
                            l for l in ch['lessons'] if l['id'] != lesson_id
                        ]

                elif op_type == 'add_method':
                    lesson_id = op.get('lesson_id') or data.get('lesson_id')
                    method = {
                        'id': data.get('id', str(uuid.uuid4())),
                        'type': data.get('type', 'theory'),
                        'title': data.get('title', 'Neue Methode'),
                        'content': data.get('content', {})
                    }
                    for ch in structure['chapters']:
                        for lesson in ch['lessons']:
                            if lesson['id'] == lesson_id:
                                lesson['methods'].append(method)
                                break

                elif op_type == 'update_method':
                    method_id = op.get('method_id') or data.get('id')
                    for ch in structure['chapters']:
                        for lesson in ch['lessons']:
                            for method in lesson['methods']:
                                if method['id'] == method_id:
                                    method.update({k: v for k, v in data.items() if k != 'id'})
                                    break

                elif op_type == 'delete_method':
                    method_id = op.get('method_id') or data.get('id')
                    for ch in structure['chapters']:
                        for lesson in ch['lessons']:
                            lesson['methods'] = [
                                m for m in lesson['methods'] if m['id'] != method_id
                            ]

                structure['meta']['last_operation'] = op_type

            except Exception as e:
                logger.error(f"Error applying operation {op_type}: {e}")

        return structure

    def _update_session(
        self,
        session_id: str,
        draft_structure: Dict,
        chat_history: List,
        file_context: List,
        tokens_delta: int = 0,
        operations_delta: int = 0
    ):
        """Aktualisiert Session in DB."""
        query = """
            UPDATE course_authoring_sessions
            SET draft_structure = %s,
                chat_history = %s,
                file_context = %s,
                total_tokens_used = total_tokens_used + %s,
                total_operations = total_operations + %s
            WHERE session_id = %s
        """
        execute_query(query, (
            json.dumps(draft_structure),
            json.dumps(chat_history),
            json.dumps(file_context),
            tokens_delta,
            operations_delta,
            session_id
        ))

    def _create_or_update_chapter(self, course_id: str, chapter_draft: Dict, user_id: str) -> str:
        """Erstellt oder aktualisiert Kapitel."""
        from app.repositories.chapter_repository import ChapterRepository

        existing_id = chapter_draft.get('existing_id')

        if existing_id:
            # Update
            ChapterRepository.update(existing_id, {
                'title': chapter_draft.get('title'),
                'description': chapter_draft.get('description')
            })
            return existing_id
        else:
            # Create
            result = ChapterRepository.create({
                'course_id': course_id,
                'title': chapter_draft.get('title', 'Neues Kapitel'),
                'description': chapter_draft.get('description', '')
            })
            return str(result['chapter_id'])

    def _create_or_update_lesson(self, chapter_id: str, lesson_draft: Dict, user_id: str) -> str:
        """Erstellt oder aktualisiert Lektion."""
        from app.repositories.lesson_repository import LessonRepository

        existing_id = lesson_draft.get('existing_id')

        if existing_id:
            # Update
            LessonRepository.update(existing_id, {
                'title': lesson_draft.get('title'),
                'lesson_type': lesson_draft.get('type', 'text')
            })
            return existing_id
        else:
            # Create
            result = LessonRepository.create({
                'chapter_id': chapter_id,
                'title': lesson_draft.get('title', 'Neue Lektion'),
                'lesson_type': lesson_draft.get('type', 'text'),
                'lm_type': lesson_draft.get('lm_type', 'LM00')
            })
            return str(result['lesson_id'])

    def _create_method(self, lesson_id: str, chapter_id: str, method_draft: Dict, user_id: str) -> str:
        """Erstellt Lernmethode."""
        method_type = method_draft.get('type', 'theory')
        content = method_draft.get('content', {})

        # Map string type to numeric LM type
        type_mapping = {
            'theory': 0,           # LM00
            'step_by_step': 1,     # LM01
            'calculator_tutorial': 1,  # LM01 (Step-by-Step variant)
            'tool_tutorial': 9,    # LM09 (Code/Config)
            'quiz': 22,            # LM22
            'flashcards': 13,      # LM13
            'exercise': 8,         # LM08
            'exam': 19,            # LM19 (IHK-Stil)
            'interactive': 2       # LM02
        }

        lm_type = type_mapping.get(method_type, 0)

        query = """
            INSERT INTO learning_method_instances (
                lesson_id, chapter_id, method_type, title,
                instructions, data, difficulty, tier
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING method_id
        """

        result = fetch_one(query, (
            lesson_id,
            chapter_id,
            lm_type,
            method_draft.get('title', 'Lernmethode'),
            content.get('instructions', ''),
            json.dumps(content),
            content.get('difficulty', 'medium'),
            content.get('tier', 'basic')
        ))

        return str(result['method_id']) if result else None


# Convenience function
def get_course_authoring_service(
    provider: str = "anthropic",
    model: str = "claude-sonnet-4-20250514"
) -> CourseAuthoringService:
    """Get course authoring service instance."""
    return CourseAuthoringService(provider=provider, model=model)
