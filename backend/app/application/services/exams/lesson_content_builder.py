"""Lesson Content Builder — generates HTML for exam practice lessons.

Converts LM instance data (math problems, cloze sentences, IHK tasks, etc.)
into readable HTML that renders in the center panel of the lesson player.
Includes scenario context (company situations, Anlagen) when available.
"""
from typing import Dict, List, Optional

from app.domain.services.lm_content_mapper import get_lm_label
from app.infrastructure.utils.markdown_converter import markdown_to_html


def build_lesson_markdown(
    lm_type: int,
    lm_data: Dict,
    chapter_label: str,
    language: str = 'de',
) -> Dict:
    """Build lesson content JSONB with content_html.

    Returns dict suitable for LessonRepository.create(content=...).
    """
    builders = {
        5: _math_markdown,
        8: _cloze_markdown,
        10: _ihk_tasks_markdown,
        11: _case_study_markdown,
        6: _flashcards_markdown,
        7: _drag_drop_markdown,
    }
    builder = builders.get(lm_type)
    if not builder:
        return {}

    lm_label = get_lm_label(lm_type, language)
    md = builder(lm_data, chapter_label, lm_label, language)
    if not md:
        return {}

    return {'content_html': markdown_to_html(md)}


def _render_scenario_contexts(data: Dict, lang: str) -> str:
    """Render scenario_contexts block if present in LM data."""
    contexts = data.get('scenario_contexts', [])
    if not contexts:
        return ''
    header = {'de': 'Ausgangssituation', 'en': 'Scenario Context'}
    lines = [f'\n## {header.get(lang, header["de"])}\n']
    for ctx in contexts:
        title = ctx.get('title', '')
        text = ctx.get('text', '')
        if title:
            lines.append(f'**{title}**\n')
        if text:
            lines.append(f'{text}\n')
        lines.append('')
    lines.append('---\n')
    return '\n'.join(lines)


def _math_markdown(
    data: Dict, chapter: str, label: str, lang: str,
) -> str:
    problems = data.get('problems', [])
    if not problems:
        return ''

    intro = {
        'de': f'Bearbeite die folgenden **{len(problems)} Rechenaufgaben** '
              f'aus echten IHK-Prüfungen zum Thema **{chapter}**.\n\n'
              f'Rechne jede Aufgabe durch und vergleiche dein Ergebnis '
              f'mit der Musterlösung.',
        'en': f'Work through the following **{len(problems)} math problems** '
              f'from real IHK exams on **{chapter}**.',
    }

    lines = [f'# {label}\n', intro.get(lang, intro['de']), '\n']
    scenario_block = _render_scenario_contexts(data, lang)
    if scenario_block:
        lines.append(scenario_block)
    lines.append('---\n')

    for i, p in enumerate(problems, 1):
        q = p.get('question', p.get('text', ''))
        if not q:
            continue
        lines.append(f'### Aufgabe {i}\n')
        lines.append(f'{q}\n')
        hint = p.get('hint', '')
        if hint:
            lines.append(f'> 💡 **Hinweis:** {hint}\n')
        lines.append('---\n')

    return '\n'.join(lines)


def _cloze_markdown(
    data: Dict, chapter: str, label: str, lang: str,
) -> str:
    sentences = data.get('sentences', [])
    # Filter out empty sentences before counting
    valid = [s for s in sentences if s.get('text', '').strip()]
    if not valid:
        return ''

    intro = {
        'de': f'Ergänze die fehlenden Begriffe in den folgenden '
              f'**{len(valid)} Lückentexten** zum Thema **{chapter}**.\n\n'
              f'Die Lücken sind mit `_____` markiert.',
        'en': f'Fill in the blanks in the following '
              f'**{len(valid)} cloze sentences** on **{chapter}**.',
    }

    lines = [f'# {label}\n', intro.get(lang, intro['de']), '\n']
    scenario_block = _render_scenario_contexts(data, lang)
    if scenario_block:
        lines.append(scenario_block)
    lines.append('---\n')

    for i, s in enumerate(valid, 1):
        text = s.get('text', '')
        # Replace {{blank}} placeholder with visible blank marker
        text = text.replace('{{blank}}', '_____')
        lines.append(f'**{i}.** {text}\n')

    return '\n'.join(lines)


def _ihk_tasks_markdown(
    data: Dict, chapter: str, label: str, lang: str,
) -> str:
    tasks = data.get('tasks', [])
    if not tasks:
        return ''

    total_points = sum(
        float(t.get('points', 0)) for t in tasks
    )
    intro = {
        'de': f'**{len(tasks)} Prüfungsaufgaben** aus echten IHK AP1 '
              f'Prüfungen zum Thema **{chapter}**.\n\n'
              f'Gesamtpunktzahl: **{int(total_points)} Punkte**. '
              f'Bearbeite jede Aufgabe wie in der echten Prüfung.',
        'en': f'**{len(tasks)} exam tasks** from real IHK AP1 '
              f'exams on **{chapter}**. '
              f'Total: **{int(total_points)} points**.',
    }

    lines = [f'# {label}\n', intro.get(lang, intro['de']), '\n']
    scenario_block = _render_scenario_contexts(data, lang)
    if scenario_block:
        lines.append(scenario_block)
    lines.append('---\n')

    for i, t in enumerate(tasks, 1):
        q = t.get('question', '')
        if not q:
            continue
        pts = int(float(t.get('points', 0)))
        pts_str = f' ({pts} Punkte)' if pts else ''
        lines.append(f'### Aufgabe {i}{pts_str}\n')
        lines.append(f'{q}\n')
        lines.append('---\n')

    return '\n'.join(lines)


def _case_study_markdown(
    data: Dict, chapter: str, label: str, lang: str,
) -> str:
    steps = data.get('steps', [])
    if not steps:
        return ''

    intro = {
        'de': f'Bearbeite die folgenden **{len(steps)} Fallstudien** '
              f'zum Thema **{chapter}**.\n\n'
              f'Lies das Szenario sorgfältig und beantworte die Fragen.',
        'en': f'Work through the following **{len(steps)} case studies** '
              f'on **{chapter}**.',
    }

    lines = [f'# {label}\n', intro.get(lang, intro['de']), '\n---\n']

    for i, s in enumerate(steps, 1):
        scenario = s.get('scenario', '')
        questions = s.get('questions', [])
        lines.append(f'### Fallstudie {i}\n')
        if scenario:
            lines.append(f'**Szenario:**\n\n{scenario}\n')
        if questions:
            lines.append('\n**Fragen:**\n')
            for j, fq in enumerate(questions, 1):
                if isinstance(fq, dict):
                    lines.append(f'{j}. {fq.get("question", fq.get("text", ""))}\n')
                else:
                    lines.append(f'{j}. {fq}\n')
        lines.append('---\n')

    return '\n'.join(lines)


def _flashcards_markdown(
    data: Dict, chapter: str, label: str, lang: str,
) -> str:
    cards = data.get('cards', [])
    if not cards:
        return ''

    intro = {
        'de': f'**{len(cards)} Lernkarten** zum Thema **{chapter}**.\n\n'
              f'Versuche die Antwort zu formulieren, bevor du sie aufdeckst.',
        'en': f'**{len(cards)} flashcards** on **{chapter}**.',
    }

    lines = [f'# {label}\n', intro.get(lang, intro['de']), '\n---\n']

    for i, c in enumerate(cards, 1):
        front = c.get('front', '')
        if not front:
            continue
        lines.append(f'### Karte {i}\n')
        lines.append(f'**Frage:** {front}\n')
        lines.append('---\n')

    return '\n'.join(lines)


def _drag_drop_markdown(
    data: Dict, chapter: str, label: str, lang: str,
) -> str:
    pairs = data.get('pairs', [])
    if not pairs:
        return ''

    intro = {
        'de': f'**{len(pairs)} Zuordnungsaufgaben** zum Thema **{chapter}**.\n\n'
              f'Ordne jedem Begriff die richtige Erklärung zu.',
        'en': f'**{len(pairs)} matching tasks** on **{chapter}**.',
    }

    lines = [f'# {label}\n', intro.get(lang, intro['de']), '\n---\n']

    for i, p in enumerate(pairs, 1):
        q = p.get('question', '')
        if not q:
            continue
        lines.append(f'**{i}.** {q}\n')

    return '\n'.join(lines)
