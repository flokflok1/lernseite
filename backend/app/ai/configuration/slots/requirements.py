"""
LM Slot Requirements - Slot requirement definitions for all LMs

This module provides Python-based definitions of slot requirements.
These requirements are also seeded into the database (lm_slot_requirements table).

WICHTIG: Die folgenden Elemente sind KEINE Lernmethoden mehr und wurden zu Features:
- Glossar-Autogenerator -> CourseFeatures.auto_glossary_enabled
- Mindmap-Generator -> CourseFeatures.auto_mindmap_enabled
- NPC-Tutor-Lecture -> TutorAgentConfig
- Adaptive Difficulty -> CourseFeatures.adaptive_difficulty_enabled
- Lernpfad-Generator -> CourseFeatures.adaptive_path_enabled
- Persona-Tutor -> TutorAgentConfig
- Daily Recall / Spaced Repetition -> CourseFeatures.spaced_repetition_enabled
- Quest/XP System -> CourseFeatures.xp_system_enabled
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from app.ai.configuration.capability_slots import CapabilitySlot


@dataclass
class SlotRequirement:
    """
    Requirement for a specific slot in a Learning Method.

    Attributes:
        slot: The capability slot
        is_required: If True, LM will not work without this slot assigned
        is_primary: If True, this is the main/fallback slot for the LM
        usage_description: How this slot is used in this LM
    """
    slot: CapabilitySlot
    is_required: bool = False
    is_primary: bool = False
    usage_description: str = ""


@dataclass
class LMSlotConfig:
    """
    Complete slot configuration for a Learning Method.

    Attributes:
        lm_id: Learning Method ID (0-32)
        name: Learning Method name
        group: Group (A=Erklaerend, B=Praxis, C=Pruefung, D=Pro, E=IT, F=Kollaborativ)
        slots: List of slot requirements
        is_active: Whether this LM is currently active (not deprecated as feature)
    """
    lm_id: int
    name: str
    group: str
    slots: List[SlotRequirement] = field(default_factory=list)
    is_active: bool = True

    @property
    def required_slots(self) -> List[CapabilitySlot]:
        """Get all required slots for this LM."""
        return [r.slot for r in self.slots if r.is_required]

    @property
    def optional_slots(self) -> List[CapabilitySlot]:
        """Get all optional slots for this LM."""
        return [r.slot for r in self.slots if not r.is_required]

    @property
    def primary_slot(self) -> Optional[CapabilitySlot]:
        """Get the primary slot for this LM."""
        for r in self.slots:
            if r.is_primary:
                return r.slot
        return None


# =============================================================================
# Group A - Erklaerend (LM00-LM03, LM06)
# =============================================================================

LM00_DEEP_EXPLANATION = LMSlotConfig(
    lm_id=0,
    name="Tiefgehende Erklaerung",
    group="A",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Haupttext-Generierung fuer tiefe Erklaerungen"),
        SlotRequirement(CapabilitySlot.TTS, is_required=False,
                        usage_description="Optionale Vorlesefunktion"),
    ]
)

LM01_STEP_BY_STEP = LMSlotConfig(
    lm_id=1,
    name="Schritt-fuer-Schritt-Erklaerung",
    group="A",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Sequenzielle Erklaerungen generieren"),
    ]
)

LM02_INTERACTIVE_THEORY = LMSlotConfig(
    lm_id=2,
    name="Interaktive Theorie",
    group="A",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Theorie mit eingebetteten Fragen"),
    ]
)

LM03_VISUALIZATION = LMSlotConfig(
    lm_id=3,
    name="Diagramm/Visualisierung",
    group="A",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Diagramm-Beschreibungen und Mermaid-Code"),
        SlotRequirement(CapabilitySlot.IMAGE_GEN, is_required=False,
                        usage_description="Optionale Bildgenerierung"),
    ]
)

LM06_SCENARIO = LMSlotConfig(
    lm_id=6,
    name="Beispiel-Szenario-Erklaerung",
    group="A",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Real-World-Cases beschreiben"),
    ]
)

# =============================================================================
# Group B - Praxis/Uebung (LM08, LM12-LM15, LM17)
# =============================================================================

LM08_WHITEBOARD = LMSlotConfig(
    lm_id=8,
    name="Whiteboard-Aufgabe",
    group="B",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Aufgaben generieren"),
        SlotRequirement(CapabilitySlot.VISION, is_required=True,
                        usage_description="Zeichnungen analysieren"),
    ]
)

LM12_MATH_INTERACTIVE = LMSlotConfig(
    lm_id=12,
    name="Mathe-Interaktiv",
    group="B",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Mathe-Erklaerungen und Feedback"),
        SlotRequirement(CapabilitySlot.VISION, is_required=False,
                        usage_description="Handschrift-Erkennung"),
    ]
)

LM13_FLASHCARDS = LMSlotConfig(
    lm_id=13,
    name="Flashcards",
    group="B",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Flashcards generieren"),
    ]
)

LM14_DRAG_DROP = LMSlotConfig(
    lm_id=14,
    name="Drag & Drop Aufgaben",
    group="B",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Zuordnungs-Aufgaben generieren"),
    ]
)

LM15_CLOZE = LMSlotConfig(
    lm_id=15,
    name="Lueckentext-Aufgaben",
    group="B",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Lueckentexte erstellen"),
    ]
)

LM17_HANDS_ON_LAB = LMSlotConfig(
    lm_id=17,
    name="Hands-on Lab",
    group="B",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Lab-Anweisungen generieren"),
        SlotRequirement(CapabilitySlot.CODE_EXEC, is_required=True,
                        usage_description="Lab-Umgebung ausfuehren"),
    ]
)

# =============================================================================
# Group C - Pruefungsorientiert (LM18-LM25)
# =============================================================================

LM18_LONG_ANSWER = LMSlotConfig(
    lm_id=18,
    name="Freitext-Langantwort",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Antworten bewerten"),
        SlotRequirement(CapabilitySlot.REASONING, is_required=False,
                        usage_description="Tiefe Bewertung komplexer Antworten"),
    ]
)

LM19_IHK_TASKS = LMSlotConfig(
    lm_id=19,
    name="IHK-Stil Aufgaben",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Pruefungsaufgaben generieren"),
        SlotRequirement(CapabilitySlot.IMAGE_GEN, is_required=False,
                        usage_description="Diagramme fuer Aufgaben"),
    ]
)

LM20_MULTI_STEP_EXAM = LMSlotConfig(
    lm_id=20,
    name="Multi-Step Praxispruefung",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Pruefungs-Szenarien generieren"),
        SlotRequirement(CapabilitySlot.CODE_EXEC, is_required=False,
                        usage_description="Praxis-Validierung"),
    ]
)

LM21_TIME_TRAINING = LMSlotConfig(
    lm_id=21,
    name="Zeitlimit-Training",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Zeitbasierte Aufgaben generieren"),
    ]
)

LM22_EXAM_QUIZ = LMSlotConfig(
    lm_id=22,
    name="Pruefungs-Quiz",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="MC-Fragen generieren"),
    ]
)

LM23_COMPREHENSION = LMSlotConfig(
    lm_id=23,
    name="Verstaendnis-Checks",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Kurze Verstaendnis-Checks"),
    ]
)

LM24_ORAL_EXPLANATION = LMSlotConfig(
    lm_id=24,
    name="Muendliche Erklaerung",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Analyse der Erklaerung"),
        SlotRequirement(CapabilitySlot.STT, is_required=True,
                        usage_description="Sprache transkribieren"),
        SlotRequirement(CapabilitySlot.TTS, is_required=False,
                        usage_description="Feedback vorlesen"),
        SlotRequirement(CapabilitySlot.REALTIME, is_required=False,
                        usage_description="Live-Dialog mit Pruefer"),
    ]
)

LM25_CHAPTER_EXAM = LMSlotConfig(
    lm_id=25,
    name="Kapitel-Endpruefung",
    group="C",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Umfassende Pruefung erstellen"),
    ]
)

# =============================================================================
# Group D - Pro (LM04 - Sokratischer Dialog)
# =============================================================================

LM04_SOCRATIC = LMSlotConfig(
    lm_id=4,
    name="Sokratischer Dialog",
    group="D",
    slots=[
        SlotRequirement(CapabilitySlot.REASONING, is_required=True, is_primary=True,
                        usage_description="Sokratische Fragen durch Reasoning"),
        SlotRequirement(CapabilitySlot.CHAT, is_required=False,
                        usage_description="Fallback fuer einfache Dialoge"),
        SlotRequirement(CapabilitySlot.REALTIME, is_required=False,
                        usage_description="Echtzeitdialog"),
    ]
)

# =============================================================================
# Group E - IT-Spezifisch (LM09-LM11, LM16)
# =============================================================================

LM09_CODE_SANDBOX = LMSlotConfig(
    lm_id=9,
    name="Code/IT-Config Sandbox",
    group="E",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Code-Generierung und Erklaerung"),
        SlotRequirement(CapabilitySlot.CODE_EXEC, is_required=False,
                        usage_description="Code-Ausfuehrung und Validierung"),
    ]
)

LM10_NETWORK_SIM = LMSlotConfig(
    lm_id=10,
    name="Netzwerk-Aufbau Simulation",
    group="E",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Netzwerk-Topologien generieren"),
        SlotRequirement(CapabilitySlot.VISION, is_required=False,
                        usage_description="Topologie-Analyse"),
    ]
)

LM11_IT_SCENARIO = LMSlotConfig(
    lm_id=11,
    name="IT-Szenario loesen",
    group="E",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="IT-Cases beschreiben"),
        SlotRequirement(CapabilitySlot.CODE_EXEC, is_required=False,
                        usage_description="Loesungen validieren"),
    ]
)

LM16_ERROR_ANALYSIS = LMSlotConfig(
    lm_id=16,
    name="Fehleranalyse",
    group="E",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Fehler beschreiben und erklaeren"),
        SlotRequirement(CapabilitySlot.CODE_EXEC, is_required=False,
                        usage_description="Code-Fehler ausfuehren"),
        SlotRequirement(CapabilitySlot.VISION, is_required=False,
                        usage_description="Screenshot-Analyse"),
    ]
)

# =============================================================================
# Group F - Kollaborativ/Reflexiv (LM26-LM32)
# =============================================================================

LM26_PEER_INSTRUCTION = LMSlotConfig(
    lm_id=26,
    name="Peer Instruction",
    group="F",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="KI-Moderation der Peer-Diskussion und Analyse der Antworten"),
    ]
)

LM27_TEAM_CASE = LMSlotConfig(
    lm_id=27,
    name="Team-Case / Gruppenfallarbeit",
    group="F",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Case-Generierung und Team-Feedback"),
        SlotRequirement(CapabilitySlot.REASONING, is_required=False,
                        usage_description="Komplexe Case-Analyse"),
    ]
)

LM28_PEER_REVIEW = LMSlotConfig(
    lm_id=28,
    name="Peer Review",
    group="F",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Rubric-Generierung und Feedback-Qualitaetspruefung"),
    ]
)

LM29_LEARNING_JOURNAL = LMSlotConfig(
    lm_id=29,
    name="Lerntagebuch / Learning Journal",
    group="F",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=False, is_primary=True,
                        usage_description="Reflexions-Prompts und Zusammenfassungen generieren"),
    ]
)

LM30_PORTFOLIO = LMSlotConfig(
    lm_id=30,
    name="Projekt-Portfolio",
    group="F",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=False, is_primary=True,
                        usage_description="Portfolio-Analyse und Kompetenz-Mapping"),
    ]
)

LM31_PROJECT_BASED = LMSlotConfig(
    lm_id=31,
    name="Projektbasiertes Lernen",
    group="F",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Projekt-Briefing und Meilenstein-Feedback"),
        SlotRequirement(CapabilitySlot.CODE_EXEC, is_required=False,
                        usage_description="Projekt-Code ausfuehren"),
    ]
)

LM32_INVERTED_CLASSROOM = LMSlotConfig(
    lm_id=32,
    name="Inverted Classroom",
    group="F",
    slots=[
        SlotRequirement(CapabilitySlot.CHAT, is_required=True, is_primary=True,
                        usage_description="Theorie-Zusammenfassungen und Aktivitaets-Koordination"),
    ]
)

# =============================================================================
# Complete LM Configuration Registry (nur AKTIVE LMs)
# =============================================================================

ALL_LM_CONFIGS: Dict[int, LMSlotConfig] = {
    # Group A - Erklaerend
    0: LM00_DEEP_EXPLANATION,
    1: LM01_STEP_BY_STEP,
    2: LM02_INTERACTIVE_THEORY,
    3: LM03_VISUALIZATION,
    6: LM06_SCENARIO,

    # Group B - Praxis
    8: LM08_WHITEBOARD,
    12: LM12_MATH_INTERACTIVE,
    13: LM13_FLASHCARDS,
    14: LM14_DRAG_DROP,
    15: LM15_CLOZE,
    17: LM17_HANDS_ON_LAB,

    # Group C - Pruefung
    18: LM18_LONG_ANSWER,
    19: LM19_IHK_TASKS,
    20: LM20_MULTI_STEP_EXAM,
    21: LM21_TIME_TRAINING,
    22: LM22_EXAM_QUIZ,
    23: LM23_COMPREHENSION,
    24: LM24_ORAL_EXPLANATION,
    25: LM25_CHAPTER_EXAM,

    # Group D - Pro
    4: LM04_SOCRATIC,

    # Group E - IT
    9: LM09_CODE_SANDBOX,
    10: LM10_NETWORK_SIM,
    11: LM11_IT_SCENARIO,
    16: LM16_ERROR_ANALYSIS,

    # Group F - Kollaborativ
    26: LM26_PEER_INSTRUCTION,
    27: LM27_TEAM_CASE,
    28: LM28_PEER_REVIEW,
    29: LM29_LEARNING_JOURNAL,
    30: LM30_PORTFOLIO,
    31: LM31_PROJECT_BASED,
    32: LM32_INVERTED_CLASSROOM,
}

# Mapping von Gruppen zu Namen
GROUP_NAMES = {
    'A': 'Erklaerend',
    'B': 'Praxis/Uebung',
    'C': 'Pruefungsorientiert',
    'D': 'Pro',
    'E': 'IT-Spezifisch',
    'F': 'Kollaborativ/Reflexiv',
}
