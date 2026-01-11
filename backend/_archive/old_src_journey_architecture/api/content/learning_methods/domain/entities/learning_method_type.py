"""
Learning Method Type Entity (DDD Domain Entity)

Represents one of the 12 Content-Lernmethoden types.
All data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class LearningMethodType:
    """
    Learning Method Type domain entity.

    Represents one of the 12 Content-Lernmethoden (LM00-LM11).
    All attributes loaded dynamically from database.

    Attributes:
        type_id: Serial ID
        method_type: Method type ID (0-11 for 12 Content-LMs)
        name: Method name
        description: Method description
        group_code: Group code (A, B, C from DB)
        tier: Access tier (basic, premium from DB)
        ki_usage: KI usage level (intensive, medium, optional from DB)
        active: Active status
        config: JSONB configuration
        icon: Icon identifier
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    type_id: int
    method_type: int  # 0-11 (12 Content-LMs)
    name: str
    description: str
    group_code: str  # Loaded from DB (A, B, C)
    tier: str  # Loaded from DB (basic, premium)
    ki_usage: str  # Loaded from DB (intensive, medium, optional)
    active: bool = True
    config: Optional[Dict[str, Any]] = None
    icon: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate learning method type entity."""
        if self.method_type < 0 or self.method_type > 11:
            raise ValueError("Method type must be between 0 and 11 (12 Content-LMs)")
        if not self.name or not self.name.strip():
            raise ValueError("Method name cannot be empty")
        if self.group_code not in ('A', 'B', 'C'):
            raise ValueError("Group code must be A, B, or C")

    def is_premium(self) -> bool:
        """Check if this learning method requires premium access."""
        return self.tier == 'premium'

    def requires_ki(self) -> bool:
        """Check if this learning method requires KI processing."""
        return self.ki_usage in ('intensive', 'medium')

    def get_group_name(self) -> str:
        """
        Get human-readable group name.

        Returns:
            Group name based on group_code
        """
        groups = {
            'A': 'Erklärend',
            'B': 'Praxis',
            'C': 'Prüfung'
        }
        return groups.get(self.group_code, 'Unknown')

    def deactivate(self) -> None:
        """Deactivate this learning method type."""
        self.active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate this learning method type."""
        self.active = True
        self.updated_at = datetime.utcnow()
