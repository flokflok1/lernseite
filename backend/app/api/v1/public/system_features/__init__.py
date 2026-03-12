"""
System Features API Package

25 System-Features organized in 10 categories.
System-Features differ from Content-Lernmethoden (12 LMs) by providing
infrastructure-level functionality (tools & services) rather than content formats.

Structure:
├── interactive/       # Interactive Tools (1 feature)
│   └── whiteboard.py         # Whiteboard Engine
├── audio/             # Audio (1 feature)
│   └── speech_to_text.py     # Speech-to-Text
├── exam/              # Exam & Assessment (3 features + simulations)
│   ├── ihk_exam.py           # IHK Exam System
│   ├── practical_exam.py     # Practical Exam Engine
│   ├── chapter_completion.py # Chapter Completion System
│   └── simulations/          # Exam Simulations (existing)
├── math_toolkit/      # Math Tools (1 feature + toolkit)
│   ├── admin/                # Admin functions
│   └── user/                 # User practice/reference/tasks
├── gamification/      # Gamification (3 features)
│   ├── adaptive_difficulty.py
│   ├── xp_quest_system.py
│   └── daily_recall.py
├── tutor/             # Tutor & Coaching (3 features)
│   ├── npc_tutor.py
│   ├── socratic_dialog.py
│   └── comprehension_checker.py # Comprehension Checker
├── collaboration/     # Collaboration (7 features)
│   ├── peer_instruction.py
│   ├── team_case.py
│   ├── peer_review.py
│   ├── learning_journal.py
│   ├── project_portfolio.py
│   ├── project_based_learning.py
│   └── inverted_classroom.py
├── it_environments/   # IT Environments (4 features)
│   ├── code_sandbox.py
│   ├── network_simulation.py
│   ├── terminal_access.py
│   └── it_sandbox.py         # IT Sandbox
├── meta/              # Meta Features (1 feature)
│   └── timer_wrapper.py
├── visualization/     # Visualization (1 feature)
│   └── mindmap_generator.py
├── learning_paths/    # Learning Paths (1 feature)
│   └── path_generator.py
└── registry.py        # Feature Registry (Panel API)

Endpoints:
- /api/v1/system-features/* - All system feature endpoints
- /api/v1/panel/system-features - Feature registry (CRUD)

ISO 9001:2015 compliant - Feature Management Layer
"""

from flask import Blueprint

# =============================================================================
# EXISTING FEATURES (Already Implemented)
# =============================================================================

# Exam Features (existing: simulations, question generator)
from app.api.v1.public.system_features.exam import exams_bp, question_generator_bp

# Math Features (existing: toolkit)
from app.api.v1.public.system_features.math import (
    math_practice_bp,
    math_reference_bp,
    math_tasks_bp
)

# Feature Registry (Panel API - existing)
from app.api.v1.public.system_features.registry import bp as registry_bp

# =============================================================================
# NEW FEATURES (Stubs - TODO: Implementation)
# =============================================================================

# TODO: Import blueprints from feature modules when implemented
# from app.api.v1.public.system_features.interactive import whiteboard_bp
# from app.api.v1.public.system_features.audio import speech_bp
# from app.api.v1.public.system_features.exam import ihk_exam_bp, practical_exam_bp, chapter_completion_bp
# from app.api.v1.public.system_features.gamification import adaptive_difficulty_bp, xp_quest_bp, daily_recall_bp
# from app.api.v1.public.system_features.tutor import npc_tutor_bp, socratic_dialog_bp, comprehension_bp
# from app.api.v1.public.system_features.collaboration import (
#     peer_instruction_bp, team_case_bp, peer_review_bp, learning_journal_bp,
#     project_portfolio_bp, project_based_learning_bp, inverted_classroom_bp
# )
# from app.api.v1.public.system_features.it_environments import code_sandbox_bp, network_simulation_bp, terminal_access_bp, it_sandbox_bp
# from app.api.v1.public.system_features.meta import timer_wrapper_bp
# from app.api.v1.public.system_features.visualization import mindmap_generator_bp
# from app.api.v1.public.system_features.learning_paths import path_generator_bp

# =============================================================================
# MAIN BLUEPRINT - System Features
# =============================================================================

system_features_bp = Blueprint('system_features', __name__, url_prefix='/system-features')

# =============================================================================
# REGISTER EXISTING FEATURES
# =============================================================================

# Exam Simulations
system_features_bp.register_blueprint(exams_bp, url_prefix='/exam/simulations')

# Question Generator (user-facing practice exam generation)
system_features_bp.register_blueprint(question_generator_bp)

# Math Toolkit
system_features_bp.register_blueprint(math_practice_bp, url_prefix='/math/toolkit')
system_features_bp.register_blueprint(math_reference_bp, url_prefix='/math/toolkit')
system_features_bp.register_blueprint(math_tasks_bp, url_prefix='/math/toolkit')


# Feature Registry (Panel API) - Registered separately in api/v1/__init__.py
# (Not under /system-features because it's a panel endpoint)

# =============================================================================
# REGISTER NEW FEATURES (TODO: Uncomment when implemented)
# =============================================================================

# Interactive Tools (1 feature)
# system_features_bp.register_blueprint(whiteboard_bp, url_prefix='/interactive/whiteboard')

# Audio (1 feature)
# system_features_bp.register_blueprint(speech_bp, url_prefix='/audio/speech-to-text')

# Exam & Assessment (3 features)
# system_features_bp.register_blueprint(ihk_exam_bp, url_prefix='/exam/ihk')
# system_features_bp.register_blueprint(practical_exam_bp, url_prefix='/exam/practical')
# system_features_bp.register_blueprint(chapter_completion_bp, url_prefix='/exam/chapter-completion')

# Gamification (3 features)
# system_features_bp.register_blueprint(adaptive_difficulty_bp, url_prefix='/gamification/adaptive-difficulty')
# system_features_bp.register_blueprint(xp_quest_bp, url_prefix='/gamification/xp-quest')
# system_features_bp.register_blueprint(daily_recall_bp, url_prefix='/gamification/daily-recall')

# Tutor & Coaching (3 features)
# system_features_bp.register_blueprint(npc_tutor_bp, url_prefix='/tutor/npc')
# system_features_bp.register_blueprint(socratic_dialog_bp, url_prefix='/tutor/socratic')
# system_features_bp.register_blueprint(comprehension_bp, url_prefix='/tutor/comprehension')

# Collaboration (7 features)
# system_features_bp.register_blueprint(peer_instruction_bp, url_prefix='/collaboration/peer-instruction')
# system_features_bp.register_blueprint(team_case_bp, url_prefix='/collaboration/team-case')
# system_features_bp.register_blueprint(peer_review_bp, url_prefix='/collaboration/peer-review')
# system_features_bp.register_blueprint(learning_journal_bp, url_prefix='/collaboration/learning-journal')
# system_features_bp.register_blueprint(project_portfolio_bp, url_prefix='/collaboration/project-portfolio')
# system_features_bp.register_blueprint(project_based_learning_bp, url_prefix='/collaboration/project-based')
# system_features_bp.register_blueprint(inverted_classroom_bp, url_prefix='/collaboration/inverted-classroom')

# IT Environments (4 features)
# system_features_bp.register_blueprint(code_sandbox_bp, url_prefix='/it-environments/code-sandbox')
# system_features_bp.register_blueprint(network_simulation_bp, url_prefix='/it-environments/network-simulation')
# system_features_bp.register_blueprint(terminal_access_bp, url_prefix='/it-environments/terminal-access')
# system_features_bp.register_blueprint(it_sandbox_bp, url_prefix='/it-environments/it-sandbox')

# Meta (1 feature)
# system_features_bp.register_blueprint(timer_wrapper_bp, url_prefix='/meta/timer-wrapper')

# Visualization (1 feature)
# system_features_bp.register_blueprint(mindmap_generator_bp, url_prefix='/visualization/mindmap-generator')

# Learning Paths (1 feature)
# system_features_bp.register_blueprint(path_generator_bp, url_prefix='/learning-paths/path-generator')

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'system_features_bp',      # Main blueprint (register this in api/v1/__init__.py)
    'registry_bp',             # Panel API (register separately)
    'exams_bp',                # Exam Simulations (for backward compatibility)
    'question_generator_bp',   # Question Generator (user-facing practice exam generation)
    # math_admin_bp moved to panel/admin/math_toolkit (Phase 1 Task 2)
    'math_practice_bp',   # Math Toolkit Practice (for backward compatibility)
    'math_reference_bp',  # Math Toolkit Reference (for backward compatibility)
    'math_tasks_bp',      # Math Toolkit Tasks (for backward compatibility)
]
