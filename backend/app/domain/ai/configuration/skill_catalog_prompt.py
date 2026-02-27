"""
Skill Catalog Prompt Builder — Domain Layer

Builds a textual description of available AI skills for use in plan
generation prompts. This is pure domain knowledge (skill definitions
and didactic guidelines) with no infrastructure imports.

Used by both PlanService (legacy) and PlanGeneratorAdapter (wizard).
"""

from __future__ import annotations


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


def _core_skills_section() -> str:
    """Core skill listings: explanatory, practice, assessment, utility."""
    return (
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
    )


def _extension_skills_section(active_sf_codes: set[str] | None) -> str:
    """Extension skills gated by active system features."""
    lines: list[str] = []
    if active_sf_codes is not None:
        for sf_code, (skill_code, desc) in SF_TO_SKILL.items():
            if sf_code in active_sf_codes:
                lines.append(f'  - {skill_code}: {desc}')
    else:
        for _sf_code, (skill_code, desc) in SF_TO_SKILL.items():
            lines.append(f'  - {skill_code}: {desc}')

    for skill_code, desc in ALWAYS_AVAILABLE_EXTENSIONS.items():
        lines.append(f'  - {skill_code}: {desc}')

    if not lines:
        return ''
    return 'EXTENSION SKILLS (advanced task types):\n' + '\n'.join(lines) + '\n\n'


def _didactic_guidelines() -> str:
    """Didactic rules mapping topic types to recommended skills."""
    return (
        'SKILL SELECTION GUIDELINES — which skill_code to use per step:\n'
        '- Theory/intro lesson → generate_theory_sheet or generate_deep_explanation\n'
        '- Visual topic → generate_diagram (+ generate_whiteboard if available)\n'
        '- Calculation topic → generate_math_interactive\n'
        '- Terminology-heavy → generate_flashcards or generate_cloze_test\n'
        '- Process/configuration → generate_step_by_step or generate_example_scenario\n'
        '- Hands-on IT practice → generate_hands_on_lab (if available)\n'
        '- Chapter final assessment → generate_chapter_exam or generate_ihk_tasks\n'
        '- Complex real-world task → generate_multi_step\n'
        '- Quick check → generate_comprehension_check (if available)\n\n'
        'IMPORTANT: The skill_code determines WHAT content the AI generates.\n'
        'The learning_methods array determines WHICH interactive tasks the learner gets.\n'
        'Both must be set correctly for each step!\n\n'
    )


def _learning_methods_section() -> str:
    """Reference table of the 12 Content-Lernmethoden for LM assignment."""
    return (
        'LEARNING METHODS (Lernmethoden) — assign to each step:\n'
        'Each step MUST include a "learning_methods" array with IDs of interactive '
        'tasks the learner will practice for that lesson.\n\n'
        'Available learning method IDs:\n'
        '  Group A — Explanatory (Verstehen):\n'
        '    0 = Deep Explanation — ausfuehrliche Erklaerung mit Analogien und Beispielen\n'
        '    1 = Step-by-Step — Schritt-fuer-Schritt Anleitung (ideal fuer Prozesse, Konfigurationen)\n'
        '    2 = Interactive Theory — Theorie mit eingebetteten Verstaendnisfragen\n'
        '    3 = Diagram/Visualization — visuelle Darstellung (Topologien, Architekturen, Ablaeufe)\n'
        '    4 = Example Scenario — konkretes Praxisbeispiel aus der echten Arbeitswelt\n'
        '  Group B — Practice (Ueben):\n'
        '    5 = Math Interactive — Berechnungen, Formeln, Umrechnungen (z.B. Subnetting, Binaer)\n'
        '    6 = Flashcards — Lernkarten fuer Begriffe, Definitionen, Abkuerzungen, Ports\n'
        '    7 = Drag & Drop — Zuordnungsaufgaben (Begriffe↔Definitionen, Schichten↔Protokolle)\n'
        '    8 = Cloze Test — Lueckentexte zum aktiven Erinnern von Fachbegriffen\n'
        '  Group C — Assessment (Pruefen):\n'
        '    9 = Free Text — offene Freitext-Fragen fuer tiefes Verstaendnis\n'
        '    10 = IHK-Style Tasks — Pruefungsaufgaben im IHK/Zertifizierungsformat\n'
        '    11 = Multi-Step Practical — mehrstufige Praxisaufgaben (Troubleshooting, Konfiguration)\n\n'
        #
        # ── Pedagogical Selection Rules ──
        #
        'PEDAGOGISCHE REGELN fuer learning_methods (PFLICHT — gruendlich beachten!):\n\n'
        '1. JEDE Lektion braucht 2-4 Lernmethoden (nie nur 1, nie mehr als 5)\n'
        '   - Mindestens 1 aus Group A (Verstehen) UND mindestens 1 aus Group B oder C (Ueben/Pruefen)\n'
        '   - Theorie allein reicht NICHT — der Lernende muss immer auch aktiv ueben\n\n'
        '2. INHALTSTYP bestimmt die beste Kombination:\n'
        '   - Fachbegriffe/Definitionen/Abkuerzungen → [0, 6, 8] (Erklaerung + Karteikarten + Lueckentext)\n'
        '   - Prozesse/Ablaeufe/Konfiguration → [1, 4, 7] (Schritt-fuer-Schritt + Beispiel + Drag&Drop)\n'
        '   - Berechnungen/Formeln/Umrechnungen → [0, 5, 8] (Erklaerung + Mathe-Interaktiv + Lueckentext)\n'
        '   - Visuelle Themen (Topologien, OSI-Modell) → [3, 7, 4] (Diagramm + Drag&Drop + Beispiel)\n'
        '   - Troubleshooting/Fehlersuche → [4, 11, 9] (Szenario + Multi-Step + Freitext)\n'
        '   - Sicherheitskonzepte/Protokolle → [0, 2, 6, 10] (Erklaerung + Interaktiv + Karten + IHK)\n'
        '   - Pruefungsvorbereitung → [10, 11, 9] (IHK + Multi-Step + Freitext)\n'
        '   - Hardware/Geraete/Kabel → [3, 6, 7] (Diagramm + Karten + Drag&Drop)\n\n'
        '3. PROGRESSION innerhalb eines Kapitels:\n'
        '   - Erste Lektion: mehr Explanatory (Group A) — Grundlagen aufbauen\n'
        '   - Mittlere Lektionen: Mix aus A + B — Wissen vertiefen und ueben\n'
        '   - Letzte Lektion: mehr Assessment (Group C) — Wissen pruefen\n\n'
        '4. VIELFALT ueber den gesamten Kurs:\n'
        '   - NICHT jede Lektion mit der gleichen Kombination [0, 6, 8]\n'
        '   - Wechsle ab: mal [0, 6, 8], dann [1, 4, 7], dann [3, 7, 9]\n'
        '   - Nutze ALLE 12 Methoden verteilt ueber den Kurs\n'
        '   - Drag&Drop (7) ist besonders gut fuer Zuordnungen — oft unterschaetzt\n'
        '   - Interactive Theory (2) bricht Monotonie auf — einstreuen!\n\n'
        '5. SCHWIERIGKEITSGRAD beachten:\n'
        '   - Beginner-Kurs: mehr [0, 6, 8, 2] (einfach, Wiederholung)\n'
        '   - Intermediate: ausgewogener Mix aller Gruppen\n'
        '   - Advanced/Pruefung: mehr [10, 11, 9, 5] (anspruchsvoll, pruefungsnah)\n\n'
    )


def _structure_rules() -> str:
    """Plan structure constraints for AI output."""
    return (
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
        '- Each step MUST include "learning_methods": [list of LM IDs]\n'
    )


def build_skill_catalog_prompt(active_sf_codes: set[str] | None = None) -> str:
    """Build a description of available skills for AI plan generation prompts.

    Args:
        active_sf_codes: Set of active system-feature codes. If None,
            all SF-gated extensions are included.

    Returns:
        Multi-line string listing all skill codes with didactic guidelines.
    """
    return (
        _core_skills_section()
        + _extension_skills_section(active_sf_codes)
        + _learning_methods_section()
        + _didactic_guidelines()
        + _structure_rules()
    )
