"""Repository for ai_pipeline.crawl_discovered_urls table."""

import logging
from typing import Any, Dict, List, Optional

from app.infrastructure.persistence.database.connection import get_db_connection

logger = logging.getLogger(__name__)


def _url_to_dict(row) -> Dict[str, Any]:
    """Map a crawl_discovered_urls row to a dictionary.

    Expected column order: url_id, domain_id, job_id, url, url_type,
    status, content_hash, pdf_cache_id, relevance_score, relevance_reason,
    has_extractable_text, page_count, file_size_bytes, last_checked_at,
    last_changed_at, error_message, created_at, domain_name (optional).
    """
    result = {
        'url_id': str(row[0]),
        'domain_id': str(row[1]),
        'job_id': str(row[2]) if row[2] else None,
        'url': row[3],
        'url_type': row[4],
        'status': row[5],
        'content_hash': row[6],
        'pdf_cache_id': str(row[7]) if row[7] else None,
        'relevance_score': float(row[8]) if row[8] is not None else None,
        'relevance_reason': row[9],
        'has_extractable_text': row[10],
        'page_count': row[11],
        'file_size_bytes': row[12],
        'last_checked_at': row[13].isoformat() if row[13] else None,
        'last_changed_at': row[14].isoformat() if row[14] else None,
        'error_message': row[15],
        'created_at': row[16].isoformat() if row[16] else None,
    }
    if len(row) > 17:
        result['domain_name'] = row[17]
    return result


class CrawlUrlRepository:
    """CRUD for discovered URLs (ai_pipeline.crawl_discovered_urls)."""

    @staticmethod
    def upsert(data: Dict[str, Any]) -> str:
        """Insert or update a discovered URL by (domain_id, url).

        On conflict, updates status, content_hash, relevance_score,
        job_id, and last_checked_at.

        Args:
            data: Must contain 'domain_id', 'url', 'url_type'.
                  May contain 'job_id', 'status', 'content_hash',
                  'relevance_score', 'relevance_reason'.

        Returns:
            The url_id (str).
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_pipeline.crawl_discovered_urls
                        (domain_id, job_id, url, url_type, status,
                         content_hash, relevance_score, relevance_reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (domain_id, url) DO UPDATE SET
                        status = COALESCE(EXCLUDED.status,
                            ai_pipeline.crawl_discovered_urls.status),
                        content_hash = COALESCE(EXCLUDED.content_hash,
                            ai_pipeline.crawl_discovered_urls.content_hash),
                        relevance_score = COALESCE(EXCLUDED.relevance_score,
                            ai_pipeline.crawl_discovered_urls.relevance_score),
                        job_id = COALESCE(EXCLUDED.job_id,
                            ai_pipeline.crawl_discovered_urls.job_id),
                        last_checked_at = NOW()
                    RETURNING url_id
                """, [
                    data['domain_id'],
                    data.get('job_id'),
                    data['url'],
                    data['url_type'],
                    data.get('status', 'discovered'),
                    data.get('content_hash'),
                    data.get('relevance_score'),
                    data.get('relevance_reason'),
                ])
                row = cur.fetchone()
                conn.commit()

        url_id = str(row[0])
        logger.debug("Upserted URL %s for domain %s", data['url'], data['domain_id'])
        return url_id

    @staticmethod
    def find_by_domain(
        domain_id: str,
        url_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Find discovered URLs for a domain with optional filters.

        Args:
            domain_id: The domain UUID.
            url_type: Optional filter (e.g. 'pdf', 'html').
            status: Optional filter (e.g. 'discovered', 'downloaded').
            limit: Max rows (default 100).
        """
        clauses = ["u.domain_id = %s"]
        params: list = [domain_id]

        if url_type:
            clauses.append("u.url_type = %s")
            params.append(url_type)
        if status:
            clauses.append("u.status = %s")
            params.append(status)

        where = "WHERE " + " AND ".join(clauses)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT u.url_id, u.domain_id, u.job_id, u.url,
                           u.url_type, u.status, u.content_hash,
                           u.pdf_cache_id, u.relevance_score,
                           u.relevance_reason, u.has_extractable_text,
                           u.page_count, u.file_size_bytes,
                           u.last_checked_at, u.last_changed_at,
                           u.error_message, u.created_at
                    FROM ai_pipeline.crawl_discovered_urls u
                    {where}
                    ORDER BY u.created_at DESC
                    LIMIT %s
                """, params + [limit])
                rows = cur.fetchall()

        return [_url_to_dict(r) for r in rows]

    @staticmethod
    def find_pdfs_paginated(
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        domain_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Find PDF URLs with pagination and optional search.

        Args:
            page: Page number (1-based).
            per_page: Items per page.
            search: Optional ILIKE search on url.
            domain_id: Optional domain filter.

        Returns:
            Dict with 'items' (list) and 'total' (int).
        """
        clauses = ["u.url_type = 'pdf'"]
        params: list = []

        if search:
            clauses.append("u.url ILIKE %s")
            escaped = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            params.append(f"%{escaped}%")
        if domain_id:
            clauses.append("u.domain_id = %s")
            params.append(domain_id)

        where = "WHERE " + " AND ".join(clauses)
        offset = (page - 1) * per_page

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Count total
                cur.execute(f"""
                    SELECT COUNT(*)
                    FROM ai_pipeline.crawl_discovered_urls u
                    {where}
                """, params)
                total = cur.fetchone()[0]

                # Fetch page
                cur.execute(f"""
                    SELECT u.url_id, u.domain_id, u.job_id, u.url,
                           u.url_type, u.status, u.content_hash,
                           u.pdf_cache_id, u.relevance_score,
                           u.relevance_reason, u.has_extractable_text,
                           u.page_count, u.file_size_bytes,
                           u.last_checked_at, u.last_changed_at,
                           u.error_message, u.created_at,
                           d.domain_name
                    FROM ai_pipeline.crawl_discovered_urls u
                    LEFT JOIN ai_pipeline.crawl_domains d
                        ON d.domain_id = u.domain_id
                    {where}
                    ORDER BY u.created_at DESC
                    LIMIT %s OFFSET %s
                """, params + [per_page, offset])
                rows = cur.fetchall()

        return {
            'items': [_url_to_dict(r) for r in rows],
            'total': total,
        }

    @staticmethod
    def count_by_status(
        domain_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """Count discovered URLs grouped by status.

        Args:
            domain_id: Optional domain filter.

        Returns:
            Dict mapping status to count, e.g. {'discovered': 42}.
        """
        clauses: list = []
        params: list = []

        if domain_id:
            clauses.append("domain_id = %s")
            params.append(domain_id)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT status, COUNT(*)
                    FROM ai_pipeline.crawl_discovered_urls
                    {where}
                    GROUP BY status
                """, params)
                rows = cur.fetchall()

        return {row[0]: row[1] for row in rows}

    @staticmethod
    def mark_downloaded(
        url_id: str,
        pdf_cache_id: str,
        content_hash: str,
        page_count: Optional[int] = None,
        file_size: Optional[int] = None,
        has_text: Optional[bool] = None,
    ) -> bool:
        """Update a URL record after successful download.

        Args:
            url_id: The URL UUID.
            pdf_cache_id: Reference to storage.pdf_cache.
            content_hash: SHA-256 of the downloaded content.
            page_count: Number of pages (PDFs).
            file_size: File size in bytes.
            has_text: Whether extractable text was found.

        Returns:
            True if a row was updated.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ai_pipeline.crawl_discovered_urls
                    SET status = 'downloaded',
                        pdf_cache_id = %s,
                        content_hash = %s,
                        page_count = %s,
                        file_size_bytes = %s,
                        has_extractable_text = %s,
                        last_checked_at = NOW()
                    WHERE url_id = %s
                """, [
                    pdf_cache_id, content_hash, page_count,
                    file_size, has_text, url_id,
                ])
                updated = cur.rowcount > 0
                conn.commit()

        if updated:
            logger.info("Marked URL %s as downloaded (cache %s)", url_id, pdf_cache_id)
        return updated

    @staticmethod
    def find_changed(domain_id: str) -> List[Dict[str, Any]]:
        """Find URLs whose content_hash changed since last download.

        Detects content changes by comparing current content_hash
        with what was previously stored. Only returns URLs that have
        been downloaded at least once (have a pdf_cache_id).

        Args:
            domain_id: The domain UUID.

        Returns:
            List of URL dicts where content changed.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT u.url_id, u.domain_id, u.job_id, u.url,
                           u.url_type, u.status, u.content_hash,
                           u.pdf_cache_id, u.relevance_score,
                           u.relevance_reason, u.has_extractable_text,
                           u.page_count, u.file_size_bytes,
                           u.last_checked_at, u.last_changed_at,
                           u.error_message, u.created_at
                    FROM ai_pipeline.crawl_discovered_urls u
                    WHERE u.domain_id = %s
                      AND u.pdf_cache_id IS NOT NULL
                      AND u.last_changed_at > u.last_checked_at
                    ORDER BY u.last_changed_at DESC
                """, [domain_id])
                rows = cur.fetchall()

        return [_url_to_dict(r) for r in rows]

    @staticmethod
    def delete(url_id: str) -> bool:
        """Delete a discovered URL record by its UUID.

        Args:
            url_id: UUID of the URL record to delete.

        Returns:
            True if a row was deleted, False otherwise.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM ai_pipeline.crawl_discovered_urls
                    WHERE url_id = %s
                """, [url_id])
                deleted = cur.rowcount > 0
                conn.commit()

        if deleted:
            logger.info("Deleted URL record %s", url_id)
        return deleted

    @staticmethod
    def get_trends(days: int = 30) -> List[Dict[str, Any]]:
        """Get daily crawl statistics over the given number of days.

        Args:
            days: Number of days to look back (default 30).

        Returns:
            List of dicts with 'date', 'pdfs_found', 'total_urls' per day.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DATE(created_at) AS day,
                           COUNT(*) FILTER (WHERE url_type = 'pdf')
                               AS pdfs_found,
                           COUNT(*) AS total_urls
                    FROM ai_pipeline.crawl_discovered_urls
                    WHERE created_at > NOW() - INTERVAL '1 day' * %s
                    GROUP BY DATE(created_at)
                    ORDER BY day
                """, [days])
                rows = cur.fetchall()

        return [
            {
                'date': row[0].isoformat(),
                'pdfs_found': row[1],
                'total_urls': row[2],
            }
            for row in rows
        ]

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Aggregate statistics across all discovered URLs.

        Returns:
            Dict with total_urls, total_pdfs, avg_relevance,
            total_size_bytes.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) AS total_urls,
                        COUNT(*) FILTER (WHERE url_type = 'pdf')
                            AS total_pdfs,
                        ROUND(AVG(relevance_score)::numeric, 2)
                            AS avg_relevance,
                        COALESCE(SUM(file_size_bytes), 0)
                            AS total_size_bytes
                    FROM ai_pipeline.crawl_discovered_urls
                """)
                row = cur.fetchone()

        return {
            'total_urls': row[0] or 0,
            'total_pdfs': row[1] or 0,
            'avg_relevance': float(row[2]) if row[2] is not None else None,
            'total_size_bytes': row[3] or 0,
        }
