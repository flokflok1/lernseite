"""
LernsystemX KI - Prompt Registry Core

Core registry functionality: PROMPT_REGISTRY dict and register_prompt().
"""

from typing import Dict
from datetime import datetime
from flask import current_app

from src.ki.prompt_models import PromptTemplate


# Global prompt registry (code-based defaults)
PROMPT_REGISTRY: Dict[str, PromptTemplate] = {}


class PromptRegistryError(Exception):
    """Exception raised for prompt registry errors"""
    pass


def register_prompt(template: PromptTemplate, overwrite: bool = False) -> None:
    """
    Register a prompt template in the global registry.

    Args:
        template: PromptTemplate instance to register
        overwrite: If True, allows overwriting existing template

    Raises:
        PromptRegistryError: If template code already exists and overwrite=False

    Examples:
        custom_template = PromptTemplate(
            code="my_custom_method",
            title="My Custom Learning Method",
            ...
        )
        register_prompt(custom_template)
    """
    if template.code in PROMPT_REGISTRY and not overwrite:
        raise PromptRegistryError(
            f"Prompt template '{template.code}' already exists. "
            f"Use overwrite=True to replace it."
        )

    # Set timestamps if not already set
    if template.created_at is None:
        template.created_at = datetime.utcnow()
    template.updated_at = datetime.utcnow()

    PROMPT_REGISTRY[template.code] = template

    current_app.logger.info(
        f"Registered prompt template: {template.code} (v{template.version})"
    )
