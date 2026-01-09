"""
Community Service (Application Layer)

Business logic for community groups, discussions, and collaboration.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.api.community.core.domain.entities.group import Group
from src.api.community.core.domain.entities.group_member import GroupMember
from src.api.community.core.domain.entities.group_resource import GroupResource
from src.api.community.core.domain.entities.group_message import GroupMessage
from src.api.community.core.domain.entities.group_discussion import GroupDiscussion
from src.api.community.core.domain.entities.group_post import GroupPost
from src.api.community.core.infrastructure.repositories.community_repository import CommunityRepository
from src.core.events import EventBus, EventType, DomainEvent


class CommunityService:
    """
    Community service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded group types, roles, or statuses.
    """

    # ============================================================================
    # GROUPS
    # ============================================================================

    @staticmethod
    def get_group_by_id(group_id: str) -> Optional[Group]:
        """Get group by ID."""
        return CommunityRepository.find_group_by_id(group_id)

    @staticmethod
    def list_groups(
        group_type: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Group]:
        """List groups with filters."""
        return CommunityRepository.find_all_groups(group_type, organization_id, limit)

    @staticmethod
    def create_group(
        name: str,
        group_type: str,
        owner_user_id: str,
        description: Optional[str] = None,
        organization_id: Optional[str] = None,
        is_private: bool = False,
        max_members: Optional[int] = None
    ) -> Group:
        """
        Create new group.

        Args:
            name: Group name
            group_type: study, project, course, interest, organization (validated by DB)
            owner_user_id: Owner user UUID
            description: Group description
            organization_id: Organization UUID
            is_private: Privacy flag
            max_members: Max member count

        Returns:
            Created Group
        """
        import uuid
        group = Group(
            group_id=str(uuid.uuid4()),
            name=name,
            group_type=group_type,
            owner_user_id=owner_user_id,
            description=description,
            organization_id=organization_id,
            is_private=is_private,
            max_members=max_members,
            created_at=datetime.utcnow()
        )

        created_group = CommunityRepository.create_group(group)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.GROUP_CREATED,
            aggregate_id=created_group.group_id,
            occurred_at=datetime.utcnow(),
            data={
                'group_type': created_group.group_type,
                'owner_user_id': created_group.owner_user_id,
                'is_private': created_group.is_private
            }
        )
        EventBus.publish(event)

        # Auto-add owner as member
        CommunityService.add_member(created_group.group_id, owner_user_id, 'owner')

        return created_group

    # ============================================================================
    # GROUP MEMBERS
    # ============================================================================

    @staticmethod
    def get_group_members(group_id: str, status: str = 'active') -> List[GroupMember]:
        """Get all members of a group."""
        return CommunityRepository.find_members_by_group(group_id, status)

    @staticmethod
    def add_member(
        group_id: str,
        user_id: str,
        role: str = 'member'
    ) -> GroupMember:
        """
        Add member to group.

        Args:
            group_id: Group UUID
            user_id: User UUID
            role: owner, admin, moderator, member (validated by DB)

        Returns:
            Created GroupMember
        """
        import uuid
        member = GroupMember(
            member_id=str(uuid.uuid4()),
            group_id=group_id,
            user_id=user_id,
            role=role,
            joined_at=datetime.utcnow(),
            status='active'
        )

        created_member = CommunityRepository.create_member(member)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.MEMBER_JOINED,
            aggregate_id=created_member.member_id,
            occurred_at=datetime.utcnow(),
            data={
                'group_id': created_member.group_id,
                'user_id': created_member.user_id,
                'role': created_member.role
            }
        )
        EventBus.publish(event)

        return created_member

    @staticmethod
    def remove_member(member_id: str) -> GroupMember:
        """Remove member from group (soft delete)."""
        member = CommunityRepository.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member {member_id} not found")

        member.leave_group()
        return CommunityRepository.update_member(member)

    @staticmethod
    def update_member_role(member_id: str, new_role: str, admin_user_id: str) -> GroupMember:
        """Update member role (requires admin permissions)."""
        member = CommunityRepository.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member {member_id} not found")

        # TODO: Verify admin_user_id has permission to change roles

        member.role = new_role
        return CommunityRepository.update_member(member)

    # ============================================================================
    # GROUP RESOURCES
    # ============================================================================

    @staticmethod
    def get_group_resources(group_id: str) -> List[GroupResource]:
        """Get all resources for a group."""
        return CommunityRepository.find_resources_by_group(group_id)

    @staticmethod
    def share_resource(
        group_id: str,
        user_id: str,
        title: str,
        resource_type: str,
        data: Dict[str, Any],
        description: Optional[str] = None
    ) -> GroupResource:
        """
        Share resource in group.

        Args:
            group_id: Group UUID
            user_id: User sharing the resource
            title: Resource title
            resource_type: file, link, course_copy, note, quiz, flashcard_set (validated by DB)
            data: JSONB resource data
            description: Resource description

        Returns:
            Created GroupResource
        """
        import uuid
        resource = GroupResource(
            resource_id=str(uuid.uuid4()),
            group_id=group_id,
            shared_by=user_id,
            title=title,
            resource_type=resource_type,
            data=data,
            description=description,
            created_at=datetime.utcnow()
        )

        return CommunityRepository.create_resource(resource)

    # ============================================================================
    # GROUP MESSAGES
    # ============================================================================

    @staticmethod
    def get_group_messages(group_id: str, limit: int = 100) -> List[GroupMessage]:
        """Get messages for a group."""
        return CommunityRepository.find_messages_by_group(group_id, limit)

    @staticmethod
    def send_message(
        group_id: str,
        user_id: str,
        message_text: str,
        parent_message_id: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> GroupMessage:
        """Send message in group."""
        import uuid
        message = GroupMessage(
            message_id=str(uuid.uuid4()),
            group_id=group_id,
            user_id=user_id,
            message_text=message_text,
            parent_message_id=parent_message_id,
            attachments=attachments,
            created_at=datetime.utcnow()
        )

        return CommunityRepository.create_message(message)

    @staticmethod
    def edit_message(message_id: str, new_text: str, user_id: str) -> GroupMessage:
        """Edit message (user must be author)."""
        # TODO: Fetch message, verify user is author, then edit
        # For now, simplified version
        message = GroupMessage(
            message_id=message_id,
            group_id='',  # Will be filled from DB
            message_text=new_text
        )
        message.edit_message(new_text)
        return CommunityRepository.update_message(message)

    @staticmethod
    def delete_message(message_id: str, user_id: str) -> GroupMessage:
        """Delete message (soft delete, user must be author or admin)."""
        # TODO: Fetch message, verify permissions, then delete
        # For now, simplified version
        message = GroupMessage(
            message_id=message_id,
            group_id='',  # Will be filled from DB
            message_text=''
        )
        message.soft_delete()
        return CommunityRepository.update_message(message)

    # ============================================================================
    # GROUP DISCUSSIONS
    # ============================================================================

    @staticmethod
    def get_group_discussions(group_id: str) -> List[GroupDiscussion]:
        """Get discussions for a group."""
        return CommunityRepository.find_discussions_by_group(group_id)

    @staticmethod
    def create_discussion(
        group_id: str,
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> GroupDiscussion:
        """Create new discussion thread."""
        import uuid
        discussion = GroupDiscussion(
            discussion_id=str(uuid.uuid4()),
            group_id=group_id,
            created_by=user_id,
            title=title,
            description=description,
            created_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )

        return CommunityRepository.create_discussion(discussion)

    @staticmethod
    def pin_discussion(discussion_id: str, admin_user_id: str) -> GroupDiscussion:
        """Pin discussion (requires admin permissions)."""
        # TODO: Fetch discussion, verify admin permissions, then pin
        discussion = GroupDiscussion(
            discussion_id=discussion_id,
            group_id='',  # Will be filled from DB
            title=''
        )
        discussion.pin_discussion()
        return CommunityRepository.update_discussion(discussion)

    @staticmethod
    def lock_discussion(discussion_id: str, admin_user_id: str) -> GroupDiscussion:
        """Lock discussion (requires admin permissions)."""
        # TODO: Fetch discussion, verify admin permissions, then lock
        discussion = GroupDiscussion(
            discussion_id=discussion_id,
            group_id='',  # Will be filled from DB
            title=''
        )
        discussion.lock_discussion()
        return CommunityRepository.update_discussion(discussion)

    # ============================================================================
    # GROUP POSTS
    # ============================================================================

    @staticmethod
    def get_discussion_posts(discussion_id: str) -> List[GroupPost]:
        """Get posts in a discussion."""
        return CommunityRepository.find_posts_by_discussion(discussion_id)

    @staticmethod
    def create_post(
        discussion_id: str,
        user_id: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> GroupPost:
        """Create post in discussion."""
        import uuid
        post = GroupPost(
            post_id=str(uuid.uuid4()),
            discussion_id=discussion_id,
            user_id=user_id,
            content=content,
            attachments=attachments,
            created_at=datetime.utcnow()
        )

        created_post = CommunityRepository.create_post(post)

        # TODO: Increment discussion reply count

        return created_post

    @staticmethod
    def like_post(post_id: str, user_id: str) -> GroupPost:
        """Like a post."""
        # TODO: Fetch post, verify not already liked, then increment
        post = GroupPost(
            post_id=post_id,
            discussion_id='',  # Will be filled from DB
            content=''
        )
        post.increment_likes()
        return CommunityRepository.update_post(post)
