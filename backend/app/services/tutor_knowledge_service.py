"""
TutorKnowledgeService - Lädt Tutor-Wissen aus DB/Kurs-Inhalten

Dieser Service stellt dem KI-Tutor das nötige Wissen zur Verfügung:
- Kurs-Inhalte (Titel, Beschreibungen, Lernziele)
- Kapitel-Struktur
- Lektions-Inhalte
- Lernmethoden-Daten
- Kurs-Dateien (PDFs, Skripte)

Der Tutor kann damit kontextbezogene Erklärungen geben,
basierend auf dem aktuellen Lernstand des Schülers.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from app.database.connection import fetch_one, fetch_all

logger = logging.getLogger(__name__)


class TutorKnowledgeService:
    """
    Service zum Laden von Tutor-Wissen aus der Datenbank.

    Der Tutor verwendet dieses Wissen um:
    - Kontextbezogene Erklärungen zu geben
    - Aufgaben basierend auf Kurs-Inhalten zu generieren
    - Verweise auf relevante Materialien zu machen
    - Den Lernfortschritt zu berücksichtigen
    """

    # =========================================================================
    # KURS-KONTEXT LADEN
    # =========================================================================

    @classmethod
    def get_course_context(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Lädt den vollständigen Kurs-Kontext für den Tutor.

        Args:
            course_id: UUID des Kurses

        Returns:
            Dict mit Kurs-Informationen für den Tutor:
            {
                'course': {...},
                'chapters': [...],
                'total_lessons': int,
                'learning_objectives': [...],
                'keywords': [...]
            }
        """
        try:
            # Kurs-Grunddaten
            course = fetch_one("""
                SELECT
                    course_id,
                    title,
                    subtitle,
                    description,
                    learning_objectives,
                    target_audience,
                    prerequisites,
                    difficulty_level,
                    language,
                    duration_hours,
                    category_id
                FROM courses
                WHERE course_id = %s
            """, (course_id,))

            if not course:
                return None

            # Kapitel mit Lektionen
            chapters = fetch_all("""
                SELECT
                    ch.chapter_id,
                    ch.title,
                    ch.description,
                    ch.order_index,
                    (SELECT COUNT(*) FROM lessons l WHERE l.chapter_id = ch.chapter_id) as lesson_count,
                    (SELECT COUNT(*) FROM learning_methods lm WHERE lm.chapter_id = ch.chapter_id) as method_count
                FROM chapters ch
                WHERE ch.course_id = %s
                ORDER BY ch.order_index
            """, (course_id,))

            # Kategorie-Name (falls vorhanden)
            category_name = None
            if course.get('category_id'):
                cat = fetch_one("""
                    SELECT name FROM course_categories WHERE category_id = %s
                """, (course['category_id'],))
                if cat:
                    category_name = cat['name']

            return {
                'course': {
                    'id': str(course['course_id']),
                    'title': course['title'],
                    'subtitle': course.get('subtitle'),
                    'description': course.get('description'),
                    'learning_objectives': course.get('learning_objectives', []),
                    'target_audience': course.get('target_audience'),
                    'prerequisites': course.get('prerequisites'),
                    'difficulty': course.get('difficulty_level', 'beginner'),
                    'language': course.get('language', 'de'),
                    'duration_hours': course.get('duration_hours'),
                    'category': category_name
                },
                'chapters': [
                    {
                        'id': str(ch['chapter_id']),
                        'title': ch['title'],
                        'description': ch.get('description'),
                        'order': ch['order_index'],
                        'lesson_count': ch['lesson_count'],
                        'method_count': ch['method_count']
                    }
                    for ch in (chapters or [])
                ],
                'total_chapters': len(chapters or []),
                'total_lessons': sum(ch['lesson_count'] for ch in (chapters or []))
            }

        except Exception as e:
            logger.error(f"Error loading course context: {e}")
            return None

    @classmethod
    def get_chapter_context(cls, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Lädt den Kapitel-Kontext mit allen Lektionen und Lernmethoden.

        Args:
            chapter_id: UUID des Kapitels

        Returns:
            Dict mit Kapitel-Details für den Tutor
        """
        try:
            # Kapitel-Grunddaten
            chapter = fetch_one("""
                SELECT
                    ch.chapter_id,
                    ch.course_id,
                    ch.title,
                    ch.description,
                    ch.order_index,
                    c.title as course_title
                FROM chapters ch
                LEFT JOIN courses c ON ch.course_id = c.course_id
                WHERE ch.chapter_id = %s
            """, (chapter_id,))

            if not chapter:
                return None

            # Lektionen des Kapitels
            lessons = fetch_all("""
                SELECT
                    lesson_id,
                    title,
                    lesson_type,
                    content,
                    order_index,
                    duration_minutes
                FROM lessons
                WHERE chapter_id = %s
                ORDER BY order_index
            """, (chapter_id,))

            # Lernmethoden des Kapitels
            methods = fetch_all("""
                SELECT
                    method_id,
                    method_type,
                    title,
                    instructions,
                    data,
                    difficulty,
                    order_index
                FROM learning_methods
                WHERE chapter_id = %s AND published = TRUE
                ORDER BY order_index
            """, (chapter_id,))

            return {
                'chapter': {
                    'id': str(chapter['chapter_id']),
                    'title': chapter['title'],
                    'description': chapter.get('description'),
                    'order': chapter['order_index'],
                    'course_id': str(chapter['course_id']),
                    'course_title': chapter['course_title']
                },
                'lessons': [
                    {
                        'id': str(l['lesson_id']),
                        'title': l['title'],
                        'type': l['lesson_type'],
                        'content_preview': (l.get('content') or '')[:500] if l.get('content') else None,
                        'order': l['order_index'],
                        'duration_minutes': l.get('duration_minutes')
                    }
                    for l in (lessons or [])
                ],
                'learning_methods': [
                    {
                        'id': str(m['method_id']),
                        'type': m['method_type'],
                        'title': m['title'],
                        'instructions': m.get('instructions'),
                        'difficulty': m.get('difficulty'),
                        'order': m['order_index']
                    }
                    for m in (methods or [])
                ]
            }

        except Exception as e:
            logger.error(f"Error loading chapter context: {e}")
            return None

    @classmethod
    def get_lesson_content(cls, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Lädt den vollständigen Inhalt einer Lektion für den Tutor.

        Args:
            lesson_id: ID der Lektion

        Returns:
            Dict mit Lektions-Inhalt
        """
        try:
            lesson = fetch_one("""
                SELECT
                    l.*,
                    ch.title as chapter_title,
                    ch.course_id,
                    c.title as course_title
                FROM lessons l
                LEFT JOIN chapters ch ON l.chapter_id = ch.chapter_id
                LEFT JOIN courses c ON ch.course_id = c.course_id
                WHERE l.lesson_id = %s
            """, (lesson_id,))

            if not lesson:
                return None

            return {
                'lesson': {
                    'id': lesson['lesson_id'],
                    'title': lesson['title'],
                    'type': lesson['lesson_type'],
                    'content': lesson.get('content'),
                    'duration_minutes': lesson.get('duration_minutes')
                },
                'chapter': {
                    'id': str(lesson['chapter_id']),
                    'title': lesson['chapter_title']
                },
                'course': {
                    'id': str(lesson['course_id']),
                    'title': lesson['course_title']
                }
            }

        except Exception as e:
            logger.error(f"Error loading lesson content: {e}")
            return None

    # =========================================================================
    # LERNMETHODEN-WISSEN
    # =========================================================================

    @classmethod
    def get_learning_method_data(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """
        Lädt die vollständigen Daten einer Lernmethode.

        Args:
            method_id: UUID der Lernmethode

        Returns:
            Dict mit Lernmethoden-Daten inkl. JSONB-Content
        """
        try:
            method = fetch_one("""
                SELECT
                    lm.*,
                    ch.title as chapter_title,
                    ch.course_id,
                    c.title as course_title
                FROM learning_methods lm
                LEFT JOIN chapters ch ON lm.chapter_id = ch.chapter_id
                LEFT JOIN courses c ON ch.course_id = c.course_id
                WHERE lm.method_id = %s
            """, (method_id,))

            if not method:
                return None

            return {
                'method': {
                    'id': str(method['method_id']),
                    'type': method['method_type'],
                    'title': method['title'],
                    'instructions': method.get('instructions'),
                    'data': method.get('data', {}),
                    'solution': method.get('solution'),
                    'difficulty': method.get('difficulty'),
                    'tier': method.get('tier')
                },
                'chapter': {
                    'id': str(method['chapter_id']),
                    'title': method['chapter_title']
                },
                'course': {
                    'id': str(method['course_id']),
                    'title': method['course_title']
                }
            }

        except Exception as e:
            logger.error(f"Error loading learning method data: {e}")
            return None

    # =========================================================================
    # KURS-DATEIEN (SKRIPTE, MATERIALIEN)
    # =========================================================================

    @classmethod
    def get_course_files(
        cls,
        course_id: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lädt Kurs-Dateien (PDFs, Skripte, Materialien).

        Args:
            course_id: UUID des Kurses
            category: Optional: 'script', 'material', 'exercise', etc.

        Returns:
            Liste der Dateien mit Metadaten
        """
        try:
            query = """
                SELECT
                    cf.course_file_id,
                    cf.file_name,
                    cf.display_name,
                    cf.description,
                    cf.file_category,
                    cf.file_type,
                    cf.ai_summary,
                    cf.ai_keywords,
                    cf.ai_processed,
                    mf.public_url,
                    mf.cdn_url
                FROM course_files cf
                LEFT JOIN media_files mf ON cf.file_id = mf.file_id
                WHERE cf.course_id = %s
            """
            params: List[Any] = [course_id]

            if category:
                query += " AND cf.file_category = %s"
                params.append(category)

            query += " ORDER BY cf.order_index"

            files = fetch_all(query, tuple(params))

            return [
                {
                    'id': str(f['course_file_id']),
                    'name': f.get('display_name') or f['file_name'],
                    'description': f.get('description'),
                    'category': f['file_category'],
                    'type': f['file_type'],
                    'url': f.get('cdn_url') or f.get('public_url'),
                    'ai_summary': f.get('ai_summary'),
                    'ai_keywords': f.get('ai_keywords'),
                    'ai_processed': f.get('ai_processed', False)
                }
                for f in (files or [])
            ]

        except Exception as e:
            logger.error(f"Error loading course files: {e}")
            return []

    # =========================================================================
    # USER PROGRESS (Lernfortschritt)
    # =========================================================================

    @classmethod
    def get_user_progress(
        cls,
        user_id: str,
        course_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Lädt den Lernfortschritt eines Users in einem Kurs.

        Args:
            user_id: UUID des Users
            course_id: UUID des Kurses

        Returns:
            Dict mit Fortschrittsdaten
        """
        try:
            # Enrollment-Status
            enrollment = fetch_one("""
                SELECT
                    enrollment_id,
                    enrollment_type,
                    progress_percentage,
                    last_accessed_at,
                    completed_at
                FROM enrollments
                WHERE user_id = %s AND course_id = %s
            """, (user_id, course_id))

            if not enrollment:
                return None

            # Abgeschlossene Lektionen
            completed_lessons = fetch_all("""
                SELECT
                    lp.lesson_id,
                    l.title,
                    lp.completed_at
                FROM lesson_progress lp
                JOIN lessons l ON lp.lesson_id = l.lesson_id
                JOIN chapters ch ON l.chapter_id = ch.chapter_id
                WHERE lp.user_id = %s AND ch.course_id = %s AND lp.completed = TRUE
                ORDER BY lp.completed_at DESC
            """, (user_id, course_id))

            # Lernmethoden-Fortschritt
            method_progress = fetch_all("""
                SELECT
                    lmp.method_id,
                    lm.title,
                    lm.method_type,
                    lmp.attempts,
                    lmp.best_score,
                    lmp.completed
                FROM learning_method_progress lmp
                JOIN learning_methods lm ON lmp.method_id = lm.method_id
                JOIN chapters ch ON lm.chapter_id = ch.chapter_id
                WHERE lmp.user_id = %s AND ch.course_id = %s
                ORDER BY lmp.updated_at DESC
            """, (user_id, course_id))

            return {
                'enrollment': {
                    'type': enrollment['enrollment_type'],
                    'progress': enrollment.get('progress_percentage', 0),
                    'last_accessed': enrollment.get('last_accessed_at'),
                    'completed': enrollment.get('completed_at') is not None
                },
                'completed_lessons': [
                    {
                        'id': l['lesson_id'],
                        'title': l['title'],
                        'completed_at': l['completed_at']
                    }
                    for l in (completed_lessons or [])
                ],
                'method_progress': [
                    {
                        'id': str(m['method_id']),
                        'title': m['title'],
                        'type': m['method_type'],
                        'attempts': m.get('attempts', 0),
                        'best_score': m.get('best_score'),
                        'completed': m.get('completed', False)
                    }
                    for m in (method_progress or [])
                ]
            }

        except Exception as e:
            logger.error(f"Error loading user progress: {e}")
            return None

    # =========================================================================
    # TUTOR-PROMPT BUILDER
    # =========================================================================

    @classmethod
    def build_tutor_context_prompt(
        cls,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[int] = None,
        method_id: Optional[str] = None,
        user_id: Optional[str] = None,
        include_files: bool = True,
        include_progress: bool = True
    ) -> str:
        """
        Baut einen Kontext-Prompt für den KI-Tutor basierend auf DB-Inhalten.

        Args:
            course_id: Kurs-ID für Kurs-Kontext
            chapter_id: Kapitel-ID für detaillierten Kapitel-Kontext
            lesson_id: Lektions-ID für Lektions-Inhalt
            method_id: Lernmethoden-ID für spezifische Aufgaben
            user_id: User-ID für Fortschrittsdaten
            include_files: Kurs-Dateien einbeziehen
            include_progress: Lernfortschritt einbeziehen

        Returns:
            Formatierter Kontext-String für den Tutor-Prompt
        """
        context_parts = []

        # Kurs-Kontext
        if course_id:
            course_ctx = cls.get_course_context(course_id)
            if course_ctx:
                context_parts.append(f"""
=== KURS-INFORMATIONEN ===
Kurs: {course_ctx['course']['title']}
{f"Untertitel: {course_ctx['course']['subtitle']}" if course_ctx['course'].get('subtitle') else ""}
Beschreibung: {course_ctx['course'].get('description', 'Keine Beschreibung verfügbar')}
Schwierigkeit: {course_ctx['course'].get('difficulty', 'Nicht angegeben')}
Sprache: {course_ctx['course'].get('language', 'de')}
Kapitel: {course_ctx['total_chapters']}
Lektionen: {course_ctx['total_lessons']}

Lernziele:
{chr(10).join(f"- {obj}" for obj in (course_ctx['course'].get('learning_objectives') or ['Keine Lernziele definiert']))}

Kapitel-Übersicht:
{chr(10).join(f"{i+1}. {ch['title']} ({ch['lesson_count']} Lektionen, {ch['method_count']} Übungen)" for i, ch in enumerate(course_ctx['chapters']))}
""".strip())

        # Kapitel-Kontext
        if chapter_id:
            chapter_ctx = cls.get_chapter_context(chapter_id)
            if chapter_ctx:
                context_parts.append(f"""
=== AKTUELLES KAPITEL ===
Kapitel: {chapter_ctx['chapter']['title']}
{f"Beschreibung: {chapter_ctx['chapter']['description']}" if chapter_ctx['chapter'].get('description') else ""}

Lektionen in diesem Kapitel:
{chr(10).join(f"- {l['title']} ({l['duration_minutes'] or '?'} Min.)" for l in chapter_ctx['lessons'])}

Übungen/Lernmethoden:
{chr(10).join(f"- {m['title']} (Typ: LM{m['type']:02d}, {m['difficulty'] or 'mittel'})" for m in chapter_ctx['learning_methods'])}
""".strip())

        # Lektions-Inhalt
        if lesson_id:
            lesson_ctx = cls.get_lesson_content(lesson_id)
            if lesson_ctx:
                content = lesson_ctx['lesson'].get('content')
                content_preview = content[:2000] + '...' if content and len(content) > 2000 else content
                context_parts.append(f"""
=== AKTUELLE LEKTION ===
Lektion: {lesson_ctx['lesson']['title']}
Typ: {lesson_ctx['lesson']['type']}
Dauer: {lesson_ctx['lesson'].get('duration_minutes') or '?'} Minuten

Inhalt:
{content_preview if content_preview else 'Kein Textinhalt verfügbar'}
""".strip())

        # Lernmethoden-Daten
        if method_id:
            method_ctx = cls.get_learning_method_data(method_id)
            if method_ctx:
                context_parts.append(f"""
=== AKTUELLE ÜBUNG ===
Übung: {method_ctx['method']['title']}
Typ: LM{method_ctx['method']['type']:02d}
Schwierigkeit: {method_ctx['method'].get('difficulty') or 'mittel'}
Tier: {method_ctx['method'].get('tier') or 'basic'}

Anweisungen:
{method_ctx['method'].get('instructions') or 'Keine spezifischen Anweisungen'}

Aufgaben-Daten:
{method_ctx['method'].get('data', {})}
""".strip())

        # Kurs-Dateien
        if include_files and course_id:
            files = cls.get_course_files(course_id)
            if files:
                file_list = '\n'.join(
                    f"- {f['name']} ({f['category']}/{f['type']})"
                    + (f": {f['ai_summary'][:200]}..." if f.get('ai_summary') else "")
                    for f in files[:10]  # Max 10 Dateien
                )
                context_parts.append(f"""
=== KURSMATERIALIEN ===
{file_list}
""".strip())

        # Lernfortschritt
        if include_progress and user_id and course_id:
            progress = cls.get_user_progress(user_id, course_id)
            if progress:
                completed_count = len(progress['completed_lessons'])
                method_count = len(progress['method_progress'])
                avg_score = sum(
                    m['best_score'] or 0
                    for m in progress['method_progress']
                    if m.get('best_score')
                ) / max(1, sum(1 for m in progress['method_progress'] if m.get('best_score')))

                context_parts.append(f"""
=== LERNFORTSCHRITT DES SCHÜLERS ===
Gesamtfortschritt: {progress['enrollment']['progress']}%
Abgeschlossene Lektionen: {completed_count}
Bearbeitete Übungen: {method_count}
Durchschnittliche Punktzahl: {avg_score:.1f}%

Zuletzt abgeschlossene Lektionen:
{chr(10).join(f"- {l['title']}" for l in progress['completed_lessons'][:5])}
""".strip())

        if not context_parts:
            return "Kein spezifischer Kurs-Kontext verfügbar."

        return '\n\n'.join(context_parts)
