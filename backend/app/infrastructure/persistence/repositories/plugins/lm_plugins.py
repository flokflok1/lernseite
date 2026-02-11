"""
Learning Methods Plugin Repository
Handles database operations for LM plugins.
"""
from typing import Optional, List, Dict
from datetime import datetime
from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class LMPluginRepository(BaseRepository):
    """Repository for Learning Method Plugins."""

    table_name = "learning_methods.lm_plugins"

    @staticmethod
    def find_by_id(plugin_id: str) -> Optional[Dict]:
        """
        Find plugin by ID.

        Args:
            plugin_id: Plugin UUID

        Returns:
            Plugin dict or None
        """
        query = f"""
            SELECT * FROM {LMPluginRepository.table_name}
            WHERE plugin_id = %s
        """
        return fetch_one(query, (plugin_id,))

    @staticmethod
    def find_by_code(plugin_code: str) -> Optional[Dict]:
        """
        Find plugin by unique code.

        Args:
            plugin_code: Plugin identifier

        Returns:
            Plugin dict or None
        """
        query = f"""
            SELECT * FROM {LMPluginRepository.table_name}
            WHERE plugin_code = %s
        """
        return fetch_one(query, (plugin_code,))

    @staticmethod
    def get_active_plugins() -> List[Dict]:
        """
        Get all active plugins (approved + is_active=true).

        Returns:
            List of active plugin dicts
        """
        query = f"""
            SELECT * FROM {LMPluginRepository.table_name}
            WHERE approval_status = 'approved' AND is_active = TRUE
            ORDER BY created_at DESC
        """
        return fetch_all(query)

    @staticmethod
    def get_pending_plugins() -> List[Dict]:
        """
        Get all plugins pending review.

        Returns:
            List of pending plugin dicts
        """
        query = f"""
            SELECT * FROM {LMPluginRepository.table_name}
            WHERE approval_status = 'pending_review'
            ORDER BY submitted_at DESC
        """
        return fetch_all(query)

    @staticmethod
    def approve_plugin(plugin_id: str, reviewed_by: str) -> bool:
        """
        Approve a plugin (change status to 'approved').

        Args:
            plugin_id: Plugin UUID
            reviewed_by: Reviewer user UUID

        Returns:
            Success boolean
        """
        query = f"""
            UPDATE {LMPluginRepository.table_name}
            SET approval_status = 'approved',
                reviewed_by = %s,
                reviewed_at = %s,
                updated_at = %s
            WHERE plugin_id = %s AND approval_status = 'pending_review'
        """
        now = datetime.utcnow()
        affected = execute_query(query, (reviewed_by, now, now, plugin_id))

        # Log approval history
        if affected > 0:
            LMPluginRepository._log_approval_action(plugin_id, 'approved', reviewed_by, None)

        return affected > 0

    @staticmethod
    def reject_plugin(plugin_id: str, reviewed_by: str, reason: str) -> bool:
        """
        Reject a plugin (change status to 'rejected').

        Args:
            plugin_id: Plugin UUID
            reviewed_by: Reviewer user UUID
            reason: Rejection reason

        Returns:
            Success boolean
        """
        query = f"""
            UPDATE {LMPluginRepository.table_name}
            SET approval_status = 'rejected',
                reviewed_by = %s,
                reviewed_at = %s,
                updated_at = %s
            WHERE plugin_id = %s
        """
        now = datetime.utcnow()
        affected = execute_query(query, (reviewed_by, now, now, plugin_id))

        # Log rejection history
        if affected > 0:
            LMPluginRepository._log_approval_action(plugin_id, 'rejected', reviewed_by, reason)

        return affected > 0

    @staticmethod
    def activate_plugin(plugin_id: str, actor_id: str) -> bool:
        """
        Activate an approved plugin (set is_active=true).

        Args:
            plugin_id: Plugin UUID
            actor_id: Actor user UUID

        Returns:
            Success boolean
        """
        query = f"""
            UPDATE {LMPluginRepository.table_name}
            SET is_active = TRUE,
                activated_at = %s,
                updated_at = %s
            WHERE plugin_id = %s AND approval_status = 'approved'
        """
        now = datetime.utcnow()
        affected = execute_query(query, (now, now, plugin_id))

        # Log activation history
        if affected > 0:
            LMPluginRepository._log_approval_action(plugin_id, 'activated', actor_id, None)

        return affected > 0

    @staticmethod
    def deactivate_plugin(plugin_id: str, actor_id: str) -> bool:
        """
        Deactivate a plugin (set is_active=false).

        Args:
            plugin_id: Plugin UUID
            actor_id: Actor user UUID

        Returns:
            Success boolean
        """
        query = f"""
            UPDATE {LMPluginRepository.table_name}
            SET is_active = FALSE,
                updated_at = %s
            WHERE plugin_id = %s
        """
        now = datetime.utcnow()
        affected = execute_query(query, (now, plugin_id))

        # Log deactivation history
        if affected > 0:
            LMPluginRepository._log_approval_action(plugin_id, 'deactivated', actor_id, None)

        return affected > 0

    @staticmethod
    def is_plugin_in_use(plugin_id: str) -> bool:
        """
        Check if plugin is used in any lessons.

        Args:
            plugin_id: Plugin UUID

        Returns:
            True if plugin is in use
        """
        query = """
            SELECT COUNT(*) as count
            FROM learning_methods.lm_plugin_usage
            WHERE plugin_id = %s
        """
        result = fetch_one(query, (plugin_id,))
        return result['count'] > 0 if result else False

    @staticmethod
    def update_file_hash(plugin_code: str, file_hash: str) -> bool:
        """
        Update file hash for existing plugin.

        Args:
            plugin_code: Plugin code
            file_hash: New file hash

        Returns:
            Success boolean
        """
        query = """
            UPDATE learning_methods.lm_plugins
            SET file_hash = %s, updated_at = NOW()
            WHERE plugin_code = %s
        """
        affected = execute_query(query, (file_hash, plugin_code))
        return affected > 0

    @staticmethod
    def insert_plugin(plugin_data: Dict) -> Optional[str]:
        """
        Insert new plugin and return plugin_id.

        Args:
            plugin_data: Plugin data dictionary with all required fields

        Returns:
            Plugin UUID or None
        """
        query = """
            INSERT INTO learning_methods.lm_plugins
            (plugin_code, name, description, group_code, tier, ki_usage, icon,
             config_schema, default_config, agent_support, prompt_template,
             file_path, file_hash, submitted_by, approval_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s, 'pending_review')
            RETURNING plugin_id
        """

        result = fetch_one(query, (
            plugin_data['plugin_code'],
            plugin_data['name'],
            plugin_data.get('description'),
            plugin_data['group_code'],
            plugin_data['tier'],
            plugin_data['ki_usage'],
            plugin_data['icon'],
            plugin_data['config_schema'],
            plugin_data.get('default_config'),
            plugin_data.get('agent_support'),
            plugin_data.get('prompt_template'),
            plugin_data['file_path'],
            plugin_data['file_hash'],
            plugin_data['submitted_by']
        ))

        return result['plugin_id'] if result else None

    @staticmethod
    def _log_approval_action(plugin_id: str, action: str, actor_id: str, reason: Optional[str]):
        """Log approval action to history table."""
        query = """
            INSERT INTO learning_methods.lm_plugin_approval_history
            (plugin_id, action, actor_id, reason)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(query, (plugin_id, action, actor_id, reason))
