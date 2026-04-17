"""
AP2 Topic — ein Kernthema der Prüfung.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from .enums import Bereich, Priority


@dataclass
class Topic:
    """Ein AP2-Kernthema (z.B. 'EPK', 'IPv6-Subnetting').

    Topics sind relativ statische Referenzdaten — aus der Prüfungsanalyse
    seit 2022. Priority steuert die Gewichtung im Mix-Training und
    Dashboard.
    """
    topic_id: UUID
    slug: str                       # z.B. 'epk', 'ipv6-subnetting'
    name_de: str
    bereich: Bereich
    priority: Priority
    expected_points: int            # Durchschnittliche Punkte in Prüfungen
    exam_count: int                 # Wie oft seit 2022 drangekommen
    name_en: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    @property
    def is_critical(self) -> bool:
        """Ist dieses Thema Bestehens-kritisch?"""
        return self.priority in (Priority.SEHR_HOCH, Priority.HOCH)

    @property
    def weight(self) -> int:
        """Gewicht für Mix-Training (höhere Prio = höheres Gewicht)."""
        mapping = {
            Priority.SEHR_HOCH: 4,
            Priority.HOCH: 3,
            Priority.MITTEL: 2,
            Priority.NIEDRIG: 1,
        }
        return mapping[self.priority]
