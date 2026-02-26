"""
Skill Catalog Prompt Builder — Domain Layer

Builds a textual description of available AI skills for use in plan
generation prompts. This is pure domain knowledge (skill definitions
and didactic guidelines) with no infrastructure imports.

Used by both PlanService (legacy) and PlanGeneratorAdapter (wizard).
"""

from typing import Optional


# Mapping: system_feature_code → (skill_code, description for prompt)
SF_TO_SKILL: dict[str, tuple[str, str]] = {
    'whiteboard_engine': ('generate_whiteboard', 'Drawing/sketching task (diagrams, topologies, flowcharts)'),
    'it_sandbox': ('generate_hands_on_lab', 'Practical IT exercise with code/terminal'),
    'timer_wrapper': ('generate_timed_challenge', 'Time-limited quiz/challenge'),
    'comprehension_checker': ('generate_comprehension_check', 'Quick understanding verification'),
    'speech_to_text': ('generate_oral_explanation', 'Oral explanation task (speech-to-text)'),
    'chapter_completion_system': ('generate_chapter_exam', 'End-of-chapter exam with mixed questions'),
}

# TrueFalse has no SF dependency — always available
ALWAYS_AVAILABLE_EXTENSIONS: dict[str, str] = {
    'generate_true_false': 'True/false statements for knowledge testing',
}


def build_skill_catalog_prompt(active_sf_codes: Optional[set[str]] = None) -> str:
    """Build a description of available skills for AI plan generation prompts.

    Args:
        active_sf_codes: Set of active system-feature codes. If None,
            all SF-gated extensions are included.

    Returns:
        Multi-line string listing all skill codes with didactic guidelines.
    """
    parts = [
        'You MUST use ONLY the following skill_code values. Do NOT invent new ones.\n\n'
        'EXPLANATORY SKILLS (Group A — teach/explain concepts):\n'
        '  - generate_deep_explanation: In-depth explanation of a topic\n'
        '  - generate_step_by_step: Step-by-step walkthrough\n'
        '  - generate_interactive_theory: Interactive theory with questions\n'
        '  - generate_diagram: Visual diagram/visualization\n'
        '  - generate_example_scenario: Practical example/scenario\n\n'
        'PRACTICE SKILLS (Group B — hands-on practice):\n'
        '  - generate_flashcards: Flashcard sets for memorization\n'
        '  - generate_drag_and_drop: Drag & drop exercises\n'
        '  - generate_cloze_test: Fill-in-the-blank exercises\n'
        '  - generate_math_interactive: Math/calculation exercises\n\n'
        'ASSESSMENT SKILLS (Group C — test knowledge):\n'
        '  - generate_free_text: Open-ended text questions\n'
        '  - generate_ihk_tasks: Exam-style tasks (IHK format)\n'
        '  - generate_multi_step: Multi-step practical tasks\n\n'
        'UTILITY SKILLS:\n'
        '  - generate_theory_sheet: Theory summary sheet for a lesson\n'
        '  - generate_quiz: Multiple-choice quiz\n'
        '  - generate_summary: Chapter summary\n'
        '  - review_content: Review existing content for quality\n\n'
    ]

    # Build extension skills block based on active system features
    extension_lines: list[str] = []
    if active_sf_codes is not None:
        for sf_code, (skill_code, desc) in SF_TO_SKILL.items():
            if sf_code in active_sf_codes:
                extension_lines.append(f'  - {skill_code}: {desc}')
    else:
        for _sf_code, (skill_code, desc) in SF_TO_SKILL.items():
            extension_lines.append(f'  - {skill_code}: {desc}')

    for skill_code, desc in ALWAYS_AVAILABLE_EXTENSIONS.items():
        extension_lines.append(f'  - {skill_code}: {desc}')

    if extension_lines:
        parts.append(
            'EXTENSION SKILLS (advanced task types):\n'
            + '\n'.join(extension_lines) + '\n\n'
        )

    parts.append(
        'DIDACTIC GUIDELINES — when to use which skill:\n'
        '- Visual/spatial topics (diagrams, topologies, architecture) → generate_diagram + generate_whiteboard\n'
        '- Calculation/formulas (subnetting, math, conversion) → generate_math_interactive + generate_step_by_step\n'
        '- Terminology/definitions → generate_flashcards + generate_cloze_test + generate_true_false\n'
        '- Configuration/CLI commands → generate_hands_on_lab + generate_example_scenario\n'
        '- Quick knowledge check between topics → generate_comprehension_check\n'
        '- End of each major chapter → generate_chapter_exam\n'
        '- Theory introduction → generate_deep_explanation + generate_theory_sheet\n'
        '- Complex multi-step processes → generate_step_by_step + generate_multi_step\n\n'
    )

    parts.append(
        'PLAN STRUCTURE RULES:\n'
        '- Organize phases by chapter/topic from the material\n'
        '- Each phase = one chapter/major topic\n'
        '- For EACH chapter, include a MIX of learning methods:\n'
        '  1. At least one explanatory skill (theory)\n'
        '  2. At least one practice skill (exercises)\n'
        '  3. Optionally an assessment skill (test)\n'
        '  4. Use extension skills where didactically appropriate\n'
        '- Cover ALL content from the material — do not skip sections\n'
        '- Each step targets one lesson (target_type: "lesson")\n'
        '- Set target_title to a descriptive lesson name\n'
    )

    return ''.join(parts)
