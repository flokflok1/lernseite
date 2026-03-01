"""
Plan Phase Prompts for the 4-Phase Wizard

Builds system/user message pairs for each phase of the AI plan wizard.
Pure infrastructure concern — no Flask, Application, or API imports.
"""

from __future__ import annotations

import re


def _normalize_pdf_text(text: str) -> str:
    """Clean up common PDF extraction artifacts for better AI processing.

    Fixes broken hyphens (e.g. 'Computer -Netzwerke' → 'Computer-Netzwerke'),
    collapsed whitespace, and stray line breaks within sentences.
    """
    # Fix broken hyphens: 'word -word' → 'word-word' (letter-space-hyphen-letter)
    text = re.sub(r'([A-Za-zÄÖÜäöüß]) -([A-Za-zÄÖÜäöüß])', r'\1-\2', text)
    # Fix reverse: 'word- word' → 'word-word'
    text = re.sub(r'([A-Za-zÄÖÜäöüß])- ([A-Za-zÄÖÜäöüß])', r'\1-\2', text)
    # Collapse multiple spaces into one
    text = re.sub(r' {2,}', ' ', text)
    # Remove stray line breaks within sentences (lowercase after newline = continuation)
    text = re.sub(r'\n([a-zäöü])', r' \1', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Phase 1: Course Definition
# ---------------------------------------------------------------------------

def _language_instruction(language: str) -> str:
    """Build a language instruction block for AI prompts.

    Tells the AI which language to use for all generated content.
    The prompt itself stays in German (the AI understands it regardless).
    """
    if language == 'de':
        return ''
    lang_name = get_language_name(language)
    return (
        f'\nSPRACHE: Alle generierten Inhalte (Titel, Beschreibungen, Texte) '
        f'MUESSEN in {lang_name} ({language}) verfasst sein!\n'
        f'Das Quellmaterial kann in einer anderen Sprache sein — '
        f'uebersetze und formuliere ALLES in {lang_name}.\n'
    )


def build_phase1_prompt(
    topic: str,
    file_text: str | None = None,
    language: str = 'de',
) -> tuple[str, str]:
    """Build prompt pair for Phase 1 (course meta extraction)."""
    lang_block = _language_instruction(language)
    system_message = (
        'Du bist ein erfahrener Kursarchitekt fuer eine Online-Lernplattform.\n'
        'Deine Aufgabe: Analysiere das Thema und erstelle eine praezise Kurs-Definition.\n\n'
        f'{lang_block}'
        'Antworte ausschliesslich mit validem JSON (keine Markdown-Fences):\n'
        '{\n'
        '  "title": "Kurstitel (kurz, praegnant)",\n'
        '  "description": "2-3 Saetze Kursbeschreibung",\n'
        '  "target_audience": "Zielgruppe",\n'
        '  "difficulty": "beginner|intermediate|advanced",\n'
        f'  "language": "{language}"\n'
        '}\n\n'
        'Regeln:\n'
        '- Titel: max 80 Zeichen, klar und beschreibend\n'
        '- Beschreibung: Lernziele und Umfang zusammenfassen\n'
        f'- Sprache im JSON MUSS "{language}" sein\n\n'
        'SCHWIERIGKEIT — waehle anhand dieser Kriterien:\n'
        '- "beginner": Keine Vorkenntnisse noetig. Einstiegskurse, '
        'Grundlagen, erste Zertifizierungen (z.B. CompTIA A+, ITIL Foundation, '
        'Einfuehrung in Programmierung, Grundlagen Netzwerktechnik)\n'
        '- "intermediate": Grundwissen wird vorausgesetzt. Aufbaukurse, '
        'fortgeschrittene Zertifizierungen (z.B. CompTIA Network+, CCNA, '
        'AWS Solutions Architect Associate, OCA Java)\n'
        '- "advanced": Mehrjaehrige Erfahrung noetig. Expertenkurse, '
        'Spezialisierungen (z.B. CCNP, CISSP, AWS Professional, '
        'Kubernetes Administrator, Systemarchitektur)'
    )

    if file_text:
        cleaned = _normalize_pdf_text(file_text[:10_000_000])
        user_message = (
            'Analysiere das folgende Dokument und leite daraus eine '
            'Kurs-Definition ab.\n'
            'Behalte den Titel und die Thematik des Dokuments bei — '
            'erfinde keinen neuen Kurs-Titel wenn das Dokument einen hat.\n\n'
            f'--- DOKUMENT ---\n{cleaned}\n--- ENDE ---'
        )
    else:
        user_message = f'Erstelle eine Kurs-Definition zum Thema: {topic}'

    return system_message, user_message


# ---------------------------------------------------------------------------
# Phase 2: Chapter Structure
# ---------------------------------------------------------------------------

_PHASE2_DOCUMENT_RULES = (
    'WICHTIGSTE REGEL — DOKUMENTSTRUKTUR UEBERNEHMEN:\n'
    'Wenn Material/Dokumente bereitgestellt werden:\n'
    '- Uebernimm die EXISTIERENDE Gliederung des Dokuments (Inhaltsverzeichnis, '
    'Ueberschriften, Kapitel) als Basis fuer die Kapitelstruktur.\n'
    '- Erfinde KEINE neue Struktur wenn das Dokument bereits eine klare '
    'Gliederung hat.\n'
    '- Du darfst die Dokumentstruktur leicht anpassen (zusammenfassen, '
    'umbenennen), aber die Reihenfolge und thematische Aufteilung MUSS '
    'dem Originaldokument entsprechen.\n'
    '- Wenn das Dokument z.B. 10 Hauptkapitel hat, erstelle ~10 Kapitel '
    '(nicht 5 oder 15).\n\n'
    'VOLLSTAENDIGKEIT — KEIN THEMA DARF FEHLEN:\n'
    '- Gehe das Dokument Abschnitt fuer Abschnitt durch und stelle sicher, '
    'dass JEDES Thema, jede Ueberschrift und jeder Folien-Titel in genau '
    'einem Kapitel erfasst ist.\n'
    '- Die Kapitel-Beschreibung MUSS alle Unterthemen auflisten, die das '
    'Kapitel abdeckt. Nenne die konkreten Begriffe/Technologien aus dem '
    'Dokument (z.B. "Windows-Uebersicht, Linux-Distributionen, Vor- und '
    'Nachteile" statt nur "Betriebssysteme").\n'
    '- Wenn ein Thema nicht eindeutig in ein Kapitel passt, ordne es dem '
    'inhaltlich naechsten zu und erwaehne es in der Beschreibung.\n'
    '- Pruefe am Ende: Gibt es Abschnitte im Dokument, die in keinem '
    'Kapitel vorkommen? Falls ja, ergaenze sie.\n\n'
    'Weitere Regeln:\n'
    '- Zwischen 3 und 30 Kapitel (je nach Dokumentumfang)\n'
    '- Logische Reihenfolge: vom Einfachen zum Komplexen\n'
    '- Keine inhaltlichen Ueberschneidungen zwischen Kapiteln\n'
    '- Jedes Kapitel hat einen klaren thematischen Fokus\n'
    '- Titel: kurz und praegnant (max 60 Zeichen)\n'
    '- Beschreibung: 2-3 Saetze mit ALLEN Unterthemen des Kapitels'
)


def build_phase2_prompt(
    course_meta: dict,
    file_text: str | None = None,
) -> tuple[str, str]:
    """Build prompt pair for Phase 2 (chapter structure generation)."""
    language = course_meta.get('language', 'de')
    lang_block = _language_instruction(language)
    system_message = (
        'Du bist ein erfahrener Kursarchitekt.\n'
        'Erstelle eine logische Kapitelstruktur fuer den gegebenen Kurs.\n\n'
        f'{lang_block}'
        'Antworte ausschliesslich mit validem JSON (keine Markdown-Fences):\n'
        '{\n'
        '  "chapters": [\n'
        '    {"title": "Kapiteltitel", "description": "Kurzbeschreibung des Kapitels"}\n'
        '  ]\n'
        '}\n\n'
        f'{_PHASE2_DOCUMENT_RULES}'
    )

    meta_section = _format_course_meta(course_meta)

    if file_text:
        cleaned = _normalize_pdf_text(file_text[:10_000_000])
        user_message = (
            f'{meta_section}\n\n'
            'Erstelle die Kapitelstruktur basierend auf dem Kurs und '
            'dem folgenden Material.\n\n'
            f'--- MATERIAL ---\n{cleaned}\n--- ENDE ---'
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
    '6. KEINE doppelten Theorie-Methoden! Gruppe A (0-4) sind alle Erklaerungen. '
    'Waehle MAXIMAL EINE aus Gruppe A pro Lektion. '
    'Kombiniere stattdessen A + B + C (z.B. 0 + 6 + 8 oder 0 + 7 + 9).\n'
)


def build_phase3_prompt(
    course_meta: dict,
    chapters: list[dict],
    skill_catalog_section: str,
) -> tuple[str, str]:
    """Build prompt pair for Phase 3 (full plan with skills)."""
    language = course_meta.get('language', 'de')
    lang_block = _language_instruction(language)
    system_message = (
        'Du bist ein erfahrener didaktischer Planer.\n'
        'Erstelle einen vollstaendigen Kursplan mit konkreten '
        'Lernschritten fuer jedes Kapitel.\n\n'
        f'{lang_block}'
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
        f'          "parameters": {{"language": "{language}"}}\n'
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


def get_language_name(code: str) -> str:
    """Map language code to human-readable name.

    Central lookup used by all prompt builders. Extend this dict
    when new languages are added to the platform.
    """
    _LANG_NAMES = {
        'de': 'Deutsch',
        'en': 'English',
        'pl': 'Polski',
        'fr': 'Français',
        'es': 'Español',
        'it': 'Italiano',
        'tr': 'Türkçe',
        'pt': 'Português',
        'nl': 'Nederlands',
        'ru': 'Русский',
        'ja': '日本語',
        'zh': '中文',
        'ko': '한국어',
        'ar': 'العربية',
    }
    return _LANG_NAMES.get(code, code)
