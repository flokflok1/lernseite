"""
LernsystemX AI Models Repository Package

Sub-packages for AI Models data access:
- crud.py: Create, Read, Update, Delete operations
- query.py: Specialized query methods (by category, by name, etc.)
- defaults.py: Default model management
- pricing.py: Pricing and cost calculations
- sync.py: Model synchronization tracking
- stats.py: Statistics and aggregation queries

This module re-exports all public methods for backward compatibility.
"""

from .crud import AIModelsCRUDRepository
from .query import AIModelsQueryRepository
from .defaults import AIModelsDefaultRepository
from .pricing import AIModelsPricingRepository
from .sync import AIModelsSyncRepository
from .stats import AIModelsStatsRepository

# Unified interface for backward compatibility
class AIModelsRepository:
    """
    Unified AI Models Repository

    Aggregates functionality from all sub-repositories for backward compatibility.
    All methods delegate to specialized repositories.
    """

    # CRUD Operations
    create = staticmethod(AIModelsCRUDRepository.create)
    update = staticmethod(AIModelsCRUDRepository.update)
    delete = staticmethod(AIModelsCRUDRepository.delete)
    upsert = staticmethod(AIModelsCRUDRepository.upsert)

    # Query Operations
    get_by_id = staticmethod(AIModelsQueryRepository.get_by_id)
    get_by_name = staticmethod(AIModelsQueryRepository.get_by_name)
    get_by_category = staticmethod(AIModelsQueryRepository.get_by_category)
    get_all = staticmethod(AIModelsQueryRepository.get_all)
    get_models_by_category = staticmethod(AIModelsQueryRepository.get_models_by_category)
    get_categories = staticmethod(AIModelsQueryRepository.get_categories)

    # Default Model Operations
    get_default_model = staticmethod(AIModelsDefaultRepository.get_default_model)
    set_default = staticmethod(AIModelsDefaultRepository.set_default)
    set_active = staticmethod(AIModelsDefaultRepository.set_active)

    # Pricing Operations
    get_all_with_pricing = staticmethod(AIModelsPricingRepository.get_all_with_pricing)
    bulk_update_prices = staticmethod(AIModelsPricingRepository.bulk_update_prices)

    # Sync Operations
    mark_synced = staticmethod(AIModelsSyncRepository.mark_synced)

    # Statistics
    count = staticmethod(AIModelsStatsRepository.count)
    get_stats = staticmethod(AIModelsStatsRepository.get_stats)


__all__ = [
    'AIModelsRepository',
    'AIModelsCRUDRepository',
    'AIModelsQueryRepository',
    'AIModelsDefaultRepository',
    'AIModelsPricingRepository',
    'AIModelsSyncRepository',
    'AIModelsStatsRepository',
]
