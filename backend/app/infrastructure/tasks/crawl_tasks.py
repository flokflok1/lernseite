"""Celery tasks for web research domain crawling.

Background tasks for crawling configured domains, discovering PDFs,
and tracking progress via Redis.
"""

import json
import logging
from typing import Dict, Any

from app.core.bootstrap.extensions import celery, redis_client

logger = logging.getLogger(__name__)

PROGRESS_KEY_PREFIX = 'crawl_job'
PROGRESS_TTL = 7200  # 2 hours


@celery.task(bind=True, max_retries=2, default_retry_delay=120)
def crawl_domain_task(self, job_id: str, domain_id: str) -> Dict[str, Any]:
    """Crawl a single domain. Called by CrawlService or Beat scheduler.

    Args:
        job_id: UUID of the crawl job record
        domain_id: UUID of the domain to crawl
    """
    from app.infrastructure.persistence.repositories.web_research.crawl_domain_repository import (
        CrawlDomainRepository,
    )
    from app.infrastructure.persistence.repositories.web_research.crawl_job_repository import (
        CrawlJobRepository,
    )
    from app.infrastructure.web_research.crawler.domain_crawler import crawl_domain

    domain = CrawlDomainRepository.find_by_id(domain_id)
    if not domain:
        logger.error("Domain %s not found, aborting crawl job %s", domain_id, job_id)
        CrawlJobRepository.mark_failed(job_id, f"Domain {domain_id} not found")
        return {'error': 'domain_not_found'}

    # Mark job as running with Celery task ID
    CrawlJobRepository.update_progress(job_id, {
        'status': 'running',
        'celery_task_id': self.request.id,
    })
    _update_redis_progress(job_id, {
        'status': 'running',
        'domain_name': domain['domain_name'],
        'pages_crawled': 0,
        'pdfs_discovered': 0,
        'progress_pct': 0,
    })

    def on_progress(stats):
        """Callback from domain_crawler for progress updates."""
        _update_redis_progress(job_id, {
            **stats,
            'domain_name': domain['domain_name'],
        })
        CrawlJobRepository.update_progress(job_id, stats)

    try:
        result = crawl_domain(domain, job_id, on_progress=on_progress)
        CrawlJobRepository.mark_completed(job_id, result)
        CrawlDomainRepository.update_crawl_stats(
            domain_id, result.get('pdfs_discovered', 0),
        )
        _update_redis_progress(job_id, {
            **result,
            'status': 'completed',
            'domain_name': domain['domain_name'],
            'progress_pct': 100,
        })
        logger.info(
            "Crawl completed for %s: %d pages, %d PDFs discovered, %d downloaded",
            domain['domain_name'],
            result.get('pages_crawled', 0),
            result.get('pdfs_discovered', 0),
            result.get('pdfs_downloaded', 0),
        )
        return result

    except Exception as exc:
        logger.exception("Crawl failed for %s", domain['domain_name'])
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            CrawlJobRepository.mark_failed(job_id, str(exc))
            _update_redis_progress(job_id, {
                'status': 'failed',
                'domain_name': domain['domain_name'],
                'error': str(exc),
            })
            return {'error': str(exc), 'status': 'failed'}


@celery.task(bind=True, max_retries=0)
def crawl_all_domains_task(self) -> Dict[str, Any]:
    """Orchestrate crawling all active domains. Called by Celery Beat."""
    from app.application.services.web_research.crawl_service import CrawlService

    logger.info("Celery Beat: Starting scheduled crawl of all active domains")
    result = CrawlService.start_crawl_all()
    logger.info(
        "Scheduled crawl dispatched: %d domains, job_ids=%s",
        result.get('domain_count', 0),
        result.get('job_ids', []),
    )
    return result


def get_crawl_progress(job_id: str) -> Dict[str, Any]:
    """Read crawl progress from Redis."""
    key = f"{PROGRESS_KEY_PREFIX}:{job_id}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return {'status': 'unknown'}


def _update_redis_progress(job_id: str, stats: dict) -> None:
    """Write crawl progress to Redis for frontend polling."""
    key = f"{PROGRESS_KEY_PREFIX}:{job_id}"
    try:
        redis_client.setex(key, PROGRESS_TTL, json.dumps(stats))
    except Exception:
        logger.warning("Redis progress update failed for job %s", job_id, exc_info=True)
