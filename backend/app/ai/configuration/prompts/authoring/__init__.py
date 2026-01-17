"""
LernsystemX Authoring Prompts

Prompt templates for universal KI-Authoring-System:
- Chapter creation and theory generation
- Lesson creation and explanation generation
- Task/exercise creation
- Learning method instance creation

Phase D4 - Universal KI-Authoring-System
"""

from .course import (
    QUICK_PROMPTS_COURSE_BUILDER,
    SYSTEM_PROMPT_COURSE_BUILDER,
    USER_PROMPT_COURSE_BUILDER,
    format_course_builder_prompt
)
from .chapter import (
    QUICK_PROMPTS_CHAPTER,
    SYSTEM_PROMPT_CHAPTER,
    USER_PROMPT_CHAPTER
)
from .lesson import (
    QUICK_PROMPTS_LESSON,
    SYSTEM_PROMPT_LESSON,
    USER_PROMPT_LESSON
)
from .method import (
    QUICK_PROMPTS_LEARNING_METHOD,
    SYSTEM_PROMPT_LEARNING_METHOD,
    USER_PROMPT_LEARNING_METHOD
)
from .general import (
    QUICK_PROMPTS_TASK,
    QUICK_PROMPTS_GENERAL,
    QUICK_PROMPTS,
    SYSTEM_PROMPTS,
    USER_PROMPTS,
    SYSTEM_PROMPT_TASK,
    SYSTEM_PROMPT_GENERAL,
    USER_PROMPT_TASK,
    USER_PROMPT_GENERAL,
    get_authoring_prompt,
    get_quick_prompts,
    format_user_prompt
)

__all__ = [
    # Course Builder
    'QUICK_PROMPTS_COURSE_BUILDER',
    'SYSTEM_PROMPT_COURSE_BUILDER',
    'USER_PROMPT_COURSE_BUILDER',
    'format_course_builder_prompt',

    # Chapter
    'QUICK_PROMPTS_CHAPTER',
    'SYSTEM_PROMPT_CHAPTER',
    'USER_PROMPT_CHAPTER',

    # Lesson
    'QUICK_PROMPTS_LESSON',
    'SYSTEM_PROMPT_LESSON',
    'USER_PROMPT_LESSON',

    # Learning Method
    'QUICK_PROMPTS_LEARNING_METHOD',
    'SYSTEM_PROMPT_LEARNING_METHOD',
    'USER_PROMPT_LEARNING_METHOD',

    # General/Task
    'QUICK_PROMPTS_TASK',
    'QUICK_PROMPTS_GENERAL',
    'QUICK_PROMPTS',  # Backward compatibility - unified dict
    'SYSTEM_PROMPTS',  # Backward compatibility - unified dict
    'USER_PROMPTS',  # Backward compatibility - unified dict
    'SYSTEM_PROMPT_TASK',
    'SYSTEM_PROMPT_GENERAL',
    'USER_PROMPT_TASK',
    'USER_PROMPT_GENERAL',

    # Helper Functions
    'get_authoring_prompt',
    'get_quick_prompts',
    'format_user_prompt'
]
