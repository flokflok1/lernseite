"""
LernsystemX - Authoring Action Repository

Database access for dynamic authoring actions (Quick-Actions).
Replaces hardcoded buttons in KI-Studio with DB-driven actions.
Enables flexible, extensible action management for bots/agents.

Phase: DB-Zentriertes KI-Authoring
"""

from typing import Optional, List, Dict, Any
import logging
import json

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class AuthoringActionRepository(BaseRepository):
    """
    Repository for authoring actions stored in database.

    Provides CRUD operations for Quick-Actions used in KI-Studio.
    Actions are categorized by context (course_builder, chat, chapter, lesson, method).
    """

    table_name = 'authoring_actions'
    pk_column = 'action_id'

    @staticmethod
    def find_by_key(action_key: str) -> Optional[Dict[str, Any]]:
        """
        Find an action by its unique key.

        Args:
            action_key: Unique action identifier (e.g., 'structure_suggest')

        Returns:
            Action dict or None if not found
        """
        query = """
            SELECT *
            FROM authoring_actions
            WHERE action_key = %s AND is_active = true
        """
        return fetch_one(query, (action_key,))

    @staticmethod
    def find_by_id(action_id: str) -> Optional[Dict[str, Any]]:
        """Find an action by its UUID."""
        query = """
            SELECT *
            FROM authoring_actions
            WHERE action_id = %s
        """
        return fetch_one(query, (action_id,))

    @staticmethod
    def get_by_category(category: str, roles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active actions for a specific category.

        Args:
            category: Action category ('course_builder', 'chat', 'chapter', 'lesson', 'method', 'content')
            roles: Optional list of user roles to filter by (checks roles_allowed)

        Returns:
            List of actions for this category, ordered by order_index
        """
        if roles:
            # Filter by roles if provided
            query = """
                SELECT
                    action_id, action_key, category, label, description, icon, color,
                    prompt_template, mode, context_entity, requires_context,
                    action_type, requires_confirmation, confirmation_label,
                    output_format, output_entity, lm_types,
                    is_premium, order_index, is_system
                FROM authoring_actions
                WHERE category = %s
                  AND is_active = true
                  AND (roles_allowed IS NULL OR roles_allowed && %s)
                ORDER BY order_index, label
            """
            return fetch_all(query, (category, roles))
        else:
            query = """
                SELECT
                    action_id, action_key, category, label, description, icon, color,
                    prompt_template, mode, context_entity, requires_context,
                    action_type, requires_confirmation, confirmation_label,
                    output_format, output_entity, lm_types,
                    is_premium, order_index, is_system
                FROM authoring_actions
                WHERE category = %s AND is_active = true
                ORDER BY order_index, label
            """
            return fetch_all(query, (category,))

    @staticmethod
    def get_all_active(roles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active actions, grouped by category.

        Args:
            roles: Optional list of user roles to filter by

        Returns:
            List of all active actions, ordered by category and order_index
        """
        if roles:
            query = """
                SELECT
                    action_id, action_key, category, label, description, icon, color,
                    prompt_template, mode, context_entity, requires_context,
                    action_type, requires_confirmation, confirmation_label,
                    output_format, output_entity, lm_types,
                    is_premium, order_index, is_system
                FROM authoring_actions
                WHERE is_active = true
                  AND (roles_allowed IS NULL OR roles_allowed && %s)
                ORDER BY category, order_index, label
            """
            return fetch_all(query, (roles,))
        else:
            query = """
                SELECT
                    action_id, action_key, category, label, description, icon, color,
                    prompt_template, mode, context_entity, requires_context,
                    action_type, requires_confirmation, confirmation_label,
                    output_format, output_entity, lm_types,
                    is_premium, order_index, is_system
                FROM authoring_actions
                WHERE is_active = true
                ORDER BY category, order_index, label
            """
            return fetch_all(query)

    @staticmethod
    def get_by_context_entity(entity: str) -> List[Dict[str, Any]]:
        """
        Get actions that apply to a specific entity type.

        Args:
            entity: Entity type ('course', 'chapter', 'lesson', 'method')

        Returns:
            List of actions for this entity
        """
        query = """
            SELECT
                action_id, action_key, category, label, description, icon, color,
                prompt_template, mode, context_entity, requires_context,
                action_type, requires_confirmation, confirmation_label,
                output_format, output_entity, lm_types,
                is_premium, order_index, is_system
            FROM authoring_actions
            WHERE context_entity = %s AND is_active = true
            ORDER BY order_index, label
        """
        return fetch_all(query, (entity,))

    @staticmethod
    def get_by_lm_type(lm_type: int) -> List[Dict[str, Any]]:
        """
        Get actions that apply to a specific learning method type.

        Args:
            lm_type: Learning method type (0-32)

        Returns:
            List of actions for this LM type
        """
        query = """
            SELECT
                action_id, action_key, category, label, description, icon, color,
                prompt_template, mode, context_entity, requires_context,
                action_type, requires_confirmation, confirmation_label,
                output_format, output_entity, lm_types,
                is_premium, order_index, is_system
            FROM authoring_actions
            WHERE (lm_types IS NULL OR %s = ANY(lm_types))
              AND is_active = true
            ORDER BY order_index, label
        """
        return fetch_all(query, (lm_type,))

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """
        Get list of all categories with action counts.

        Returns:
            List of categories with counts
        """
        query = """
            SELECT
                category,
                COUNT(*) as action_count,
                COUNT(CASE WHEN is_system THEN 1 END) as system_count
            FROM authoring_actions
            WHERE is_active = true
            GROUP BY category
            ORDER BY category
        """
        return fetch_all(query)

    @staticmethod
    def create(action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new authoring action.

        Args:
            action_data: Action data dict

        Returns:
            Created action or None
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
            update_data: Fields to update

        Returns:
            Updated action or None
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
            return AuthoringActionRepository.find_by_id(action_id)

        params.append(action_id)

        query = f"""
            UPDATE authoring_actions
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
            UPDATE authoring_actions
            SET is_active = false, updated_at = NOW()
            WHERE action_id = %s AND is_system = false
            RETURNING action_id
        """
        result = fetch_one(query, (action_id,))
        return result is not None

    @staticmethod
    def log_usage(
        action_id: str,
        user_id: str,
        session_id: str = None,
        context_data: Dict = None,
        was_successful: bool = True,
        was_confirmed: bool = None,
        result_entity_id: str = None,
        tokens_input: int = None,
        tokens_output: int = None,
        cost_eur: float = None,
        response_time_ms: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Log action usage for analytics.

        Args:
            action_id: Action used
            user_id: User who used it
            session_id: Optional authoring session ID
            context_data: Context when action was triggered
            was_successful: Whether the action succeeded
            was_confirmed: Whether user confirmed (if confirmation required)
            result_entity_id: ID of created/modified entity
            tokens_input: Input tokens used
            tokens_output: Output tokens generated
            cost_eur: Total cost
            response_time_ms: Generation time

        Returns:
            Usage record or None
        """
        tokens_total = None
        if tokens_input is not None and tokens_output is not None:
            tokens_total = tokens_input + tokens_output

        context_json = json.dumps(context_data) if context_data else None

        query = """
            INSERT INTO authoring_action_usage (
                action_id, user_id, session_id, context_data,
                was_successful, was_confirmed, result_entity_id,
                tokens_input, tokens_output, tokens_total,
                cost_eur, response_time_ms
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            RETURNING usage_id
        """
        return fetch_one(query, (
            action_id, user_id, session_id, context_json,
            was_successful, was_confirmed, result_entity_id,
            tokens_input, tokens_output, tokens_total,
            cost_eur, response_time_ms
        ))

    @staticmethod
    def get_usage_stats(action_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics for an action or all actions.

        Args:
            action_id: Optional action to filter by
            days: Number of days to look back

        Returns:
            Statistics dict
        """
        if action_id:
            query = """
                SELECT
                    COUNT(*) as total_uses,
                    COUNT(CASE WHEN was_successful THEN 1 END) as successful_uses,
                    COUNT(CASE WHEN was_confirmed THEN 1 END) as confirmed_uses,
                    SUM(tokens_total) as total_tokens,
                    SUM(cost_eur) as total_cost,
                    AVG(response_time_ms) as avg_response_time
                FROM authoring_action_usage
                WHERE action_id = %s
                  AND created_at >= NOW() - INTERVAL '%s days'
            """
            result = fetch_one(query, (action_id, days))
        else:
            query = """
                SELECT
                    COUNT(*) as total_uses,
                    COUNT(CASE WHEN was_successful THEN 1 END) as successful_uses,
                    COUNT(CASE WHEN was_confirmed THEN 1 END) as confirmed_uses,
                    SUM(tokens_total) as total_tokens,
                    SUM(cost_eur) as total_cost,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(DISTINCT action_id) as actions_used,
                    COUNT(DISTINCT user_id) as unique_users
                FROM authoring_action_usage
                WHERE created_at >= NOW() - INTERVAL '%s days'
            """
            result = fetch_one(query, (days,))

        return result or {}

    @staticmethod
    def get_popular_actions(limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get most popular actions by usage.

        Args:
            limit: Maximum number of actions to return
            days: Number of days to look back

        Returns:
            List of popular actions with usage counts
        """
        query = """
            SELECT
                a.action_id, a.action_key, a.category, a.label, a.icon,
                COUNT(u.usage_id) as usage_count,
                COUNT(CASE WHEN u.was_successful THEN 1 END) as success_count
            FROM authoring_actions a
            LEFT JOIN authoring_action_usage u ON a.action_id = u.action_id
                AND u.created_at >= NOW() - INTERVAL '%s days'
            WHERE a.is_active = true
            GROUP BY a.action_id, a.action_key, a.category, a.label, a.icon
            ORDER BY usage_count DESC
            LIMIT %s
        """
        return fetch_all(query, (days, limit))

    @staticmethod
    def duplicate(action_id: str, new_key: str, created_by: str = None) -> Optional[Dict[str, Any]]:
        """
        Duplicate an action with a new key.

        Args:
            action_id: Source action UUID
            new_key: Key for the new action
            created_by: User ID creating the duplicate

        Returns:
            New action or None
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
            FROM authoring_actions
            WHERE action_id = %s
            RETURNING *
        """
        return fetch_one(query, (new_key, created_by, action_id))

    @staticmethod
    def reorder(category: str, order_updates: List[Dict[str, Any]]) -> bool:
        """
        Update order_index for multiple actions.

        Args:
            category: Category to reorder
            order_updates: List of {"action_id": str, "order_index": int}

        Returns:
            True if successful
        """
        for update in order_updates:
            query = """
                UPDATE authoring_actions
                SET order_index = %s, updated_at = NOW()
                WHERE action_id = %s AND category = %s
            """
            execute_query(query, (update['order_index'], update['action_id'], category))

        return True
