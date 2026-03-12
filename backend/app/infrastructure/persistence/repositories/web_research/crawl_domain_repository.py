"""Repository for ai_pipeline.crawl_domains table."""

import json
import logging
from typing import Any, Dict, List, Optional

from app.infrastructure.persistence.database.connection import get_db_connection

logger = logging.getLogger(__name__)

# Fields that accept scalar values on update
_SCALAR_FIELDS = {
    'display_name', 'base_url', 'crawl_schedule',
    'rate_limit_seconds', 'max_pages_per_crawl', 'max_depth', 'is_active',
}

# Fields that require JSON serialization on update
_JSONB_FIELDS = {'url_patterns', 'config'}


def _row_to_dict(row) -> Dict[str, Any]:
    """Map a crawl_domains row tuple to a dictionary."""
    return {
        'domain_id': str(row[0]),
        'domain_name': row[1],
        'base_url': row[2],
        'display_name': row[3],
        'url_patterns': row[4] or [],
        'crawl_schedule': row[5],
        'rate_limit_seconds': float(row[6]) if row[6] is not None else None,
        'max_pages_per_crawl': row[7],
        'max_depth': row[8],
        'is_active': row[9],
        'last_crawled_at': row[10].isoformat() if row[10] else None,
        'total_pdfs_found': row[11],
        'config': row[12] or {},
        'created_at': row[13].isoformat() if row[13] else None,
        'updated_at': row[14].isoformat() if row[14] else None,
    }


_SELECT_COLUMNS = """
    domain_id, domain_name, base_url, display_name,
    url_patterns, crawl_schedule, rate_limit_seconds,
    max_pages_per_crawl, max_depth, is_active,
    last_crawled_at, total_pdfs_found, config,
    created_at, updated_at
"""


class CrawlDomainRepository:
    """CRUD and stats for crawl domains (ai_pipeline.crawl_domains)."""

    @staticmethod
    def find_all(active_only: bool = False) -> List[Dict[str, Any]]:
        """List all crawl domains, optionally filtered to active only.

        Args:
            active_only: When True, return only domains with is_active=True.

        Returns:
            List of domain dicts ordered by display_name.
        """
        where = "WHERE is_active = TRUE" if active_only else ""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT {_SELECT_COLUMNS}
                    FROM ai_pipeline.crawl_domains
                    {where}
                    ORDER BY display_name
                """)
                rows = cur.fetchall()

        return [_row_to_dict(row) for row in rows]

    @staticmethod
    def find_by_id(domain_id: str) -> Optional[Dict[str, Any]]:
        """Find a single crawl domain by its UUID.

        Args:
            domain_id: UUID of the domain.

        Returns:
            Domain dict or None if not found.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT {_SELECT_COLUMNS}
                    FROM ai_pipeline.crawl_domains
                    WHERE domain_id = %s
                    LIMIT 1
                """, [domain_id])
                row = cur.fetchone()

        if not row:
            return None

        return _row_to_dict(row)

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, str]:
        """Insert a new crawl domain.

        Args:
            data: Dict with keys matching crawl_domains columns.
                  Required: domain_name, base_url, display_name.

        Returns:
            Dict with 'domain_id' (str UUID) of the created row.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_pipeline.crawl_domains
                        (domain_name, base_url, display_name,
                         url_patterns, crawl_schedule,
                         rate_limit_seconds, max_pages_per_crawl,
                         max_depth, is_active, config)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING domain_id
                """, [
                    data['domain_name'],
                    data['base_url'],
                    data['display_name'],
                    json.dumps(data.get('url_patterns', [])),
                    data.get('crawl_schedule', 'weekly'),
                    data.get('rate_limit_seconds', 2),
                    data.get('max_pages_per_crawl', 100),
                    data.get('max_depth', 3),
                    data.get('is_active', True),
                    json.dumps(data.get('config', {})),
                ])
                result = cur.fetchone()
                conn.commit()

        return {'domain_id': str(result[0])}

    @staticmethod
    def update(domain_id: str, data: Dict[str, Any]) -> bool:
        """Update allowed fields for a crawl domain.

        Args:
            domain_id: UUID of the domain to update.
            data: Dict of field names to new values. Only allowed
                  scalar and JSONB fields are applied.

        Returns:
            True if a row was updated, False otherwise.
        """
        set_parts = []
        params = []

        for key, value in data.items():
            if key in _SCALAR_FIELDS:
                set_parts.append(f"{key} = %s")
                params.append(value)
            elif key in _JSONB_FIELDS:
                set_parts.append(f"{key} = %s")
                params.append(json.dumps(value))

        if not set_parts:
            logger.warning("update() called with no valid fields for %s", domain_id)
            return False

        set_parts.append("updated_at = NOW()")
        params.append(domain_id)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE ai_pipeline.crawl_domains
                    SET {', '.join(set_parts)}
                    WHERE domain_id = %s
                """, params)
                updated = cur.rowcount > 0
                conn.commit()

        return updated

    @staticmethod
    def delete(domain_id: str) -> bool:
        """Delete a crawl domain by UUID.

        Args:
            domain_id: UUID of the domain to delete.

        Returns:
            True if a row was deleted, False otherwise.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM ai_pipeline.crawl_domains
                    WHERE domain_id = %s
                """, [domain_id])
                deleted = cur.rowcount > 0
                conn.commit()

        return deleted

    @staticmethod
    def update_crawl_stats(domain_id: str, pdfs_found: int) -> bool:
        """Update crawl statistics after a crawl run.

        Sets last_crawled_at to NOW() and total_pdfs_found to the
        given count.

        Args:
            domain_id: UUID of the domain.
            pdfs_found: Total number of PDFs discovered.

        Returns:
            True if a row was updated, False otherwise.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ai_pipeline.crawl_domains
                    SET last_crawled_at = NOW(),
                        total_pdfs_found = %s,
                        updated_at = NOW()
                    WHERE domain_id = %s
                """, [pdfs_found, domain_id])
                updated = cur.rowcount > 0
                conn.commit()

        return updated
