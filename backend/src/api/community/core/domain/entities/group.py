"""
Group Entity (DDD Domain Entity)

Represents a community study group or team.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Group:
    """
    Group domain entity.

    Community groups for study, projects, courses, interests, or organizations.

    Attributes:
        group_id: UUID
        owner_user_id: Owner user UUID
        organization_id: Organization UUID (optional)
        name: Group name
        description: Group description
        group_type: Type (study, project, course, interest, organization)
        is_private: Privacy flag
        max_members: Maximum member count (optional)
        avatar_url: Group avatar URL
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    group_id: str
    name: str
    group_type: str
    owner_user_id: Optional[str] = None
    organization_id: Optional[str] = None
    description: Optional[str] = None
    is_private: bool = False
    max_members: Optional[int] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate group entity."""
        if not self.group_id or not self.group_id.strip():
            raise ValueError("Group ID cannot be empty")

        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")

        valid_types = ('study', 'project', 'course', 'interest', 'organization')
        if self.group_type not in valid_types:
            raise ValueError(f"Invalid group type. Must be one of: {valid_types}")

        if self.max_members is not None and self.max_members < 0:
            raise ValueError("Max members cannot be negative")

    def is_study_group(self) -> bool:
        """Check if this is a study group."""
        return self.group_type == 'study'

    def is_project_group(self) -> bool:
        """Check if this is a project group."""
        return self.group_type == 'project'

    def is_course_group(self) -> bool:
        """Check if this is a course group."""
        return self.group_type == 'course'

    def is_organization_group(self) -> bool:
        """Check if this is an organization group."""
        return self.group_type == 'organization'

    def has_member_limit(self) -> bool:
        """Check if group has a member limit."""
        return self.max_members is not None

    def is_owned_by(self, user_id: str) -> bool:
        """Check if user is the group owner."""
        return self.owner_user_id == user_id
