"""
i18n Translation Repository Part 2 - Comparison and analytics methods.

Extends TranslationRepository with:
- Similarity calculation between translation texts
- Change detection (new, changed, deleted, conflicts)
- Translation counting and statistics

No ORM - Uses psycopg3 with direct SQL and parameterized queries.
"""

from typing import Optional, Dict, Any
import difflib

from psycopg.rows import dict_row

from .translation import TranslationRepository


# ---------------------------------------------------------------------------
# Comparison methods
# ---------------------------------------------------------------------------

@staticmethod
def calculate_similarity(
    text1: Optional[str],
    text2: Optional[str]
) -> float:
    """
    Calculate similarity between two texts using SequenceMatcher.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score (0.0-1.0)
    """
    if not text1 or not text2:
        return 0.0 if (text1 or text2) else 1.0

    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.ratio()


TranslationRepository.calculate_similarity = calculate_similarity


@staticmethod
def detect_changes(
    frontend_translations: Dict[str, str],
    database_translations: Dict[str, str],
    previous_values: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Detect translation changes by comparing frontend and database versions.

    Args:
        frontend_translations: Dict of frontend translations {key: value}
        database_translations: Dict of database translations {key: value}
        previous_values: Optional dict of previous database values for change detection

    Returns:
        Dict with keys: new, changed, deleted, conflicts
        Each containing list of change records with details
    """
    previous_values = previous_values or {}

    result: Dict[str, Any] = {
        'new': [],
        'changed': [],
        'deleted': [],
        'conflicts': []
    }

    frontend_keys = set(frontend_translations.keys())
    database_keys = set(database_translations.keys())
    all_keys = frontend_keys | database_keys

    for key in all_keys:
        frontend_value = frontend_translations.get(key)
        database_value = database_translations.get(key)
        previous_value = previous_values.get(key)

        if key in frontend_keys and key not in database_keys:
            # NEW: In frontend but not in database
            result['new'].append({
                'key': key,
                'frontend_value': frontend_value,
                'database_value': None,
                'previous_value': None
            })

        elif key in database_keys and key not in frontend_keys:
            # DELETED: In database but not in frontend
            result['deleted'].append({
                'key': key,
                'frontend_value': None,
                'database_value': database_value,
                'previous_value': previous_value
            })

        elif frontend_value != database_value:
            # CHANGED or CONFLICT
            if database_value != previous_value:
                # Both frontend and database changed - CONFLICT
                similarity = TranslationRepository.calculate_similarity(
                    frontend_value, database_value
                )
                result['conflicts'].append({
                    'key': key,
                    'frontend_value': frontend_value,
                    'database_value': database_value,
                    'previous_value': previous_value,
                    'similarity': similarity
                })
            else:
                # Only frontend changed - CHANGED
                result['changed'].append({
                    'key': key,
                    'frontend_value': frontend_value,
                    'database_value': database_value,
                    'previous_value': previous_value
                })

    return result


TranslationRepository.detect_changes = detect_changes


# ---------------------------------------------------------------------------
# Analytics methods
# ---------------------------------------------------------------------------

def count_translations(
    self,
    language_code: Optional[str] = None
) -> int:
    """
    Count translations.

    Args:
        language_code: Optional language filter

    Returns:
        Number of translation entries
    """
    with self.conn.cursor() as cursor:
        if language_code:
            cursor.execute(
                "SELECT COUNT(*) FROM support_systems.translations WHERE language_code = %s",
                (language_code,)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM support_systems.translations"
            )

        return cursor.fetchone()[0]


TranslationRepository.count_translations = count_translations


def get_translation_statistics(self) -> Dict[str, Any]:
    """
    Get translation statistics.

    Returns:
        Dict with statistics by language
    """
    with self.conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT
                language_code,
                COUNT(*) as total_keys,
                COUNT(CASE WHEN updated_at = created_at THEN 1 END) as new_count,
                MAX(updated_at) as last_updated
            FROM support_systems.translations
            GROUP BY language_code
            ORDER BY language_code
            """
        )
        rows = cursor.fetchall()

        stats: Dict[str, Any] = {}
        for row in rows:
            stats[row['language_code']] = {
                'total_keys': row['total_keys'],
                'new_count': row['new_count'],
                'last_updated': row['last_updated'].isoformat() if row['last_updated'] else None
            }

        return stats


TranslationRepository.get_translation_statistics = get_translation_statistics
