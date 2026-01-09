"""Subscription Entity"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class Subscription:
    """User subscription entity."""
    subscription_id: str
    user_id: str
    plan_type: str
    status: str
    price: Decimal
    started_at: datetime
    expires_at: Optional[datetime] = None
    
    def is_active(self) -> bool:
        return self.status == 'active' and (not self.expires_at or self.expires_at > datetime.utcnow())
