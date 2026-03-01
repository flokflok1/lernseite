"""
Quality profiles for AI Editor generation.

Each profile controls all generation parameters:
- Token budget (ratio of model's max output — no artificial cap)
- Temperature (creativity vs precision)
- History depth and context size
- Content validation strictness
- Retry behavior
- Pipeline mode (single-shot vs multi-step)

The user pays per token from their balance, so there is NO artificial
output cap. The only limit is the model's own max_output_tokens.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QualityProfile:
    """Immutable configuration for a single generation request."""

    # --- Identity ---
    level: str                      # schnell, standard, hoch, maximum
    label: str                      # Display name for UI

    # --- Token Budget ---
    # Fraction of model's max_output_tokens (0.0-1.0)
    # No cap: user pays per token, model limit is the only ceiling
    output_token_ratio: float
    min_output_tokens: int          # Floor (never go below)

    # --- Temperature ---
    temperature_structure: float    # For structure operations (chapters, lessons)
    temperature_content: float      # For content generation (theory, text)
    temperature_methods: float      # For method generation (quiz, exercise)
    temperature_default: float      # Fallback when mode not specified

    # --- History Context ---
    history_message_limit: int      # Max messages from chat history
    history_char_limit: int         # Max total chars for history in prompt
    history_message_char_limit: int  # Max chars per individual message

    # --- Content Validation ---
    validate_content: bool          # Run ContentValidator?
    min_raw_text_length: int        # Minimum lesson theory length (chars)
    min_quiz_questions: int         # Minimum questions per quiz
    min_flashcard_count: int        # Minimum cards per flashcard set
    require_exercise_solution: bool  # Require modelAnswer for exercises?

    # --- Retry ---
    max_retries: int                # Auto-retry on validation errors (0=disabled)
    retry_temperature_drop: float   # Reduce temperature by this on retry

    # --- Pipeline ---
    pipeline_enabled: bool          # Use multi-step pipeline?
    pipeline_batch_size: int        # Chapters per pipeline step
    methods_per_lesson: int         # Target methods per lesson (for prompt)


# ============================================================================
# Predefined Levels
# ============================================================================

QUALITY_LEVELS: Dict[str, QualityProfile] = {
    'schnell': QualityProfile(
        level='schnell',
        label='Schnell',
        output_token_ratio=0.5,
        min_output_tokens=4000,
        temperature_structure=0.4,
        temperature_content=0.6,
        temperature_methods=0.5,
        temperature_default=0.6,
        history_message_limit=5,
        history_char_limit=2000,
        history_message_char_limit=200,
        validate_content=True,
        min_raw_text_length=30,
        min_quiz_questions=1,
        min_flashcard_count=2,
        require_exercise_solution=False,
        max_retries=0,
        retry_temperature_drop=0.0,
        pipeline_enabled=False,
        pipeline_batch_size=0,
        methods_per_lesson=1,
    ),

    'standard': QualityProfile(
        level='standard',
        label='Standard',
        output_token_ratio=0.75,
        min_output_tokens=8000,
        temperature_structure=0.4,
        temperature_content=0.7,
        temperature_methods=0.6,
        temperature_default=0.7,
        history_message_limit=15,
        history_char_limit=5000,
        history_message_char_limit=500,
        validate_content=True,
        min_raw_text_length=50,
        min_quiz_questions=2,
        min_flashcard_count=3,
        require_exercise_solution=True,
        max_retries=1,
        retry_temperature_drop=0.15,
        pipeline_enabled=False,
        pipeline_batch_size=3,
        methods_per_lesson=2,
    ),

    'hoch': QualityProfile(
        level='hoch',
        label='Hoch',
        output_token_ratio=0.9,
        min_output_tokens=16000,
        temperature_structure=0.3,
        temperature_content=0.75,
        temperature_methods=0.6,
        temperature_default=0.7,
        history_message_limit=25,
        history_char_limit=8000,
        history_message_char_limit=800,
        validate_content=True,
        min_raw_text_length=100,
        min_quiz_questions=3,
        min_flashcard_count=5,
        require_exercise_solution=True,
        max_retries=1,
        retry_temperature_drop=0.2,
        pipeline_enabled=True,
        pipeline_batch_size=3,
        methods_per_lesson=2,
    ),

    'maximum': QualityProfile(
        level='maximum',
        label='Maximum',
        output_token_ratio=1.0,
        min_output_tokens=16000,
        temperature_structure=0.3,
        temperature_content=0.8,
        temperature_methods=0.6,
        temperature_default=0.7,
        history_message_limit=30,
        history_char_limit=12000,
        history_message_char_limit=1000,
        validate_content=True,
        min_raw_text_length=200,
        min_quiz_questions=5,
        min_flashcard_count=5,
        require_exercise_solution=True,
        max_retries=2,
        retry_temperature_drop=0.2,
        pipeline_enabled=True,
        pipeline_batch_size=2,
        methods_per_lesson=3,
    ),
}


def get_quality_profile(level: str = 'standard') -> QualityProfile:
    """Get a quality profile by level name."""
    profile = QUALITY_LEVELS.get(level)
    if not profile:
        logger.warning(f"Unknown quality level '{level}', using 'standard'")
        return QUALITY_LEVELS['standard']
    return profile


def list_quality_levels() -> List[Dict]:
    """List all available quality levels for the UI."""
    return [
        {
            'level': p.level,
            'label': p.label,
            'description': _LEVEL_DESCRIPTIONS[p.level],
            'icon': _LEVEL_ICONS[p.level],
            'estimated_time': _LEVEL_TIMES[p.level],
            'token_ratio': p.output_token_ratio,
            'pipeline': p.pipeline_enabled,
            'methods_per_lesson': p.methods_per_lesson,
            'retries': p.max_retries,
        }
        for p in QUALITY_LEVELS.values()
    ]


_LEVEL_DESCRIPTIONS = {
    'schnell': 'Schnelle Generierung, Basis-Inhalte. Gut zum Ausprobieren.',
    'standard': 'Ausgewogene Qualitaet mit Validierung und Retry.',
    'hoch': 'Hochwertige Inhalte mit Multi-Step-Pipeline und strenger Validierung.',
    'maximum': 'Maximale Qualitaet. Volle Token-Kapazitaet, mehrere Durchlaeufe.',
}

_LEVEL_ICONS = {
    'schnell': 'zap',
    'standard': 'star',
    'hoch': 'target',
    'maximum': 'diamond',
}

_LEVEL_TIMES = {
    'schnell': '~15-30s',
    'standard': '~30-60s',
    'hoch': '~1-2min',
    'maximum': '~2-5min',
}
