"""
Plan Prompts Part 2 — Chat Refinement & Flat Plan Prompts

Split from plan_prompts.py to respect G01 (500 LOC limit).
Contains: build_plan_chat_prompt, build_flat_plan_prompt,
build_flat_plan_from_text_prompt.
"""

from __future__ import annotations

from app.infrastructure.ai.plan.plan_prompts import (
    _normalize_pdf_text,
    get_language_name,
)


# ---------------------------------------------------------------------------
# Plan Chat Refinement
# ---------------------------------------------------------------------------

_CHAT_SKILL_CODES = (
    'VERFUEGBARE SKILL-CODES:\n'
    '  generate_theory_sheet — Theorie-Zusammenfassung\n'
    '  generate_deep_explanation — Tiefgehende Erklaerung\n'
    '  generate_step_by_step — Schritt-fuer-Schritt Anleitung\n'
    '  generate_interactive_theory — Interaktive Theorie\n'
    '  generate_diagram — Diagramm/Visualisierung\n'
    '  generate_example_scenario — Praxisbeispiel/Szenario\n'
    '  generate_math_interactive — Interaktive Mathe-Uebung\n'
    '  generate_flashcards — Karteikarten\n'
    '  generate_drag_and_drop — Drag & Drop Zuordnung\n'
    '  generate_cloze_test — Lueckentext\n'
    '  generate_free_text — Freitext-Aufgabe\n'
    '  generate_ihk_tasks — IHK-Pruefungsaufgaben\n'
    '  generate_multi_step — Mehrstufige Praxisaufgabe\n'
    '  generate_quiz — Multiple-Choice Quiz\n'
    '  generate_chapter_exam — Kapitel-Abschlusspruefung\n'
    '  generate_true_false — Wahr/Falsch Aussagen\n'
    '  generate_comprehension_check — Verstaendnis-Check\n\n'
    'LERNMETHODEN IDs (fuer learning_methods Array):\n'
    '  Gruppe A (Erklaerung — max 1 pro Lektion!): '
    '0=Erklaerung, 1=Schritt-fuer-Schritt, 2=Interaktive Theorie, '
    '3=Diagramm, 4=Praxisbeispiel\n'
    '  Gruppe B (Uebung): 5=Mathe, 6=Karteikarten, 7=Drag&Drop, 8=Lueckentext\n'
    '  Gruppe C (Pruefung): 9=Freitext, 10=IHK-Aufgaben, 11=Mehrstufige Praxis\n'
    '  REGEL: Waehle 1x Gruppe A + 1-2x Gruppe B/C. NICHT 0+2 oder 0+1!\n'
)


def _build_patch_operations(language: str) -> str:
    """Build the plan_patch operations reference for the chat prompt."""
    return (
        'PLAN_PATCH OPERATIONEN (Phase 3):\n'
        '  Nutze die Phase-Indizes [0], [1], [2]... aus dem Plan oben.\n\n'
        '  MEHRERE Phasen auf einmal ersetzen (BEVORZUGT bei Massenänderungen!):\n'
        '  {"replace_phases": [\n'
        '    {"index": 3, "phase": {"title": "...", "steps": [...]}},\n'
        '    {"index": 6, "phase": {"title": "...", "steps": [...]}},\n'
        '    {"index": 10, "phase": {"title": "...", "steps": [...]}}\n'
        '  ]}\n\n'
        '  Einzelne Phase ersetzen:\n'
        '  {"replace_phase": {"index": 0, "phase": {"title": "...", '
        '"steps": [{"skill_code": "...", "target_type": "lesson", '
        '"target_title": "...", "learning_methods": [...], '
        f'"parameters": {{"language": "{language}"}}}}]}}}}\n\n'
        '  Neue Phase hinzufuegen:\n'
        '  {"add_phases": [{"title": "...", "chapter_index": 3, '
        '"steps": [...]}]}\n\n'
        '  Steps zu bestehender Phase hinzufuegen:\n'
        '  {"add_steps": {"phase_index": 3, "steps": [...]}}\n\n'
        '  Phase entfernen (NUR wenn ganzes Kapitel weg soll):\n'
        '  {"remove_phases": [2]}\n'
    )


_CHAT_RULES = (
    'WICHTIGE REGELN:\n'
    '1. Wenn der User eine Aenderung will → plan_patch MUSS gesetzt sein!\n'
    '   NIEMALS "Ich werde..." oder "Ich kann..." ohne plan_patch!\n'
    '2. Wenn du einen Step ersetzt/entfernst → IMMER einen Ersatz liefern.\n'
    '3. replace_phase/replace_phases ersetzt die GANZE Phase — alle Steps '
    'muessen drin sein, auch die unveraenderten!\n'
    '4. Achte auf Duplikate: Keine zwei Steps mit gleichem target_title.\n'
    '5. Sei konkret in assistant_message: "Ich habe X durch Y ersetzt" '
    'statt "Ich kann das aendern".\n'
    '6. Du hast Zugriff auf den KOMPLETTEN Chatverlauf. Beziehe dich auf '
    'fruehere Nachrichten wenn relevant.\n'
    '7. MASSENAENDERUNGEN: Wenn der User eine Aenderung will die MEHRERE '
    'Kapitel betrifft (z.B. "ersetze alle Quiz durch Freitext"), dann '
    'nutze replace_phases und aendere ALLE betroffenen Phasen auf einmal! '
    'Gehe JEDEN Phase-Index durch und pruefe ob er betroffen ist. '
    'Lass KEINE Phase aus!\n'
)


_CHAT_CORE_TASK = (
    'Du bist ein erfahrener Kursplaner und didaktischer Experte.\n'
    'Du hilfst dem Benutzer, seinen Kursplan zu verfeinern.\n\n'
    'DEINE KERNAUFGABE:\n'
    '- Du KENNST den aktuellen Plan (siehe unten) und arbeitest damit.\n'
    '- Wenn der User eine Aenderung will: MACH sie sofort im plan_patch.\n'
    '- Wenn der User diskutieren will: Gib konkrete Vorschlaege mit '
    'Begruendung, aber aendere nichts.\n'
    '- Wenn der User ein Problem nennt (Duplikate, fehlende Inhalte, '
    'falsche Methoden): Analysiere den Plan, finde das Problem, '
    'und schlage die Loesung mit konkretem plan_patch vor.\n\n'
    'QUALITAETSPRUEFUNG — pruefe bei jeder Antwort:\n'
    '- Gibt es Duplikate? (gleicher target_title oder sehr aehnliche Steps)\n'
    '- Fehlt ein Ersatz? (Wenn ein Step entfernt wird, MUSS ein neuer kommen)\n'
    '- Passt die Lernmethode zum Inhalt?\n'
    '- Hat jedes Kapitel mindestens 2 Steps?\n'
)

_CHAT_THINKING_PROCESS = (
    'DENKPROZESS (intern, NICHT in die Antwort schreiben):\n'
    'Bevor du antwortest, durchlaufe diese Schritte:\n'
    '1. Was will der User? (Aenderung, Diskussion, Problem melden)\n'
    '2. Welche Phase(n)/Steps sind betroffen?\n'
    '3. Gibt es Duplikate oder Luecken im aktuellen Plan?\n'
    '4. Was ist die konkrete Aenderung (plan_patch)?\n'
    '5. Sind nach der Aenderung noch alle Kapitel vollstaendig?\n'
)


def _build_file_section(file_text: str | None) -> str:
    """Build the uploaded material section for chat prompts."""
    if not file_text:
        return ''
    cleaned = _normalize_pdf_text(file_text[:10_000_000])
    return (
        '\n\nHOCHGELADENES MATERIAL:\n'
        f'--- DOKUMENT ---\n{cleaned}\n--- ENDE ---\n'
        'Du HAST Zugriff auf dieses Material. Nutze es als primaere '
        'Wissensquelle fuer inhaltliche Entscheidungen.\n'
    )


def build_plan_chat_prompt(
    plan_data: dict,
    current_phase: int,
    file_text: str | None = None,
) -> str:
    """Build system message for plan chat refinement."""
    course_meta = plan_data.get('course_meta', {})
    language = course_meta.get('language', 'de') if isinstance(course_meta, dict) else 'de'

    phase_labels = {
        1: 'Kurs-Definition (Titel, Beschreibung, Zielgruppe)',
        2: 'Kapitelstruktur',
        3: 'Vollstaendiger Kursplan mit Lernschritten',
    }
    phase_label = phase_labels.get(current_phase, 'Kursplan')

    return (
        f'{_CHAT_CORE_TASK}\n'
        f'Aktuelle Phase: {current_phase} — {phase_label}\n\n'
        f'AKTUELLER PLAN (vollstaendig):\n{_format_plan_for_chat(plan_data)}\n\n'
        f'{_CHAT_SKILL_CODES}\n'
        'ANTWORTFORMAT (PFLICHT — NUR valides JSON!):\n'
        '{\n'
        '  "assistant_message": "Deine Antwort an den User (konkret, nicht vage)",\n'
        '  "plan_patch": null oder {...Aenderungen...}\n'
        '}\n\n'
        f'{_build_patch_operations(language)}\n'
        f'{_CHAT_THINKING_PROCESS}\n'
        f'{_CHAT_RULES}'
        f'{_build_file_section(file_text)}'
        '\nERINNERUNG: Valides JSON. Konkrete Aenderungen. Keine leeren Versprechen.'
    )


# ---------------------------------------------------------------------------
# Flat Plan Prompts (legacy single-shot generation)
# ---------------------------------------------------------------------------

def build_flat_plan_prompt(
    course_title: str,
    scope: str,
    chapters: list[dict],
    language: str,
    skill_catalog_section: str,
) -> tuple[str, str]:
    """Build prompt pair for single-shot flat plan generation."""
    lang_name = get_language_name(language)
    lang_instruction = (
        f'\nALL generated content (titles, descriptions) MUST be in {lang_name}.\n'
        if language != 'de' else ''
    )

    system_msg = (
        'You are an expert educational content planner. '
        'Generate a structured content plan as JSON.\n\n'
        f'{lang_instruction}'
        f'{skill_catalog_section}'
    )

    import json as _json
    user_msg = (
        f'Create a content plan for the course: {course_title}\n'
        f'Scope: {scope}\n'
        f'Existing chapters: {_json.dumps(chapters)}\n\n'
        'Return ONLY valid JSON (no markdown fences) with format:\n'
        '{"phases": [{"phase_id": "uuid", "order": 1, '
        '"title": "Chapter Name", "steps": [{"step_id": "uuid", "order": 1, '
        '"skill_code": "generate_deep_explanation", "target_type": "lesson", '
        '"target_id": null, "target_title": "Lesson Title", '
        f'"parameters": {{"language": "{language}"}}, '
        '"status": "pending"}]}]}'
    )

    return system_msg, user_msg


def build_flat_plan_from_text_prompt(
    extracted_text: str,
    language: str,
    skill_catalog_section: str,
) -> tuple[str, str]:
    """Build prompt pair for plan generation from uploaded file text."""
    lang_name = get_language_name(language)

    system_msg = (
        'You are an expert educational content planner. '
        'Analyze educational material and create a comprehensive '
        'structured course plan as JSON.\n\n'
        'IMPORTANT: The source material may be in any language. '
        f'ALL output (chapter titles, lesson titles, descriptions) '
        f'MUST be in {lang_name}. '
        'Use the source material as a structural reference for topics, '
        f'but generate all text in {lang_name}.\n\n'
        f'{skill_catalog_section}'
    )

    user_msg = (
        'Analyze this educational material and create a COMPLETE '
        'content plan covering ALL chapters and topics WITHOUT '
        'EXCEPTION:\n\n'
        f'{extracted_text}\n\n'
        'CRITICAL: You MUST cover EVERY topic from the material. '
        'Do NOT skip or merge topics.\n'
        'If the material has 30+ topics, create 30+ phases. '
        'Missing topics = FAILURE.\n'
        'Each major topic/chapter = one phase.\n'
        'For each phase, include multiple steps with different '
        'learning methods (theory + practice + assessment).\n\n'
        f'LANGUAGE: ALL titles and descriptions MUST be in '
        f'{lang_name}.\n\n'
        'Return ONLY valid JSON (no markdown fences) with format:\n'
        '{"phases": [{"phase_id": "uuid", "order": 1, '
        '"title": "Chapter Title", "steps": [{"step_id": "uuid", '
        '"order": 1, "skill_code": "generate_deep_explanation", '
        '"target_type": "lesson", "target_id": null, '
        '"target_title": "Lesson Title", '
        f'"parameters": {{"language": "{language}"}}, '
        '"status": "pending"}]}]}'
    )

    return system_msg, user_msg


# ---------------------------------------------------------------------------
# Private helpers (chat-specific)
# ---------------------------------------------------------------------------

def _format_plan_for_chat(plan_data: dict) -> str:
    """Format plan data with full detail for chat context."""
    if not plan_data:
        return '(Kein Plan vorhanden)'

    lines = []

    # Course meta
    course_meta = plan_data.get('course_meta', {})
    if isinstance(course_meta, dict) and course_meta:
        lines.append(f'KURS: {course_meta.get("title", "?")}')
        if course_meta.get('description'):
            lines.append(f'Beschreibung: {course_meta["description"]}')
        if course_meta.get('target_audience'):
            lines.append(f'Zielgruppe: {course_meta["target_audience"]}')
        if course_meta.get('difficulty'):
            lines.append(f'Schwierigkeit: {course_meta["difficulty"]}')
    elif 'title' in plan_data:
        lines.append(f'KURS: {plan_data["title"]}')

    # Chapters
    chapters = plan_data.get('chapters', [])
    if chapters:
        lines.append(f'\nKAPITEL ({len(chapters)}):')
        for i, ch in enumerate(chapters):
            desc = ch.get('description', '')
            desc_str = f' — {desc}' if desc else ''
            lines.append(f'  {i + 1}. {ch.get("title", "?")}{desc_str}')

    # Phases/steps — detailed view with indices
    phases = plan_data.get('phases', [])
    if phases:
        total_steps = sum(len(p.get('steps', [])) for p in phases)
        lines.append(f'\nPLAN ({len(phases)} Kapitel, {total_steps} Schritte):')
        for idx, phase in enumerate(phases):
            title = phase.get('title', '?')
            steps = phase.get('steps', [])
            lines.append(f'\n  [{idx}] {title} ({len(steps)} Schritte):')
            for step_idx, step in enumerate(steps):
                skill = step.get('skill_code', '?')
                target = step.get('target_title', '')
                lms = step.get('learning_methods', [])
                lm_str = f'  [LM-IDs: {lms}]' if lms else ''
                lines.append(
                    f'    {step_idx+1}. "{target}" → {skill}{lm_str}'
                )

    return '\n'.join(lines) if lines else '(Leerer Plan)'
