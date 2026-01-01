"""
LernsystemX Services Package

Service layer for business logic and external integrations:
- AI Adapter: Multi-provider AI integration
- Billing Service: Token and subscription management
- Email Service: Email sending and templating
- File Service: File upload and processing
- Analytics Service: Usage analytics and reporting

ISO 9001:2015 compliant - Service layer architecture
"""

from app.services.ai_adapter import AIAdapter
from app.services.billing_service import BillingService

__all__ = [
    'AIAdapter',
    'BillingService'
]
