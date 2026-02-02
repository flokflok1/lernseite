"""
Organization-Based Rollout

Enable features for specific organizations (schools, companies)
"""

from typing import List, Optional
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class OrganizationRolloutRepository(BaseRepository):
    """Repository for organisation rollout"""
    
    @staticmethod
    def is_org_enabled(feature_name: str, organisation_id: str) -> Optional[bool]:
        """Check if feature is explicitly enabled/disabled for organisation"""
        query = """
            SELECT is_enabled 
            FROM feature_flags.organisation_rollout
            WHERE feature_name = %s AND organisation_id = %s
        """
        result = OrganizationRolloutRepository.fetch_one(
            query, (feature_name, organisation_id)
        )
        return result['is_enabled'] if result else None


class OrganizationRollout:
    """Organization-based feature rollout"""
    
    @staticmethod
    def is_enabled_for_org(feature_name: str, organisation_id: str) -> Optional[bool]:
        """
        Check if feature is enabled for organisation.
        
        Returns:
            True if explicitly enabled
            False if explicitly disabled
            None if no override (use default)
        """
        return OrganizationRolloutRepository.is_org_enabled(
            feature_name, organisation_id
        )
    
    @staticmethod
    def enable_for_org(feature_name: str, organisation_id: str) -> bool:
        """Enable feature for specific organisation"""
        query = """
            INSERT INTO feature_flags.organisation_rollout 
            (feature_name, organisation_id, is_enabled)
            VALUES (%s, %s, TRUE)
            ON CONFLICT (feature_name, organisation_id)
            DO UPDATE SET is_enabled = TRUE
        """
        result = OrganizationRolloutRepository.execute(
            query, (feature_name, organisation_id)
        )
        return result > 0
    
    @staticmethod
    def disable_for_org(feature_name: str, organisation_id: str) -> bool:
        """Disable feature for specific organisation"""
        query = """
            INSERT INTO feature_flags.organisation_rollout 
            (feature_name, organisation_id, is_enabled)
            VALUES (%s, %s, FALSE)
            ON CONFLICT (feature_name, organisation_id)
            DO UPDATE SET is_enabled = FALSE
        """
        result = OrganizationRolloutRepository.execute(
            query, (feature_name, organisation_id)
        )
        return result > 0
