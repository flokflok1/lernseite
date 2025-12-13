"""
LernsystemX Admin AI Studio - Utility Functions

Helper functions for AI Studio chat and content generation:
- build_chat_context: Build context information for chat
- analyze_chat_intent: Analyze user message intent
- get_info_response: Get information response without AI
- get_fallback_response: Generate fallback response when AI unavailable
- generate_chat_actions: Generate action buttons based on conversation

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
Module split according to 35_Developer-Guide-KI-Prompts.md guidelines
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

from app.repositories.course_repository import CourseRepository
from app.repositories.chapter_repository import ChapterRepository


def build_chat_context(user_id: str, course_id: Optional[str], context: dict) -> Dict[str, Any]:
    """
    Build context information for chat.

    Gathers all relevant information about the current course, chapter,
    and selected files to provide context for AI chat responses.

    Args:
        user_id: Current user's ID
        course_id: Optional course ID
        context: Context dictionary with mode, chapter_id, file_ids

    Returns:
        Dictionary with all gathered context information
    """
    result = {
        'user_id': user_id,
        'course_id': course_id,
        'mode': context.get('mode', 'new_chapters'),
        'files': [],
        'chapters': []
    }

    # Get course info
    if course_id:
        course = CourseRepository.find_by_id(course_id)
        if course:
            result['course_title'] = course.get('title', '')
            result['course_description'] = course.get('description', '')

    # Get chapter info if in edit mode
    chapter_id = context.get('chapter_id')
    if chapter_id:
        chapter = ChapterRepository.find_by_id(chapter_id)
        if chapter:
            result['chapter_id'] = chapter_id
            result['chapter_title'] = chapter.get('title', '')
            result['chapter_description'] = chapter.get('description', '')

    # Get file info
    file_ids = context.get('file_ids', [])
    if file_ids and course_id:
        from app.repositories.course_file_repository import CourseFileRepository
        for file_id in file_ids[:10]:  # Limit to 10 files
            try:
                file_info = CourseFileRepository.find_by_id(file_id)
                if file_info:
                    result['files'].append({
                        'file_id': file_id,
                        'filename': file_info.get('original_filename', ''),
                        'mime_type': file_info.get('mime_type', '')
                    })
            except Exception:
                pass

    # Get existing chapters for context
    if course_id:
        try:
            chapters = ChapterRepository.find_by_course(course_id)
            result['chapters'] = [
                {'chapter_id': c['chapter_id'], 'title': c.get('title', ''), 'order': c.get('order_index', 0)}
                for c in chapters[:20]
            ]
        except Exception:
            pass

    return result


def analyze_chat_intent(message: str) -> Dict[str, str]:
    """
    Analyze user message intent.

    Determines whether the user is asking for information or
    requesting content generation.

    Args:
        message: User's chat message

    Returns:
        Dictionary with 'type' (info/generate) and additional context
    """
    message_lower = message.lower()

    # Information queries
    info_keywords = ['was kann', 'was ist', 'wie funktioniert', 'erklaere', 'hilfe', 'help']
    for keyword in info_keywords:
        if keyword in message_lower:
            return {'type': 'info', 'topic': 'general'}

    # Chapter creation
    if any(w in message_lower for w in ['kapitel erstellen', 'neues kapitel', 'kapitel anlegen']):
        return {'type': 'generate', 'action': 'create_chapter'}

    # Lesson creation
    if any(w in message_lower for w in ['lektion erstellen', 'lektionen', 'unterricht']):
        return {'type': 'generate', 'action': 'create_lessons'}

    # Learning methods
    if any(w in message_lower for w in ['lernmethode', 'quiz', 'uebung', 'methode']):
        return {'type': 'generate', 'action': 'create_methods'}

    # Analysis
    if any(w in message_lower for w in ['analysier', 'struktur', 'vorschlag']):
        return {'type': 'generate', 'action': 'analyze'}

    # Default: let AI handle it
    return {'type': 'generate', 'action': 'general'}


def get_info_response(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get information response without AI.

    Returns pre-defined helpful information for common questions
    without needing to call the AI service.

    Args:
        topic: The topic to provide information about
        context: Current context with course and file information

    Returns:
        Dictionary with 'content' and optional 'actions'
    """
    responses = {
        'general': {
            'content': """Mit dem KI-Authoring-Studio kannst du:

- **Dateien analysieren** - Lade PDFs oder andere Dokumente hoch und lasse sie analysieren
- **Kapitelstruktur erstellen** - Die KI schlaegt basierend auf deinen Inhalten eine Struktur vor
- **Lektionen generieren** - Erstelle automatisch Lektionen mit Theorie und Uebungen
- **Lernmethoden hinzufuegen** - Fuege Quiz, Karteikarten und andere Methoden hinzu

Waehle links einen Kurs und Dateien aus, um zu starten.""",
            'actions': []
        }
    }

    response = responses.get(topic, responses['general'])

    # Add context-specific actions
    if context.get('course_id') and context.get('files'):
        response['actions'].append({
            'id': 'analyze-files',
            'type': 'primary',
            'label': 'Dateien analysieren',
            'action': 'analyze_files'
        })

    return response


def get_fallback_response(message: str, context: Dict[str, Any]) -> str:
    """
    Generate fallback response when AI is unavailable.

    Provides helpful responses based on message content without
    needing AI service.

    Args:
        message: User's chat message
        context: Current context with course and file information

    Returns:
        Fallback response string
    """
    message_lower = message.lower()

    if 'kapitel' in message_lower:
        if context.get('files'):
            return f"""Ich werde ein Kapitel basierend auf den {len(context['files'])} ausgewaehlten Datei(en) erstellen.

Bitte gib mir noch folgende Informationen:
1. Wie soll das Kapitel heissen?
2. Welche Hauptthemen soll es abdecken?
3. Wie viele Lektionen soll es ungefaehr haben?"""
        else:
            return 'Um ein Kapitel zu erstellen, waehle bitte zuerst Quelldateien im "Dateien"-Tab aus.'

    if 'lektion' in message_lower:
        if context.get('chapter_id'):
            return f"""Ich erstelle Lektionen fuer "{context.get('chapter_title', 'das Kapitel')}".

Basierend auf dem Kapitelinhalt schlage ich vor:
1. Einfuehrung - Ueberblick und Lernziele
2. Grundlagen - Basiswissen und Definitionen
3. Praxis - Anwendung und Uebungen
4. Zusammenfassung - Kernpunkte und Wiederholung

Soll ich diese Lektionen erstellen?"""
        else:
            return 'Bitte waehle zuerst ein Kapitel aus, fuer das Lektionen erstellt werden sollen.'

    if 'lernmethode' in message_lower or 'quiz' in message_lower:
        return """Fuer das Kapitel empfehle ich folgende Lernmethoden:

- **Quiz (LM20)** - Multiple-Choice Fragen zum Testen
- **Karteikarten (LM13)** - Wichtige Begriffe einpraegen
- **Lueckentext (LM15)** - Aktives Erinnern foerdern
- **Mindmap (LM05)** - Zusammenhaenge visualisieren

Welche Methoden soll ich erstellen?"""

    # Default
    hints = []
    if not context.get('course_id'):
        hints.append('Waehle zuerst einen Kurs aus')
    if not context.get('files'):
        hints.append('Waehle Quelldateien im Dateien-Tab aus')
    if not context.get('chapter_id'):
        hints.append('Oder waehle ein bestehendes Kapitel zum Bearbeiten')

    return f"""Ich verstehe deine Anfrage. Um dir besser helfen zu koennen:

{chr(10).join('- ' + h for h in hints) if hints else ''}

Was moechtest du als naechstes tun?"""


def generate_chat_actions(message: str, ai_response: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate action buttons based on conversation.

    Analyzes the message and context to suggest relevant
    actions the user can take.

    Args:
        message: User's chat message
        ai_response: AI's response text
        context: Current context with course and file information

    Returns:
        List of action button dictionaries
    """
    actions = []
    message_lower = message.lower()

    # Context-based actions
    if context.get('files') and context.get('course_id'):
        if 'kapitel' in message_lower or 'struktur' in message_lower:
            actions.append({
                'id': 'create-chapter',
                'type': 'primary',
                'label': 'Kapitel erstellen',
                'action': 'create_chapter'
            })
            actions.append({
                'id': 'suggest-structure',
                'type': 'secondary',
                'label': 'Struktur anpassen',
                'action': 'edit_structure'
            })

    if context.get('chapter_id'):
        if 'lektion' in message_lower:
            actions.append({
                'id': 'create-lessons',
                'type': 'primary',
                'label': 'Lektionen erstellen',
                'action': 'create_lessons'
            })
        if 'methode' in message_lower or 'quiz' in message_lower:
            actions.append({
                'id': 'create-methods',
                'type': 'primary',
                'label': 'Alle erstellen',
                'action': 'create_all_methods'
            })
            actions.append({
                'id': 'select-methods',
                'type': 'secondary',
                'label': 'Auswaehlen',
                'action': 'select_methods'
            })

    return actions
