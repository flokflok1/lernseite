"""
i18n Service
============
Service for internationalization with AI moderation support.
"""

from typing import Optional, Dict, List, Any
from app.database.connection import fetch_one, fetch_all, execute_query
from app.services.cache_service import CacheService
import logging

logger = logging.getLogger(__name__)


class I18nService:
    """Service for managing translations and i18n operations."""

    # Cache TTL for bundles (1 hour)
    BUNDLE_CACHE_TTL = 3600

    # Cached primary language code
    _primary_language: Optional[str] = None

    @staticmethod
    def get_primary_language() -> str:
        """Get the primary language code from database (cached)."""
        if I18nService._primary_language:
            return I18nService._primary_language

        try:
            query = "SELECT language_code FROM supported_languages WHERE is_primary = TRUE LIMIT 1"
            result = fetch_one(query)
            if result:
                I18nService._primary_language = result['language_code']
                return I18nService._primary_language
        except Exception as e:
            logger.warning(f"Could not fetch primary language: {e}")

        # Fallback to German
        return 'de'

    @staticmethod
    def invalidate_primary_language_cache():
        """Clear cached primary language."""
        I18nService._primary_language = None

    @staticmethod
    def get_bundle(language_code: str, namespace: Optional[str] = None) -> Dict[str, str]:
        """
        Get translation bundle for a language.
        Uses database function with fallback support.
        """
        cache_key = f"i18n:bundle:{language_code}:{namespace or 'all'}"

        # Try cache first
        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        try:
            # Cast parameters to varchar for PostgreSQL function call
            query = "SELECT get_i18n_bundle(%s::varchar, %s::varchar) AS bundle"
            result = fetch_one(query, (language_code, namespace))

            if result and result.get('bundle'):
                bundle = result['bundle']
                CacheService.cache_set(cache_key, bundle, I18nService.BUNDLE_CACHE_TTL)
                return bundle

            return {}
        except Exception as e:
            logger.error(f"Error fetching i18n bundle: {e}")
            return {}

    @staticmethod
    def get_languages() -> List[Dict[str, Any]]:
        """Get all available languages with progress statistics."""
        cache_key = "i18n:languages"

        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        primary_lang = I18nService.get_primary_language()

        try:
            # Get total keys count
            key_count_query = "SELECT COUNT(*) as cnt FROM i18n_keys WHERE TRUE"
            key_count_result = fetch_one(key_count_query)
            total_keys = key_count_result['cnt'] if key_count_result else 0

            query = """
                SELECT
                    sl.language_code,
                    sl.language_name,
                    sl.native_name,
                    sl.flag_emoji,
                    COALESCE(sl.is_primary, FALSE) as is_primary,
                    COALESCE(sl.priority, 100) as priority,
                    sl.fallback_language,
                    COALESCE(sl.rtl, FALSE) as rtl,
                    sl.active,
                    %s as total_keys,
                    COALESCE(trans_count.cnt, 0) as translated_keys,
                    CASE WHEN %s > 0 THEN ROUND(COALESCE(trans_count.cnt, 0) * 100.0 / %s) ELSE 0 END as completion_percent,
                    0 as verified_keys,
                    0 as pending_suggestions
                FROM supported_languages sl
                LEFT JOIN (
                    SELECT language_code, COUNT(*) as cnt
                    FROM i18n_translations
                    GROUP BY language_code
                ) trans_count ON sl.language_code = trans_count.language_code
                WHERE sl.active = TRUE
                ORDER BY sl.priority, sl.language_name
            """
            result = fetch_all(query, (total_keys, total_keys, total_keys))
            languages = result if result else []

            CacheService.cache_set(cache_key, languages, 300)
            return languages
        except Exception as e:
            logger.error(f"Error fetching languages: {e}")
            return []

    @staticmethod
    def get_language_progress(language_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed progress for a specific language."""
        try:
            # Get total keys count
            key_count_query = "SELECT COUNT(*) as cnt FROM i18n_keys WHERE TRUE"
            key_count_result = fetch_one(key_count_query)
            total_keys = key_count_result['cnt'] if key_count_result else 0

            query = """
                SELECT
                    sl.language_code,
                    sl.language_name,
                    sl.native_name,
                    sl.flag_emoji,
                    COALESCE(sl.is_primary, FALSE) as is_primary,
                    COALESCE(sl.priority, 100) as priority,
                    sl.fallback_language,
                    sl.active,
                    %s as total_keys,
                    COALESCE(trans_count.cnt, 0) as translated_keys,
                    CASE WHEN %s > 0 THEN ROUND(COALESCE(trans_count.cnt, 0) * 100.0 / %s) ELSE 0 END as completion_percent
                FROM supported_languages sl
                LEFT JOIN (
                    SELECT language_code, COUNT(*) as cnt
                    FROM i18n_translations
                    WHERE language_code = %s
                    GROUP BY language_code
                ) trans_count ON sl.language_code = trans_count.language_code
                WHERE sl.language_code = %s
            """
            progress = fetch_one(query, (total_keys, total_keys, total_keys, language_code, language_code))

            if not progress:
                return None

            return {
                'progress': progress,
                'missing_sample': []
            }
        except Exception as e:
            logger.error(f"Error fetching language progress: {e}")
            return None

    @staticmethod
    def submit_suggestion(
        user_id: str,
        language_code: str,
        suggested_value: str,
        translation_id: Optional[str] = None,
        key_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Optional[str]:
        """Submit a translation suggestion."""
        try:
            query = """
                INSERT INTO i18n_suggestions
                    (translation_id, key_id, language_code, suggested_value, reason, suggested_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING suggestion_id
            """
            result = fetch_one(query, (
                translation_id, key_id, language_code, suggested_value, reason, user_id
            ))

            if result:
                I18nService.invalidate_cache(language_code)
                return str(result['suggestion_id'])

            return None
        except Exception as e:
            logger.error(f"Error submitting suggestion: {e}")
            return None

    @staticmethod
    def vote_suggestion(user_id: str, suggestion_id: str, vote_type: str) -> bool:
        """Vote for a translation suggestion."""
        try:
            query = """
                INSERT INTO i18n_suggestion_votes (suggestion_id, user_id, vote_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (suggestion_id, user_id)
                DO UPDATE SET vote_type = EXCLUDED.vote_type
            """
            execute_query(query, (suggestion_id, user_id, vote_type))
            return True
        except Exception as e:
            logger.error(f"Error voting suggestion: {e}")
            return False

    @staticmethod
    def get_suggestions(
        language_code: Optional[str] = None,
        status: str = 'pending',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get translation suggestions."""
        try:
            query = """
                SELECT
                    s.suggestion_id,
                    s.translation_id,
                    s.key_id,
                    s.language_code,
                    s.suggested_value,
                    s.reason,
                    s.suggested_by,
                    u.username as suggested_by_username,
                    s.suggested_at,
                    s.votes_up,
                    s.votes_down,
                    s.vote_score,
                    s.status,
                    t.value as current_value,
                    COALESCE(k.key_path, '') as key_path
                FROM i18n_suggestions s
                LEFT JOIN users u ON s.suggested_by = u.user_id
                LEFT JOIN i18n_translations t ON s.translation_id = t.translation_id
                LEFT JOIN i18n_keys k ON COALESCE(s.key_id, t.key_id) = k.key_id
                WHERE s.status = %s
                AND (%s IS NULL OR s.language_code = %s)
                ORDER BY s.vote_score DESC, s.suggested_at DESC
                LIMIT %s
            """
            return fetch_all(query, (status, language_code, language_code, limit)) or []
        except Exception as e:
            logger.error(f"Error fetching suggestions: {e}")
            return []

    @staticmethod
    def request_translation(
        user_id: str,
        target_language: str,
        scope: str = 'full',
        namespace_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Request translation for a language (on-demand)."""
        try:
            check_query = """
                SELECT request_id, request_count
                FROM i18n_translation_requests
                WHERE target_language = %s AND scope = %s
                AND status IN ('pending', 'processing')
            """
            existing = fetch_one(check_query, (target_language, scope))

            if existing:
                update_query = """
                    UPDATE i18n_translation_requests
                    SET request_count = request_count + 1, priority = priority + 1
                    WHERE request_id = %s
                    RETURNING request_id, request_count
                """
                result = fetch_one(update_query, (existing['request_id'],))
            else:
                insert_query = """
                    INSERT INTO i18n_translation_requests
                        (target_language, scope, namespace_id, requested_by)
                    VALUES (%s, %s, %s, %s)
                    RETURNING request_id, request_count
                """
                result = fetch_one(insert_query, (
                    target_language, scope, namespace_id, user_id
                ))

            return result
        except Exception as e:
            logger.error(f"Error requesting translation: {e}")
            return None

    @staticmethod
    def get_moderation_dashboard() -> List[Dict[str, Any]]:
        """Get moderation dashboard data."""
        try:
            query = """
                SELECT
                    sl.language_code,
                    sl.language_name,
                    sl.flag_emoji,
                    0 AS pending_count,
                    0 AS ai_reviewing_count,
                    0 AS awaiting_human_count,
                    0 AS pending_suggestions,
                    0 AS ai_reviews_24h,
                    NULL AS avg_quality_7d
                FROM supported_languages sl
                WHERE sl.active = TRUE
                ORDER BY sl.priority
            """
            return fetch_all(query) or []
        except Exception as e:
            logger.error(f"Error fetching moderation dashboard: {e}")
            return []

    @staticmethod
    def get_moderation_queue(
        status: Optional[str] = None,
        language_code: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get moderation queue items."""
        return []

    @staticmethod
    def review_queue_item(
        queue_id: str,
        user_id: str,
        decision: str,
        comment: Optional[str] = None
    ) -> bool:
        """Human review of a queue item."""
        return True

    @staticmethod
    def get_namespaces() -> List[Dict[str, Any]]:
        """Get all i18n namespaces."""
        try:
            query = """
                SELECT
                    n.namespace_id,
                    n.namespace_code,
                    n.name,
                    n.description,
                    n.icon,
                    n.sort_order,
                    0 as key_count
                FROM i18n_namespaces n
                WHERE n.is_active = TRUE
                ORDER BY n.sort_order
            """
            return fetch_all(query) or []
        except Exception as e:
            logger.error(f"Error fetching namespaces: {e}")
            return []

    @staticmethod
    def get_keys(
        namespace_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get translation keys with pagination."""
        try:
            # Build WHERE conditions
            conditions = ["1=1"]  # Always true base condition
            params = []

            if namespace_id:
                conditions.append("k.namespace_id = %s")
                params.append(namespace_id)

            if search:
                conditions.append("(k.key_path ILIKE %s OR k.context ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])

            where_clause = " AND ".join(conditions)

            # Count total
            count_query = f"""
                SELECT COUNT(*) as total
                FROM i18n_keys k
                WHERE {where_clause}
            """
            count_result = fetch_one(count_query, tuple(params))
            total = count_result['total'] if count_result else 0

            primary_lang = I18nService.get_primary_language()

            # Get keys with translation counts
            query = f"""
                SELECT
                    k.key_id,
                    k.namespace_id,
                    n.namespace_code,
                    k.key_path,
                    k.context as description,
                    k.context as context_hint,
                    k.max_length,
                    k.placeholders,
                    TRUE as is_active,
                    k.created_at,
                    (SELECT value FROM i18n_translations WHERE key_id = k.key_id AND language_code = %s LIMIT 1) as primary_value,
                    (SELECT COUNT(*) FROM i18n_translations WHERE key_id = k.key_id) as translation_count,
                    (SELECT COUNT(*) FROM supported_languages WHERE active = TRUE) as total_languages
                FROM i18n_keys k
                LEFT JOIN i18n_namespaces n ON k.namespace_id = n.namespace_id
                WHERE {where_clause}
                ORDER BY n.sort_order, k.key_path
                LIMIT %s OFFSET %s
            """
            # Insert primary_lang at the beginning of params
            params.insert(0, primary_lang)
            params.extend([limit, offset])
            keys = fetch_all(query, tuple(params)) or []

            return {
                'keys': keys,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        except Exception as e:
            logger.error(f"Error fetching keys: {e}")
            return {'keys': [], 'total': 0, 'limit': limit, 'offset': offset}

    @staticmethod
    def get_key_translations(key_id: str) -> List[Dict[str, Any]]:
        """Get all translations for a key."""
        try:
            query = """
                SELECT
                    t.translation_id,
                    t.key_id,
                    t.language_code,
                    sl.language_name,
                    sl.native_name,
                    sl.flag_emoji,
                    t.value,
                    t.is_verified,
                    t.is_machine_translated,
                    t.translator_id,
                    u.username as translator_name,
                    t.created_at,
                    t.updated_at
                FROM i18n_translations t
                JOIN supported_languages sl ON t.language_code = sl.language_code
                LEFT JOIN users u ON t.translator_id = u.user_id
                WHERE t.key_id = %s
                ORDER BY sl.priority, sl.language_code
            """
            return fetch_all(query, (key_id,)) or []
        except Exception as e:
            logger.error(f"Error fetching key translations: {e}")
            return []

    @staticmethod
    def create_key(
        namespace_id: int,
        key_path: str,
        description: Optional[str] = None,
        context_hint: Optional[str] = None,
        max_length: Optional[int] = None,
        placeholders: Optional[List[str]] = None
    ) -> Optional[int]:
        """Create a new translation key."""
        try:
            import json
            query = """
                INSERT INTO i18n_keys (namespace_id, key_path, description, context_hint, max_length, placeholders)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING key_id
            """
            result = fetch_one(query, (
                namespace_id, key_path, description, context_hint, max_length,
                json.dumps(placeholders) if placeholders else None
            ))
            return result['key_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating key: {e}")
            return None

    @staticmethod
    def set_translation(
        key_id: str,
        language_code: str,
        value: str,
        translator_id: Optional[str] = None,
        is_machine_translated: bool = False
    ) -> bool:
        """Set or update a translation."""
        try:
            source = 'ai' if is_machine_translated else 'manual'
            query = """
                INSERT INTO i18n_translations (key_id, language_code, value, created_by, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (key_id, language_code)
                DO UPDATE SET
                    value = EXCLUDED.value,
                    created_by = COALESCE(EXCLUDED.created_by, i18n_translations.created_by),
                    source = EXCLUDED.source,
                    updated_at = NOW()
            """
            execute_query(query, (key_id, language_code, value, translator_id, source))
            I18nService.invalidate_cache(language_code)
            return True
        except Exception as e:
            logger.error(f"Error setting translation: {e}")
            return False

    @staticmethod
    def generate_ai_translation(
        key_id: int,
        target_language: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Generate AI translation for a key."""
        from app.services.ai_adapter import AIAdapter

        primary_lang = I18nService.get_primary_language()

        try:
            # Get key info and primary language source
            key_query = """
                SELECT
                    k.key_path,
                    k.context as description,
                    k.context as context_hint,
                    k.placeholders,
                    n.namespace_code,
                    t.value as source_value,
                    sl.language_name as source_language_name
                FROM i18n_keys k
                LEFT JOIN i18n_namespaces n ON k.namespace_id = n.namespace_id
                LEFT JOIN i18n_translations t ON k.key_id = t.key_id AND t.language_code = %s
                LEFT JOIN supported_languages sl ON sl.language_code = %s
                WHERE k.key_id = %s
            """
            key_info = fetch_one(key_query, (primary_lang, primary_lang, key_id))

            if not key_info or not key_info.get('source_value'):
                return {'success': False, 'error': f'No {primary_lang.upper()} source text found'}

            # Get target language info
            lang_query = "SELECT language_name, native_name FROM supported_languages WHERE language_code = %s"
            lang_info = fetch_one(lang_query, (target_language,))

            if not lang_info:
                return {'success': False, 'error': 'Target language not found'}

            source_lang_name = key_info.get('source_language_name', 'German')

            # Build AI prompt
            prompt = f"""Translate the following {source_lang_name} text to {lang_info['language_name']} ({lang_info['native_name']}).

Context: This is a UI text for key "{key_info['key_path']}" in namespace "{key_info['namespace_code']}".
{f"Description: {key_info['description']}" if key_info.get('description') else ""}
{f"Context hint: {key_info['context_hint']}" if key_info.get('context_hint') else ""}
{f"Placeholders to preserve: {key_info['placeholders']}" if key_info.get('placeholders') else ""}

{source_lang_name} text:
{key_info['source_value']}

IMPORTANT:
- Keep any placeholders like {{name}}, {{count}}, etc. unchanged
- Match the tone and formality of the original
- Keep it concise - this is UI text
- Return ONLY the translated text, nothing else"""

            # Call AI
            result = AIAdapter.generate_content(
                prompt=prompt,
                provider='anthropic',
                user_id=user_id,
                max_tokens=500
            )

            if result and result.get('content'):
                translated_text = result['content'].strip()

                # Save translation
                I18nService.set_translation(
                    key_id=key_id,
                    language_code=target_language,
                    value=translated_text,
                    translator_id=user_id,
                    is_machine_translated=True
                )

                return {
                    'success': True,
                    'translation': translated_text,
                    'tokens_used': result.get('tokens_used', 0)
                }

            return {'success': False, 'error': 'AI generation failed'}

        except Exception as e:
            logger.error(f"Error generating AI translation: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def bulk_generate_translations(
        target_language: str,
        namespace_id: Optional[int] = None,
        user_id: str = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Generate AI translations for multiple missing keys."""
        primary_lang = I18nService.get_primary_language()

        try:
            # Find keys missing translations for target language
            query = """
                SELECT k.key_id, k.key_path
                FROM i18n_keys k
                WHERE NOT EXISTS (
                    SELECT 1 FROM i18n_translations t
                    WHERE t.key_id = k.key_id AND t.language_code = %s
                )
                AND EXISTS (
                    SELECT 1 FROM i18n_translations t
                    WHERE t.key_id = k.key_id AND t.language_code = %s
                )
            """
            params = [target_language, primary_lang]

            if namespace_id:
                query += " AND k.namespace_id = %s"
                params.append(namespace_id)

            query += " LIMIT %s"
            params.append(limit)

            missing_keys = fetch_all(query, tuple(params)) or []

            results = {
                'total': len(missing_keys),
                'success': 0,
                'failed': 0,
                'tokens_used': 0,
                'details': []
            }

            for key in missing_keys:
                result = I18nService.generate_ai_translation(
                    key_id=key['key_id'],
                    target_language=target_language,
                    user_id=user_id
                )

                if result and result.get('success'):
                    results['success'] += 1
                    results['tokens_used'] += result.get('tokens_used', 0)
                else:
                    results['failed'] += 1

                results['details'].append({
                    'key_path': key['key_path'],
                    'success': result.get('success', False) if result else False,
                    'error': result.get('error') if result else 'Unknown error'
                })

            I18nService.invalidate_cache(target_language)
            return results

        except Exception as e:
            logger.error(f"Error in bulk translation: {e}")
            return {'error': str(e)}

    @staticmethod
    def get_ai_config() -> Dict[str, Any]:
        """Get AI moderation configuration."""
        try:
            query = "SELECT config_key, config_value FROM i18n_ai_config"
            rows = fetch_all(query) or []
            return {row['config_key']: row['config_value'] for row in rows}
        except Exception as e:
            logger.error(f"Error fetching AI config: {e}")
            return {}

    @staticmethod
    def update_ai_config(config_key: str, config_value: Any, user_id: str) -> bool:
        """
        Update a single AI config value.

        Args:
            config_key: The config key to update (e.g., 'moderation_model')
            config_value: The new value (will be stored as JSONB)
            user_id: The user making the change

        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            # Convert value to JSON string for JSONB storage
            json_value = json.dumps(config_value)

            query = """
                INSERT INTO i18n_ai_config (config_key, config_value, updated_by, updated_at)
                VALUES (%s, %s::jsonb, %s, NOW())
                ON CONFLICT (config_key) DO UPDATE SET
                    config_value = EXCLUDED.config_value,
                    updated_by = EXCLUDED.updated_by,
                    updated_at = NOW()
            """
            execute_query(query, (config_key, json_value, user_id))
            logger.info(f"Updated i18n config '{config_key}' by user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating AI config '{config_key}': {e}")
            return False

    @staticmethod
    def invalidate_cache(language_code: Optional[str] = None):
        """Invalidate i18n cache."""
        try:
            if language_code:
                CacheService.cache_delete(f"i18n:bundle:{language_code}:all")
            else:
                CacheService.cache_delete("i18n:*")
            CacheService.cache_delete("i18n:languages")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
