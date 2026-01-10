"""Organisation Service"""
from typing import Optional, List
from datetime import datetime
import logging
from src.core.events.event_bus import EventBus, DomainEvent, EventType
from src.api.organisations.core.domain.entities.organisation import Organisation
from src.api.organisations.core.infrastructure.repositories.organisation_repository import OrganisationRepository

logger = logging.getLogger(__name__)

class OrganisationService:
    @staticmethod
    def get_organisation(org_id: str) -> Optional[Organisation]:
        return OrganisationRepository.find_by_id(org_id)
    
    @staticmethod
    def list_organisations(limit: int = 100) -> List[Organisation]:
        return OrganisationRepository.list_organisations(limit)
