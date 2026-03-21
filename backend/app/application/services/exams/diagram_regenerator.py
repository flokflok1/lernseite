"""Diagram Regenerator -- converts text-description Anlagen to visual HTML.

Finds Anlagen that contain text descriptions of diagrams (e.g., "Das Diagramm
zeigt...") and regenerates them as structured HTML using CSS classes
(diagram-node, diagram-line, diagram-row, diagram-group, diagram-label).
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_DIAGRAM_PROMPT = """Du bekommst eine Text-Beschreibung eines Diagramms aus einer IHK-Pruefung.
Konvertiere diese in visuelles HTML mit CSS-Klassen.

AKTUELLER INHALT:
{current_html}

TITEL: {title}

VERFUEGBARE CSS-KLASSEN:
- <div class="diagram-node">Name<br><small class="diagram-label">Detail</small></div> -- Ein Geraet/Knoten
- <div class="diagram-line"></div> -- Eine Verbindungslinie zwischen Knoten
- <div class="diagram-row"> ... </div> -- Eine Zeile mit Knoten und Linien (flex, horizontal)
- <div class="diagram-group"><strong>Bereichsname</strong> ... </div> -- Ein Container/Bereich
- <small class="diagram-label">Text</small> -- Beschriftung

REGELN:
1. Verwende NUR diese CSS-Klassen, KEINE inline-styles
2. Jedes Geraet/jede Entitaet als eigene diagram-node
3. Verbindungen als diagram-line zwischen den Nodes
4. Logische Gruppen (Subnetze, Bereiche) als diagram-group
5. IP-Adressen, Ports, Typen als diagram-label innerhalb der Nodes
6. Zeilen mit diagram-row (flexbox, horizontal)
7. Fuer ERM: Entitaeten als diagram-node, Beziehungen als diagram-label
8. Fuer UML: Klassen als diagram-node mit Attributen/Methoden als <small>
9. Behalte ALLE technischen Details (IPs, Portnummern, Geraetetypen)
10. Kein <p>Das Diagramm zeigt...</p> -- NUR das visuelle HTML

Antworte NUR mit dem HTML, keine Erklaerung."""


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences from AI response."""
    if '```html' in text:
        text = text.split('```html')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].split('```')[0].strip()
    return text


def regenerate_diagram(anlage: Dict) -> Optional[str]:
    """Regenerate a single text-description Anlage as visual HTML.

    Args:
        anlage: Dict with keys content_html, title, anlage_id.

    Returns:
        New HTML string using diagram CSS classes, or None on failure.
    """
    from app.infrastructure.ai.task_model_resolver import resolve_model_for_task
    from app.infrastructure.ai.adapter import AIAdapter

    current_html = anlage.get('content_html', '')
    title = anlage.get('title', '')

    prompt = _DIAGRAM_PROMPT.format(
        current_html=current_html,
        title=title,
    )

    try:
        provider, model = resolve_model_for_task('default')
        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_request(
            prompt=prompt,
            language='de',
            temperature=0.2,
        )
        html = _strip_code_fences(response.get('output_text', ''))
        if html and len(html) > 20:
            return html
        logger.warning(
            "AI returned insufficient HTML for anlage %s",
            anlage.get('anlage_id'),
        )
        return None
    except Exception:
        logger.exception(
            "Failed to regenerate diagram for anlage %s",
            anlage.get('anlage_id'),
        )
        return None


def regenerate_all_text_diagrams() -> Dict:
    """Find and regenerate all text-description diagrams.

    Returns:
        Dict with keys: found, regenerated, failed, details.
    """
    from app.infrastructure.persistence.repositories.exams.questions import (
        ExamQuestionRepository,
    )

    text_diagrams = ExamQuestionRepository.find_text_diagram_anlagen()
    results: Dict = {
        'found': len(text_diagrams),
        'regenerated': 0,
        'failed': 0,
        'details': [],
    }

    for td in text_diagrams:
        new_html = regenerate_diagram(td)
        if new_html:
            ExamQuestionRepository.update_anlage_content(
                str(td['anlage_id']), new_html,
            )
            results['regenerated'] += 1
            results['details'].append({
                'exam': td['exam_title'],
                'anlage': td['number'],
                'title': td['title'],
                'status': 'ok',
            })
            logger.info(
                "Regenerated diagram: %s Anlage %s",
                td['exam_title'], td['number'],
            )
        else:
            results['failed'] += 1
            results['details'].append({
                'exam': td['exam_title'],
                'anlage': td['number'],
                'title': td['title'],
                'status': 'failed',
            })

    return results
