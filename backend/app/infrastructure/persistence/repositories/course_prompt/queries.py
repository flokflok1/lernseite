"""
Shared Query Constants and Helpers for Course Prompts

Provides common SQL SELECT statements and helper functions
for course prompt queries to reduce duplication.

Part of: repositories/course_prompt package
"""

from typing import Dict, Any

# ========================================================================
# COMMON SELECT COLUMNS
# ========================================================================

COURSE_PROMPT_COLUMNS = """
    course_prompt_id::text,
    course_id::text,
    scope,
    language,
    prompt_system,
    prompt_user_template,
    metadata,
    is_active,
    created_by::text,
    created_at,
    updated_at
"""

# ========================================================================
# QUERY TEMPLATES
# ========================================================================

FIND_BY_ID_QUERY = f"""
    SELECT {COURSE_PROMPT_COLUMNS}
    FROM courses.course_prompts
    WHERE course_prompt_id = %s
"""

FIND_BY_COURSE_ACTIVE_QUERY = f"""
    SELECT {COURSE_PROMPT_COLUMNS}
    FROM courses.course_prompts
    WHERE course_id = %s AND is_active = TRUE
    ORDER BY scope, language NULLS FIRST
"""

FIND_BY_COURSE_ALL_QUERY = f"""
    SELECT {COURSE_PROMPT_COLUMNS}
    FROM courses.course_prompts
    WHERE course_id = %s
    ORDER BY scope, language NULLS FIRST
"""

FIND_BY_COURSE_AND_SCOPE_QUERY_NO_LANG = f"""
    SELECT {COURSE_PROMPT_COLUMNS}
    FROM courses.course_prompts
    WHERE course_id = %s
      AND scope = %s
      AND language IS NULL
      AND is_active = TRUE
"""

FIND_BY_COURSE_AND_SCOPE_QUERY_WITH_LANG = f"""
    SELECT {COURSE_PROMPT_COLUMNS}
    FROM courses.course_prompts
    WHERE course_id = %s
      AND scope = %s
      AND language = %s
      AND is_active = TRUE
"""

FIND_BY_SCOPE_ACTIVE_QUERY = f"""
    SELECT {COURSE_PROMPT_COLUMNS}
    FROM courses.course_prompts
    WHERE scope = %s AND is_active = TRUE
    ORDER BY created_at DESC
"""

FIND_BY_SCOPE_ALL_QUERY = f"""
    SELECT {COURSE_PROMPT_COLUMNS}
    FROM courses.course_prompts
    WHERE scope = %s
    ORDER BY created_at DESC
"""

COUNT_BY_COURSE_QUERY = """
    SELECT COUNT(*)
    FROM courses.course_prompts
    WHERE course_id = %s AND is_active = TRUE
"""

COUNT_BY_SCOPE_QUERY = """
    SELECT COUNT(DISTINCT course_id)
    FROM courses.course_prompts
    WHERE scope = %s AND is_active = TRUE
"""


def get_insert_returning() -> str:
    """Get INSERT statement with RETURNING clause."""
    return f"""
        INSERT INTO course_prompts (
            course_id,
            scope,
            language,
            prompt_system,
            prompt_user_template,
            metadata,
            is_active,
            created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING {COURSE_PROMPT_COLUMNS}
    """


def get_upsert_returning() -> str:
    """Get UPSERT statement with RETURNING clause."""
    return f"""
        INSERT INTO course_prompts (
            course_id,
            scope,
            language,
            prompt_system,
            prompt_user_template,
            metadata,
            is_active,
            created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (course_id, scope, language)
        DO UPDATE SET
            prompt_system = EXCLUDED.prompt_system,
            prompt_user_template = EXCLUDED.prompt_user_template,
            metadata = EXCLUDED.metadata,
            is_active = EXCLUDED.is_active
        RETURNING {COURSE_PROMPT_COLUMNS}
    """


def build_update_query(
    language: bool = False,
    prompt_system: bool = False,
    prompt_user_template: bool = False,
    metadata: bool = False,
    is_active: bool = False
) -> str:
    """
    Build a dynamic UPDATE query based on provided flags.

    Args:
        language: Include language in update
        prompt_system: Include prompt_system in update
        prompt_user_template: Include prompt_user_template in update
        metadata: Include metadata in update
        is_active: Include is_active in update

    Returns:
        UPDATE query string with RETURNING clause
    """
    update_fields = []

    if language:
        update_fields.append("language = %s")
    if prompt_system:
        update_fields.append("prompt_system = %s")
    if prompt_user_template:
        update_fields.append("prompt_user_template = %s")
    if metadata:
        update_fields.append("metadata = %s")
    if is_active:
        update_fields.append("is_active = %s")

    fields_str = ', '.join(update_fields)
    return f"""
        UPDATE courses.course_prompts
        SET {fields_str}
        WHERE course_prompt_id = %s
        RETURNING {COURSE_PROMPT_COLUMNS}
    """
