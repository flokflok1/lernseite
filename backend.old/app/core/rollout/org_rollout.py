"""
Organization-Based Rollout

Enable features for specific organizations (schools, companies)
"""

from typing import List, Optional
from app.repositories.base_repository import BaseRepository


class OrganizationRolloutRepository(BaseRepository):
    """Repository for organization rollout"""
    
    @staticmethod
    def is_org_enabled(feature_name: str, organization_id: str) -> Optional[bool]:
        """Check if feature is explicitly enabled/disabled for organization"""
        query = """
            SELECT is_enabled 
            FROM feature_flags.organization_rollout
            WHERE feature_name = %s AND organization_id = %s
        """
        result = OrganizationRolloutRepository.fetch_one(
            query, (feature_name, organization_id)
        )
        return result['is_enabled'] if result else None


class OrganizationRollout:
    """Organization-based feature rollout"""
    
    @staticmethod
    def is_enabled_for_org(feature_name: str, organization_id: str) -> Optional[bool]:
        """
        Check if feature is enabled for organization.
        
        Returns:
            True if explicitly enabled
            False if explicitly disabled
            None if no override (use default)
        """
        return OrganizationRolloutRepository.is_org_enabled(
            feature_name, organization_id
        )
    
    @staticmethod
    def enable_for_org(feature_name: str, organization_id: str) -> bool:
        """Enable feature for specific organization"""
        query = """
            INSERT INTO feature_flags.organization_rollout 
            (feature_name, organization_id, is_enabled)
            VALUES (%s, %s, TRUE)
            ON CONFLICT (feature_name, organization_id)
            DO UPDATE SET is_enabled = TRUE
        """
        result = OrganizationRolloutRepository.execute(
            query, (feature_name, organization_id)
        )
        return result > 0
    
    @staticmethod
    def disable_for_org(feature_name: str, organization_id: str) -> bool:
        """Disable feature for specific organization"""
        query = """
            INSERT INTO feature_flags.organization_rollout 
            (feature_name, organization_id, is_enabled)
            VALUES (%s, %s, FALSE)
            ON CONFLICT (feature_name, organization_id)
            DO UPDATE SET is_enabled = FALSE
        """
        result = OrganizationRolloutRepository.execute(
            query, (feature_name, organization_id)
        )
        return result > 0
