"""
ExamArchive Service - Text Extraction & Vision Analysis (Part 2)

Text extraction and Vision AI analysis for PDF and image files.
Split from archive_service.py for G01 compliance (<500 LOC).

- PDF text: Extracted via PDFService (fallback)
- Images (JPG/PNG): OCR via Vision-AI (provider from system config)
- Vision pipeline: PDF pages → images → Vision AI → structured JSON
"""

import os
import base64
import logging
from typing import Optional

from app.application.services.content.pdf.bridge import PDFService

logger = logging.getLogger(__name__)

# Supported file extensions (shared with archive_service.py)
PDF_EXTENSIONS = {'.pdf'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


def extract_text(filepath: str) -> Optional[str]:
    """
    Extract text from a file (PDF or image).

    For PDFs, uses PDFService. For images, uses Vision-AI OCR.

    Args:
        filepath: Absolute path to the file

    Returns:
        Extracted text or None on failure
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return extract_text_from_image(filepath)
    return extract_pdf_text(filepath)


def extract_pdf_text(filepath: str) -> Optional[str]:
    """Extract text from a PDF file via PDFService."""
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()

        result = PDFService.extract_text(
            file_bytes, os.path.basename(filepath), use_cache=False
        )
        return result.get('extracted_text')
    except Exception as e:
        logger.warning("PDF extraction failed for %s: %s", filepath, e)
        return None


def resolve_vision_model(
    provider: str | None = None, model: str | None = None,
) -> tuple:
    """
    Resolve vision-capable AI provider and model from system config.

    If caller provides both provider and model, those are used directly.
    Otherwise falls back through:
    1. Default 'vision' category model from DB
    2. Default 'chat' category model (GPT-4o, Gemini Pro support vision)
    3. Hardcoded fallback: openai/gpt-4o
    """
    if provider and model:
        return (provider, model)
    try:
        from app.infrastructure.persistence.repositories.ai_models import (
            AIModelsRepository,
        )
        # Try vision-specific model first
        vision = AIModelsRepository.get_default_model('vision')
        if vision:
            return (
                vision.get('provider_name', 'openai'),
                vision.get('model_name', 'gpt-4o'),
            )
        # Fall back to chat model (most chat models support vision)
        chat = AIModelsRepository.get_default_model('chat')
        if chat:
            return (
                chat.get('provider_name', 'openai'),
                chat.get('model_name', 'gpt-4o'),
            )
    except Exception as e:
        logger.debug("Could not resolve vision model from DB: %s", e)
    return ('openai', 'gpt-4o')


def extract_text_from_image(filepath: str) -> Optional[str]:
    """
    Extract text from an exam photo using Vision-AI OCR.

    Dynamically resolves the vision-capable AI provider from system
    configuration. Supports OpenAI (GPT-4o) and Google (Gemini).

    Args:
        filepath: Absolute path to the image file

    Returns:
        Transcribed text or None on failure
    """
    try:
        with open(filepath, 'rb') as f:
            image_bytes = f.read()

        ext = os.path.splitext(filepath)[1].lower().lstrip('.')
        mime_type = 'jpeg' if ext in ('jpg', 'jpeg') else 'png'
        b64 = base64.b64encode(image_bytes).decode('utf-8')

        messages = [
            {
                'role': 'system',
                'content': (
                    'Du bist ein OCR-Spezialist für Prüfungsbögen. '
                    'Transkribiere den gesamten sichtbaren Text aus dem '
                    'Foto einer Prüfungsseite. Gib NUR den transkribierten '
                    'Text zurück, keine Erklärungen oder Kommentare. '
                    'Behalte die Struktur bei (Aufgabennummern, '
                    'Unterpunkte, Tabellen).'
                ),
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': (
                            'Transkribiere den gesamten Text aus '
                            'diesem Prüfungsfoto:'
                        ),
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': (
                                f'data:image/{mime_type};base64,{b64}'
                            ),
                        },
                    },
                ],
            },
        ]

        provider, model = resolve_vision_model()
        logger.info(
            "Vision OCR using %s/%s for %s",
            provider, model, os.path.basename(filepath),
        )

        from app.infrastructure.ai.adapter import AIAdapter
        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_messages(
            messages, temperature=0.1, max_tokens=4000
        )
        text = response.get('output_text', '').strip()
        if text:
            logger.info(
                "Vision OCR extracted %d chars from %s",
                len(text), os.path.basename(filepath),
            )
            return text
        return None
    except Exception as e:
        logger.warning(
            "Vision OCR failed for %s: %s", filepath, e
        )
        return None


# ---------------------------------------------------------------------------
# Vision Pipeline: PDF → images → Vision AI → structured JSON
# ---------------------------------------------------------------------------


def convert_pdf_to_images(pdf_path: str, dpi: int = 200) -> list[str]:
    """Convert PDF pages to base64-encoded PNG images for Vision AI.

    Args:
        pdf_path: Absolute path to PDF file
        dpi: Resolution (200 = good quality/token balance)

    Returns:
        List of base64-encoded PNG strings (one per page)
    """
    from pdf2image import convert_from_path
    import io

    logger.info("Converting PDF to images: %s (dpi=%d)", pdf_path, dpi)
    images = convert_from_path(pdf_path, dpi=dpi)
    result = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        result.append(b64)
        buf.close()
    logger.info("Converted %d pages to images", len(result))
    return result


def analyze_exam_with_vision(
    page_images: list[str],
    solution_text: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> dict | None:
    """Analyze exam pages with Vision AI.

    Sends all page images to a vision-capable model which extracts
    complete scenarios, questions, tables, and Anlagen.

    Args:
        page_images: List of base64-encoded PNG images (one per page)
        solution_text: Optional solution text for answer extraction
        provider: AI provider (None = auto-resolve)
        model: AI model (None = auto-resolve)

    Returns:
        Parsed dict with 'scenarios' and 'questions' keys, or None
    """
    if not page_images:
        logger.warning("No page images provided for vision analysis")
        return None

    content = _build_vision_message_content(page_images, solution_text)
    resolved_provider, resolved_model = resolve_vision_model(provider, model)

    logger.info(
        "Sending %d page images to Vision AI (%s/%s)",
        len(page_images), resolved_provider, resolved_model,
    )

    from app.infrastructure.ai.adapter import AIAdapter
    adapter = AIAdapter(provider=resolved_provider, model=resolved_model)

    response = adapter.send_messages(
        messages=[{"role": "user", "content": content}],
        temperature=0.2,
        max_tokens=16000,
    )

    output_text = response.get('output_text', '')
    if not output_text:
        logger.error("Vision AI returned empty response")
        return None

    return _parse_vision_response(output_text)


def _build_vision_message_content(
    page_images: list[str],
    solution_text: str | None = None,
) -> list[dict]:
    """Build multi-part message content with text prompt and page images."""
    content: list[dict] = [
        {"type": "text", "text": _build_vision_prompt(solution_text)},
    ]
    for img_b64 in page_images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_b64}",
                "detail": "high",
            },
        })
    return content


_VISION_PROMPT_BASE = """Du siehst die Seiten einer Pruefung oder eines Examens als Bilder.

STRUKTUR EINER PRUEFUNG:
- Eine Pruefung hat mehrere AUFGABEN (Aufgabe 1, 2, 3, 4 oder Question 1, 2, 3)
- Jede Aufgabe kann eine HANDLUNGSSITUATION haben (= Szenario mit Kontext, Firma, Situation)
- Jede Aufgabe hat TEILAUFGABEN (1.1, 1.2, 1a, 1b, 2.1 usw.) = die eigentlichen Fragen
- Die PUNKTZAHL steht oft RECHTS neben jeder Frage (z.B. "5" oder "8 Punkte")
- ANLAGEN/APPENDICES sind separate Dokumente (Tabellen, Angebote, Diagramme)

REGELN:
1. Jede AUFGABE = ein scenario (mit eigenem Szenario-Text)
2. Jede TEILAUFGABE = eine question (verknuepft mit dem Szenario ueber scenario_number)
3. MISCHE NIEMALS Szenarien verschiedener Aufgaben
4. question_number = ORIGINAL-Nummer aus der Pruefung (z.B. "1.1", "2.3", "3.2.1")
5. points = MUSS die echte Punktzahl sein (steht rechts). Wenn nicht lesbar: 5
6. Anlagen NICHT in den Szenario-Text einbetten, sondern in das anlagen-Array
7. Szenario-Text als HTML: <p>, <strong>, <ul>/<ol>
8. Anlagen-Inhalt als HTML: <table> fuer Tabellen, <p> fuer Text

JSON-FORMAT:
```json
{{
  "scenarios": [
    {{
      "number": 1,
      "title": "Firmenname oder Situationstitel",
      "context": "<p>VOLLSTAENDIGER Handlungssituation-Text...</p>",
      "context_html": true,
      "anlagen": [
        {{
          "name": "Anlage 1: Titel der Anlage",
          "content_html": "<table><thead>...</thead><tbody>...</tbody></table>"
        }}
      ]
    }}
  ],
  "questions": [
    {{
      "scenario_number": 1,
      "question_number": "1.1",
      "text": "Exakter Aufgabentext",
      "question_type": "essay",
      "points": 5,
      "topics": ["netzwerk"],
      "solution_text": ""
    }}
  ]
}}
```

question_type: mcq, essay, calculation, code, fill_blank, case_study, ordering, matching, short_answer
topics: projektmanagement, kalkulation, netzwerk, subnetting, ipv4, routing, firewall, vpn, wlan, dhcp, sql, datenbanken, erm, programmierung, python, java, html, json, xml, csv, it_sicherheit, datenschutz, dsgvo, virtualisierung, cloud, backup, raid, hardware, software, wirtschaft, vertragsrecht, arbeitsrecht, rechtsformen, qualitaetsmanagement, organisationsformen, energiekosten"""


def _build_vision_prompt(solution_text: str | None = None) -> str:
    """Build the Vision AI prompt for exam page analysis."""
    if not solution_text:
        return _VISION_PROMPT_BASE
    return (
        _VISION_PROMPT_BASE
        + "\n\n--- LOESUNGSHINWEISE ---\n"
        + solution_text
        + "\n--- ENDE LOESUNGSHINWEISE ---\n\n"
        "Nutze die Loesungshinweise um die Musterloesungen "
        "den Aufgaben zuzuordnen."
    )


def _parse_vision_response(response: str) -> dict | None:
    """Parse Vision AI JSON response."""
    import json
    import re

    if not response:
        return None

    # Try to extract JSON from markdown code block
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON object directly
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        logger.error("Failed to parse Vision AI response as JSON")
        return None
