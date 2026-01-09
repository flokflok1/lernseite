"""
LernsystemX - Authoring Action CRUD Operations

Database access for create, update, delete, and duplicate operations
on authoring actions used in KI-Studio.
"""

from typing import Optional, Dict, Any
import logging
import json

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, execute_query

logger = logging.getLogger(__name__)


class AuthoringActionCRUD(BaseRepository):
    """
    CRUD operations for authoring actions.

    Handles create, update, delete, and duplicate operations
    on actions stored in the database.
    """

    table_name = 'learning_methods.authoring_actions'
    pk_column = 'action_id'

    @staticmethod
    def create(action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new authoring action.

        Args:
            action_data: Action data dict with fields:
                - action_key: Unique identifier
                - category: Action category
                - label: Human-readable label
                - description: Description text
                - icon, color: UI properties
                - prompt_template: KI prompt template
                - mode: Execution mode
                - context_entity: Entity type (course, chapter, lesson, method)
                - requires_context: JSONB dict of required context
                - variables: JSONB list of template variables
                - action_type: Type of action (default: 'chat')
                - requires_confirmation: Boolean
                - confirmation_label: Confirmation button text
                - model: KI model name
                - provider: Provider (anthropic, openai, etc.)
                - temperature: KI temperature parameter
                - max_tokens: Maximum tokens to generate
                - output_format: Format of output (default: 'text')
                - output_entity: Output target entity type
                - output_schema: JSONB schema for output
                - lm_types: Array of learning method types
                - roles_allowed: Array of allowed roles
                - is_premium: Boolean
                - order_index: Display order (default: 0)
                - is_system: System action flag (default: False)
                - is_active: Active flag (default: True)
                - created_by: User ID who created

        Returns:
            Created action dict or None if creation failed
        """
        # Convert dict/list fields to JSONB
        requires_context = action_data.get('requires_context', {})
        if isinstance(requires_context, dict):
            requires_context = json.dumps(requires_context)

        variables = action_data.get('variables', [])
        if isinstance(variables, list):
            variables = json.dumps(variables)

        output_schema = action_data.get('output_schema')
        if output_schema and isinstance(output_schema, dict):
            output_schema = json.dumps(output_schema)

        lm_types = action_data.get('lm_types')
        roles_allowed = action_data.get('roles_allowed', ['admin', 'creator', 'teacher'])

        query = """
            INSERT INTO authoring_actions (
                action_key, category, label, description, icon, color,
                prompt_template, mode, context_entity, requires_context,
                variables, action_type, requires_confirmation, confirmation_label,
                model, provider, temperature, max_tokens,
                output_format, output_entity, output_schema,
                lm_types, roles_allowed, is_premium,
                order_index, is_system, is_active,
                created_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s
            )
            RETURNING *
        """
        params = (
            action_data.get('action_key'),
            action_data.get('category'),
            action_data.get('label'),
            action_data.get('description'),
            action_data.get('icon'),
            action_data.get('color'),
            action_data.get('prompt_template'),
            action_data.get('mode'),
            action_data.get('context_entity'),
            requires_context,
            variables,
            action_data.get('action_type', 'chat'),
            action_data.get('requires_confirmation', False),
            action_data.get('confirmation_label'),
            action_data.get('model'),
            action_data.get('provider'),
            action_data.get('temperature'),
            action_data.get('max_tokens'),
            action_data.get('output_format', 'text'),
            action_data.get('output_entity'),
            output_schema,
            lm_types,
            roles_allowed,
            action_data.get('is_premium', False),
            action_data.get('order_index', 0),
            action_data.get('is_system', False),
            action_data.get('is_active', True),
            action_data.get('created_by')
        )
        return fetch_one(query, params)

    @staticmethod
    def update(action_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing action.

        Note: System actions (is_system=true) cannot have their
        action_key changed.

        Args:
            action_id: Action UUID
            update_data: Fields to update. Allowed fields:
                - category, label, description, icon, color
                - prompt_template, mode, context_entity, requires_context
                - variables, action_type, requires_confirmation, confirmation_label
                - model, provider, temperature, max_tokens
                - output_format, output_entity, output_schema
                - lm_types, roles_allowed, is_premium
                - order_index, is_active
                - updated_by

        Returns:
            Updated action dict or None if not found
        """
        allowed_fields = [
            'category', 'label', 'description', 'icon', 'color',
            'prompt_template', 'mode', 'context_entity', 'requires_context',
            'variables', 'action_type', 'requires_confirmation', 'confirmation_label',
            'model', 'provider', 'temperature', 'max_tokens',
            'output_format', 'output_entity', 'output_schema',
            'lm_types', 'roles_allowed', 'is_premium',
            'order_index', 'is_active',
            'updated_by'
        ]

        set_clauses = []
        params = []

        for field in allowed_fields:
            if field in update_data:
                value = update_data[field]

                # Convert dict/list to JSON
                if field in ('requires_context', 'variables', 'output_schema') and isinstance(value, (dict, list)):
                    value = json.dumps(value)

                set_clauses.append(f"{field} = %s")
                params.append(value)

        if not set_clauses:
            # No fields to update, return current action
            from app.repositories.authoring_action.queries import AuthoringActionQueries
            return AuthoringActionQueries.find_by_id(action_id)

        params.append(action_id)

        query = f"""
            UPDATE learning_methods.authoring_actions
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE action_id = %s
            RETURNING *
        """
        return fetch_one(query, tuple(params))

    @staticmethod
    def delete(action_id: str) -> bool:
        """
        Delete an action (soft delete by setting is_active=false).

        System actions cannot be deleted.

        Args:
            action_id: Action UUID

        Returns:
            True if deleted, False if not found or system action
        """
        query = """
            UPDATE learning_methods.authoring_actions
            SET is_active = false, updated_at = NOW()
            WHERE action_id = %s AND is_system = false
            RETURNING action_id
        """
        result = fetch_one(query, (action_id,))
        return result is not None

    @staticmethod
    def duplicate(action_id: str, new_key: str, created_by: str = None) -> Optional[Dict[str, Any]]:
        """
        Duplicate an action with a new key.

        Creates a new action by copying all properties from the source
        action, with a new action_key and modified label (adds ' (Kopie)').

        Args:
            action_id: Source action UUID
            new_key: Key for the new action
            created_by: User ID creating the duplicate

        Returns:
            New action dict or None if source not found
        """
        query = """
            INSERT INTO authoring_actions (
                action_key, category, label, description, icon, color,
                prompt_template, mode, context_entity, requires_context,
                variables, action_type, requires_confirmation, confirmation_label,
                model, provider, temperature, max_tokens,
                output_format, output_entity, output_schema,
                lm_types, roles_allowed, is_premium,
                order_index, is_system, is_active,
                created_by
            )
            SELECT
                %s, category, label || ' (Kopie)', description, icon, color,
                prompt_template, mode, context_entity, requires_context,
                variables, action_type, requires_confirmation, confirmation_label,
                model, provider, temperature, max_tokens,
                output_format, output_entity, output_schema,
                lm_types, roles_allowed, is_premium,
                order_index + 1, false, true,
                %s
            FROM learning_methods.authoring_actions
            WHERE action_id = %s
            RETURNING *
        """
        return fetch_one(query, (new_key, created_by, action_id))
