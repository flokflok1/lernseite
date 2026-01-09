"""
Learning Method Mapping - Content-LMs Only (12 Methoden)

Defines the 12 Content-Lernmethoden (lm00-lm11).
System-Features are in system_features_mapping.py

Structure:
- Gruppe A (Erklärend): lm00-lm04 (5 Methoden)
- Gruppe B (Praxis):    lm05-lm08 (4 Methoden)
- Gruppe C (Prüfung):   lm09-lm11 (3 Methoden)

REMOVED (now System-Features):
- Whiteboard-Aufgabe (old lm05) → whiteboard_engine
- Hands-on Lab (old lm10) → it_sandbox
- Zeitlimit-Training (old lm14) → timer_wrapper
- Mündliche Erklärung (old lm17) → speech_to_text
- IHK-Stil Aufgaben (old lm10) → ihk_exam_system
- Multi-Step Praxisprüfung (old lm11) → practical_exam_engine
- Verständnis-Checks (old lm13) → comprehension_checker
- Kapitel-Endprüfung (old lm14) → chapter_completion_system

Referenz: 02_Lernmethoden.md (Master-Dokument)
          02a_System-Features.md (System-Features)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class AgentSupport:
    """Agent-based learning support configuration"""
    agent_can_handle: bool  # Can agent answer without AI?
    requires_fresh_ai: bool  # Always needs fresh AI generation?
    knowledge_domains: List[str]  # Which knowledge domains? (networking, programming, etc.)
    knowledge_cacheable: bool  # Can agent cache answers for this LM?
    complexity_threshold: int  # 1-5: When to escalate to AI (1=low, 5=high)


@dataclass
class LearningMethodDefinition:
    """Definition of a Content-Lernmethode (Aufgabenformat)"""
    lm_id: int
    name: str
    description: str
    group: str  # A, B, C
    tier: str  # basic, premium
    icon: str
    prompt_template: Optional[str] = None
    default_config: Optional[dict] = None
    agent_support: Optional[AgentSupport] = None  # New: Agent-based intelligence


# ============================================================================
# Content-Lernmethoden Registry (12 LMs)
# ============================================================================

LEARNING_METHODS: Dict[int, LearningMethodDefinition] = {
    # ========================================================================
    # Gruppe A: Erklärend (lm00-lm04) - 5 Methoden
    # ========================================================================
    0: LearningMethodDefinition(
        lm_id=0,
        name="Tiefgehende Erklärung",
        description="Erklärung mit Beispielen & Analogien (Agent entscheidet: DB vs AI)",
        group="A",
        tier="basic",
        icon="book-open",
        prompt_template="deep_explanation",
        default_config={"min_examples": 2, "include_analogies": True},
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["general"],
            knowledge_cacheable=True,
            complexity_threshold=2
        )
    ),
    1: LearningMethodDefinition(
        lm_id=1,
        name="Schritt-für-Schritt",
        description="Sequenzielle Anleitung in nummerierten Schritten",
        group="A",
        tier="basic",
        icon="list-ordered",
        prompt_template="step_by_step",
        default_config={"min_steps": 3, "max_steps": 10},
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["general"],
            knowledge_cacheable=True,
            complexity_threshold=2
        )
    ),
    2: LearningMethodDefinition(
        lm_id=2,
        name="Interaktive Theorie",
        description="Theorie mit interaktiven Frage-Antwort-Elementen",
        group="A",
        tier="basic",
        icon="lightbulb",
        prompt_template="interactive_theory",
        default_config={"question_frequency": "medium", "feedback_mode": "immediate"},
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["general"],
            knowledge_cacheable=True,
            complexity_threshold=2
        )
    ),
    3: LearningMethodDefinition(
        lm_id=3,
        name="Diagramm/Visualisierung",
        description="Grafische Darstellung komplexer Konzepte (User erstellt Diagramm)",
        group="A",
        tier="basic",
        icon="chart-network",
        prompt_template="diagram_visualization",
        default_config={"diagram_type": "network", "render_engine": "mermaid"},
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["general"],
            knowledge_cacheable=True,
            complexity_threshold=3
        )
    ),
    4: LearningMethodDefinition(
        lm_id=4,
        name="Beispiel-Szenario",
        description="Praxisnahes Anwendungsbeispiel mit Kontext",
        group="A",
        tier="basic",
        icon="clipboard-list",
        prompt_template="example_scenario",
        default_config={"complexity": "medium", "allow_multiple_solutions": True},
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["general"],
            knowledge_cacheable=True,
            complexity_threshold=3
        )
    ),

    # ========================================================================
    # Gruppe B: Praxis (lm05-lm08) - 4 Methoden
    # ========================================================================
    5: LearningMethodDefinition(
        lm_id=5,
        name="Mathe-Interaktiv",
        description="Mathematische Aufgaben mit Schritt-Erkennung",
        group="B",
        tier="basic",
        icon="calculator",
        prompt_template="math_interactive",
        default_config={"show_steps": True, "allow_calculator": False},
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["math"],
            knowledge_cacheable=True,
            complexity_threshold=3
        )
    ),
    6: LearningMethodDefinition(
        lm_id=6,
        name="Flashcards",
        description="Digitale Lernkarten für Wiederholung",
        group="B",
        tier="basic",
        icon="cards",
        prompt_template="flashcards",
        default_config={"spaced_repetition": True, "shuffle": True},
        agent_support=AgentSupport(
            agent_can_handle=False,
            requires_fresh_ai=False,
            knowledge_domains=[],
            knowledge_cacheable=False,
            complexity_threshold=1
        )
    ),
    7: LearningMethodDefinition(
        lm_id=7,
        name="Drag & Drop",
        description="Zuordnungsaufgaben per Drag & Drop",
        group="B",
        tier="basic",
        icon="hand-pointer",
        prompt_template="drag_drop",
        default_config={"randomize_order": True, "show_hints": False},
        agent_support=AgentSupport(
            agent_can_handle=False,
            requires_fresh_ai=False,
            knowledge_domains=[],
            knowledge_cacheable=False,
            complexity_threshold=1
        )
    ),
    8: LearningMethodDefinition(
        lm_id=8,
        name="Lückentext",
        description="Lückentexte mit Auto-Korrektur",
        group="B",
        tier="basic",
        icon="align-left",
        prompt_template="fill_blanks",
        default_config={"case_sensitive": False, "allow_synonyms": True},
        agent_support=AgentSupport(
            agent_can_handle=False,
            requires_fresh_ai=False,
            knowledge_domains=[],
            knowledge_cacheable=False,
            complexity_threshold=1
        )
    ),

    # ========================================================================
    # Gruppe C: Prüfung (lm09-lm11) - 3 Methoden
    # ========================================================================
    9: LearningMethodDefinition(
        lm_id=9,
        name="Freitext-Langantwort",
        description="Offene Fragen mit Agent-Bewertung (nutzt DB-Wissen + AI bei Bedarf)",
        group="C",
        tier="premium",
        icon="pen-fancy",
        prompt_template="long_answer",
        default_config={"min_words": 100, "ai_grading": True},
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["general"],
            knowledge_cacheable=True,
            complexity_threshold=4
        )
    ),
    10: LearningMethodDefinition(
        lm_id=10,
        name="Multiple-Choice Quiz",
        description="Multiple-Choice Quiz in Prüfungsformat",
        group="C",
        tier="basic",
        icon="question-circle",
        prompt_template="multiple_choice_quiz",
        default_config={"questions_per_set": 20, "randomize": True},
        agent_support=AgentSupport(
            agent_can_handle=False,
            requires_fresh_ai=False,
            knowledge_domains=[],
            knowledge_cacheable=False,
            complexity_threshold=1
        )
    ),
    11: LearningMethodDefinition(
        lm_id=11,
        name="True/False",
        description="Richtig/Falsch Aussagen bewerten",
        group="C",
        tier="basic",
        icon="check-circle",
        prompt_template="true_false",
        default_config={"randomize": True, "show_explanations": True},
        agent_support=AgentSupport(
            agent_can_handle=False,
            requires_fresh_ai=False,
            knowledge_domains=[],
            knowledge_cacheable=False,
            complexity_threshold=1
        )
    ),
}


# ============================================================================
# Active Content-LMs (12)
# ============================================================================
ACTIVE_LEARNING_METHODS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


# ============================================================================
# Groups
# ============================================================================
GROUP_A_EXPLAINING = [0, 1, 2, 3, 4]  # 5 LMs
GROUP_B_PRACTICE = [5, 6, 7, 8]  # 4 LMs
GROUP_C_EXAM = [9, 10, 11]  # 3 LMs


# ============================================================================
# Helper Functions
# ============================================================================

def get_learning_method(lm_id: int) -> Optional[LearningMethodDefinition]:
    """Get learning method definition by ID"""
    return LEARNING_METHODS.get(lm_id)


def get_learning_methods_by_group(group: str) -> List[LearningMethodDefinition]:
    """Get all learning methods for a specific group (A, B, C)"""
    return [lm for lm in LEARNING_METHODS.values() if lm.group == group]


def get_learning_methods_by_tier(tier: str) -> List[LearningMethodDefinition]:
    """Get all learning methods for a specific tier (basic, premium)"""
    return [lm for lm in LEARNING_METHODS.values() if lm.tier == tier]


def get_learning_methods_with_agent_support() -> List[LearningMethodDefinition]:
    """Get all learning methods that have agent support enabled"""
    return [lm for lm in LEARNING_METHODS.values() if lm.agent_support and lm.agent_support.agent_can_handle]


def get_learning_methods_by_domain(domain: str) -> List[LearningMethodDefinition]:
    """Get all learning methods for a specific knowledge domain"""
    return [
        lm for lm in LEARNING_METHODS.values()
        if lm.agent_support and domain in lm.agent_support.knowledge_domains
    ]


def is_valid_lm_id(lm_id: int) -> bool:
    """Check if LM ID is valid (0-11 for Content-LMs)"""
    return lm_id in ACTIVE_LEARNING_METHODS


# Backward compatibility aliases
def validate_lm_id(lm_id: int) -> bool:
    """Alias for is_valid_lm_id (backward compatibility)"""
    return is_valid_lm_id(lm_id)


def get_method_by_id(lm_id: int) -> Optional[LearningMethodDefinition]:
    """Alias for get_learning_method (backward compatibility)"""
    return get_learning_method(lm_id)


def get_all_methods_as_dict() -> Dict[int, Dict[str, Any]]:
    """
    Get all learning methods as dictionary (for API responses)

    Returns:
        Dict mapping lm_id to serialized LearningMethodDefinition
    """
    result = {}
    for lm_id, lm in LEARNING_METHODS.items():
        result[lm_id] = {
            "lm_id": lm.lm_id,
            "name": lm.name,
            "description": lm.description,
            "group": lm.group,
            "tier": lm.tier,
            "icon": lm.icon,
            "prompt_template": lm.prompt_template,
            "default_config": lm.default_config,
            "agent_support": {
                "agent_can_handle": lm.agent_support.agent_can_handle,
                "requires_fresh_ai": lm.agent_support.requires_fresh_ai,
                "knowledge_domains": lm.agent_support.knowledge_domains,
                "knowledge_cacheable": lm.agent_support.knowledge_cacheable,
                "complexity_threshold": lm.agent_support.complexity_threshold
            } if lm.agent_support else None
        }
    return result


def get_group_info(group: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a learning method group

    Args:
        group: Group identifier (A, B, C)

    Returns:
        Dict with group info or None if invalid
    """
    groups = {
        "A": {
            "name": "Erklärend",
            "description": "Explaining methods for understanding concepts",
            "lm_ids": GROUP_A_EXPLAINING,
            "count": len(GROUP_A_EXPLAINING)
        },
        "B": {
            "name": "Praxis",
            "description": "Practice methods for applying knowledge",
            "lm_ids": GROUP_B_PRACTICE,
            "count": len(GROUP_B_PRACTICE)
        },
        "C": {
            "name": "Prüfung",
            "description": "Exam preparation methods",
            "lm_ids": GROUP_C_EXAM,
            "count": len(GROUP_C_EXAM)
        }
    }
    return groups.get(group.upper())


def get_lm_prompt_template(lm_id: int) -> Optional[str]:
    """Get prompt template key for LM"""
    lm = get_learning_method(lm_id)
    return lm.prompt_template if lm else None


def get_lm_default_config(lm_id: int) -> Optional[dict]:
    """Get default config for LM"""
    lm = get_learning_method(lm_id)
    return lm.default_config if lm else None


# ============================================================================
# Validation
# ============================================================================

def validate_lm_data(lm_id: int, data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate LM data structure

    Returns:
        (is_valid, error_message)
    """
    lm = get_learning_method(lm_id)
    if not lm:
        return False, f"Invalid LM ID: {lm_id}. Valid range: 0-11"

    # Add specific validation logic per LM type here
    # For now, just basic validation
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"

    return True, None
