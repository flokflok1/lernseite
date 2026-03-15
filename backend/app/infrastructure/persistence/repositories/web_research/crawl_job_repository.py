"""Repository for ai_pipeline.crawl_jobs table."""

import json
import logging
from typing import Any, Dict, List, Optional

from app.infrastructure.persistence.database.connection import get_db_connection

logger = logging.getLogger(__name__)


def _job_to_dict(row) -> Dict[str, Any]:
    """Map a crawl_jobs row to a dictionary.

    Expected column order: job_id, domain_id, status, started_at,
    completed_at, pages_crawled, pdfs_discovered, pdfs_downloaded,
    pdfs_new, pdfs_updated, errors_count, error_log, celery_task_id,
    progress_pct, created_at, domain_name (optional).
    """
    result = {
        'job_id': str(row[0]),
        'domain_id': str(row[1]),
        'status': row[2],
        'started_at': row[3].isoformat() if row[3] else None,
        'completed_at': row[4].isoformat() if row[4] else None,
        'pages_crawled': row[5] or 0,
        'pdfs_discovered': row[6] or 0,
        'pdfs_downloaded': row[7] or 0,
        'pdfs_new': row[8] or 0,
        'pdfs_updated': row[9] or 0,
        'errors_count': row[10] or 0,
        'error_log': row[11] or [],
        'celery_task_id': row[12],
        'progress_pct': row[13] or 0,
        'created_at': row[14].isoformat() if row[14] else None,
    }
    if len(row) > 15:
        result['domain_name'] = row[15]
    return result


class CrawlJobRepository:
    """CRUD for crawl jobs (ai_pipeline.crawl_jobs)."""

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, str]:
        """Insert a new crawl job with status='pending'.

        Args:
            data: Must contain 'domain_id'. May contain 'celery_task_id'.

        Returns:
            Dict with 'job_id'.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ai_pipeline.crawl_jobs
                        (domain_id, status, celery_task_id)
                    VALUES (%s, 'pending', %s)
                    RETURNING job_id
                """, [
                    data['domain_id'],
                    data.get('celery_task_id'),
                ])
                row = cur.fetchone()
                conn.commit()

        job_id = str(row[0])
        logger.info("Created crawl job %s for domain %s", job_id, data['domain_id'])
        return {'job_id': job_id}

    @staticmethod
    def find_by_id(job_id: str) -> Optional[Dict[str, Any]]:
        """Find a single crawl job by ID, including domain_name."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT j.job_id, j.domain_id, j.status, j.started_at,
                           j.completed_at, j.pages_crawled, j.pdfs_discovered,
                           j.pdfs_downloaded, j.pdfs_new, j.pdfs_updated,
                           j.errors_count, j.error_log, j.celery_task_id,
                           j.progress_pct, j.created_at,
                           d.domain_name
                    FROM ai_pipeline.crawl_jobs j
                    JOIN ai_pipeline.crawl_domains d
                        ON d.domain_id = j.domain_id
                    WHERE j.job_id = %s
                """, [job_id])
                row = cur.fetchone()

        if not row:
            return None
        return _job_to_dict(row)

    @staticmethod
    def find_recent(
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        domain_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return recent crawl jobs, newest first.

        Args:
            limit: Max rows to return (default 50).
            offset: Number of rows to skip (default 0).
            status: Optional filter by job status.
            domain_id: Optional filter by domain.
        """
        clauses = []
        params: list = []

        if status:
            clauses.append("j.status = %s")
            params.append(status)
        if domain_id:
            clauses.append("j.domain_id = %s")
            params.append(domain_id)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT j.job_id, j.domain_id, j.status, j.started_at,
                           j.completed_at, j.pages_crawled, j.pdfs_discovered,
                           j.pdfs_downloaded, j.pdfs_new, j.pdfs_updated,
                           j.errors_count, j.error_log, j.celery_task_id,
                           j.progress_pct, j.created_at,
                           d.domain_name
                    FROM ai_pipeline.crawl_jobs j
                    LEFT JOIN ai_pipeline.crawl_domains d
                        ON d.domain_id = j.domain_id
                    {where}
                    ORDER BY j.created_at DESC
                    LIMIT %s OFFSET %s
                """, params + [limit, offset])
                rows = cur.fetchall()

        return [_job_to_dict(r) for r in rows]

    @staticmethod
    def count(
        status: Optional[str] = None,
        domain_id: Optional[str] = None,
    ) -> int:
        """Count crawl jobs with optional filters."""
        clauses = []
        params: list = []

        if status:
            clauses.append("status = %s")
            params.append(status)
        if domain_id:
            clauses.append("domain_id = %s")
            params.append(domain_id)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT COUNT(*)
                    FROM ai_pipeline.crawl_jobs
                    {where}
                """, params)
                return cur.fetchone()[0]

    @staticmethod
    def update_progress(job_id: str, data: Dict[str, Any]) -> bool:
        """Update progress fields on a crawl job.

        Only updates fields that are present in the data dict.
        Allowed keys: status, pages_crawled, pdfs_discovered,
        pdfs_downloaded, pdfs_new, pdfs_updated, errors_count,
        progress_pct.

        Returns:
            True if a row was updated.
        """
        allowed = {
            'status', 'pages_crawled', 'pdfs_discovered',
            'pdfs_downloaded', 'pdfs_new', 'pdfs_updated',
            'errors_count', 'progress_pct', 'celery_task_id',
        }
        sets = []
        params: list = []

        for key in allowed:
            if key in data:
                sets.append(f"{key} = %s")
                params.append(data[key])

        # Auto-set started_at when transitioning to 'running'
        if data.get('status') == 'running':
            sets.append("started_at = COALESCE(started_at, NOW())")

        if not sets:
            return False

        params.append(job_id)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE ai_pipeline.crawl_jobs
                    SET {', '.join(sets)}
                    WHERE job_id = %s
                """, params)
                updated = cur.rowcount > 0
                conn.commit()

        return updated

    @staticmethod
    def mark_completed(job_id: str, stats: Dict[str, Any]) -> bool:
        """Mark a job as completed and merge final stats.

        Args:
            job_id: The job UUID.
            stats: Dict with counter fields (pages_crawled,
                   pdfs_discovered, pdfs_downloaded, pdfs_new,
                   pdfs_updated, errors_count).

        Returns:
            True if a row was updated.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ai_pipeline.crawl_jobs
                    SET status = 'completed',
                        completed_at = NOW(),
                        pages_crawled = COALESCE(%s, pages_crawled),
                        pdfs_discovered = COALESCE(%s, pdfs_discovered),
                        pdfs_downloaded = COALESCE(%s, pdfs_downloaded),
                        pdfs_new = COALESCE(%s, pdfs_new),
                        pdfs_updated = COALESCE(%s, pdfs_updated),
                        errors_count = COALESCE(%s, errors_count),
                        progress_pct = 100
                    WHERE job_id = %s
                """, [
                    stats.get('pages_crawled'),
                    stats.get('pdfs_discovered'),
                    stats.get('pdfs_downloaded'),
                    stats.get('pdfs_new'),
                    stats.get('pdfs_updated'),
                    stats.get('errors_count'),
                    job_id,
                ])
                updated = cur.rowcount > 0
                conn.commit()

        if updated:
            logger.info("Crawl job %s completed", job_id)
        return updated

    @staticmethod
    def mark_failed(job_id: str, error_msg: str) -> bool:
        """Mark a job as failed and append error to error_log.

        Args:
            job_id: The job UUID.
            error_msg: Human-readable error description.

        Returns:
            True if a row was updated.
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ai_pipeline.crawl_jobs
                    SET status = 'failed',
                        completed_at = NOW(),
                        error_log = COALESCE(error_log, '[]'::jsonb)
                            || %s::jsonb
                    WHERE job_id = %s
                """, [
                    json.dumps([{'error': error_msg}]),
                    job_id,
                ])
                updated = cur.rowcount > 0
                conn.commit()

        if updated:
            logger.warning("Crawl job %s failed: %s", job_id, error_msg)
        return updated

    @staticmethod
    def mark_cancelled(job_id: str) -> bool:
        """Mark a pending or running job as cancelled.

        Args:
            job_id: The job UUID.

        Returns:
            True if a row was updated (only pending/running jobs can be cancelled).
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ai_pipeline.crawl_jobs
                    SET status = 'cancelled',
                        completed_at = NOW()
                    WHERE job_id = %s
                      AND status IN ('pending', 'running')
                """, [job_id])
                updated = cur.rowcount > 0
                conn.commit()

        if updated:
            logger.info("Crawl job %s cancelled", job_id)
        return updated
