"""Crawl Service -- Application layer orchestration for web crawling.

Coordinates between API/Celery callers and infrastructure repositories.
All database access is delegated to repository classes (G09 compliance).
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Threshold in days for domain health classification
_STALE_THRESHOLD_DAYS = 14
_ERROR_THRESHOLD_DAYS = 30


def _build_domain_status(domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map each domain to a health status based on last_crawled_at age.

    Status values:
    - 'good':  crawled within the last 7 days
    - 'stale': crawled but older than _STALE_THRESHOLD_DAYS
    - 'error': not crawled for over _ERROR_THRESHOLD_DAYS
    - 'never': never been crawled
    """
    now = datetime.now(timezone.utc)
    result = []

    for domain in domains:
        last_crawled = domain.get('last_crawled_at')
        if not last_crawled:
            status = 'never'
        else:
            if isinstance(last_crawled, str):
                last_crawled = datetime.fromisoformat(last_crawled)
            if last_crawled.tzinfo is None:
                last_crawled = last_crawled.replace(tzinfo=timezone.utc)
            age_days = (now - last_crawled).days

            if age_days <= 7:
                status = 'good'
            elif age_days <= _STALE_THRESHOLD_DAYS:
                status = 'stale'
            else:
                status = 'error'

        result.append({
            'domain_id': domain['domain_id'],
            'domain_name': domain.get('domain_name', ''),
            'display_name': domain.get('display_name', ''),
            'is_active': domain.get('is_active', False),
            'last_crawled_at': domain.get('last_crawled_at'),
            'total_pdfs_found': domain.get('total_pdfs_found', 0),
            'health': status,
        })

    return result


def _find_latest_crawl(
    domains: List[Dict[str, Any]],
) -> Optional[str]:
    """Find the most recent last_crawled_at across all domains.

    Returns:
        ISO-formatted datetime string, or None if no domain was ever crawled.
    """
    latest = None
    for domain in domains:
        val = domain.get('last_crawled_at')
        if val and (latest is None or val > latest):
            latest = val
    return latest


class CrawlService:
    """Orchestrate crawl operations between API/Celery and infrastructure."""

    @staticmethod
    def start_crawl(
        domain_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Start a crawl job for one domain or all active domains.

        Creates job record(s) and dispatches Celery task(s).

        Args:
            domain_id: If given, crawl only this domain.
                       If None, crawl all active domains.

        Returns:
            Dict with 'job_ids' (list of str) and 'domain_count' (int).

        Raises:
            ValueError: If a specific domain_id is not found.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_domain_repository import (
            CrawlDomainRepository,
        )
        from app.infrastructure.persistence.repositories.web_research.crawl_job_repository import (
            CrawlJobRepository,
        )

        if domain_id:
            domain = CrawlDomainRepository.find_by_id(domain_id)
            if not domain:
                raise ValueError(f"Domain {domain_id} not found")
            domains = [domain]
        else:
            domains = CrawlDomainRepository.find_all(active_only=True)
            if not domains:
                logger.info("No active domains found, nothing to crawl")
                return {'job_ids': [], 'domain_count': 0}

        job_ids = _dispatch_crawl_jobs(domains, CrawlJobRepository)
        return {'job_ids': job_ids, 'domain_count': len(domains)}

    @staticmethod
    def start_crawl_all() -> Dict[str, Any]:
        """Start crawl for all active domains.

        Convenience wrapper for Celery Beat scheduled calls.
        """
        return CrawlService.start_crawl(domain_id=None)

    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """Aggregate dashboard statistics.

        Returns:
            Dict with total_pdfs, total_domains, active_domains,
            active_jobs, cache_size_mb, last_crawl_at, domain_status.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_domain_repository import (
            CrawlDomainRepository,
        )
        from app.infrastructure.persistence.repositories.web_research.crawl_job_repository import (
            CrawlJobRepository,
        )
        from app.infrastructure.persistence.repositories.web_research.crawl_url_repository import (
            CrawlUrlRepository,
        )

        domains = CrawlDomainRepository.find_all()
        url_stats = CrawlUrlRepository.get_stats()
        active_jobs = CrawlJobRepository.find_recent(
            limit=10, status='running',
        )
        domain_status = _build_domain_status(domains)

        return {
            'total_pdfs': url_stats.get('total_pdfs', 0),
            'total_domains': len(domains),
            'active_domains': sum(
                1 for d in domains if d.get('is_active')
            ),
            'active_jobs': len(active_jobs),
            'cache_size_mb': round(
                url_stats.get('total_size_bytes', 0) / (1024 * 1024), 1,
            ),
            'last_crawl_at': _find_latest_crawl(domains),
            'domain_status': domain_status,
        }

    @staticmethod
    def list_jobs(
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        domain_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List crawl jobs with basic pagination.

        Args:
            page: Page number (1-based).
            per_page: Items per page.
            status: Optional status filter.
            domain_id: Optional domain filter.

        Returns:
            Dict with 'items', 'total', 'page', 'per_page'.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_job_repository import (
            CrawlJobRepository,
        )

        offset = (page - 1) * per_page
        jobs = CrawlJobRepository.find_recent(
            limit=per_page, offset=offset,
            status=status, domain_id=domain_id,
        )
        total = CrawlJobRepository.count(
            status=status, domain_id=domain_id,
        )
        return {
            'items': jobs,
            'total': total,
            'page': page,
            'per_page': per_page,
        }

    @staticmethod
    def get_job_detail(job_id: str) -> Optional[Dict[str, Any]]:
        """Get a single job with optional live progress from Redis.

        Args:
            job_id: UUID of the crawl job.

        Returns:
            Job dict (with 'live_progress' if running), or None.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_job_repository import (
            CrawlJobRepository,
        )

        job = CrawlJobRepository.find_by_id(job_id)
        if not job:
            return None

        if job.get('status') == 'running':
            job['live_progress'] = _get_live_progress(job_id)

        return job

    @staticmethod
    def list_pdfs(
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        domain_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List discovered PDFs with pagination.

        Args:
            page: Page number (1-based).
            per_page: Items per page.
            search: Optional ILIKE search on URL.
            domain_id: Optional domain filter.

        Returns:
            Dict with 'items' and 'total'.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_url_repository import (
            CrawlUrlRepository,
        )

        return CrawlUrlRepository.find_pdfs_paginated(
            page, per_page, search, domain_id,
        )

    @staticmethod
    def delete_pdf(url_id: str) -> bool:
        """Delete a discovered URL record.

        Args:
            url_id: UUID of the URL record.

        Returns:
            True if deleted, False if not found.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_url_repository import (
            CrawlUrlRepository,
        )

        return CrawlUrlRepository.delete(url_id)

    @staticmethod
    def get_crawl_trends(days: int = 30) -> List[Dict[str, Any]]:
        """Get daily crawl statistics over the given time period.

        Args:
            days: Number of days to look back (default 30).

        Returns:
            List of dicts with 'date', 'pdfs_found', 'total_urls'.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_url_repository import (
            CrawlUrlRepository,
        )

        return CrawlUrlRepository.get_trends(days)


    # ==========================================================================
    # DOMAIN CRUD (delegated to repository, G09 compliance)
    # ==========================================================================

    @staticmethod
    def list_domains() -> List[Dict[str, Any]]:
        """List all configured crawl domains."""
        from app.infrastructure.persistence.repositories.web_research.crawl_domain_repository import (
            CrawlDomainRepository,
        )
        return CrawlDomainRepository.find_all()

    @staticmethod
    def create_domain(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new crawl domain.

        Args:
            data: Must contain 'domain_name', 'base_url', 'display_name'.

        Returns:
            Dict with domain fields.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_domain_repository import (
            CrawlDomainRepository,
        )
        result = CrawlDomainRepository.create(data)
        logger.info("Created domain: %s", data.get('domain_name'))
        return result

    @staticmethod
    def update_domain(
        domain_id: str, data: Dict[str, Any],
    ) -> bool:
        """Update a crawl domain configuration.

        Returns:
            True if updated, False if not found.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_domain_repository import (
            CrawlDomainRepository,
        )
        updated = CrawlDomainRepository.update(domain_id, data)
        if updated:
            logger.info("Updated domain %s", domain_id)
        return updated

    @staticmethod
    def delete_domain(domain_id: str) -> bool:
        """Delete a crawl domain.

        Returns:
            True if deleted, False if not found.
        """
        from app.infrastructure.persistence.repositories.web_research.crawl_domain_repository import (
            CrawlDomainRepository,
        )
        deleted = CrawlDomainRepository.delete(domain_id)
        if deleted:
            logger.info("Deleted domain %s", domain_id)
        return deleted


def _dispatch_crawl_jobs(
    domains: List[Dict[str, Any]],
    job_repo: type,
) -> List[str]:
    """Create job records and dispatch Celery tasks for each domain.

    Args:
        domains: List of domain dicts to crawl.
        job_repo: CrawlJobRepository class.

    Returns:
        List of created job_id strings.
    """
    job_ids: List[str] = []

    for domain in domains:
        job = job_repo.create({'domain_id': domain['domain_id']})
        job_id = job['job_id']
        _dispatch_celery_task(job_id, domain['domain_id'])
        job_ids.append(job_id)
        logger.info(
            "Dispatched crawl job %s for %s",
            job_id, domain.get('domain_name', domain['domain_id']),
        )

    return job_ids


def _dispatch_celery_task(job_id: str, domain_id: str) -> None:
    """Dispatch the Celery crawl task, handling import gracefully.

    The crawl_tasks module may not exist yet (created in Task 9).
    Logs a warning instead of crashing if unavailable.
    """
    try:
        from app.infrastructure.tasks.crawl_tasks import crawl_domain_task
        crawl_domain_task.delay(job_id, domain_id)
    except ImportError:
        logger.warning(
            "crawl_tasks module not available; job %s created but not dispatched",
            job_id,
        )


def _get_live_progress(job_id: str) -> Optional[Dict[str, Any]]:
    """Fetch live progress from Redis via crawl_tasks helper.

    Returns None if the module is unavailable or progress is unknown.
    """
    try:
        from app.infrastructure.tasks.crawl_tasks import get_crawl_progress
        progress = get_crawl_progress(job_id)
        if progress and progress.get('status') != 'unknown':
            return progress
    except ImportError:
        logger.debug("crawl_tasks not available for live progress")
    return None
