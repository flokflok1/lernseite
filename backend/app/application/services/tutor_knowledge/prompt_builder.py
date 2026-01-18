"""
Prompt Builder - Tutor Context Prompt Construction
"""

from typing import Optional
import logging

from . import context_loader, method_loader, file_loader, progress_loader

logger = logging.getLogger(__name__)


def build_tutor_context_prompt(
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
        course_ctx = context_loader.get_course_context(course_id)
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
        chapter_ctx = context_loader.get_chapter_context(chapter_id)
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
        lesson_ctx = context_loader.get_lesson_content(lesson_id)
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
        method_ctx = method_loader.get_learning_method_data(method_id)
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
        files = file_loader.get_course_files(course_id)
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
        progress = progress_loader.get_user_progress(user_id, course_id)
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
