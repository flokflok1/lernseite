"""
Agent Organization Extensions Repository

Database access for organization-specific agent customizations:
- Organization-level agent configuration overrides
- Custom personas, languages, and terminology per org
- Context merging for effective agent configuration

ISO 9001:2015 compliant - Agent extension management
"""

import json
from typing import Dict, Any, Optional
from app.repositories.base_repository import BaseRepository


class AgentExtensionRepository(BaseRepository):
    """
    Repository for organization-specific agent extensions

    Tables:
    - agent_org_extensions: Organization customizations for agents
    """

    @staticmethod
    def get_org_extension(
        agent_id: str,
        organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get organization-specific agent extension

        Args:
            agent_id: Agent UUID
            organization_id: Organization UUID

        Returns:
            Extension data or None if not found
        """
        query = """
            SELECT
                extension_id,
                agent_id,
                organization_id,
                custom_persona,
                custom_language,
                custom_terminology,
                custom_examples,
                additional_context,
                blocked_topics,
                enabled,
                created_at,
                updated_at
            FROM agent_org_extensions
            WHERE agent_id = %s AND organization_id = %s
        """
        return AgentExtensionRepository.fetch_one(query, (agent_id, organization_id))

    @staticmethod
    def create_org_extension(
        agent_id: str,
        organization_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create organization-specific agent extension

        Args:
            agent_id: Agent UUID
            organization_id: Organization UUID
            **kwargs: Extension settings including:
                - custom_persona: Organization-specific agent persona
                - custom_language: Default language for org
                - custom_terminology: JSON of org-specific terms
                - custom_examples: JSON of org-specific examples
                - additional_context: Extra context for agent
                - blocked_topics: JSON list of topics to avoid

        Returns:
            Created extension data
        """
        query = """
            INSERT INTO agent_org_extensions (
                agent_id,
                organization_id,
                custom_persona,
                custom_language,
                custom_terminology,
                custom_examples,
                additional_context,
                blocked_topics
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """
        return AgentExtensionRepository.fetch_one(query, (
            agent_id,
            organization_id,
            kwargs.get('custom_persona'),
            kwargs.get('custom_language'),
            json.dumps(kwargs.get('custom_terminology', {})),
            json.dumps(kwargs.get('custom_examples', [])),
            kwargs.get('additional_context'),
            json.dumps(kwargs.get('blocked_topics', []))
        ))

    @staticmethod
    def update_org_extension(
        extension_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Update organization extension

        Args:
            extension_id: Extension UUID
            **kwargs: Fields to update (same keys as create_org_extension)

        Returns:
            Updated extension data or None if no valid updates
        """
        allowed_fields = {
            'custom_persona', 'custom_language', 'custom_terminology',
            'custom_examples', 'additional_context', 'blocked_topics', 'enabled'
        }

        updates = {}
        for k, v in kwargs.items():
            if k not in allowed_fields:
                continue
            if k in ('custom_terminology', 'custom_examples', 'blocked_topics'):
                updates[k] = json.dumps(v) if v else None
            else:
                updates[k] = v

        if not updates:
            return None

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        query = f"""
            UPDATE agent_org_extensions
            SET {set_clause}, updated_at = NOW()
            WHERE extension_id = %s
            RETURNING *
        """
        values = list(updates.values()) + [extension_id]
        return AgentExtensionRepository.fetch_one(query, tuple(values))

    @staticmethod
    def get_effective_agent_config(
        base_agent: Dict[str, Any],
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get effective agent configuration, merging base + org extension

        Combines base agent configuration with organization-specific
        overrides to produce the final configuration used for a course
        within an organization context.

        Args:
            base_agent: Base agent configuration dict
            organization_id: Optional organization UUID for merging extensions

        Returns:
            Merged agent configuration with organization overrides applied
        """
        config = {
            'agent_id': base_agent['agent_id'],
            'course_id': base_agent['course_id'],
            'name': base_agent['name'],
            'persona': base_agent['persona'],
            'language': base_agent['language'],
            'primary_provider': base_agent['primary_provider'],
            'primary_model': base_agent['primary_model'],
            'temperature': float(base_agent['temperature']) if base_agent['temperature'] else 0.7,
            'max_tokens': base_agent['max_tokens'],
            'knowledge_status': base_agent['knowledge_status'],
            'custom_terminology': {},
            'blocked_topics': []
        }

        # Merge organization extension if available
        if organization_id:
            ext = AgentExtensionRepository.get_org_extension(
                base_agent['agent_id'],
                organization_id
            )
            if ext and ext.get('enabled', True):
                if ext.get('custom_persona'):
                    config['persona'] = ext['custom_persona']
                if ext.get('custom_language'):
                    config['language'] = ext['custom_language']
                if ext.get('custom_terminology'):
                    config['custom_terminology'] = ext['custom_terminology']
                if ext.get('blocked_topics'):
                    config['blocked_topics'] = ext['blocked_topics']
                if ext.get('additional_context'):
                    config['additional_context'] = ext['additional_context']

        return config
