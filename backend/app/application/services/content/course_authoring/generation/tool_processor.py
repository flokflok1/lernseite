"""
Tool Call Processor — Wandelt KI Tool Calls in Operations um.

Konvertiert das normalisierte Tool-Call-Format
  [{name: "add_chapter", arguments: {title: "..."}}]
in das bestehende Operations-Format für StructureOperations:
  [{op: "add_chapter", data: {title: "..."}, chapter_id: "..."}]

DDD-Layer: Application (Orchestrierung)
"""

import logging
from typing import Dict, List

from app.domain.ai.tool_definitions import TOOL_NAMES

logger = logging.getLogger(__name__)

# Felder die von arguments auf Operation-Ebene gehoben werden
# (chapter_id, lesson_id, method_id stehen auf der Op, nicht in data)
LIFT_FIELDS = {
    'update_chapter': ['chapter_id'],
    'delete_chapter': ['chapter_id'],
    'add_lesson': ['chapter_id'],
    'update_lesson': ['lesson_id'],
    'delete_lesson': ['lesson_id'],
    'add_method': ['lesson_id'],
    'update_method': ['method_id'],
    'delete_method': ['method_id'],
    'reorder_lessons': ['chapter_id'],
}


class ToolCallProcessor:
    """Konvertiert AI Tool Calls in Operations für StructureOperations."""

    @staticmethod
    def to_operations(tool_calls: List[Dict]) -> List[Dict]:
        """
        Wandelt Tool Calls in Operations um.

        Args:
            tool_calls: [{name: str, arguments: dict}, ...]
                Normalisiertes Format (provider-agnostisch)

        Returns:
            [{op: str, data: dict, chapter_id?: str, lesson_id?: str}, ...]
                Format für StructureOperations.apply_operations()
        """
        operations = []

        for call in tool_calls:
            name = call.get('name', '')
            arguments = call.get('arguments', {})

            if name not in TOOL_NAMES:
                logger.warning(f"Unknown tool call '{name}', skipping")
                continue

            if not isinstance(arguments, dict):
                logger.warning(f"Tool '{name}' has non-dict arguments, skipping")
                continue

            op = ToolCallProcessor._convert_single(name, arguments)
            if op:
                operations.append(op)

        logger.info(
            f"Converted {len(tool_calls)} tool calls to "
            f"{len(operations)} operations"
        )
        return operations

    @staticmethod
    def _convert_single(name: str, arguments: Dict) -> Dict:
        """Konvertiert einen einzelnen Tool Call in eine Operation."""
        operation = {'op': name}
        data = {}

        # ID-Felder auf Operation-Ebene heben
        lift = LIFT_FIELDS.get(name, [])
        for field in lift:
            if field in arguments:
                operation[field] = arguments[field]

        # Rest geht in data (ohne die gehobenen Felder)
        for key, value in arguments.items():
            if key not in lift:
                data[key] = value

        operation['data'] = data
        return operation
