"""
Organization-Based Rollout

Enable features for specific organizations (schools, companies)
"""

from typing import Optional
from app.infrastructure.persistence.repositories.feature_flags.organisation import OrganizationRolloutRepository


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
        result = OrganizationRolloutRepository.upsert_org_rollout(
            feature_name, organisation_id, True
        )
        return result > 0

    @staticmethod
    def disable_for_org(feature_name: str, organisation_id: str) -> bool:
        """Disable feature for specific organisation"""
        result = OrganizationRolloutRepository.upsert_org_rollout(
            feature_name, organisation_id, False
        )
        return result > 0
