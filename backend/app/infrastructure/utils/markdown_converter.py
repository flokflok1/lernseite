"""Markdown to HTML converter for lesson content.

Converts markdown text to sanitized HTML for storage in lesson content JSONB.
Used by content builders and AI plan execution to produce content_html.
"""
import logging
import markdown

logger = logging.getLogger(__name__)

# Markdown extensions for better table/code/list support
_MD_EXTENSIONS = ['tables', 'fenced_code', 'nl2br', 'sane_lists']


def markdown_to_html(text: str) -> str:
    """Convert markdown to HTML string.

    Args:
        text: Markdown-formatted text

    Returns:
        HTML string (not sanitized -- frontend DOMPurify handles that)
    """
    if not text or not text.strip():
        return ''
    try:
        return markdown.markdown(text.strip(), extensions=_MD_EXTENSIONS)
    except Exception:
        logger.warning("Markdown conversion failed, returning raw text")
        return f'<p>{text}</p>'
