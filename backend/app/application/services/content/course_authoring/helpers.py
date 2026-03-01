"""
Helper utilities for course authoring service.
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DataHelpers:
    """Data parsing and extraction helpers."""

    @staticmethod
    def _strip_json_comments(json_str: str) -> str:
        """
        Strip JS-style comments from JSON string.

        Handles:
        - Single-line comments: // ...
        - Multi-line comments: /* ... */
        - Trailing commas before } or ]

        Does NOT strip inside quoted strings.
        """
        # Remove single-line comments (// ...) — but not inside strings
        # Strategy: match strings first to skip them, then remove comments
        result = []
        i = 0
        while i < len(json_str):
            # Skip quoted strings
            if json_str[i] == '"':
                j = i + 1
                while j < len(json_str):
                    if json_str[j] == '\\':
                        j += 2
                        continue
                    if json_str[j] == '"':
                        j += 1
                        break
                    j += 1
                result.append(json_str[i:j])
                i = j
            # Single-line comment
            elif json_str[i:i+2] == '//':
                # Skip to end of line
                end = json_str.find('\n', i)
                if end == -1:
                    break
                i = end
            # Multi-line comment
            elif json_str[i:i+2] == '/*':
                end = json_str.find('*/', i + 2)
                if end == -1:
                    break
                i = end + 2
            else:
                result.append(json_str[i])
                i += 1

        cleaned = ''.join(result)

        # Remove trailing commas before } or ]
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

        return cleaned

    @staticmethod
    def parse_ai_response(output: str) -> Tuple[str, Dict]:
        """
        Parst KI-Response in message und patch.

        Args:
            output: KI-Output text

        Returns:
            Tuple of (assistant_message, structure_patch)
            If JSON parsing fails, structure_patch will contain
            {'_parse_error': '...'} so callers can report the error.
        """
        assistant_message = output
        structure_patch = None

        try:
            json_str = None

            # Versuche JSON zu extrahieren
            if '```json' in output:
                start = output.find('```json') + 7
                end = output.find('```', start)
                if end > start:
                    json_str = output[start:end].strip()
            elif output.strip().startswith('{'):
                json_str = output.strip()

            if json_str:
                # Strip JS-style comments before parsing
                cleaned = DataHelpers._strip_json_comments(json_str)
                data = json.loads(cleaned)
                assistant_message = data.get('assistant_message', output[:500])
                structure_patch = data.get('structure_patch')

        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse AI response as JSON: {e}")
            # Preserve the assistant message from raw output if possible
            # and signal the parse error to the caller
            structure_patch = {'_parse_error': str(e)}
            # Try to extract a human-readable message from the raw text
            if '```json' in output:
                # Text before the JSON block might be a message
                before_json = output[:output.find('```json')].strip()
                if before_json:
                    assistant_message = before_json

        return assistant_message, structure_patch

    @staticmethod
    def format_history_for_prompt(
        history: List[Dict],
        max_chars: int = 6000,
        message_char_limit: int = 500
    ) -> str:
        """
        Formatiert Chat-History für Prompt mit Token-Budget.

        Newest messages get priority. Each message capped at message_char_limit.
        Total output capped at max_chars.

        Args:
            history: Chat history list
            max_chars: Max total chars for history
            message_char_limit: Max chars per individual message

        Returns:
            Formatted history string
        """
        if not history:
            return "Keine vorherigen Nachrichten."

        lines = []
        total_chars = 0

        for msg in reversed(history):
            role = 'Benutzer' if msg.get('role') == 'user' else 'Assistent'
            content = msg.get('content', '')[:message_char_limit]
            line = f"{role}: {content}"

            if total_chars + len(line) > max_chars:
                break

            lines.insert(0, line)
            total_chars += len(line)

        return "\n".join(lines) if lines else "Keine vorherigen Nachrichten."

    @staticmethod
    def extract_file_context(file_ids: List[str]) -> str:
        """
        Extrahiert Text-Kontext aus Dateien.

        Args:
            file_ids: List of file IDs

        Returns:
            Extracted file context string
        """
        try:
            from app.application.services.system.files.context import FileContextService
            return FileContextService.extract_for_ai_context(file_ids, 'course')
        except Exception as e:
            logger.warning(f"Could not extract file context: {e}")
            return ""


class ActivityLogGenerator:
    """Generates activity log entries for structure changes."""

    # Method type labels for human-readable output
    METHOD_LABELS = {
        'calculator_tutorial': 'Taschenrechner-Tutorial',
        'tool_tutorial': 'Tool-Tutorial',
        'step_by_step': 'Prozess-Anleitung',
        'theory': 'Theorieblatt',
        'quiz': 'Quiz',
        'flashcards': 'Karteikarten',
        'exercise': 'Übungsaufgabe',
        'exam': 'Prüfungssimulation',
        'interactive': 'Interaktive Übung',
        'video': 'Video-Lektion'
    }

    @staticmethod
    def generate_entry(
        operations: List[Dict],
        draft_structure: Dict
    ) -> Dict[str, Any]:
        """
        Generiert einen Activity-Log-Eintrag aus den angewandten Operationen.

        Args:
            operations: Liste der angewandten Operationen
            draft_structure: Aktuelle Draft-Struktur

        Returns:
            Activity-Log-Entry mit timestamp, summary, operations
        """
        op_summaries = []
        op_types = []

        for op in operations:
            op_type = op.get('op', '')
            data = op.get('data', {})
            op_types.append(op_type)

            # Zusammenfassung basierend auf Operation generieren
            summary = ActivityLogGenerator._summarize_operation(op_type, data)
            if summary:
                op_summaries.append(summary)

        # Zusammenfassung kombinieren
        if len(op_summaries) == 1:
            summary = op_summaries[0]
        elif len(op_summaries) <= 3:
            summary = "; ".join(op_summaries)
        else:
            summary = f"{len(op_summaries)} Änderungen durchgeführt"

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': summary,
            'operations': op_types,
            'details': op_summaries
        }

    @staticmethod
    def _summarize_operation(op_type: str, data: Dict) -> str:
        """Generate summary text for a single operation."""
        if op_type == 'add_chapter':
            title = data.get('title', 'Unbenanntes Kapitel')
            lessons_count = len(data.get('lessons', []))
            if lessons_count:
                return f"Kapitel '{title}' erstellt ({lessons_count} Lektionen)"
            return f"Kapitel '{title}' erstellt"

        elif op_type == 'update_chapter':
            title = data.get('title', '')
            return f"Kapitel '{title}' aktualisiert"

        elif op_type == 'delete_chapter':
            return "Kapitel gelöscht"

        elif op_type == 'add_lesson':
            title = data.get('title', 'Unbenannte Lektion')
            return f"Lektion '{title}' hinzugefügt"

        elif op_type == 'update_lesson':
            title = data.get('title', '')
            return f"Lektion '{title}' aktualisiert"

        elif op_type == 'delete_lesson':
            return "Lektion gelöscht"

        elif op_type == 'add_method':
            method_type = data.get('type', 'unknown')
            label = ActivityLogGenerator.METHOD_LABELS.get(method_type, method_type)
            return f"{label} hinzugefügt"

        elif op_type == 'update_method':
            return "Lernmethode aktualisiert"

        elif op_type == 'delete_method':
            return "Lernmethode gelöscht"

        return None
