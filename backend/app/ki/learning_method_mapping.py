"""
LernsystemX KI - Learning Method Mapping (19 Content-Lernmethoden, 3 Gruppen A-C)

Vollständiges Mapping aller 19 aktiven Content-Lernmethoden auf:
- Name (Deutsch)
- Gruppe (A, B, C)
- Typ (explanatory, practice, exam)
- Default Prompt-Key
- KI-Nutzungsintensität

WICHTIG: Dieses Modul enthält NUR Content-Lernmethoden (Aufgaben/Prüfungsformate).
System-Features (Tutor, Gamification, IT-Umgebungen, Kollaboration) sind in
separaten Modulen definiert (siehe 02a_System-Features.md).

Aktuelle Content-LM-Struktur (Stand: 2025-12):
- A: Erklärend (LM00-LM03, LM06) - 5 Methoden
- B: Praxis (LM08, LM12-LM15, LM17) - 6 Methoden
- C: Prüfung (LM18-LM25) - 8 Methoden

DEAKTIVIERT / Zu System-Features verschoben:
- LM04: Sokratischer Dialog → TutorAgent / Pro-Feature
- LM05: Mindmap-Generator → CourseFeatures
- LM07: NPC-Tutor-Lecture → TutorAgent
- LM09-LM11, LM16: IT-Sandboxes → System-Feature IT-Umgebungen
- LM26-LM32: Kollaborative Methoden → System-Features Kollaboration

Referenz: 02_Lernmethoden.md (Master-Dokument)
          02a_System-Features.md (System-Features)
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


class LearningMethodGroup(str, Enum):
    """Gruppen-Codes für die 19 Content-Lernmethoden (3 Gruppen)"""
    A = 'A'  # Erklärende Methoden (LM00-LM03, LM06) - 5 Methoden
    B = 'B'  # Praxis/Übung (LM08, LM12-LM15, LM17) - 6 Methoden
    C = 'C'  # Prüfungsorientiert (LM18-LM25) - 8 Methoden


class LearningMethodType(str, Enum):
    """Methodentypen für semantische Klassifizierung"""
    EXPLANATORY = 'explanatory'   # Erklärend (A)
    PRACTICE = 'practice'         # Übung (B)
    EXAM = 'exam'                 # Prüfung (C)


class KIUsage(str, Enum):
    """KI-Nutzungsintensität"""
    INTENSIVE = 'intensive'  # KI-intensiv (Vollgenerierung)
    MEDIUM = 'medium'        # Mittlere KI-Nutzung (Unterstützung)
    OPTIONAL = 'optional'    # KI optional (manuelle Erstellung möglich)


@dataclass(frozen=True)
class LearningMethodDefinition:
    """Definition einer Content-Lernmethode"""
    lm_id: int                          # 0-25 (mit Lücken bei 4, 5, 7, 9-11, 16)
    name: str                           # Deutscher Name
    group: LearningMethodGroup          # A, B, C
    method_type: LearningMethodType     # explanatory, practice, exam
    ki_usage: KIUsage                   # intensive, medium, optional
    prompt_key: str                     # Prompt-Template-Key
    description: str                    # Kurzbeschreibung
    active: bool = True                 # Ob die Methode aktiv ist


# =============================================================================
# VOLLSTÄNDIGES MAPPING ALLER 19 CONTENT-LERNMETHODEN
# =============================================================================

LEARNING_METHODS: Dict[int, LearningMethodDefinition] = {
    # =========================================================================
    # GRUPPE A – Erklärend (5 Methoden)
    # =========================================================================
    0: LearningMethodDefinition(
        lm_id=0,
        name="Tiefgehende Erklärung",
        group=LearningMethodGroup.A,
        method_type=LearningMethodType.EXPLANATORY,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="deep_explanation",
        description="KI-generierte Erklärung mit Beispielen & Analogien"
    ),
    1: LearningMethodDefinition(
        lm_id=1,
        name="Schritt-für-Schritt",
        group=LearningMethodGroup.A,
        method_type=LearningMethodType.EXPLANATORY,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="step_by_step",
        description="Sequenzielle Anleitung in nummerierten Schritten"
    ),
    2: LearningMethodDefinition(
        lm_id=2,
        name="Interaktive Theorie",
        group=LearningMethodGroup.A,
        method_type=LearningMethodType.EXPLANATORY,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="interactive_theory",
        description="Theorieblöcke mit eingebetteten Kontrollfragen"
    ),
    3: LearningMethodDefinition(
        lm_id=3,
        name="Diagramm/Visualisierung",
        group=LearningMethodGroup.A,
        method_type=LearningMethodType.EXPLANATORY,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="visualization",
        description="Visuelle Modelle (Netzwerk, OSI, ER, Flows)"
    ),
    6: LearningMethodDefinition(
        lm_id=6,
        name="Beispiel-Szenario",
        group=LearningMethodGroup.A,
        method_type=LearningMethodType.EXPLANATORY,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="scenario_explanation",
        description="Realitätsnahe Case-Erklärung eines Konzepts"
    ),

    # =========================================================================
    # GRUPPE B – Praxis (6 Methoden)
    # =========================================================================
    8: LearningMethodDefinition(
        lm_id=8,
        name="Whiteboard-Aufgabe",
        group=LearningMethodGroup.B,
        method_type=LearningMethodType.PRACTICE,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="whiteboard",
        description="Lernende zeichnen/verbinden Topologien, Skizzen"
    ),
    12: LearningMethodDefinition(
        lm_id=12,
        name="Mathe-Interaktiv",
        group=LearningMethodGroup.B,
        method_type=LearningMethodType.PRACTICE,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="math_interactive",
        description="Rechenaufgaben mit Schritt-für-Schritt-Erklärung"
    ),
    13: LearningMethodDefinition(
        lm_id=13,
        name="Flashcards",
        group=LearningMethodGroup.B,
        method_type=LearningMethodType.PRACTICE,
        ki_usage=KIUsage.OPTIONAL,
        prompt_key="flashcards",
        description="Karteikarten mit Spaced-Repetition"
    ),
    14: LearningMethodDefinition(
        lm_id=14,
        name="Drag & Drop",
        group=LearningMethodGroup.B,
        method_type=LearningMethodType.PRACTICE,
        ki_usage=KIUsage.OPTIONAL,
        prompt_key="drag_drop",
        description="Zuordnungs-/Matching-Aufgaben"
    ),
    15: LearningMethodDefinition(
        lm_id=15,
        name="Lückentext",
        group=LearningMethodGroup.B,
        method_type=LearningMethodType.PRACTICE,
        ki_usage=KIUsage.OPTIONAL,
        prompt_key="fill_blanks",
        description="Fill-in-the-blanks in Texten/Configs"
    ),
    17: LearningMethodDefinition(
        lm_id=17,
        name="Hands-on Lab",
        group=LearningMethodGroup.B,
        method_type=LearningMethodType.PRACTICE,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="hands_on_lab",
        description="Virtuelle Umgebung (Terminal/IDE) mit Aufgabe"
    ),

    # =========================================================================
    # GRUPPE C – Prüfung (8 Methoden)
    # =========================================================================
    18: LearningMethodDefinition(
        lm_id=18,
        name="Freitext-Langantwort",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="long_answer",
        description="Lange Antworten, KI bewertet mit Rubric"
    ),
    19: LearningMethodDefinition(
        lm_id=19,
        name="IHK-Stil Aufgaben",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="ihk_style",
        description="Prüfungsnahe MC/Lückentext/Szenario"
    ),
    20: LearningMethodDefinition(
        lm_id=20,
        name="Multi-Step Praxisprüfung",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="multi_step_exam",
        description="Mehrstufige Prüfungsketten"
    ),
    21: LearningMethodDefinition(
        lm_id=21,
        name="Zeitlimit-Training",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.OPTIONAL,
        prompt_key="time_limit",
        description="Aufgaben unter Zeitdruck (Countdown)"
    ),
    22: LearningMethodDefinition(
        lm_id=22,
        name="Prüfungs-Quiz",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.OPTIONAL,
        prompt_key="exam_quiz",
        description="Quiz mit sofortigem Feedback"
    ),
    23: LearningMethodDefinition(
        lm_id=23,
        name="Verständnis-Checks",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.OPTIONAL,
        prompt_key="comprehension_check",
        description="Single-Item-Checks nach Lerneinheit"
    ),
    24: LearningMethodDefinition(
        lm_id=24,
        name="Mündliche Erklärung",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="oral_explanation",
        description="User erklärt mündlich, KI bewertet"
    ),
    25: LearningMethodDefinition(
        lm_id=25,
        name="Kapitel-Endprüfung",
        group=LearningMethodGroup.C,
        method_type=LearningMethodType.EXAM,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="chapter_exam",
        description="Größere Prüfung am Kapitelende"
    ),
}


# =============================================================================
# SYSTEM-FEATURES (frühere LMs, jetzt eigenständige Features)
# =============================================================================

SYSTEM_FEATURES: Dict[int, Dict] = {
    # Gruppe D (Pro) → TutorAgent
    4: {
        'name': 'Sokratischer Dialog',
        'former_group': 'D',
        'moved_to': 'TutorAgent / Pro-Feature',
        'description': 'KI fragt, User leitet Konzept selbst her'
    },
    # Deaktivierte Visualisierung
    5: {
        'name': 'Mindmap-Generator',
        'former_group': 'A',
        'moved_to': 'CourseFeatures.mindmap',
        'description': 'Kursweite Mindmaps aus Theorie-Inhalten'
    },
    # Deaktivierter Tutor
    7: {
        'name': 'NPC-Tutor-Lecture',
        'former_group': 'A',
        'moved_to': 'TutorAgent',
        'description': 'KI-basierter Tutor mit Personas'
    },
    # Gruppe E (IT) → IT-Umgebungen
    9: {
        'name': 'Code/IT-Config Sandbox',
        'former_group': 'E',
        'moved_to': 'System-Feature IT-Umgebungen',
        'description': 'Code-/Config-Editor mit Tests & Output'
    },
    10: {
        'name': 'Netzwerk-Simulation',
        'former_group': 'E',
        'moved_to': 'System-Feature IT-Umgebungen',
        'description': 'Simulierte Netzumgebung (Router, Switch, Ping)'
    },
    11: {
        'name': 'IT-Szenario lösen',
        'former_group': 'E',
        'moved_to': 'System-Feature IT-Umgebungen',
        'description': 'Troubleshooting mit Logs/Configs'
    },
    16: {
        'name': 'Fehleranalyse',
        'former_group': 'E',
        'moved_to': 'System-Feature IT-Umgebungen',
        'description': 'Defekter Code/Config, Fehler finden & erklären'
    },
    # Gruppe F (Kollaborativ) → Kollaborations-Features
    26: {
        'name': 'Peer Instruction',
        'former_group': 'F',
        'moved_to': 'System-Feature Kollaboration',
        'description': 'Think–Pair–Share mit Erstantwort → Diskussion'
    },
    27: {
        'name': 'Team-Case / Gruppenfallarbeit',
        'former_group': 'F',
        'moved_to': 'System-Feature Kollaboration',
        'description': 'Teams lösen Fall mit Rollen'
    },
    28: {
        'name': 'Peer Review (strukturiert)',
        'former_group': 'F',
        'moved_to': 'System-Feature Kollaboration',
        'description': 'Rubric-basiertes Feedback zu Arbeiten anderer'
    },
    29: {
        'name': 'Lerntagebuch / Learning Journal',
        'former_group': 'F',
        'moved_to': 'System-Feature Kollaboration',
        'description': 'Regelmäßige Reflexionseinträge'
    },
    30: {
        'name': 'Projekt-Portfolio',
        'former_group': 'F',
        'moved_to': 'System-Feature Kollaboration',
        'description': 'Artefakte-Sammlung mit Meta-Kommentar'
    },
    31: {
        'name': 'Projektbasiertes Lernen',
        'former_group': 'F',
        'moved_to': 'System-Feature Kollaboration',
        'description': 'Mehrwöchiges IT-Projekt'
    },
    32: {
        'name': 'Inverted Classroom',
        'former_group': 'F',
        'moved_to': 'System-Feature Kollaboration',
        'description': 'Async Theorie + sync Praxis'
    },
}


# =============================================================================
# NAME-ZU-ID MAPPING (für Legacy-Kompatibilität)
# =============================================================================

# Mapping: Name (DE) -> LM-ID (nur Content-LMs)
LEARNING_METHOD_NAME_TO_ID: Dict[str, int] = {
    method.name: method.lm_id for method in LEARNING_METHODS.values()
}

# Mapping: Prompt-Key -> LM-ID (nur Content-LMs)
PROMPT_KEY_TO_LM_ID: Dict[str, int] = {
    method.prompt_key: method.lm_id for method in LEARNING_METHODS.values()
}

# Legacy-Mapping für Abwärtskompatibilität
LEARNING_METHOD_TO_PROMPT: Dict[str, str] = {
    method.name: method.prompt_key for method in LEARNING_METHODS.values()
}


# =============================================================================
# HELPER-FUNKTIONEN
# =============================================================================

def get_method_by_id(lm_id: int) -> Optional[LearningMethodDefinition]:
    """
    Holt Content-Lernmethode nach ID.

    Args:
        lm_id: Lernmethoden-ID

    Returns:
        LearningMethodDefinition oder None
    """
    return LEARNING_METHODS.get(lm_id)


def get_method_by_name(name: str) -> Optional[LearningMethodDefinition]:
    """
    Holt Content-Lernmethode nach deutschem Namen.

    Args:
        name: Deutscher Name der Methode

    Returns:
        LearningMethodDefinition oder None
    """
    lm_id = LEARNING_METHOD_NAME_TO_ID.get(name)
    if lm_id is not None:
        return LEARNING_METHODS.get(lm_id)
    return None


def get_methods_by_group(group: LearningMethodGroup) -> List[LearningMethodDefinition]:
    """
    Holt alle Content-Lernmethoden einer Gruppe.

    Args:
        group: Gruppen-Code (A, B, C)

    Returns:
        Liste der Lernmethoden in der Gruppe
    """
    return [m for m in LEARNING_METHODS.values() if m.group == group]


def get_prompt_template_for_method(method_name: str) -> str:
    """
    Legacy-Funktion: Holt Prompt-Template-Code für eine Lernmethode.

    Args:
        method_name: Lernmethoden-Name

    Returns:
        Prompt-Template-Code

    Raises:
        ValueError: Wenn Methode nicht gefunden
    """
    template_code = LEARNING_METHOD_TO_PROMPT.get(method_name)

    if not template_code:
        raise ValueError(
            f"Kein Prompt-Template für Lernmethode '{method_name}'. "
            f"Verfügbare Methoden: {', '.join(LEARNING_METHOD_TO_PROMPT.keys())}"
        )

    return template_code


def get_prompt_key_for_lm_id(lm_id: int) -> Optional[str]:
    """
    Holt Prompt-Key für eine LM-ID.

    Args:
        lm_id: Lernmethoden-ID

    Returns:
        Prompt-Key oder None
    """
    method = LEARNING_METHODS.get(lm_id)
    return method.prompt_key if method else None


def get_all_methods_as_dict() -> List[Dict]:
    """
    Gibt alle aktiven Content-Lernmethoden als Liste von Dicts zurück.

    Returns:
        Liste mit allen 19 Content-Lernmethoden als Dicts
    """
    return [
        {
            "lm_id": m.lm_id,
            "name": m.name,
            "group": m.group.value,
            "method_type": m.method_type.value,
            "ki_usage": m.ki_usage.value,
            "prompt_key": m.prompt_key,
            "description": m.description,
        }
        for m in LEARNING_METHODS.values()
    ]


def get_group_info() -> Dict[str, Dict]:
    """
    Gibt Informationen über alle 3 Content-LM-Gruppen zurück.

    Returns:
        Dict mit Gruppeninfos
    """
    group_counts = {}
    for method in LEARNING_METHODS.values():
        group = method.group.value
        if group not in group_counts:
            group_counts[group] = 0
        group_counts[group] += 1

    return {
        'A': {'name': 'Erklärend', 'count': group_counts.get('A', 0)},
        'B': {'name': 'Praxis', 'count': group_counts.get('B', 0)},
        'C': {'name': 'Prüfung', 'count': group_counts.get('C', 0)}
    }


def validate_lm_id(lm_id: int) -> bool:
    """
    Validiert, ob eine LM-ID eine gültige Content-Lernmethode ist.

    Args:
        lm_id: Zu validierende ID

    Returns:
        True wenn gültige Content-LM, False sonst
    """
    return lm_id in LEARNING_METHODS


def is_system_feature(lm_id: int) -> bool:
    """
    Prüft ob eine ID ein System-Feature ist (frühere LM).

    Args:
        lm_id: LM-ID

    Returns:
        True wenn System-Feature
    """
    return lm_id in SYSTEM_FEATURES


def get_system_feature_info(lm_id: int) -> Optional[Dict]:
    """
    Holt Info zu einem System-Feature (wenn vorhanden).

    Args:
        lm_id: Feature-ID

    Returns:
        Feature-Info oder None
    """
    return SYSTEM_FEATURES.get(lm_id)


# =============================================================================
# VALID LM IDs (für DB-Validierung)
# =============================================================================

# Alle gültigen Content-LM IDs (für Constraint-Checks)
VALID_CONTENT_LM_IDS = frozenset(LEARNING_METHODS.keys())
# {0, 1, 2, 3, 6, 8, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25}

# Alle System-Feature IDs (für Referenz)
SYSTEM_FEATURE_IDS = frozenset(SYSTEM_FEATURES.keys())
# {4, 5, 7, 9, 10, 11, 16, 26, 27, 28, 29, 30, 31, 32}
