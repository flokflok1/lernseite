# KI Prompts Package
from .authoring import (
    get_authoring_prompt,
    get_quick_prompts,
    format_user_prompt,
    format_course_builder_prompt,
    QUICK_PROMPTS,
    SYSTEM_PROMPTS,
    USER_PROMPTS
)

__all__ = [
    'get_authoring_prompt',
    'get_quick_prompts',
    'format_user_prompt',
    'format_course_builder_prompt',
    'QUICK_PROMPTS',
    'SYSTEM_PROMPTS',
    'USER_PROMPTS'
]
