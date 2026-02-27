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
    '1. Jede Lektion beginnt mit einem Theorie-Skill '
    '(generate_theory_sheet oder generate_deep_explanation)\n'
    '2. Nach der Theorie: 2-3 weitere Lernmethoden pro Lektion (im learning_methods Array)\n'
    '3. Am Ende jedes Kapitels: eine Assessment-Lektion '
    '(generate_ihk_tasks, generate_multi_step oder generate_chapter_exam)\n'
    '4. Die learning_methods IDs MUESSEN zum Inhalt passen — '
    'siehe die PEDAGOGISCHE REGELN im Skill-Katalog!\n'
    '5. Abwechslung: Nicht jede Lektion gleich aufbauen\n'
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
        '          "target_type": "lesson",\n'
        '          "target_title": "Lektionsname",\n'
        '          "learning_methods": [0, 6, 8],\n'
        '          "parameters": {"language": "de"}\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        '}\n\n'
        'WICHTIG: "learning_methods" ist ein Array von Lernmethoden-IDs (0-11), '
        'die der Lektion zugeordnet werden. Siehe Skill-Katalog fuer die IDs.'
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
    file_text: str | None = None,
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

    file_section = ''
    if file_text:
        truncated = file_text[:4000]
        file_section = (
            '\n\nHOCHGELADENES MATERIAL (Auszug):\n'
            f'--- DOKUMENT ---\n{truncated}\n--- ENDE ---\n'
            'Du HAST Zugriff auf dieses Material. Nutze es als Kontext.\n'
        )

    return (
        'Du bist ein Kursplanungs-Assistent.\n'
        'WICHTIG: Antworte IMMER mit validem JSON, NIEMALS mit Freitext!\n\n'
        f'Aktuelle Phase: {current_phase} — {phase_label}\n\n'
        f'Aktueller Plan:\n{plan_summary}\n\n'
        'ANTWORTFORMAT (PFLICHT — nur JSON, kein Freitext!):\n'
        '{\n'
        '  "assistant_message": "<hier deine Antwort schreiben>",\n'
        '  "plan_patch": null\n'
        '}\n\n'
        'KRITISCHE REGEL: Wenn der Benutzer eine Aenderung wuenscht '
        '(hinzufuegen, entfernen, aendern, erweitern, mehr Inhalt, etc.), '
        'MUSST du einen plan_patch senden! Antworte NIEMALS nur verbal '
        'mit plan_patch: null wenn eine Aenderung gewuenscht ist.\n\n'
        'PLAN_PATCH BEISPIELE nach Phase:\n'
        'Phase 1: {"title": "Neuer Titel", "difficulty": "advanced"}\n'
        'Phase 2: {"chapters": [{"title": "...", "description": "..."}]}\n'
        'Phase 3 — INKREMENTELLE Aenderungen (NICHT das gesamte phases-Array!):\n'
        '  Nutze die Phase-Indizes aus dem Plan oben (z.B. [0], [1], [2]...).\n'
        '  Neue Phase hinzufuegen: {"add_phases": [{"title": "OSI-Modell", '
        '"chapter_index": 3, "steps": [{"skill_code": "generate_theory_sheet", '
        '"target_type": "lesson", "target_title": "Das OSI-Schichtenmodell", '
        '"learning_methods": [0, 3, 7], "parameters": {"language": "de"}}]}]}\n'
        '  Phase entfernen: {"remove_phases": [2]}\n'
        '  Phase komplett ersetzen: {"replace_phase": {"index": 5, '
        '"phase": {"title": "...", "steps": [...]}}}\n'
        '  Steps zu bestehender Phase hinzufuegen: {"add_steps": {"phase_index": 3, '
        '"steps": [{"skill_code": "generate_drag_and_drop", "target_type": "lesson", '
        '"target_title": "OSI-Schichten zuordnen", "learning_methods": [7], '
        '"parameters": {"language": "de"}}]}}\n\n'
        'VERBOTEN bei Phase 3:\n'
        '- NIEMALS eine Phase entfernen (remove_phases) wenn der User nur '
        'einen Step aendern will — nutze stattdessen replace_phase!\n'
        '- NIEMALS das gesamte phases-Array senden — nur inkrementelle Ops!\n'
        '- NIEMALS plan_patch: null wenn der User explizit eine Aenderung will!\n\n'
        'LERNMETHODEN IDs: 0=Erklaerung, 1=Schritt-fuer-Schritt, '
        '2=Interaktive Theorie, 3=Diagramm, 4=Praxisbeispiel, '
        '5=Mathe, 6=Karteikarten, 7=Drag&Drop, 8=Lueckentext, '
        '9=Freitext, 10=IHK-Aufgaben, 11=Mehrstufige Praxis\n\n'
        'Wenn keine Aenderung noetig ist (reine Informationsfrage), '
        'setze plan_patch auf null.\n'
        f'{file_section}'
        '\nERINNERUNG: Deine Antwort MUSS valides JSON sein mit '
        '"assistant_message" und "plan_patch" Feldern!'
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

    # Phases/steps if present — show indices for incremental patches
    phases = plan_data.get('phases', [])
    if phases:
        lines.append(f'\nPhasen ({len(phases)}):')
        for idx, phase in enumerate(phases):
            title = phase.get('title', '?')
            steps = phase.get('steps', [])
            lines.append(f'  [{idx}] {title} ({len(steps)} Schritte)')
            for step_idx, step in enumerate(steps):
                skill = step.get('skill_code', '?')
                target = step.get('target_title', '')
                lms = step.get('learning_methods', [])
                lm_str = f' [LM: {lms}]' if lms else ''
                lines.append(f'    {step_idx+1}. {skill}: {target}{lm_str}')

    return '\n'.join(lines) if lines else '(Leerer Plan)'
