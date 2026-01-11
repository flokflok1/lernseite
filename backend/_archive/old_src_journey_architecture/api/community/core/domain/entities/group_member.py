"""
GroupMember Entity (DDD Domain Entity)

Represents a member of a community group.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GroupMember:
    """
    GroupMember domain entity.

    Membership with roles and status tracking.

    Attributes:
        member_id: UUID
        group_id: Parent group UUID
        user_id: Member user UUID
        role: Member role (owner, admin, moderator, member)
        joined_at: Join timestamp
        left_at: Leave timestamp (NULL if active)
        status: Membership status (active, inactive, banned)
    """

    member_id: str
    group_id: str
    user_id: str
    role: str = 'member'
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    status: str = 'active'

    def __post_init__(self):
        """Validate group member entity."""
        if not self.member_id or not self.member_id.strip():
            raise ValueError("Member ID cannot be empty")

        if not self.group_id or not self.group_id.strip():
            raise ValueError("Group ID cannot be empty")

        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")

        valid_roles = ('owner', 'admin', 'moderator', 'member')
        if self.role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {valid_roles}")

        valid_statuses = ('active', 'inactive', 'banned')
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

    def is_owner(self) -> bool:
        """Check if member is the group owner."""
        return self.role == 'owner'

    def is_admin(self) -> bool:
        """Check if member is an admin."""
        return self.role == 'admin'

    def is_moderator(self) -> bool:
        """Check if member is a moderator."""
        return self.role == 'moderator'

    def has_admin_permissions(self) -> bool:
        """Check if member has admin permissions (owner or admin)."""
        return self.role in ('owner', 'admin')

    def has_moderation_permissions(self) -> bool:
        """Check if member can moderate (owner, admin, or moderator)."""
        return self.role in ('owner', 'admin', 'moderator')

    def is_active(self) -> bool:
        """Check if membership is active."""
        return self.status == 'active' and self.left_at is None

    def is_banned(self) -> bool:
        """Check if member is banned."""
        return self.status == 'banned'

    def leave_group(self) -> None:
        """Mark member as having left the group."""
        self.left_at = datetime.utcnow()
        self.status = 'inactive'

    def ban_member(self) -> None:
        """Ban member from group."""
        self.status = 'banned'
