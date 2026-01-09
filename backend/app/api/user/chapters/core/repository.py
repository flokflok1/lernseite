"""
LernsystemX Chapter Theory Repository

Database access functions for chapter theory content.
All DB operations use direct SQL with psycopg connection pooling.

Functions:
    - get_chapter_theory: Get theory by chapter_id and style
    - get_chapter_theory_by_id: Get theory by ID
    - list_chapter_theories: List all theories for a chapter
    - save_chapter_theory: Create new chapter theory
    - update_chapter_theory_title: Update theory title
    - delete_chapter_theory_by_id: Delete theory by ID
    - get_chapter_info: Get chapter with course context
    - get_chapter_lessons: Get lessons in chapter

DDD Refactored: 2026-01-08 - Moved to core/
Repository Pattern per Developer-Guide-KI
"""

from datetime import datetime
import json
import logging
from typing import Optional

from app.database.connection import fetch_one, fetch_all

logger = logging.getLogger(__name__)


def get_chapter_theory(chapter_id: str, style: str = 'adhs') -> Optional[dict]:
    """Get chapter theory from database (legacy - gets first match).

    Args:
        chapter_id: UUID of the chapter
        style: Theory style (adhs, detailed, short, exam_focus, standard)

    Returns:
        Theory record dict or None if not found
    """
    query = """
        SELECT
            theory_id, chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE chapter_id = %s AND style = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    return fetch_one(query, (chapter_id, style))


def get_chapter_theory_by_id(theory_id: str) -> Optional[dict]:
    """Get chapter theory by ID.

    Args:
        theory_id: UUID of the theory record

    Returns:
        Theory record dict or None if not found
    """
    query = """
        SELECT
            theory_id, chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE theory_id = %s
    """
    return fetch_one(query, (theory_id,))


def list_chapter_theories(chapter_id: str) -> list:
    """List all theories for a chapter.

    Args:
        chapter_id: UUID of the chapter

    Returns:
        List of theory records, ordered by creation date descending
    """
    query = """
        SELECT
            theory_id, chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE chapter_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (chapter_id,)) or []


def save_chapter_theory(
    chapter_id: str,
    style: str,
    theory_data: dict,
    title: Optional[str] = None,
    audio_url: Optional[str] = None,
    audio_duration: Optional[int] = None,
    tokens_used: int = 0,
    model_used: Optional[str] = None,
    user_id: Optional[str] = None
) -> dict:
    """Create new chapter theory (always creates new, no upsert).

    Args:
        chapter_id: UUID of the chapter
        style: Theory style (adhs, detailed, short, exam_focus, standard)
        theory_data: JSON-serializable theory content
        title: Optional title (auto-generated if not provided)
        audio_url: Optional URL to TTS audio
        audio_duration: Optional audio duration in seconds
        tokens_used: Number of tokens used for generation
        model_used: AI model identifier
        user_id: UUID of user who generated the theory

    Returns:
        Created theory record
    """
    # Generate default title if not provided
    if not title:
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
        style_names = {
            'adhs': 'ADHS-freundlich',
            'detailed': 'Ausfuehrlich',
            'short': 'Kurz & Kompakt',
            'exam_focus': 'Pruefungsfokus',
            'standard': 'Standard'
        }
        style_name = style_names.get(style, style)
        title = f"{style_name} ({timestamp})"

    query = """
        INSERT INTO chapter_theory (
            chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING theory_id, chapter_id, style, title, created_at, updated_at
    """
    result = fetch_one(query, (
        chapter_id, style, title, json.dumps(theory_data),
        audio_url, audio_duration,
        tokens_used, model_used, user_id
    ))
    logger.info(f"Created chapter theory: {result}")
    return result


def update_chapter_theory_title(theory_id: str, title: str) -> Optional[dict]:
    """Update the title of a chapter theory.

    Args:
        theory_id: UUID of the theory record
        title: New title

    Returns:
        Updated record or None if not found
    """
    query = """
        UPDATE chapter_theory
        SET title = %s, updated_at = NOW()
        WHERE theory_id = %s
        RETURNING theory_id, title, updated_at
    """
    return fetch_one(query, (title, theory_id))


def delete_chapter_theory_by_id(theory_id: str) -> bool:
    """Delete a specific chapter theory by ID.

    Args:
        theory_id: UUID of the theory record

    Returns:
        True if deleted, False if not found
    """
    query = """
        DELETE FROM chapter_theory
        WHERE theory_id = %s
        RETURNING theory_id
    """
    result = fetch_one(query, (theory_id,))
    return result is not None


def delete_chapter_theory_by_style(chapter_id: str, style: Optional[str] = None) -> bool:
    """Delete chapter theory by chapter_id and optional style.

    Args:
        chapter_id: UUID of the chapter
        style: Optional style filter. If None, deletes ALL theories for chapter.

    Returns:
        True if any deleted, False if none found
    """
    if style:
        query = """
            DELETE FROM chapter_theory
            WHERE chapter_id = %s AND style = %s
            RETURNING theory_id
        """
        result = fetch_one(query, (chapter_id, style))
    else:
        query = """
            DELETE FROM chapter_theory
            WHERE chapter_id = %s
            RETURNING theory_id
        """
        result = fetch_one(query, (chapter_id,))

    return result is not None


def get_chapter_info(chapter_id: str) -> Optional[dict]:
    """Get chapter with course info for context.

    Args:
        chapter_id: UUID of the chapter

    Returns:
        Chapter record with course title or None
    """
    query = """
        SELECT
            c.chapter_id, c.title, c.description, c.order_index,
            co.course_id, co.title as course_title
        FROM chapters c
        JOIN courses co ON c.course_id = co.course_id
        WHERE c.chapter_id = %s
    """
    return fetch_one(query, (chapter_id,))


def get_chapter_lessons(chapter_id: str) -> list:
    """Get lessons in chapter for context.

    Args:
        chapter_id: UUID of the chapter

    Returns:
        List of lesson records (max 15)
    """
    query = """
        SELECT lesson_id, title, order_index
        FROM lessons
        WHERE chapter_id = %s
        ORDER BY order_index
        LIMIT 15
    """
    return fetch_all(query, (chapter_id,)) or []


def get_fallback_theory(chapter_id: str) -> Optional[dict]:
    """Get any available theory for chapter (fallback when style not found).

    Args:
        chapter_id: UUID of the chapter

    Returns:
        Most recent theory regardless of style, or None
    """
    query = """
        SELECT
            theory_id, chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE chapter_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    return fetch_one(query, (chapter_id,))
