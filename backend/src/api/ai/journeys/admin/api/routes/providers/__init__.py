"""
AI Providers Admin Package (DDD)

Endpoints for AI provider management using DDD patterns:
- Uses AIProviderFactory for creation
- Uses AIHealthMonitoringService for health checks
- Publishes AIProviderHealthChangedEvent on status changes
- Uses Repository Pattern for persistence

Blueprints:
    - providers_crud_bp: CRUD operations
    - providers_api_keys_bp: API key management
    - providers_testing_bp: Connection testing
    - providers_health_bp: Health monitoring
"""

from .crud import providers_crud_bp
from .api_keys import providers_api_keys_bp
from .testing import providers_testing_bp
from .health import providers_health_bp

__all__ = [
    'providers_crud_bp',
    'providers_api_keys_bp',
    'providers_testing_bp',
    'providers_health_bp'
]
