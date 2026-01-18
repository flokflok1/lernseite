"""
Preview Generation for Authoring Service

Handles:
- HTML/Markdown preview generation
- Content formatting for preview
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PreviewGenerator:
    """Generate previews of generated content."""

    @staticmethod
    def generate(
        content_type: str,
        generated_content: Dict[str, Any],
        format_type: str = 'html'
    ) -> Dict[str, Any]:
        """
        Generate preview of content without saving.

        Args:
            content_type: Type of content (chapter_theory, lesson_explanation, etc.)
            generated_content: Generated content data
            format_type: Output format (html, markdown, json)

        Returns:
            Dict with preview HTML/Markdown/JSON
        """
        if content_type == 'chapter_theory':
            return PreviewGenerator._preview_chapter_theory(generated_content, format_type)
        elif content_type == 'lesson_explanation':
            return PreviewGenerator._preview_lesson_explanation(generated_content, format_type)
        elif content_type == 'task':
            return PreviewGenerator._preview_task(generated_content, format_type)
        elif content_type == 'learning_method':
            return PreviewGenerator._preview_learning_method(generated_content, format_type)
        else:
            return {
                'preview': json.dumps(generated_content, indent=2, ensure_ascii=False),
                'format': 'json'
            }

    @staticmethod
    def _preview_chapter_theory(content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for chapter theory."""
        if format_type == 'html':
            html = ['<div class="chapter-theory-preview">']

            if content.get('overview'):
                html.append(
                    f'<div class="overview"><h3>Übersicht</h3><p>{content["overview"]}</p></div>'
                )

            if content.get('learningGoals'):
                html.append('<div class="learning-goals"><h3>Lernziele</h3><ul>')
                for goal in content['learningGoals']:
                    html.append(f'<li>{goal}</li>')
                html.append('</ul></div>')

            if content.get('concepts'):
                html.append('<div class="concepts"><h3>Konzepte</h3>')
                for concept in content['concepts']:
                    emoji = concept.get('emoji', '')
                    title = concept.get('title', '')
                    html.append(f'<div class="concept"><h4>{emoji} {title}</h4>')
                    description = concept.get('description', concept.get('oneLiner', ''))
                    html.append(f'<p>{description}</p>')
                    if concept.get('formula'):
                        html.append(f'<code class="formula">{concept["formula"]}</code>')
                    html.append('</div>')
                html.append('</div>')

            if content.get('terms'):
                html.append('<div class="terms"><h3>Begriffe</h3><dl>')
                for term in content['terms']:
                    term_text = term.get('term', '')
                    definition = term.get('simple', term.get('definition', ''))
                    html.append(f'<dt>{term_text}</dt>')
                    html.append(f'<dd>{definition}</dd>')
                html.append('</dl></div>')

            html.append('</div>')
            return {'preview': '\n'.join(html), 'format': 'html'}
        else:
            return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}

    @staticmethod
    def _preview_lesson_explanation(content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for lesson explanation."""
        if format_type == 'html':
            html = ['<div class="lesson-explanation-preview">']

            if content.get('steps'):
                html.append('<div class="steps">')
                for i, step in enumerate(content['steps'], 1):
                    title = step.get('title', '')
                    html.append(f'<div class="step"><h4>Schritt {i}: {title}</h4>')
                    speech = step.get('speech', '')
                    html.append(f'<p class="speech">{speech}</p>')
                    if step.get('calculator'):
                        calc = step['calculator']
                        result = step.get('result', '')
                        html.append(f'<code class="calculator">{calc} = {result}</code>')
                    html.append('</div>')
                html.append('</div>')

            html.append('</div>')
            return {'preview': '\n'.join(html), 'format': 'html'}
        else:
            return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}

    @staticmethod
    def _preview_task(content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for task."""
        if format_type == 'html':
            html = ['<div class="task-preview">']

            if content.get('title'):
                html.append(f'<h3>{content["title"]}</h3>')

            if content.get('description'):
                html.append(f'<div class="description">{content["description"]}</div>')

            if content.get('instructions'):
                instructions = content["instructions"]
                html.append(
                    f'<div class="instructions"><strong>Aufgabe:</strong> {instructions}</div>'
                )

            html.append('</div>')
            return {'preview': '\n'.join(html), 'format': 'html'}
        else:
            return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}

    @staticmethod
    def _preview_learning_method(content: Dict, format_type: str) -> Dict[str, Any]:
        """Generate preview for learning method."""
        return {'preview': json.dumps(content, indent=2, ensure_ascii=False), 'format': 'json'}
