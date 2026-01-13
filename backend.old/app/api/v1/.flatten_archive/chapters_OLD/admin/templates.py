"""
LernsystemX Chapter Theory Generation - Prompt Templates

Style-specific prompt templates for theory generation.
Supports: adhs, detailed, short, exam_focus, standard.

Functions:
- get_theory_prompts: Get system and user prompts based on style
- _get_adhs_prompts: ADHS-friendly with whiteboard animations
- _get_detailed_prompts: Detailed academic style
- _get_short_prompts: Short and compact
- _get_exam_focus_prompts: IHK exam-focused
- _get_standard_prompts: Standard balanced

DDD Refactored: 2026-01-08 - Moved from generation/templates.py
Admin-only (used by generation logic)
"""


def get_theory_prompts(style: str, context: dict) -> tuple[str, str]:
    """Get prompts for theory generation based on style.

    Args:
        style: Theory style
        context: Dict with chapter context

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    chapter_title = context.get('chapter_title', '')
    course_title = context.get('course_title', '')
    chapter_description = context.get('chapter_description', '')
    lesson_titles = context.get('lesson_titles', '')

    base_context = f"""
Kontext:
- Kapitel: {chapter_title}
- Kurs: {course_title}
- Beschreibung: {chapter_description}
- Lektionen: {lesson_titles}
- Zielgruppe: Fachinformatiker Systemintegration (FISI)
- Niveau: IHK-Pruefung
"""

    if style == 'adhs':
        return _get_adhs_prompts(chapter_title, base_context)
    elif style == 'detailed':
        return _get_detailed_prompts(chapter_title, base_context)
    elif style == 'short':
        return _get_short_prompts(chapter_title, base_context)
    elif style == 'exam_focus':
        return _get_exam_focus_prompts(chapter_title, base_context)
    else:  # standard
        return _get_standard_prompts(chapter_title, base_context)


def _get_adhs_prompts(chapter_title: str, base_context: str) -> tuple[str, str]:
    """ADHS-friendly prompts with whiteboard animations."""
    system = """Du bist ein erfahrener IT-Ausbilder, spezialisiert auf ADHS-freundliches Lernen.
Deine Erklaerungen sind:
- KURZ und praegnant (max. 2-3 Saetze pro Punkt)
- VISUELL strukturiert mit Aufzaehlungen
- SCHRITTWEISE aufgebaut
- Mit KONKRETEN Beispielen
- Ohne Fachjargon (oder sofort erklaert)

Du erstellst auch WHITEBOARD-ANIMATIONEN die synchron zur Erklaerung ablaufen.

Antworte NUR mit validem JSON."""

    user = f"""Erstelle ein ADHS-freundliches Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "overview": "Kurze Uebersicht (2-3 Saetze)",
    "learningGoals": ["Ziel 1 (kurz!)", "Ziel 2", ...],
    "concepts": [
        {{
            "title": "Konzept",
            "emoji": "passendes Emoji",
            "oneLiner": "Ein Satz",
            "example": "Beispiel",
            "tip": "Merkhilfe"
        }}
    ],
    "terms": [{{"term": "Begriff", "simple": "Einfach erklaert", "example": "Alltagsbeispiel"}}],
    "examTips": ["Tipp 1", "Tipp 2"],
    "summary": "3 Bullet Points",
    "whiteboardActions": [
        {{
            "type": "write",
            "content": "Ueberschrift oder Text",
            "position": {{"x": 50, "y": 10}},
            "duration": 1500,
            "color": "#1f2937",
            "fontSize": 24
        }},
        {{
            "type": "schema",
            "position": {{"x": 10, "y": 25}},
            "schema": [
                {{"name": "Zeile 1", "operator": "=", "value": "Wert 1", "highlight": false}},
                {{"name": "Zeile 2", "operator": "+", "value": "Wert 2", "highlight": true}}
            ],
            "duration": 2000
        }},
        {{
            "type": "arrow",
            "position": {{"x": 30, "y": 50}},
            "endPosition": {{"x": 70, "y": 50}},
            "duration": 800,
            "color": "#3b82f6"
        }},
        {{
            "type": "highlight",
            "content": "Wichtiger Begriff",
            "position": {{"x": 50, "y": 70}},
            "duration": 500,
            "color": "#fbbf24"
        }}
    ]
}}

WICHTIG fuer whiteboardActions:
- Erstelle 5-8 Animationen die das Thema VISUELL erklaeren
- Nutze verschiedene Typen: write, schema, arrow, highlight, underline
- Position ist in Prozent (0-100)
- Bei Kalkulationen/Formeln nutze "schema" mit Zeilen
- Bei Prozessen nutze Pfeile
- Wichtiges mit "highlight" hervorheben
- Baue das Bild Schritt fuer Schritt auf"""

    return system, user


def _get_detailed_prompts(chapter_title: str, base_context: str) -> tuple[str, str]:
    """Detailed academic-style prompts."""
    system = """Du bist ein IT-Ausbilder mit akademischem Hintergrund.
Erstelle ausfuehrliche, gut strukturierte Lerninhalte mit allen Details.
Antworte NUR mit validem JSON."""

    user = f"""Erstelle ein ausfuehrliches Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "overview": "Ausfuehrliche Uebersicht mit Einordnung",
    "learningGoals": ["Detailliertes Lernziel 1", ...],
    "prerequisites": ["Vorwissen 1", ...],
    "concepts": [
        {{
            "title": "Konzept",
            "description": "Ausfuehrliche Erklaerung",
            "background": "Hintergrund",
            "formula": "Formel falls relevant",
            "examples": ["Beispiel 1", "Beispiel 2"],
            "commonMistakes": ["Fehler 1"]
        }}
    ],
    "terms": [{{"term": "Begriff", "definition": "Vollstaendige Definition", "usage": "Verwendung"}}],
    "examRelevance": "Detaillierte Pruefungsrelevanz",
    "summary": "Zusammenfassung"
}}"""

    return system, user


def _get_short_prompts(chapter_title: str, base_context: str) -> tuple[str, str]:
    """Short and compact prompts."""
    system = """Du bist ein IT-Ausbilder, der auf Effizienz setzt.
Erstelle extrem kompakte Zusammenfassungen - nur das Wichtigste.
Antworte NUR mit validem JSON."""

    user = f"""Erstelle eine Kurzuebersicht fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "title": "Kapiteltitel",
    "keyPoints": ["Punkt 1", "Punkt 2", "Punkt 3", "Punkt 4", "Punkt 5"],
    "mustKnowTerms": [{{"term": "Begriff", "definition": "Ein-Satz-Definition"}}],
    "examFormula": "Wichtigste Formel",
    "oneMinuteSummary": "Das Kapitel in 60 Sekunden"
}}"""

    return system, user


def _get_exam_focus_prompts(chapter_title: str, base_context: str) -> tuple[str, str]:
    """IHK exam-focused prompts."""
    system = """Du bist ein IHK-Pruefer und kennst die AP1-Pruefung genau.
Erstelle Lerninhalte mit klarem Pruefungsfokus.
Antworte NUR mit validem JSON."""

    user = f"""Erstelle ein pruefungsfokussiertes Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "examRelevance": "HOCH/MITTEL/NIEDRIG",
    "typicalPoints": "Typische Punktzahl",
    "mustKnow": ["Das MUSS sitzen 1", "Das MUSS sitzen 2"],
    "typicalTasks": [
        {{
            "type": "Aufgabentyp",
            "example": "Beispielaufgabe",
            "solution": "Loesungsweg",
            "points": "Punktzahl",
            "timeMinutes": "Zeit"
        }}
    ],
    "commonMistakes": [{{"mistake": "Fehler", "consequence": "Punktabzug", "howToAvoid": "Vermeidung"}}],
    "examTips": ["Tipp 1", "Tipp 2"],
    "lastMinuteChecklist": ["Check 1", "Check 2"]
}}"""

    return system, user


def _get_standard_prompts(chapter_title: str, base_context: str) -> tuple[str, str]:
    """Standard balanced prompts."""
    system = """Du bist ein erfahrener IT-Ausbilder fuer Fachinformatiker.
Erstelle strukturierte, pruefungsrelevante Lerninhalte.
Antworte NUR mit validem JSON."""

    user = f"""Erstelle ein Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "overview": "Uebersicht",
    "learningGoals": ["Ziel 1", "Ziel 2", ...],
    "concepts": [{{"title": "Konzept", "description": "Erklaerung", "formula": "optional"}}],
    "terms": [{{"term": "Begriff", "definition": "Definition"}}],
    "examRelevance": "Pruefungsrelevanz"
}}"""

    return system, user
