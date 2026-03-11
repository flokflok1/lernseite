"""Repository for ai_pipeline.web_research_cache table."""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from app.infrastructure.persistence.database.connection import get_db_connection

logger = logging.getLogger(__name__)

DEFAULT_TTL_DAYS = 7


class ResearchCacheRepository:
    """CRUD for web research cache entries."""

    @staticmethod
    def find_cached(
        position_id: int, language: str = 'de',
    ) -> Optional[Dict[str, Any]]:
        """Find cached research result. Returns None if not found or expired."""
        cache_key = f"pos:{position_id}:lang:{language}"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT cache_id, summary, key_points, difficulty_level,
                           recommended_study_time_minutes, sources,
                           grounding_status, queries_used, search_language,
                           created_at
                    FROM ai_pipeline.web_research_cache
                    WHERE cache_key = %s AND expires_at > NOW()
                    LIMIT 1
                """, [cache_key])
                row = cur.fetchone()

        if not row:
            return None

        ResearchCacheRepository._increment_access(cache_key)

        return {
            'cache_id': str(row[0]),
            'summary': row[1],
            'key_points': row[2] or [],
            'difficulty_level': row[3],
            'recommended_study_time_minutes': row[4],
            'sources': row[5] or [],
            'grounding_status': row[6],
            'queries_used': row[7] or [],
            'search_language': row[8],
            'created_at': row[9].isoformat() if row[9] else None,
            'cached': True,
        }

    @staticmethod
    def save(
        position_id: int, language: str, summary: str,
        key_points: list, sources: list, grounding_status: str,
        queries_used: list, search_language: str,
        difficulty_level: str = None, study_time_minutes: int = None,
        ttl_days: int = DEFAULT_TTL_DAYS,
    ) -> str:
        """Save research result. Upserts on cache_key. Returns cache_id."""
        cache_key = f"pos:{position_id}:lang:{language}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl_days)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_pipeline.web_research_cache
                        (position_id, language, cache_key, summary,
                         key_points, difficulty_level,
                         recommended_study_time_minutes, sources,
                         grounding_status, queries_used,
                         search_language, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cache_key) DO UPDATE SET
                        summary = EXCLUDED.summary,
                        key_points = EXCLUDED.key_points,
                        difficulty_level = EXCLUDED.difficulty_level,
                        recommended_study_time_minutes = EXCLUDED.recommended_study_time_minutes,
                        sources = EXCLUDED.sources,
                        grounding_status = EXCLUDED.grounding_status,
                        queries_used = EXCLUDED.queries_used,
                        search_language = EXCLUDED.search_language,
                        expires_at = EXCLUDED.expires_at,
                        access_count = 0
                    RETURNING cache_id
                """, [
                    position_id, language, cache_key, summary,
                    json.dumps(key_points), difficulty_level,
                    study_time_minutes, json.dumps(sources),
                    grounding_status, json.dumps(queries_used),
                    search_language, expires_at,
                ])
                result = cur.fetchone()
                conn.commit()

        cache_id = str(result[0]) if result else None
        logger.info(
            "Cached research for position %d (%s), expires %s",
            position_id, language, expires_at.date(),
        )
        return cache_id

    @staticmethod
    def _increment_access(cache_key: str) -> None:
        """Increment access count (best-effort)."""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE ai_pipeline.web_research_cache
                        SET access_count = access_count + 1,
                            last_accessed_at = NOW()
                        WHERE cache_key = %s
                    """, [cache_key])
                    conn.commit()
        except Exception:
            pass

    @staticmethod
    def delete_expired() -> int:
        """Delete expired entries. Returns count deleted."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM ai_pipeline.web_research_cache
                    WHERE expires_at < NOW()
                """)
                count = cur.rowcount
                conn.commit()
        if count:
            logger.info("Deleted %d expired research cache entries", count)
        return count
