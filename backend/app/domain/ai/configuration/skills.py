"""
LernsystemX AI Skill Definitions

Pure domain-level catalog of all executable AI skills for the Unified AI Editor.
Maps the 12 Content-Lernmethoden + utility skills to executable definitions.

No infrastructure imports allowed (DDD domain layer).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SkillParameter:
    """A configurable parameter for a skill."""
    key: str
    label_i18n_key: str
    param_type: str  # 'string', 'number', 'select', 'boolean'
    default_value: object = None
    options: tuple = ()  # tuple of (value, label_i18n_key) pairs
    required: bool = False


@dataclass(frozen=True)
class SkillDefinition:
    """
    Defines an executable AI skill in the Unified Editor.

    Each skill maps to either a Content-Lernmethode (LM 0-11) or a utility action.
    The prompt_template_code references a registered PromptTemplate.

    content_scope: 'course' = generates course content (shown in AI Editor),
                   'session' = runs at session/user level (hidden from AI Editor).
    required_feature_code: If set, the skill is only available when this
                           System Feature is active in the admin panel.
    """
    code: str
    name_i18n_key: str
    description_i18n_key: str
    icon: str
    category: str  # 'explanatory', 'practice', 'assessment', 'content', 'review', 'interactive'
    prompt_template_code: str
    learning_method_id: Optional[int] = None
    required_context: tuple = ('course',)
    parameters: tuple = ()
    supports_variants: bool = True
    estimated_tokens: int = 8000
    content_scope: str = 'course'  # 'course' | 'session'
    required_feature_code: Optional[str] = None


# ---------------------------------------------------------------------------
# Shared parameter definitions (reused across skills)
# ---------------------------------------------------------------------------

_DIFFICULTY_PARAM = SkillParameter(
    key='difficulty',
    label_i18n_key='aiEditor.skills.params.difficulty',
    param_type='select',
    default_value='medium',
    options=(
        ('easy', 'aiEditor.skills.params.difficultyEasy'),
        ('medium', 'aiEditor.skills.params.difficultyMedium'),
        ('hard', 'aiEditor.skills.params.difficultyHard'),
    ),
)

_COUNT_PARAM = SkillParameter(
    key='count',
    label_i18n_key='aiEditor.skills.params.count',
    param_type='number',
    default_value=5,
)

_LANGUAGE_PARAM = SkillParameter(
    key='language',
    label_i18n_key='aiEditor.skills.params.language',
    param_type='select',
    default_value='de',
    options=(
        ('de', 'common.languages.de'),
        ('en', 'common.languages.en'),
        ('pl', 'common.languages.pl'),
    ),
)


# ---------------------------------------------------------------------------
# Skill Catalog — 12 Content-Lernmethoden + 4 Utility + 7 Extension Skills
# ---------------------------------------------------------------------------

SKILL_CATALOG: dict[str, SkillDefinition] = {

    # ── Group A: Explanatory (LM 0-4) ──────────────────────────────────

    'generate_deep_explanation': SkillDefinition(
        code='generate_deep_explanation',
        name_i18n_key='learningMethods.lm00.name',
        description_i18n_key='aiEditor.skills.generateDeepExplanation.desc',
        icon='BookOpen',
        category='explanatory',
        prompt_template_code='ai_editor_methods',
        learning_method_id=0,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_step_by_step': SkillDefinition(
        code='generate_step_by_step',
        name_i18n_key='learningMethods.lm01.name',
        description_i18n_key='aiEditor.skills.generateStepByStep.desc',
        icon='ListOrdered',
        category='explanatory',
        prompt_template_code='ai_editor_methods',
        learning_method_id=1,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_interactive_theory': SkillDefinition(
        code='generate_interactive_theory',
        name_i18n_key='learningMethods.lm02.name',
        description_i18n_key='aiEditor.skills.generateInteractiveTheory.desc',
        icon='MessageSquare',
        category='explanatory',
        prompt_template_code='ai_editor_methods',
        learning_method_id=2,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_diagram': SkillDefinition(
        code='generate_diagram',
        name_i18n_key='learningMethods.lm03.name',
        description_i18n_key='aiEditor.skills.generateDiagram.desc',
        icon='GitBranch',
        category='explanatory',
        prompt_template_code='ai_editor_methods',
        learning_method_id=3,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_example_scenario': SkillDefinition(
        code='generate_example_scenario',
        name_i18n_key='learningMethods.lm04.name',
        description_i18n_key='aiEditor.skills.generateExampleScenario.desc',
        icon='Lightbulb',
        category='explanatory',
        prompt_template_code='ai_editor_methods',
        learning_method_id=4,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
    ),

    # ── Group B: Practice (LM 5-8) ─────────────────────────────────────

    'generate_math_interactive': SkillDefinition(
        code='generate_math_interactive',
        name_i18n_key='learningMethods.lm05.name',
        description_i18n_key='aiEditor.skills.generateMathInteractive.desc',
        icon='Calculator',
        category='practice',
        prompt_template_code='ai_editor_methods',
        learning_method_id=5,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_flashcards': SkillDefinition(
        code='generate_flashcards',
        name_i18n_key='learningMethods.lm06.name',
        description_i18n_key='aiEditor.skills.generateFlashcards.desc',
        icon='Layers',
        category='practice',
        prompt_template_code='ai_editor_methods',
        learning_method_id=6,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_drag_and_drop': SkillDefinition(
        code='generate_drag_and_drop',
        name_i18n_key='learningMethods.lm07.name',
        description_i18n_key='aiEditor.skills.generateDragAndDrop.desc',
        icon='Move',
        category='practice',
        prompt_template_code='ai_editor_methods',
        learning_method_id=7,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_cloze_test': SkillDefinition(
        code='generate_cloze_test',
        name_i18n_key='learningMethods.lm08.name',
        description_i18n_key='aiEditor.skills.generateClozeTest.desc',
        icon='FileText',
        category='practice',
        prompt_template_code='ai_editor_methods',
        learning_method_id=8,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
    ),

    # ── Group C: Assessment (LM 9-11) ──────────────────────────────────

    'generate_free_text': SkillDefinition(
        code='generate_free_text',
        name_i18n_key='learningMethods.lm09.name',
        description_i18n_key='aiEditor.skills.generateFreeText.desc',
        icon='PenTool',
        category='assessment',
        prompt_template_code='ai_editor_methods',
        learning_method_id=9,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_ihk_tasks': SkillDefinition(
        code='generate_ihk_tasks',
        name_i18n_key='learningMethods.lm10.name',
        description_i18n_key='aiEditor.skills.generateIhkTasks.desc',
        icon='ClipboardCheck',
        category='assessment',
        prompt_template_code='ai_editor_methods',
        learning_method_id=10,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_multi_step': SkillDefinition(
        code='generate_multi_step',
        name_i18n_key='learningMethods.lm11.name',
        description_i18n_key='aiEditor.skills.generateMultiStep.desc',
        icon='GitMerge',
        category='assessment',
        prompt_template_code='ai_editor_methods',
        learning_method_id=11,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
    ),

    # ── Utility Skills ──────────────────────────────────────────────────

    'generate_theory_sheet': SkillDefinition(
        code='generate_theory_sheet',
        name_i18n_key='aiEditor.skills.generateTheorySheet.name',
        description_i18n_key='aiEditor.skills.generateTheorySheet.desc',
        icon='FileText',
        category='content',
        prompt_template_code='ai_editor_theory',
        required_context=('course', 'lesson'),
        parameters=(_LANGUAGE_PARAM,),
        estimated_tokens=12000,
    ),

    'generate_quiz': SkillDefinition(
        code='generate_quiz',
        name_i18n_key='aiEditor.skills.generateQuiz.name',
        description_i18n_key='aiEditor.skills.generateQuiz.desc',
        icon='HelpCircle',
        category='content',
        prompt_template_code='ai_editor_quiz',
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
        estimated_tokens=10000,
    ),

    'review_content': SkillDefinition(
        code='review_content',
        name_i18n_key='aiEditor.skills.reviewContent.name',
        description_i18n_key='aiEditor.skills.reviewContent.desc',
        icon='CheckCircle',
        category='review',
        prompt_template_code='ai_editor_review',
        required_context=('course', 'lesson'),
        parameters=(_LANGUAGE_PARAM,),
        supports_variants=False,
        estimated_tokens=8000,
    ),

    'generate_summary': SkillDefinition(
        code='generate_summary',
        name_i18n_key='aiEditor.skills.generateSummary.name',
        description_i18n_key='aiEditor.skills.generateSummary.desc',
        icon='AlignLeft',
        category='content',
        prompt_template_code='ai_editor_summary',
        required_context=('course', 'chapter'),
        parameters=(_LANGUAGE_PARAM,),
        estimated_tokens=10000,
    ),

    # ── Extension Skills (type-IDs 100-106, no LM mapping) ───────────────

    'generate_whiteboard': SkillDefinition(
        code='generate_whiteboard',
        name_i18n_key='aiEditor.skills.generateWhiteboard.name',
        description_i18n_key='aiEditor.skills.generateWhiteboard.desc',
        icon='PenTool',
        category='interactive',
        prompt_template_code='ai_editor_methods',
        learning_method_id=None,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
        required_feature_code='whiteboard_engine',
    ),

    'generate_hands_on_lab': SkillDefinition(
        code='generate_hands_on_lab',
        name_i18n_key='aiEditor.skills.generateHandsOnLab.name',
        description_i18n_key='aiEditor.skills.generateHandsOnLab.desc',
        icon='Terminal',
        category='practice',
        prompt_template_code='ai_editor_methods',
        learning_method_id=None,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
        required_feature_code='it_sandbox',
    ),

    'generate_timed_challenge': SkillDefinition(
        code='generate_timed_challenge',
        name_i18n_key='aiEditor.skills.generateTimedChallenge.name',
        description_i18n_key='aiEditor.skills.generateTimedChallenge.desc',
        icon='Clock',
        category='assessment',
        prompt_template_code='ai_editor_methods',
        learning_method_id=None,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
        required_feature_code='timer_wrapper',
    ),

    'generate_true_false': SkillDefinition(
        code='generate_true_false',
        name_i18n_key='aiEditor.skills.generateTrueFalse.name',
        description_i18n_key='aiEditor.skills.generateTrueFalse.desc',
        icon='CheckSquare',
        category='assessment',
        prompt_template_code='ai_editor_methods',
        learning_method_id=None,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
    ),

    'generate_comprehension_check': SkillDefinition(
        code='generate_comprehension_check',
        name_i18n_key='aiEditor.skills.generateComprehensionCheck.name',
        description_i18n_key='aiEditor.skills.generateComprehensionCheck.desc',
        icon='Brain',
        category='assessment',
        prompt_template_code='ai_editor_methods',
        learning_method_id=None,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
        content_scope='session',
        required_feature_code='comprehension_checker',
    ),

    'generate_oral_explanation': SkillDefinition(
        code='generate_oral_explanation',
        name_i18n_key='aiEditor.skills.generateOralExplanation.name',
        description_i18n_key='aiEditor.skills.generateOralExplanation.desc',
        icon='Mic',
        category='explanatory',
        prompt_template_code='ai_editor_methods',
        learning_method_id=None,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _LANGUAGE_PARAM),
        content_scope='session',
        required_feature_code='speech_to_text',
    ),

    'generate_chapter_exam': SkillDefinition(
        code='generate_chapter_exam',
        name_i18n_key='aiEditor.skills.generateChapterExam.name',
        description_i18n_key='aiEditor.skills.generateChapterExam.desc',
        icon='Award',
        category='assessment',
        prompt_template_code='ai_editor_methods',
        learning_method_id=None,
        required_context=('course', 'lesson'),
        parameters=(_DIFFICULTY_PARAM, _COUNT_PARAM, _LANGUAGE_PARAM),
        required_feature_code='chapter_completion_system',
    ),
}


# ---------------------------------------------------------------------------
# Accessor functions
# ---------------------------------------------------------------------------

def get_skill(code: str) -> Optional[SkillDefinition]:
    """Get a skill definition by code."""
    return SKILL_CATALOG.get(code)


def get_skills_by_category(category: str) -> list[SkillDefinition]:
    """Get all skills in a category."""
    return [s for s in SKILL_CATALOG.values() if s.category == category]


def get_all_skills() -> list[SkillDefinition]:
    """Get all skill definitions."""
    return list(SKILL_CATALOG.values())


def get_course_skills() -> list[SkillDefinition]:
    """Get only course-scoped skills (for AI Editor)."""
    return [s for s in SKILL_CATALOG.values() if s.content_scope == 'course']


def get_skill_codes() -> list[str]:
    """Get all skill codes."""
    return list(SKILL_CATALOG.keys())
