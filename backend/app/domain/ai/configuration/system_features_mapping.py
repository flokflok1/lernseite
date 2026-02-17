"""
System Features Mapping

Defines all System-Features (Tools/Services separate from Content-LMs).

Categories (10 — 1:1 with DB support_systems.system_features):
- Interactive Tools: whiteboard_engine
- Audio: speech_to_text
- Meta Features: timer_wrapper
- Tutor & Coaching: npc_tutor, socratic_dialog, comprehension_checker
- Gamification: adaptive_difficulty, xp_quest_system, daily_recall
- Learning Paths: learning_path_generator
- Collaboration: peer_review, team_case, learning_journal, project_portfolio, inverted_classroom, peer_instruction, project_based_learning
- Exam Systems: ihk_exam_system, practical_exam_engine, chapter_completion_system
- Visualization: mindmap_generator
- IT Environments: code_sandbox, network_simulation, terminal_access, it_sandbox

FORMERLY Content-LMs (now System-Features):
- Whiteboard-Aufgabe (old lm05) → whiteboard_engine
- Hands-on Lab (old lm10) → it_sandbox
- Zeitlimit-Training (old lm14) → timer_wrapper
- Mündliche Erklärung (old lm17) → speech_to_text
- IHK-Stil Aufgaben (old lm10) → ihk_exam_system
- Multi-Step Praxisprüfung (old lm11) → practical_exam_engine
- Verständnis-Checks (old lm13) → comprehension_checker
- Kapitel-Endprüfung (old lm14) → chapter_completion_system

Referenz: 02a_System-Features.md (Master-Dokument)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SystemFeatureDefinition:
    """Definition of a System Feature (Tool/Service)"""
    feature_code: str
    feature_name: str
    description: str
    category: str
    requires_infrastructure: bool
    requires_external_service: bool
    icon: str
    former_lm_id: Optional[int] = None
    default_config: Optional[dict] = None


# ============================================================================
# System Features Registry
# ============================================================================

SYSTEM_FEATURES: Dict[str, SystemFeatureDefinition] = {
    # ========================================================================
    # Interactive Tools (formerly Content-LMs)
    # ========================================================================
    "whiteboard_engine": SystemFeatureDefinition(
        feature_code="whiteboard_engine",
        feature_name="Whiteboard-Engine",
        description="Interaktive Whiteboard-Aufgaben mit KI-Erkennung (Formeln, Diagramme, Keywords)",
        category="interactive_tools",
        requires_infrastructure=True,
        requires_external_service=True,
        icon="pencil-ruler",
        former_lm_id=5,
        default_config={
            "recognition_types": ["formula", "diagram", "network", "keywords"],
            "ai_feedback": True,
            "save_history": True
        }
    ),
    "it_sandbox": SystemFeatureDefinition(
        feature_code="it_sandbox",
        feature_name="IT-Sandbox",
        description="Praktische Übungen in simulierten IT-Umgebungen (Code, Config, Netzwerk, Terminal)",
        category="it_environments",
        requires_infrastructure=True,
        requires_external_service=True,
        icon="laptop-code",
        former_lm_id=10,
        default_config={
            "sandbox_types": ["code", "config", "network", "terminal"],
            "max_duration": 3600,
            "auto_cleanup": True
        }
    ),
    "speech_to_text": SystemFeatureDefinition(
        feature_code="speech_to_text",
        feature_name="Speech-to-Text Engine",
        description="Sprachaufnahme mit KI-Transkription & Bewertung",
        category="audio",
        requires_infrastructure=True,
        requires_external_service=True,
        icon="microphone",
        former_lm_id=17,
        default_config={
            "max_duration": 600,
            "language": "de-DE",
            "ai_grading": True,
            "provider": "whisper"
        }
    ),

    # ========================================================================
    # Meta Features
    # ========================================================================
    "timer_wrapper": SystemFeatureDefinition(
        feature_code="timer_wrapper",
        feature_name="Timer/Zeitlimit-Feature",
        description="Zeitbegrenzung für beliebige Aufgaben (Meta-Feature)",
        category="meta_features",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="clock",
        former_lm_id=14,
        default_config={
            "default_time_limit": 60,
            "show_remaining_time": True,
            "auto_submit": True
        }
    ),

    # ========================================================================
    # Visualization Features
    # ========================================================================
    "mindmap_generator": SystemFeatureDefinition(
        feature_code="mindmap_generator",
        feature_name="Mindmap-Generator",
        description="Generiert kursweite Mindmaps aus Theorie-Inhalten",
        category="visualization",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="sitemap",
        former_lm_id=None,
        default_config={
            "auto_generate": True,
            "max_depth": 3,
            "style": "hierarchical"
        }
    ),

    # ========================================================================
    # Tutor & Coaching
    # ========================================================================
    "npc_tutor": SystemFeatureDefinition(
        feature_code="npc_tutor",
        feature_name="NPC-/Persona-Tutor",
        description="KI-basierter Tutor mit verschiedenen Rollen/Personas",
        category="tutor",
        requires_infrastructure=False,
        requires_external_service=True,
        icon="user-graduate",
        former_lm_id=None,
        default_config={
            "personas": ["professor", "peer", "mentor", "coach"],
            "conversation_style": "adaptive",
            "remember_context": True
        }
    ),
    "socratic_dialog": SystemFeatureDefinition(
        feature_code="socratic_dialog",
        feature_name="Sokratischer Dialog",
        description="KI-geführter Dialog zur Wissensvermittlung",
        category="tutor",
        requires_infrastructure=False,
        requires_external_service=True,
        icon="comments",
        former_lm_id=None,
        default_config={
            "max_questions": 10,
            "difficulty_adaptation": True
        }
    ),

    # ========================================================================
    # Gamification
    # ========================================================================
    "adaptive_difficulty": SystemFeatureDefinition(
        feature_code="adaptive_difficulty",
        feature_name="Adaptive Schwierigkeit",
        description="Passt Aufgabenschwierigkeit automatisch an Leistungsstand an",
        category="gamification",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="chart-line",
        former_lm_id=None,
        default_config={
            "adjustment_algorithm": "elo",
            "min_attempts": 3
        }
    ),
    "xp_quest_system": SystemFeatureDefinition(
        feature_code="xp_quest_system",
        feature_name="XP & Quest System",
        description="Erfahrungspunkte, Level, Achievements, Daily Quests",
        category="gamification",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="trophy",
        former_lm_id=None,
        default_config={
            "xp_per_task": 100,
            "daily_quests_count": 3
        }
    ),
    "daily_recall": SystemFeatureDefinition(
        feature_code="daily_recall",
        feature_name="Daily Recall",
        description="Tägliche Wiederholungslogik (Spaced Repetition)",
        category="gamification",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="calendar-check",
        former_lm_id=None,
        default_config={
            "algorithm": "sm2",
            "daily_limit": 20
        }
    ),

    # ========================================================================
    # Learning Paths
    # ========================================================================
    "learning_path_generator": SystemFeatureDefinition(
        feature_code="learning_path_generator",
        feature_name="Lernpfad-Generator",
        description="KI-gestützte Lernpfad-Erstellung und -Optimierung",
        category="learning_paths",
        requires_infrastructure=False,
        requires_external_service=True,
        icon="route",
        former_lm_id=None,
        default_config={
            "personalized": True,
            "adapt_to_performance": True
        }
    ),

    # ========================================================================
    # Collaboration
    # ========================================================================
    "peer_review": SystemFeatureDefinition(
        feature_code="peer_review",
        feature_name="Peer Review",
        description="Gegenseitige Bewertung von Lösungen",
        category="collaboration",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="users",
        former_lm_id=None,
        default_config={
            "anonymous": True,
            "min_reviews": 2
        }
    ),
    "team_case": SystemFeatureDefinition(
        feature_code="team_case",
        feature_name="Team-Case",
        description="Kollaborative Fallbearbeitung",
        category="collaboration",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="people-carry",
        former_lm_id=None
    ),
    "learning_journal": SystemFeatureDefinition(
        feature_code="learning_journal",
        feature_name="Lerntagebuch",
        description="Persönliche Reflexion und Dokumentation",
        category="collaboration",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="book",
        former_lm_id=None
    ),
    "project_portfolio": SystemFeatureDefinition(
        feature_code="project_portfolio",
        feature_name="Projekt-Portfolio",
        description="Sammlung eigener Projekte",
        category="collaboration",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="folder-open",
        former_lm_id=None
    ),
    "inverted_classroom": SystemFeatureDefinition(
        feature_code="inverted_classroom",
        feature_name="Inverted Classroom",
        description="Flipped Classroom Unterstützung",
        category="collaboration",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="chalkboard-teacher",
        former_lm_id=None
    ),
    "peer_instruction": SystemFeatureDefinition(
        feature_code="peer_instruction",
        feature_name="Peer Instruction",
        description="Peer Instruction Methode mit interaktiven Diskussionen",
        category="collaboration",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="comments",
        former_lm_id=None
    ),
    "project_based_learning": SystemFeatureDefinition(
        feature_code="project_based_learning",
        feature_name="Project-Based Learning",
        description="Projektbasiertes Lernen mit Kollaborations-Tools",
        category="collaboration",
        requires_infrastructure=False,
        requires_external_service=False,
        icon="project-diagram",
        former_lm_id=None
    ),

    # ========================================================================
    # Exam & Assessment Systems
    # ========================================================================
    "ihk_exam_system": SystemFeatureDefinition(
        feature_code="ihk_exam_system",
        feature_name="IHK-Prüfungssystem",
        description="Prüfungsaufgaben nach IHK/Kammer-Standard mit spezieller Bewertungslogik",
        category="exam_systems",
        requires_infrastructure=True,
        requires_external_service=True,
        icon="file-certificate",
        former_lm_id=10,
        default_config={
            "question_types": ["multiple_choice", "scenario", "calculation"],
            "time_limit": 60,
            "certification_mode": True
        }
    ),
    "practical_exam_engine": SystemFeatureDefinition(
        feature_code="practical_exam_engine",
        feature_name="Praxisprüfungs-Engine",
        description="Mehrstufige praktische Prüfungen mit Bewertungslogik",
        category="exam_systems",
        requires_infrastructure=True,
        requires_external_service=True,
        icon="tasks",
        former_lm_id=11,
        default_config={
            "min_steps": 3,
            "partial_grading": True,
            "real_world_simulation": True
        }
    ),
    "comprehension_checker": SystemFeatureDefinition(
        feature_code="comprehension_checker",
        feature_name="Verständnis-Checker",
        description="Automatische Verständniskontrolle nach Lerneinheiten (Tutor-Feature)",
        category="tutor",
        requires_infrastructure=False,
        requires_external_service=True,
        icon="check-square",
        former_lm_id=13,
        default_config={
            "questions_per_check": 5,
            "instant_feedback": True,
            "adaptive_difficulty": True
        }
    ),
    "chapter_completion_system": SystemFeatureDefinition(
        feature_code="chapter_completion_system",
        feature_name="Kapitelabschluss-System",
        description="Umfassende Abschlussprüfung mit Fortschrittstracking",
        category="exam_systems",
        requires_infrastructure=True,
        requires_external_service=True,
        icon="graduation-cap",
        former_lm_id=14,
        default_config={
            "comprehensive": True,
            "time_limit": 90,
            "certificate_on_pass": True,
            "unlock_next_chapter": True
        }
    ),

    # ========================================================================
    # IT Environments (specific types)
    # ========================================================================
    "code_sandbox": SystemFeatureDefinition(
        feature_code="code_sandbox",
        feature_name="Code-Sandbox",
        description="Isolierte Code-Ausführungsumgebung",
        category="it_environments",
        requires_infrastructure=True,
        requires_external_service=False,
        icon="code",
        former_lm_id=None,
        default_config={
            "languages": ["python", "javascript", "java", "go"],
            "max_execution_time": 30
        }
    ),
    "network_simulation": SystemFeatureDefinition(
        feature_code="network_simulation",
        feature_name="Netzwerk-Simulation",
        description="Virtuelle Netzwerk-Topologien",
        category="it_environments",
        requires_infrastructure=True,
        requires_external_service=False,
        icon="network-wired",
        former_lm_id=None,
        default_config={
            "max_nodes": 20,
            "protocols": ["tcp", "udp", "icmp"]
        }
    ),
    "terminal_access": SystemFeatureDefinition(
        feature_code="terminal_access",
        feature_name="Terminal-Zugriff",
        description="Web-basierter Terminal-Zugang",
        category="it_environments",
        requires_infrastructure=True,
        requires_external_service=False,
        icon="terminal",
        former_lm_id=None,
        default_config={
            "shell": "bash",
            "max_session_time": 1800
        }
    ),
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_system_feature(feature_code: str) -> Optional[SystemFeatureDefinition]:
    """Get system feature definition by code"""
    return SYSTEM_FEATURES.get(feature_code)


def get_features_by_category(category: str) -> List[SystemFeatureDefinition]:
    """Get all system features for a specific category"""
    return [f for f in SYSTEM_FEATURES.values() if f.category == category]


def get_features_requiring_infrastructure() -> List[SystemFeatureDefinition]:
    """Get all features that require infrastructure"""
    return [f for f in SYSTEM_FEATURES.values() if f.requires_infrastructure]


def get_features_requiring_external_service() -> List[SystemFeatureDefinition]:
    """Get all features that require external services (AI, APIs)"""
    return [f for f in SYSTEM_FEATURES.values() if f.requires_external_service]


def is_valid_feature_code(feature_code: str) -> bool:
    """Check if feature code is valid"""
    return feature_code in SYSTEM_FEATURES


def get_feature_default_config(feature_code: str) -> Optional[dict]:
    """Get default config for feature"""
    feature = get_system_feature(feature_code)
    return feature.default_config if feature else None


# ============================================================================
# Categories
# ============================================================================
FEATURE_CATEGORIES = {
    # 10 DB categories with 25 features (source: support_systems.system_features)
    # Note: math_toolkit is NOT listed here — it has no DB category entry
    # and is managed separately via /system-features/math/toolkit/ endpoints.
    "interactive_tools": ["whiteboard_engine"],
    "audio": ["speech_to_text"],
    "meta_features": ["timer_wrapper"],
    "visualization": ["mindmap_generator"],
    "tutor": ["npc_tutor", "socratic_dialog", "comprehension_checker"],
    "gamification": ["adaptive_difficulty", "xp_quest_system", "daily_recall"],
    "learning_paths": ["learning_path_generator"],
    "collaboration": ["peer_review", "team_case", "learning_journal", "project_portfolio", "inverted_classroom", "peer_instruction", "project_based_learning"],
    "exam_systems": ["ihk_exam_system", "practical_exam_engine", "chapter_completion_system"],
    "it_environments": ["code_sandbox", "network_simulation", "terminal_access", "it_sandbox"],
}
