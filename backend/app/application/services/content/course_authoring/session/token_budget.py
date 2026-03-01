"""
Dynamic token budget calculation for AI Editor.

Calculates optimal max_tokens based on:
1. Model's actual context_window and max_output_tokens
2. QualityProfile's output_token_ratio (no artificial cap)
3. Estimated prompt size (system + user + tools)

The user pays per token, so the only ceiling is the model's own limit.
"""

import logging
from typing import Dict

from app.application.services.content.course_authoring.quality_profile import (
    QualityProfile,
)

logger = logging.getLogger(__name__)

CHARS_PER_TOKEN = 4
SAFETY_MARGIN_RATIO = 0.10
TOOL_DEFINITION_TOKENS = 3000


class TokenBudget:
    """Calculates dynamic token budgets for AI requests."""

    @staticmethod
    def estimate_prompt_tokens(system_prompt: str, user_prompt: str) -> int:
        """Rough token estimate for input."""
        text_chars = len(system_prompt) + len(user_prompt)
        return (text_chars // CHARS_PER_TOKEN) + TOOL_DEFINITION_TOKENS

    @staticmethod
    def get_model_limits(provider: str, model: str) -> Dict[str, int]:
        """
        Get context_window and max_output_tokens for a model.
        Checks DB first, falls back to config.py.
        """
        try:
            from app.infrastructure.persistence.repositories.ai_models.query import (
                AIModelsQueryRepository,
            )
            db_model = AIModelsQueryRepository.get_by_name(model, provider)
            if db_model:
                cw = db_model.get('context_window')
                mo = db_model.get('max_output_tokens')
                if cw and mo:
                    return {'context_window': int(cw), 'max_output_tokens': int(mo)}
        except Exception:
            pass

        try:
            from app.infrastructure.ai.config import PROVIDERS
            cfg = PROVIDERS.get(provider, {}).get('models', {}).get(model, {})
            return {
                'context_window': cfg.get('context_window', 128000),
                'max_output_tokens': cfg.get('max_tokens', 32000),
            }
        except Exception:
            pass

        return {'context_window': 128000, 'max_output_tokens': 32000}

    @staticmethod
    def compute(
        provider: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        profile: QualityProfile = None
    ) -> int:
        """
        Calculate optimal max_tokens for a request.

        No artificial cap — model's own limit is the ceiling.
        User pays per token from their balance.

        Args:
            provider: AI provider name
            model: AI model name
            system_prompt: System prompt text
            user_prompt: User prompt text
            profile: Quality profile (uses standard defaults if None)

        Returns:
            Optimal max_tokens value
        """
        if profile is None:
            from app.application.services.content.course_authoring.quality_profile import (
                get_quality_profile,
            )
            profile = get_quality_profile('standard')

        limits = TokenBudget.get_model_limits(provider, model)
        estimated_input = TokenBudget.estimate_prompt_tokens(
            system_prompt, user_prompt
        )

        # Model's hard output limit
        model_max = limits['max_output_tokens']

        # Quality profile's desired ratio of that limit
        desired = int(model_max * profile.output_token_ratio)

        # Ensure we don't exceed context window
        safety = int(limits['context_window'] * SAFETY_MARGIN_RATIO)
        context_available = limits['context_window'] - estimated_input - safety
        result = min(desired, context_available, model_max)

        # Never below profile's minimum
        result = max(result, profile.min_output_tokens)

        logger.info(
            f"Token budget [{profile.level}]: "
            f"model_max={model_max}, ratio={profile.output_token_ratio}, "
            f"desired={desired}, input~={estimated_input} -> "
            f"max_tokens={result}"
        )
        return result
