"""
LernsystemX KI - Learning Method Mapping (31 Methoden, 6 Gruppen A-F)

Vollständiges Mapping aller 31 aktiven Lernmethoden auf:
- Name (Deutsch)
- Gruppe (A, B, C, D, E, F)
- Typ (explanatory, practice, exam, pro, it, collaborative)
- Default Prompt-Key
- KI-Nutzungsintensität

WICHTIG: LM05 (Mindmap) und LM07 (NPC-Tutor) sind deaktiviert und wurden
zu CourseFeatures bzw. TutorAgent verschoben.

Aktuelle LM-Struktur (Stand: 2025):
- A: Erklärend (LM00-LM03, LM06) - 5 Methoden
- B: Praxis (LM08, LM12-LM15, LM17) - 6 Methoden
- C: Prüfung (LM18-LM25) - 8 Methoden
- D: Pro (LM04) - 1 Methode
- E: IT (LM09-LM11, LM16) - 4 Methoden
- F: Kollaborativ (LM26-LM32) - 7 Methoden

Referenz: 02_Lernmethoden.md (Master-Dokument - muss aktualisiert werden)
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


class LearningMethodGroup(str, Enum):
    """Gruppen-Codes für die 31 aktiven Lernmethoden (6 Gruppen)"""
    A = 'A'  # Erklärende Methoden (LM00-LM03, LM06) - 5 Methoden
    B = 'B'  # Praxis/Übung (LM08, LM12-LM15, LM17) - 6 Methoden
    C = 'C'  # Prüfungsorientiert (LM18-LM25) - 8 Methoden
    D = 'D'  # Pro (LM04) - 1 Methode
    E = 'E'  # IT-Spezifisch (LM09-LM11, LM16) - 4 Methoden
    F = 'F'  # Kollaborativ (LM26-LM32) - 7 Methoden


class LearningMethodType(str, Enum):
    """Methodentypen für semantische Klassifizierung"""
    EXPLANATORY = 'explanatory'      # Erklärend (A)
    PRACTICE = 'practice'            # Übung (B)
    EXAM = 'exam'                    # Prüfung (C)
    PRO = 'pro'                      # Pro (D)
    IT = 'it'                        # IT-Spezifisch (E)
    COLLABORATIVE = 'collaborative'  # Kollaborativ (F)


class KIUsage(str, Enum):
    """KI-Nutzungsintensität"""
    INTENSIVE = 'intensive'  # KI-intensiv (Vollgenerierung)
    MEDIUM = 'medium'        # Mittlere KI-Nutzung (Unterstützung)
    OPTIONAL = 'optional'    # KI optional (manuelle Erstellung möglich)


@dataclass(frozen=True)
class LearningMethodDefinition:
    """Definition einer Lernmethode"""
    lm_id: int                          # 0-32 (mit Lücken bei 5, 7)
    name: str                           # Deutscher Name
    group: LearningMethodGroup          # A, B, C, D, E, F
    method_type: LearningMethodType     # explanatory, practice, exam, pro, it, collaborative
    ki_usage: KIUsage                   # intensive, medium, optional
    prompt_key: str                     # Prompt-Template-Key
    description: str                    # Kurzbeschreibung
    active: bool = True                 # Ob die Methode aktiv ist


# =============================================================================
# VOLLSTÄNDIGES MAPPING ALLER 31 AKTIVEN LERNMETHODEN
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
    # LM05 (Mindmap) ist DEAKTIVIERT - verschoben zu CourseFeatures
    6: LearningMethodDefinition(
        lm_id=6,
        name="Beispiel-Szenario",
        group=LearningMethodGroup.A,
        method_type=LearningMethodType.EXPLANATORY,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="scenario_explanation",
        description="Realitätsnahe Case-Erklärung eines Konzepts"
    ),
    # LM07 (NPC-Tutor) ist DEAKTIVIERT - verschoben zu TutorAgent

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

    # =========================================================================
    # GRUPPE D – Pro (1 Methode)
    # =========================================================================
    4: LearningMethodDefinition(
        lm_id=4,
        name="Sokratischer Dialog",
        group=LearningMethodGroup.D,
        method_type=LearningMethodType.PRO,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="socratic_dialog",
        description="KI fragt, User leitet Konzept selbst her"
    ),

    # =========================================================================
    # GRUPPE E – IT-Spezifisch (4 Methoden)
    # =========================================================================
    9: LearningMethodDefinition(
        lm_id=9,
        name="Code/IT-Config Sandbox",
        group=LearningMethodGroup.E,
        method_type=LearningMethodType.IT,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="code_sandbox",
        description="Code-/Config-Editor mit Tests & Output"
    ),
    10: LearningMethodDefinition(
        lm_id=10,
        name="Netzwerk-Simulation",
        group=LearningMethodGroup.E,
        method_type=LearningMethodType.IT,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="network_sim",
        description="Simulierte Netzumgebung (Router, Switch, Ping)"
    ),
    11: LearningMethodDefinition(
        lm_id=11,
        name="IT-Szenario lösen",
        group=LearningMethodGroup.E,
        method_type=LearningMethodType.IT,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="it_scenario",
        description="Troubleshooting mit Logs/Configs"
    ),
    16: LearningMethodDefinition(
        lm_id=16,
        name="Fehleranalyse",
        group=LearningMethodGroup.E,
        method_type=LearningMethodType.IT,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="error_analysis",
        description="Defekter Code/Config, Fehler finden & erklären"
    ),

    # =========================================================================
    # GRUPPE F – Kollaborativ (7 Methoden)
    # =========================================================================
    26: LearningMethodDefinition(
        lm_id=26,
        name="Peer Instruction",
        group=LearningMethodGroup.F,
        method_type=LearningMethodType.COLLABORATIVE,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="peer_instruction",
        description="Think–Pair–Share mit Erstantwort → Diskussion"
    ),
    27: LearningMethodDefinition(
        lm_id=27,
        name="Team-Case / Gruppenfallarbeit",
        group=LearningMethodGroup.F,
        method_type=LearningMethodType.COLLABORATIVE,
        ki_usage=KIUsage.INTENSIVE,
        prompt_key="team_case",
        description="Teams lösen Fall mit Rollen"
    ),
    28: LearningMethodDefinition(
        lm_id=28,
        name="Peer Review (strukturiert)",
        group=LearningMethodGroup.F,
        method_type=LearningMethodType.COLLABORATIVE,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="peer_review",
        description="Rubric-basiertes Feedback zu Arbeiten anderer"
    ),
    29: LearningMethodDefinition(
        lm_id=29,
        name="Lerntagebuch / Learning Journal",
        group=LearningMethodGroup.F,
        method_type=LearningMethodType.COLLABORATIVE,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="learning_journal",
        description="Regelmäßige Reflexionseinträge"
    ),
    30: LearningMethodDefinition(
        lm_id=30,
        name="Projekt-Portfolio",
        group=LearningMethodGroup.F,
        method_type=LearningMethodType.COLLABORATIVE,
        ki_usage=KIUsage.OPTIONAL,
        prompt_key="portfolio",
        description="Artefakte-Sammlung mit Meta-Kommentar"
    ),
    31: LearningMethodDefinition(
        lm_id=31,
        name="Projektbasiertes Lernen",
        group=LearningMethodGroup.F,
        method_type=LearningMethodType.COLLABORATIVE,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="project_based",
        description="Mehrwöchiges IT-Projekt"
    ),
    32: LearningMethodDefinition(
        lm_id=32,
        name="Inverted Classroom",
        group=LearningMethodGroup.F,
        method_type=LearningMethodType.COLLABORATIVE,
        ki_usage=KIUsage.MEDIUM,
        prompt_key="inverted_classroom",
        description="Async Theorie + sync Praxis"
    ),
}


# =============================================================================
# DEAKTIVIERTE METHODEN (für Referenz)
# =============================================================================

DEACTIVATED_METHODS = {
    5: {
        'name': 'Mindmap-Generator',
        'reason': 'Verschoben zu CourseFeatures (kurs-weite Funktion)',
        'replacement': 'CourseFeatures.mindmap'
    },
    7: {
        'name': 'NPC-Tutor-Lecture',
        'reason': 'Verschoben zu TutorAgent (eigenständiges System)',
        'replacement': 'TutorAgent'
    }
}


# =============================================================================
# NAME-ZU-ID MAPPING (für Legacy-Kompatibilität)
# =============================================================================

# Mapping: Name (DE) -> LM-ID
LEARNING_METHOD_NAME_TO_ID: Dict[str, int] = {
    method.name: method.lm_id for method in LEARNING_METHODS.values()
}

# Mapping: Prompt-Key -> LM-ID
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
    Holt Lernmethode nach ID.

    Args:
        lm_id: Lernmethoden-ID

    Returns:
        LearningMethodDefinition oder None
    """
    return LEARNING_METHODS.get(lm_id)


def get_method_by_name(name: str) -> Optional[LearningMethodDefinition]:
    """
    Holt Lernmethode nach deutschem Namen.

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
    Holt alle Lernmethoden einer Gruppe.

    Args:
        group: Gruppen-Code (A, B, C, D, E, F)

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
    Gibt alle aktiven Lernmethoden als Liste von Dicts zurück (für API-Responses).

    Returns:
        Liste mit allen Lernmethoden als Dicts
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
    Gibt Informationen über alle 6 Gruppen zurück.

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
        'C': {'name': 'Prüfung', 'count': group_counts.get('C', 0)},
        'D': {'name': 'Pro', 'count': group_counts.get('D', 0)},
        'E': {'name': 'IT', 'count': group_counts.get('E', 0)},
        'F': {'name': 'Kollaborativ', 'count': group_counts.get('F', 0)}
    }


def validate_lm_id(lm_id: int) -> bool:
    """
    Validiert, ob eine LM-ID gültig ist (aktive Methode).

    Args:
        lm_id: Zu validierende ID

    Returns:
        True wenn gültig und aktiv, False sonst
    """
    return lm_id in LEARNING_METHODS


def is_method_deactivated(lm_id: int) -> bool:
    """
    Prüft ob eine Methode deaktiviert wurde.

    Args:
        lm_id: LM-ID

    Returns:
        True wenn deaktiviert
    """
    return lm_id in DEACTIVATED_METHODS
