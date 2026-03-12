"""Admin Crawler API Blueprint registration.

Endpoints (routes.py):
- GET  /status       Dashboard stats
- POST /start        Trigger crawl
- GET  /jobs         List jobs (paginated)
- GET  /jobs/<id>    Job detail
- GET  /pdfs         PDF library (paginated, searchable)
- DELETE /pdfs/<id>  Remove PDF

Endpoints (routes_part2.py):
- GET    /domains         List domains
- POST   /domains         Create domain
- PUT    /domains/<id>    Update domain
- DELETE /domains/<id>    Delete domain
- GET    /stats/trends    Crawl trends
"""

from app.api.v1.panel.admin.crawler.routes import crawler_bp
from app.api.v1.panel.admin.crawler import routes_part2  # noqa: F401 -- registers routes

from app.api.v1 import api_v1

api_v1.register_blueprint(crawler_bp)

__all__ = ['crawler_bp']
