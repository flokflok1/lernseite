"""Organisation Entity"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class Organisation:
    """Organisation entity (Schools, Companies)."""
    organization_id: str
    name: str
    type: str  # school, company, institution
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    billing_email: Optional[str] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country: str = 'DE'
    address_postal_code: Optional[str] = None
    tax_id: Optional[str] = None
    token_pool: Decimal = Decimal('0.00')
    token_pool_limit: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None
    max_users: int = 100
    max_courses: Optional[int] = None
    status: str = 'active'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    def __post_init__(self):
        valid_types = ('school', 'company', 'institution', 'other')
        if self.type not in valid_types:
            raise ValueError(f"Invalid type: {self.type}")
        valid_statuses = ('active', 'inactive', 'suspended')
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}")
    
    def is_active(self) -> bool:
        return self.status == 'active' and self.deleted_at is None
