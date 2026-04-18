"""
AP2 LearningItem — Atom des Active-Recall-Flows.

Pro Topic existieren mehrere Items pro Type:
- Blurt: 2-3 offene Prompts ("Alles über EPK aufschreiben")
- Cued:  5-7 gezielte Fragen
- Application: 1-3 echte Prüfungsaufgaben

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from .enums import ItemType


@dataclass(frozen=True)
class GradingCriterion:
    """Ein Bewertungskriterium für die KI-Prüfer-Beurteilung.

    Beispiel für EPK-Aufgabe:
      GradingCriterion('konnektoren_verwendet', 4.0,
                       'XOR/UND/ODER korrekt eingesetzt')
    """
    criterion: str
    weight: float
    description: str
    required: bool = False          # Bei False kann Kriterium fehlen ohne 0 Punkte


@dataclass
class LearningItem:
    """Ein Lern-Atom (Blurting-Prompt, Karteikarte, oder Prüfungsaufgabe).

    expected_answer_structure ist eine Checkliste (Dict/List) die der
    KI-Prüfer beim Bewerten abhakt. Z.B. für EPK-Blurt:
      {"required_concepts": ["Ereignis", "Funktion", "Konnektor",
                              "XOR", "UND", "ODER", "Start/End"]}
    """
    item_id: UUID
    topic_id: UUID
    item_type: ItemType
    prompt: str
    model_answer: str
    points: float = 1.0
    source_exam: Optional[str] = None        # 'S2024-PB2-1.1' | 'ki-generated'
    anlage_id: Optional[UUID] = None         # Referenz auf Anlage (bei Application)
    expected_answer_structure: Optional[dict] = None
    grading_criteria: list[GradingCriterion] = field(default_factory=list)
    difficulty: int = 3                      # 1-5
    estimated_time_sec: int = 120
    is_active: bool = True
    calculator_hint: Optional[dict] = None   # Casio FX-991DE X Step-Guide
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def has_anlage(self) -> bool:
        return self.anlage_id is not None

    @property
    def is_blurt(self) -> bool:
        return self.item_type == ItemType.BLURT

    @property
    def is_application(self) -> bool:
        return self.item_type == ItemType.APPLICATION
