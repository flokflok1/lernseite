"""
AP2 Trainer API Blueprint — alle Routes für /api/v1/user/exam-trainer/ap2.

DDD: API-Layer. Keine Geschäftslogik, keine SQL — nur Routing,
Auth, JSON-Mapping, Service-Aufrufe.
"""

from flask import Blueprint

ap2_trainer_bp = Blueprint(
    'ap2_trainer',
    __name__,
    url_prefix='/user/exam-trainer/ap2',
)

# Route-Module hängen sich an das Blueprint
from .stats import register_stats_routes      # noqa: E402
from .study import register_study_routes      # noqa: E402
from .anlagen import register_anlagen_routes  # noqa: E402
from .cheatsheets import register_cheatsheet_routes  # noqa: E402
from .modules import register_module_routes   # noqa: E402

register_stats_routes(ap2_trainer_bp)
register_study_routes(ap2_trainer_bp)
register_anlagen_routes(ap2_trainer_bp)
register_cheatsheet_routes(ap2_trainer_bp)
register_module_routes(ap2_trainer_bp)

__all__ = ['ap2_trainer_bp']
