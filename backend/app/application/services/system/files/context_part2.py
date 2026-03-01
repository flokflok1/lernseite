"""
LernsystemX File Context Service - Part 2

Higher-level file context operations:
- Multi-file context combining (get_file_context)
- AI prompt formatting (extract_for_ai_context)
- File preview (get_file_preview)
- File validation (validate_file)

Phase D4 - Universal KI-Authoring-System
"""

import io
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# DOCX Library
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from app.application.services.content.pdf import PDFService
from app.infrastructure.persistence.repositories.courses.content.files import CourseFileRepository

from .context import FileContextService, FileContextError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Extended methods for FileContextService
# ---------------------------------------------------------------------------
# These methods are added to the class via assignment at module load time,
# keeping the main context.py under 500 lines while preserving the single
# class interface for callers.
# ---------------------------------------------------------------------------


@classmethod
def get_file_context(
    cls,
    file_ids: List[str],
    max_length: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get combined text context from multiple files.

    Args:
        file_ids: List of file IDs from course_files table
        max_length: Optional max total character length

    Returns:
        Dict with:
        - combined_text: str (all files combined)
        - files: List of file info dicts
        - total_word_count: int
        - total_char_count: int
        - truncated: bool (if max_length exceeded)
    """
    if not file_ids:
        return {
            'combined_text': '',
            'files': [],
            'total_word_count': 0,
            'total_char_count': 0,
            'truncated': False
        }

    max_len = max_length or cls.MAX_CONTEXT_LENGTH
    files_info = []
    combined_parts = []
    total_chars = 0
    truncated = False

    for file_id in file_ids:
        try:
            # Get file from database
            file_record = CourseFileRepository.find_by_id(file_id)
            if not file_record:
                logger.warning(f"File not found: {file_id}")
                continue

            # Get file content
            file_path = file_record.get('file_path')
            filename = file_record.get('original_filename', 'unknown')

            if not file_path:
                logger.warning(f"No file path for: {file_id}")
                continue

            # Read file content
            try:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
            except FileNotFoundError:
                logger.warning(f"File not found on disk: {file_path}")
                continue

            # Extract text
            extraction = cls.extract_text(file_content, filename)
            text = extraction['text']

            # Check length limits
            if total_chars + len(text) > max_len:
                remaining = max_len - total_chars
                if remaining > 500:  # Only add if meaningful amount left
                    text = text[:remaining] + '\n\n[... Text abgeschnitten ...]'
                    extraction['char_count'] = remaining
                    truncated = True
                else:
                    truncated = True
                    break

            total_chars += len(text)

            # Add file header
            header = f"\n\n=== Datei: {filename} ===\n\n"
            combined_parts.append(header + text)

            files_info.append({
                'file_id': file_id,
                'filename': filename,
                'file_type': extraction['file_type'],
                'word_count': extraction['word_count'],
                'char_count': extraction['char_count'],
                'metadata': extraction.get('metadata', {})
            })

        except Exception as e:
            logger.error(f"Error processing file {file_id}: {str(e)}")
            files_info.append({
                'file_id': file_id,
                'filename': 'unknown',
                'error': str(e)
            })

    combined_text = ''.join(combined_parts).strip()

    return {
        'combined_text': combined_text,
        'files': files_info,
        'total_word_count': len(combined_text.split()),
        'total_char_count': len(combined_text),
        'truncated': truncated
    }


@classmethod
def extract_for_ai_context(
    cls,
    file_ids: List[str],
    context_type: str = 'general'
) -> str:
    """
    Extract and format file content for AI prompts.

    Args:
        file_ids: List of file IDs
        context_type: Type of context ('general', 'chapter', 'lesson', 'task')

    Returns:
        Formatted context string for AI prompts
    """
    context_data = cls.get_file_context(file_ids)

    if not context_data['combined_text']:
        return ""

    # Format header based on context type
    headers = {
        'general': "Referenz-Material",
        'chapter': "Kapitel-Quelldokumente",
        'lesson': "Lektions-Referenzmaterial",
        'task': "Aufgaben-Kontext"
    }

    header = headers.get(context_type, "Referenz-Material")

    # Build context string
    tag_name = header.lower().replace(' ', '_').replace('-', '_')
    parts = [f"<{tag_name}>"]

    # Add file summary
    if context_data['files']:
        parts.append(f"\nEnthaltene Dateien ({len(context_data['files'])}):")
        for f in context_data['files']:
            if 'error' not in f:
                parts.append(f"- {f['filename']} ({f['file_type']}, {f['word_count']} Wörter)")

    parts.append("\n--- Inhalt ---\n")
    parts.append(context_data['combined_text'])

    if context_data['truncated']:
        parts.append("\n\n[Hinweis: Text wurde aufgrund der Länge gekürzt]")

    parts.append(f"\n</{tag_name}>")

    return '\n'.join(parts)


@classmethod
def get_file_preview(
    cls,
    file_id: str,
    max_chars: int = 2000
) -> Dict[str, Any]:
    """
    Get a quick preview of a file.

    Args:
        file_id: File ID
        max_chars: Maximum characters for preview

    Returns:
        Dict with preview text and basic info
    """
    try:
        file_record = CourseFileRepository.find_by_id(file_id)
        if not file_record:
            return {'error': 'File not found', 'preview': ''}

        file_path = file_record.get('file_path')
        filename = file_record.get('original_filename', 'unknown')

        if not file_path:
            return {'error': 'No file path', 'preview': ''}

        with open(file_path, 'rb') as f:
            file_content = f.read()

        extraction = cls.extract_text(file_content, filename)
        text = extraction['text']

        preview = text[:max_chars]
        if len(text) > max_chars:
            preview += '\n\n[...]'

        return {
            'preview': preview,
            'filename': filename,
            'file_type': extraction['file_type'],
            'word_count': extraction['word_count'],
            'char_count': extraction['char_count'],
            'truncated': len(text) > max_chars
        }

    except Exception as e:
        logger.error(f"Preview error for {file_id}: {str(e)}")
        return {'error': str(e), 'preview': ''}


@classmethod
def validate_file(cls, file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Validate if a file can be processed.

    Args:
        file_content: Raw file bytes
        filename: Original filename

    Returns:
        Dict with:
        - valid: bool
        - file_type: str
        - error: Optional[str]
    """
    ext = Path(filename).suffix.lower()

    if ext not in cls.SUPPORTED_EXTENSIONS:
        return {
            'valid': False,
            'file_type': ext,
            'error': f"Unsupported file type. Supported: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
        }

    # Type-specific validation
    try:
        if ext == '.pdf':
            is_valid, error = PDFService.validate_pdf(file_content)
            return {
                'valid': is_valid,
                'file_type': 'pdf',
                'error': error
            }
        elif ext == '.docx':
            if not DOCX_AVAILABLE:
                return {
                    'valid': False,
                    'file_type': 'docx',
                    'error': 'DOCX support not available'
                }
            try:
                doc_file = io.BytesIO(file_content)
                DocxDocument(doc_file)
                return {'valid': True, 'file_type': 'docx', 'error': None}
            except Exception as e:
                return {
                    'valid': False,
                    'file_type': 'docx',
                    'error': f"Invalid DOCX file: {str(e)}"
                }
        else:
            # Text files - check if decodable
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    file_content.decode(encoding)
                    return {
                        'valid': True,
                        'file_type': 'txt' if ext == '.txt' else 'markdown',
                        'error': None
                    }
                except UnicodeDecodeError:
                    continue
            return {
                'valid': False,
                'file_type': 'txt',
                'error': 'Cannot decode text file'
            }

    except Exception as e:
        return {
            'valid': False,
            'file_type': ext,
            'error': str(e)
        }


# ---------------------------------------------------------------------------
# Attach methods to FileContextService
# ---------------------------------------------------------------------------
FileContextService.get_file_context = get_file_context
FileContextService.extract_for_ai_context = extract_for_ai_context
FileContextService.get_file_preview = get_file_preview
FileContextService.validate_file = validate_file
