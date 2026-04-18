"""
AP2 Anlage (Prüfungs-Appendix) + Hotspots für Beschriftungs-Aufgaben.

In echten IHK-Prüfungen werden Anlagen direkt beschriftet (IP-Adressen in
Netzpläne, Organisationseinheiten in EPKs etc.). Punkte gibt's nur bei
korrekter Position.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from .enums import AnlageType, HotspotType


@dataclass(frozen=True)
class Hotspot:
    """Ein beschriftbarer Slot in einer Anlage.

    x/y/width/height sind relativ zum Anlagenbild (Pixel-Koordinaten
    im original-hochgeladenen Bild). Das Frontend skaliert responsive.
    """
    hotspot_id: str                 # eindeutig innerhalb der Anlage
    x: int
    y: int
    width: int
    height: int
    hotspot_type: HotspotType
    correct_answers: list[str]      # mehrere Varianten zulässig
    points: float = 1.0
    tolerance: str = 'case-insensitive'  # 'exact' | 'case-insensitive' | 'numeric' | 'ip-address'
    placeholder: Optional[str] = None
    hint: Optional[str] = None
    dropdown_options: list[str] = field(default_factory=list)


@dataclass
class Anlage:
    """Eine Prüfungs-Anlage (Netzplan, ER-Modell, Datenblatt etc.).

    Entweder `image_url` ODER `svg_markup` gesetzt (nicht beide).
    Hotspots sind beschriftbare Positionen — bei type='image' ohne Hotspots
    reine Lese-Anlage.
    """
    anlage_id: UUID
    slug: str
    title: str
    anlage_type: AnlageType
    hotspots: list[Hotspot] = field(default_factory=list)
    source_exam: Optional[str] = None        # 'S2024-PB2', 'AP1-2026'
    anlage_number: Optional[int] = None      # "Anlage 2" → 2
    image_url: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    svg_markup: Optional[str] = None
    description: Optional[str] = None
    footnote: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def has_hotspots(self) -> bool:
        return len(self.hotspots) > 0

    @property
    def total_points(self) -> float:
        """Summe aller Hotspot-Punkte."""
        return sum(h.points for h in self.hotspots)
