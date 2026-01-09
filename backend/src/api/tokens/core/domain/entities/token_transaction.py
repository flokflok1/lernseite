"""Token Transaction Entity"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class TokenTransaction:
    transaction_id: str
    user_id: str
    amount: Decimal
    type: str
    created_at: Optional[datetime] = None
