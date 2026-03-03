"""
ExamArchive Service - Text Extraction (Part 2)

Text extraction functions for PDF and image files.
Split from archive_service.py for G01 compliance (<500 LOC).

- PDF: Extracted via PDFService
- Images (JPG/PNG): OCR via Vision-AI (provider from system config)
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


def resolve_vision_model() -> tuple:
    """
    Resolve vision-capable AI provider and model from system config.

    Fallback chain:
    1. Default 'vision' category model from DB
    2. Default 'chat' category model (GPT-4o, Gemini Pro support vision)
    3. Hardcoded fallback: openai/gpt-4o
    """
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
                    'Du bist ein OCR-Spezialist für IHK-Prüfungsbögen. '
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
                            'diesem IHK-Prüfungsfoto:'
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
