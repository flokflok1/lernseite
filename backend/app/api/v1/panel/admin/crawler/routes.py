"""Admin Crawler API routes.

Provides endpoints for managing the web research crawler:
- Dashboard status/stats
- Start crawl jobs
- List/view crawl jobs
- PDF library (list, delete)

All endpoints require admin authentication.
No business logic here -- delegates to CrawlService (G09).
"""

from flask import Blueprint, jsonify, request
from app.api.middleware.auth import admin_required

crawler_bp = Blueprint('admin_crawler', __name__, url_prefix='/admin/crawler')


@crawler_bp.route('/status', methods=['GET'])
@admin_required
def get_crawler_status():
    """Return aggregated dashboard statistics for the crawler system."""
    from app.application.services.web_research.crawl_service import CrawlService

    stats = CrawlService.get_dashboard_stats()
    return jsonify(stats), 200


@crawler_bp.route('/start', methods=['POST'])
@admin_required
def start_crawl():
    """Trigger a crawl for one domain or all active domains.

    Request JSON (optional):
        domain_id (str): Crawl only this domain. Omit for all active domains.

    Returns 202 on success, 404 if specific domain_id not found.
    """
    from app.application.services.web_research.crawl_service import CrawlService

    data = request.get_json(silent=True) or {}
    domain_id = data.get('domain_id')

    try:
        result = CrawlService.start_crawl(domain_id=domain_id)
        return jsonify(result), 202
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@crawler_bp.route('/jobs', methods=['GET'])
@admin_required
def list_crawl_jobs():
    """List crawl jobs with pagination and optional filters.

    Query parameters:
        page (int): Page number, default 1.
        per_page (int): Items per page, default 20.
        status (str): Filter by job status.
        domain_id (str): Filter by domain.
    """
    from app.application.services.web_research.crawl_service import CrawlService

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    domain_id = request.args.get('domain_id')

    result = CrawlService.list_jobs(page, per_page, status, domain_id)
    return jsonify(result), 200


@crawler_bp.route('/jobs/<job_id>', methods=['GET'])
@admin_required
def get_crawl_job(job_id):
    """Get detail for a single crawl job (includes live progress if running)."""
    from app.application.services.web_research.crawl_service import CrawlService

    job = CrawlService.get_job_detail(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job), 200


@crawler_bp.route('/pdfs', methods=['GET'])
@admin_required
def list_crawler_pdfs():
    """List discovered PDFs with pagination and optional search.

    Query parameters:
        page (int): Page number, default 1.
        per_page (int): Items per page, default 20.
        search (str): ILIKE search on URL.
        domain_id (str): Filter by domain.
    """
    from app.application.services.web_research.crawl_service import CrawlService

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search')
    domain_id = request.args.get('domain_id')

    result = CrawlService.list_pdfs(page, per_page, search, domain_id)
    return jsonify(result), 200


@crawler_bp.route('/pdfs/<url_id>', methods=['DELETE'])
@admin_required
def delete_crawler_pdf(url_id):
    """Delete a discovered PDF URL record."""
    from app.application.services.web_research.crawl_service import CrawlService

    deleted = CrawlService.delete_pdf(url_id)
    if not deleted:
        return jsonify({'error': 'PDF not found'}), 404
    return jsonify({'deleted': True}), 200
