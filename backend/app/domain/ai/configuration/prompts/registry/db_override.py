"""
LernsystemX KI - Prompt Registry DB Override

Database override logic for prompt templates.
"""

from typing import Dict
import json
from flask import current_app

from app.domain.ai.configuration.prompt_models import PromptTemplate, PromptMessage, PromptVariable


# Enable/disable DB override lookup (can be disabled for performance in tests)
DB_OVERRIDE_ENABLED: bool = True


def db_record_to_template(record: Dict) -> PromptTemplate:
    """
    Convert a database record to a PromptTemplate instance.

    The DB stores system_prompt and user_prompt_template separately,
    while PromptTemplate uses a messages list.

    Args:
        record: Database record dict

    Returns:
        PromptTemplate instance
    """
    # Build messages list from DB fields
    messages = []

    if record.get('system_prompt'):
        messages.append(PromptMessage(
            role='system',
            content=record['system_prompt']
        ))

    if record.get('user_prompt_template'):
        messages.append(PromptMessage(
            role='user',
            content=record['user_prompt_template']
        ))

    # Parse variables from JSONB
    variables_data = record.get('variables', [])
    if isinstance(variables_data, str):
        variables_data = json.loads(variables_data)

    variables = []
    for var in variables_data:
        variables.append(PromptVariable(
            name=var.get('name'),
            description=var.get('description', ''),
            required=var.get('required', True),
            default=var.get('default')
        ))

    # Build tags from category/style
    tags = [record.get('category', ''), record.get('style', '')]
    if record.get('tts_enabled'):
        tags.append('tts')

    return PromptTemplate(
        code=record['code'],
        title=record.get('title', record['code']),
        description=record.get('description', ''),
        version=record.get('version', 1),
        tags=tags,
        messages=messages,
        variables=variables,
        model=record.get('model'),
        max_tokens=record.get('max_tokens'),
        temperature=float(record.get('temperature', 0.7)),
        language_mode='target',
        allowed_roles=[],
        created_at=record.get('created_at'),
        updated_at=record.get('updated_at'),
        created_by=str(record.get('created_by')) if record.get('created_by') else 'system'
    )
