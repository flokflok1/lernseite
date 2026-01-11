#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""

if __name__ == "__main__":
    print("Testing imports from authoring package...")

    # Test individual module imports
    print("  - Importing course module...")
    from course import (
        QUICK_PROMPTS_COURSE_BUILDER,
        SYSTEM_PROMPT_COURSE_BUILDER,
        USER_PROMPT_COURSE_BUILDER,
        format_course_builder_prompt
    )

    print("  - Importing chapter module...")
    from chapter import (
        QUICK_PROMPTS_CHAPTER,
        SYSTEM_PROMPT_CHAPTER,
        USER_PROMPT_CHAPTER
    )

    print("  - Importing lesson module...")
    from lesson import (
        QUICK_PROMPTS_LESSON,
        SYSTEM_PROMPT_LESSON,
        USER_PROMPT_LESSON
    )

    print("  - Importing method module...")
    from method import (
        QUICK_PROMPTS_LEARNING_METHOD,
        SYSTEM_PROMPT_LEARNING_METHOD,
        USER_PROMPT_LEARNING_METHOD
    )

    print("  - Importing general module...")
    from general import (
        QUICK_PROMPTS_TASK,
        QUICK_PROMPTS_GENERAL,
        QUICK_PROMPTS,
        SYSTEM_PROMPTS,
        USER_PROMPTS,
        get_authoring_prompt,
        get_quick_prompts,
        format_user_prompt
    )

    # Test package-level import
    print("  - Testing package-level import...")
    import __init__ as authoring

    # Verify backward compatibility
    print("\nVerifying backward compatibility...")
    assert 'chapter' in QUICK_PROMPTS
    assert 'lesson' in QUICK_PROMPTS
    assert 'task' in QUICK_PROMPTS
    assert 'learning_method' in QUICK_PROMPTS
    assert 'general' in QUICK_PROMPTS
    assert 'course_builder' in QUICK_PROMPTS

    assert 'chapter' in SYSTEM_PROMPTS
    assert 'chapter' in USER_PROMPTS

    print("✓ All imports successful!")
    print("✓ Backward compatibility verified!")

    # Count items
    print(f"\nQUICK_PROMPTS contains {len(QUICK_PROMPTS)} context types")
    print(f"SYSTEM_PROMPTS contains {len(SYSTEM_PROMPTS)} prompts")
    print(f"USER_PROMPTS contains {len(USER_PROMPTS)} prompts")
