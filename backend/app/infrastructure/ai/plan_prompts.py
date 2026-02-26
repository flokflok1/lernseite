"""
Plan Phase Prompts for the 4-Phase Wizard

Builds system/user message pairs for each phase of the AI plan wizard.
Pure infrastructure concern — no Flask, Application, or API imports.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Phase 1: Course Definition
# ---------------------------------------------------------------------------

def build_phase1_prompt(
    topic: str,
    file_text: str | None = None,
) -> tuple[str, str]:
    """Build prompt pair for Phase 1 (course meta extraction)."""
    system_message = (
        'Du bist ein erfahrener Kursarchitekt fuer eine Online-Lernplattform.\n'
        'Deine Aufgabe: Analysiere das Thema und erstelle eine praezise Kurs-Definition.\n\n'
        'Antworte ausschliesslich mit validem JSON (keine Markdown-Fences):\n'
        '{\n'
        '  "title": "Kurstitel (kurz, praegnant)",\n'
        '  "description": "2-3 Saetze Kursbeschreibung",\n'
        '  "target_audience": "Zielgruppe (z.B. Fachinformatiker, Studenten)",\n'
        '  "difficulty": "beginner|intermediate|advanced",\n'
        '  "language": "de"\n'
        '}\n\n'
        'Regeln:\n'
        '- Titel: max 80 Zeichen, klar und beschreibend\n'
        '- Beschreibung: Lernziele und Umfang zusammenfassen\n'
        '- Schwierigkeit anhand des Themas/Materials einschaetzen\n'
        '- Sprache aus dem Material/Thema ableiten (Standard: de)'
    )

    if file_text:
        truncated = file_text[:6000]
        user_message = (
            'Analysiere das folgende Dokument und leite daraus eine '
            'Kurs-Definition ab.\n\n'
            f'--- DOKUMENT ---\n{truncated}\n--- ENDE ---'
        )
    else:
        user_message = f'Erstelle eine Kurs-Definition zum Thema: {topic}'

    return system_message, user_message


# ---------------------------------------------------------------------------
# Phase 2: Chapter Structure
# ---------------------------------------------------------------------------

def build_phase2_prompt(
    course_meta: dict,
    file_text: str | None = None,
) -> tuple[str, str]:
    """Build prompt pair for Phase 2 (chapter structure generation)."""
    system_message = (
        'Du bist ein erfahrener Kursarchitekt.\n'
        'Erstelle eine logische Kapitelstruktur fuer den gegebenen Kurs.\n\n'
        'Antworte ausschliesslich mit validem JSON (keine Markdown-Fences):\n'
        '{\n'
        '  "chapters": [\n'
        '    {"title": "Kapiteltitel", "description": "Kurzbeschreibung des Kapitels"}\n'
        '  ]\n'
        '}\n\n'
        'Regeln:\n'
        '- Zwischen 5 und 12 Kapitel\n'
        '- Logische Reihenfolge: vom Einfachen zum Komplexen\n'
        '- Keine inhaltlichen Ueberschneidungen zwischen Kapiteln\n'
        '- Jedes Kapitel hat einen klaren thematischen Fokus\n'
        '- Titel: kurz und praegnant (max 60 Zeichen)\n'
        '- Beschreibung: 1-2 Saetze, was im Kapitel behandelt wird'
    )

    meta_section = _format_course_meta(course_meta)

    if file_text:
        truncated = file_text[:8000]
        user_message = (
            f'{meta_section}\n\n'
            'Erstelle die Kapitelstruktur basierend auf dem Kurs und '
            'dem folgenden Material.\n\n'
            f'--- MATERIAL ---\n{truncated}\n--- ENDE ---'
        )
    else:
        user_message = (
            f'{meta_section}\n\n'
            'Erstelle eine sinnvolle Kapitelstruktur fuer diesen Kurs.'
        )

    return system_message, user_message


# ---------------------------------------------------------------------------
# Phase 3: Full Plan Generation
# ---------------------------------------------------------------------------

_DIDACTIC_GUIDELINES = (
    'DIDAKTISCHE REGELN (PFLICHT):\n'
    '1. Jedes Kapitel MUSS mit generate_theory_sheet beginnen '
    '(target_type: "chapter")\n'
    '2. Jede Lektion MUSS mit generate_theory_sheet beginnen '
    '(target_type: "lesson")\n'
    '3. Nach der Theorie: 2-3 Lernmethoden pro Lektion\n'
    '4. Am Ende jedes Kapitels: generate_chapter_exam '
    '(falls verfuegbar)\n\n'
    'ZUORDNUNG nach Inhaltstyp:\n'
    '- Konzepte/Definitionen -> generate_flashcards, generate_cloze_test\n'
    '- Prozesse/Ablaeufe -> generate_step_by_step, generate_multi_step\n'
    '- Berechnungen/Formeln -> generate_math_interactive\n'
    '- Praxisbeispiele -> generate_example_scenario\n'
    '- Visuelle Themen -> generate_diagram\n'
    '- Verstaendnispruefung -> generate_free_text\n'
    '- Pruefungsvorbereitung -> generate_ihk_tasks\n'
)


def build_phase3_prompt(
    course_meta: dict,
    chapters: list[dict],
    skill_catalog_section: str,
) -> tuple[str, str]:
    """Build prompt pair for Phase 3 (full plan with skills)."""
    system_message = (
        'Du bist ein erfahrener didaktischer Planer.\n'
        'Erstelle einen vollstaendigen Kursplan mit konkreten '
        'Lernschritten fuer jedes Kapitel.\n\n'
        f'{skill_catalog_section}\n'
        f'{_DIDACTIC_GUIDELINES}\n'
        'Antworte ausschliesslich mit validem JSON (keine Markdown-Fences):\n'
        '{\n'
        '  "phases": [\n'
        '    {\n'
        '      "title": "Kapiteltitel",\n'
        '      "chapter_index": 0,\n'
        '      "steps": [\n'
        '        {\n'
        '          "skill_code": "generate_theory_sheet",\n'
        '          "target_type": "chapter",\n'
        '          "target_title": "Kapitelname",\n'
        '          "parameters": {"language": "de"}\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    meta_section = _format_course_meta(course_meta)
    chapters_section = _format_chapters(chapters)

    user_message = (
        f'{meta_section}\n\n'
        f'{chapters_section}\n\n'
        'Erstelle den vollstaendigen Kursplan mit Lernschritten '
        'fuer jedes Kapitel.'
    )

    return system_message, user_message


# ---------------------------------------------------------------------------
# Phase 4: Chat Refinement
# ---------------------------------------------------------------------------

def build_plan_chat_prompt(
    plan_data: dict,
    current_phase: int,
) -> str:
    """Build system message for plan chat refinement."""
    phase_labels = {
        1: 'Kurs-Definition (Titel, Beschreibung, Zielgruppe)',
        2: 'Kapitelstruktur',
        3: 'Vollstaendiger Kursplan mit Lernschritten',
        4: 'Chat-Verfeinerung',
    }
    phase_label = phase_labels.get(current_phase, 'Unbekannt')
    plan_summary = _format_plan_for_chat(plan_data)

    return (
        'Du bist ein Kursplanungs-Assistent.\n'
        f'Aktuelle Phase: {current_phase} — {phase_label}\n\n'
        f'Aktueller Plan:\n{plan_summary}\n\n'
        'Der Benutzer moechte den Plan anpassen. '
        'Antworte mit validem JSON:\n'
        '{\n'
        '  "assistant_message": "Deine Antwort an den Benutzer",\n'
        '  "plan_patch": null\n'
        '}\n\n'
        'Wenn du eine Aenderung am Plan vorschlaegst, '
        'setze plan_patch auf ein Objekt mit den geaenderten Feldern.\n'
        'Beispiel plan_patch fuer Phase 1: '
        '{"title": "Neuer Titel", "difficulty": "advanced"}\n'
        'Beispiel plan_patch fuer Phase 2: '
        '{"chapters": [{"title": "...", "description": "..."}]}\n'
        'Beispiel plan_patch fuer Phase 3: '
        '{"phases": [...]}\n\n'
        'Wenn keine Aenderung noetig ist, setze plan_patch auf null.'
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _format_course_meta(course_meta: dict) -> str:
    """Format course metadata for prompt inclusion."""
    title = course_meta.get('title', 'Unbekannt')
    description = course_meta.get('description', '')
    audience = course_meta.get('target_audience', '')
    difficulty = course_meta.get('difficulty', '')
    language = course_meta.get('language', 'de')

    lines = [f'KURS: {title}']
    if description:
        lines.append(f'Beschreibung: {description}')
    if audience:
        lines.append(f'Zielgruppe: {audience}')
    if difficulty:
        lines.append(f'Schwierigkeit: {difficulty}')
    lines.append(f'Sprache: {language}')

    return '\n'.join(lines)


def _format_chapters(chapters: list[dict]) -> str:
    """Format chapter list for prompt inclusion."""
    if not chapters:
        return 'KAPITEL: (keine)'

    lines = ['KAPITEL:']
    for i, ch in enumerate(chapters):
        title = ch.get('title', f'Kapitel {i + 1}')
        desc = ch.get('description', '')
        entry = f'  {i + 1}. {title}'
        if desc:
            entry += f' — {desc}'
        lines.append(entry)

    return '\n'.join(lines)


def _format_plan_for_chat(plan_data: dict) -> str:
    """Format plan data compactly for chat context."""
    if not plan_data:
        return '(Kein Plan vorhanden)'

    lines = []

    # Course meta if present
    if 'title' in plan_data:
        lines.append(f'Kurs: {plan_data["title"]}')
    if 'description' in plan_data:
        lines.append(f'Beschreibung: {plan_data["description"]}')

    # Chapters if present
    chapters = plan_data.get('chapters', [])
    if chapters:
        lines.append(f'\nKapitel ({len(chapters)}):')
        for i, ch in enumerate(chapters):
            lines.append(f'  {i + 1}. {ch.get("title", "?")}')

    # Phases/steps if present
    phases = plan_data.get('phases', [])
    if phases:
        lines.append(f'\nPhasen ({len(phases)}):')
        for phase in phases:
            title = phase.get('title', '?')
            steps = phase.get('steps', [])
            lines.append(f'  - {title} ({len(steps)} Schritte)')
            for step in steps[:5]:
                skill = step.get('skill_code', '?')
                target = step.get('target_title', '')
                lines.append(f'    * {skill}: {target}')
            if len(steps) > 5:
                lines.append(f'    ... +{len(steps) - 5} weitere')

    return '\n'.join(lines) if lines else '(Leerer Plan)'
