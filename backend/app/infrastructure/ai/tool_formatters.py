"""
Tool Schema Formatters — Konvertiert provider-agnostische Tool-Definitionen
in das Format des jeweiligen AI Providers.

Die Tool-Definitionen kommen aus der Domain (domain/ai/tool_definitions.py).
Hier wird nur das FORMAT konvertiert, nicht die Semantik.

DDD-Layer: Infrastructure (Provider-spezifische Transformation)
"""

import json
from typing import Dict, List


def to_openai_tools(tools: List[Dict]) -> List[Dict]:
    """
    Konvertiert in OpenAI Function Calling Format.

    OpenAI erwartet:
    [{
        "type": "function",
        "function": {
            "name": "...",
            "description": "...",
            "parameters": { JSON Schema }
        }
    }]
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool["parameters"]
            }
        }
        for tool in tools
    ]


def to_anthropic_tools(tools: List[Dict]) -> List[Dict]:
    """
    Konvertiert in Anthropic Tool Use Format.

    Anthropic erwartet:
    [{
        "name": "...",
        "description": "...",
        "input_schema": { JSON Schema }
    }]
    """
    return [
        {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "input_schema": tool["parameters"]
        }
        for tool in tools
    ]


def to_google_tools(tools: List[Dict]) -> List[Dict]:
    """
    Konvertiert in Google Gemini Function Calling Format.

    Google erwartet:
    [{
        "function_declarations": [{
            "name": "...",
            "description": "...",
            "parameters": { JSON Schema }
        }]
    }]

    Hinweis: Google gruppiert alle Declarations in einem Tool-Objekt.
    """
    return [{
        "function_declarations": [
            {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool["parameters"]
            }
            for tool in tools
        ]
    }]


def normalize_tool_calls(provider: str, raw_response: Dict) -> tuple:
    """
    Extrahiert Text + Tool Calls aus der provider-spezifischen Response.

    Returns:
        (output_text: str, tool_calls: list[{name, arguments}])
    """
    if provider == 'openai':
        return _normalize_openai(raw_response)
    elif provider == 'anthropic':
        return _normalize_anthropic(raw_response)
    elif provider == 'google':
        return _normalize_google(raw_response)
    else:
        return raw_response.get('output_text', ''), []


def _normalize_openai(data: Dict) -> tuple:
    """
    OpenAI Response:
    choices[0].message.content = Text
    choices[0].message.tool_calls = [{id, type, function: {name, arguments: JSON-String}}]
    """
    message = data.get('message', {})
    text = message.get('content', '') or ''
    raw_calls = message.get('tool_calls', []) or []

    tool_calls = []
    for call in raw_calls:
        func = call.get('function', {})
        name = func.get('name', '')
        args_str = func.get('arguments', '{}')
        try:
            arguments = json.loads(args_str) if isinstance(args_str, str) else args_str
        except json.JSONDecodeError:
            arguments = {}
        tool_calls.append({'name': name, 'arguments': arguments})

    return text, tool_calls


def _normalize_anthropic(data: Dict) -> tuple:
    """
    Anthropic Response:
    content = [{type: "text", text: "..."}, {type: "tool_use", id, name, input: {dict}}]
    """
    content_blocks = data.get('content', [])
    text_parts = []
    tool_calls = []

    for block in content_blocks:
        if block.get('type') == 'text':
            text_parts.append(block.get('text', ''))
        elif block.get('type') == 'tool_use':
            tool_calls.append({
                'name': block.get('name', ''),
                'arguments': block.get('input', {})
            })

    return ' '.join(text_parts), tool_calls


def _normalize_google(data: Dict) -> tuple:
    """
    Google Response:
    candidates[0].content.parts = [{text: "..."}, {functionCall: {name, args: {dict}}}]
    """
    parts = data.get('parts', [])
    text_parts = []
    tool_calls = []

    for part in parts:
        if 'text' in part:
            text_parts.append(part['text'])
        elif 'functionCall' in part:
            fc = part['functionCall']
            tool_calls.append({
                'name': fc.get('name', ''),
                'arguments': fc.get('args', {})
            })

    return ' '.join(text_parts), tool_calls
