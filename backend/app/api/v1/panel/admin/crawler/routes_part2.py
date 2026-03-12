"""Admin Crawler API -- Domain CRUD + Statistics endpoints."""

from flask import jsonify, request
from app.api.middleware.auth import admin_required
from app.api.v1.panel.admin.crawler.routes import crawler_bp


@crawler_bp.route('/domains', methods=['GET'])
@admin_required
def list_domains():
    """List all configured crawl domains."""
    from app.application.services.web_research.crawl_service import CrawlService
    domains = CrawlService.list_domains()
    return jsonify({'items': domains}), 200


@crawler_bp.route('/domains', methods=['POST'])
@admin_required
def create_domain():
    """Add a new crawl domain."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    required = ['domain_name', 'base_url', 'display_name']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    from app.application.services.web_research.crawl_service import CrawlService
    try:
        result = CrawlService.create_domain(data)
        return jsonify(result), 201
    except Exception as e:
        if 'duplicate key' in str(e).lower() or 'unique' in str(e).lower():
            return jsonify({'error': f'Domain "{data["domain_name"]}" already exists'}), 409
        raise


@crawler_bp.route('/domains/<domain_id>', methods=['PUT'])
@admin_required
def update_domain(domain_id):
    """Update a crawl domain configuration."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    from app.application.services.web_research.crawl_service import CrawlService
    updated = CrawlService.update_domain(domain_id, data)
    if not updated:
        return jsonify({'error': 'Domain not found'}), 404
    return jsonify({'updated': True}), 200


@crawler_bp.route('/domains/<domain_id>', methods=['DELETE'])
@admin_required
def delete_domain(domain_id):
    """Delete a crawl domain."""
    from app.application.services.web_research.crawl_service import CrawlService
    deleted = CrawlService.delete_domain(domain_id)
    if not deleted:
        return jsonify({'error': 'Domain not found'}), 404
    return jsonify({'deleted': True}), 200


@crawler_bp.route('/stats/trends', methods=['GET'])
@admin_required
def get_crawl_trends():
    """Get crawl statistics over time."""
    days = request.args.get('days', 30, type=int)
    days = min(days, 365)  # Cap at 1 year

    from app.application.services.web_research.crawl_service import CrawlService
    trends = CrawlService.get_crawl_trends(days)
    return jsonify({'items': trends, 'days': days}), 200
