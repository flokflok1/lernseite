"""
Community Repository (Infrastructure Layer)

Database access for:
- groups
- group_members
- group_resources
- group_messages
- group_discussions
- group_posts

ALL queries use parameterized statements for security.
NO hardcoded values - everything loaded from database.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from src.core.database import get_db_connection
from src.api.community.core.domain.entities.group import Group
from src.api.community.core.domain.entities.group_member import GroupMember
from src.api.community.core.domain.entities.group_resource import GroupResource
from src.api.community.core.domain.entities.group_message import GroupMessage
from src.api.community.core.domain.entities.group_discussion import GroupDiscussion
from src.api.community.core.domain.entities.group_post import GroupPost


class CommunityRepository:
    """
    Community Repository - Groups, Members, Resources, Messages, Discussions, Posts.
    """

    # ============================================================================
    # GROUPS
    # ============================================================================

    @staticmethod
    def find_group_by_id(group_id: str) -> Optional[Group]:
        """Find group by ID."""
        query = """
            SELECT group_id, owner_user_id, organization_id, name, description,
                   group_type, is_private, max_members, avatar_url, created_at, updated_at
            FROM support_systems.groups
            WHERE group_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (group_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return Group(
                    group_id=row[0],
                    owner_user_id=row[1],
                    organization_id=row[2],
                    name=row[3],
                    description=row[4],
                    group_type=row[5],
                    is_private=row[6] or False,
                    max_members=row[7],
                    avatar_url=row[8],
                    created_at=row[9],
                    updated_at=row[10]
                )

    @staticmethod
    def find_all_groups(
        group_type: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Group]:
        """Find all groups with filters."""
        query = """
            SELECT group_id, owner_user_id, organization_id, name, description,
                   group_type, is_private, max_members, avatar_url, created_at, updated_at
            FROM support_systems.groups
            WHERE 1=1
        """
        params = []

        if group_type:
            query += " AND group_type = %s"
            params.append(group_type)

        if organization_id:
            query += " AND organization_id = %s"
            params.append(organization_id)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    Group(
                        group_id=row[0],
                        owner_user_id=row[1],
                        organization_id=row[2],
                        name=row[3],
                        description=row[4],
                        group_type=row[5],
                        is_private=row[6] or False,
                        max_members=row[7],
                        avatar_url=row[8],
                        created_at=row[9],
                        updated_at=row[10]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_group(group: Group) -> Group:
        """Create new group."""
        query = """
            INSERT INTO support_systems.groups
            (group_id, owner_user_id, organization_id, name, description,
             group_type, is_private, max_members, avatar_url, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING group_id, owner_user_id, organization_id, name, description,
                      group_type, is_private, max_members, avatar_url, created_at, updated_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    group.group_id,
                    group.owner_user_id,
                    group.organization_id,
                    group.name,
                    group.description,
                    group.group_type,
                    group.is_private,
                    group.max_members,
                    group.avatar_url,
                    group.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return Group(
                    group_id=row[0],
                    owner_user_id=row[1],
                    organization_id=row[2],
                    name=row[3],
                    description=row[4],
                    group_type=row[5],
                    is_private=row[6] or False,
                    max_members=row[7],
                    avatar_url=row[8],
                    created_at=row[9],
                    updated_at=row[10]
                )

    # ============================================================================
    # GROUP MEMBERS
    # ============================================================================

    @staticmethod
    def find_member_by_id(member_id: str) -> Optional[GroupMember]:
        """Find group member by ID."""
        query = """
            SELECT member_id, group_id, user_id, role, joined_at, left_at, status
            FROM support_systems.group_members
            WHERE member_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (member_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return GroupMember(
                    member_id=row[0],
                    group_id=row[1],
                    user_id=row[2],
                    role=row[3] or 'member',
                    joined_at=row[4],
                    left_at=row[5],
                    status=row[6] or 'active'
                )

    @staticmethod
    def find_members_by_group(group_id: str, status: str = 'active') -> List[GroupMember]:
        """Find all members of a group."""
        query = """
            SELECT member_id, group_id, user_id, role, joined_at, left_at, status
            FROM support_systems.group_members
            WHERE group_id = %s AND status = %s
            ORDER BY joined_at ASC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (group_id, status))
                rows = cur.fetchall()

                return [
                    GroupMember(
                        member_id=row[0],
                        group_id=row[1],
                        user_id=row[2],
                        role=row[3] or 'member',
                        joined_at=row[4],
                        left_at=row[5],
                        status=row[6] or 'active'
                    )
                    for row in rows
                ]

    @staticmethod
    def create_member(member: GroupMember) -> GroupMember:
        """Create new group member."""
        query = """
            INSERT INTO support_systems.group_members
            (member_id, group_id, user_id, role, joined_at, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING member_id, group_id, user_id, role, joined_at, left_at, status
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    member.member_id,
                    member.group_id,
                    member.user_id,
                    member.role,
                    member.joined_at or datetime.utcnow(),
                    member.status
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupMember(
                    member_id=row[0],
                    group_id=row[1],
                    user_id=row[2],
                    role=row[3] or 'member',
                    joined_at=row[4],
                    left_at=row[5],
                    status=row[6] or 'active'
                )

    @staticmethod
    def update_member(member: GroupMember) -> GroupMember:
        """Update group member."""
        query = """
            UPDATE support_systems.group_members
            SET role = %s, left_at = %s, status = %s
            WHERE member_id = %s
            RETURNING member_id, group_id, user_id, role, joined_at, left_at, status
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    member.role,
                    member.left_at,
                    member.status,
                    member.member_id
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupMember(
                    member_id=row[0],
                    group_id=row[1],
                    user_id=row[2],
                    role=row[3] or 'member',
                    joined_at=row[4],
                    left_at=row[5],
                    status=row[6] or 'active'
                )

    # ============================================================================
    # GROUP RESOURCES
    # ============================================================================

    @staticmethod
    def find_resources_by_group(group_id: str) -> List[GroupResource]:
        """Find all resources for a group."""
        query = """
            SELECT resource_id, group_id, shared_by, title, resource_type,
                   data, description, created_at
            FROM support_systems.group_resources
            WHERE group_id = %s
            ORDER BY created_at DESC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (group_id,))
                rows = cur.fetchall()

                return [
                    GroupResource(
                        resource_id=row[0],
                        group_id=row[1],
                        shared_by=row[2],
                        title=row[3],
                        resource_type=row[4],
                        data=row[5] or {},
                        description=row[6],
                        created_at=row[7]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_resource(resource: GroupResource) -> GroupResource:
        """Create new group resource."""
        query = """
            INSERT INTO support_systems.group_resources
            (resource_id, group_id, shared_by, title, resource_type, data, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING resource_id, group_id, shared_by, title, resource_type,
                      data, description, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    resource.resource_id,
                    resource.group_id,
                    resource.shared_by,
                    resource.title,
                    resource.resource_type,
                    json.dumps(resource.data),
                    resource.description,
                    resource.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupResource(
                    resource_id=row[0],
                    group_id=row[1],
                    shared_by=row[2],
                    title=row[3],
                    resource_type=row[4],
                    data=row[5] or {},
                    description=row[6],
                    created_at=row[7]
                )

    # ============================================================================
    # GROUP MESSAGES
    # ============================================================================

    @staticmethod
    def find_messages_by_group(group_id: str, limit: int = 100) -> List[GroupMessage]:
        """Find messages for a group (excluding deleted)."""
        query = """
            SELECT message_id, group_id, user_id, parent_message_id, message_text,
                   attachments, edited, edited_at, deleted, deleted_at, created_at
            FROM community.group_messages
            WHERE group_id = %s AND deleted = FALSE
            ORDER BY created_at DESC
            LIMIT %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (group_id, limit))
                rows = cur.fetchall()

                return [
                    GroupMessage(
                        message_id=row[0],
                        group_id=row[1],
                        user_id=row[2],
                        parent_message_id=row[3],
                        message_text=row[4],
                        attachments=row[5],
                        edited=row[6] or False,
                        edited_at=row[7],
                        deleted=row[8] or False,
                        deleted_at=row[9],
                        created_at=row[10]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_message(message: GroupMessage) -> GroupMessage:
        """Create new group message."""
        query = """
            INSERT INTO community.group_messages
            (message_id, group_id, user_id, parent_message_id, message_text, attachments, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING message_id, group_id, user_id, parent_message_id, message_text,
                      attachments, edited, edited_at, deleted, deleted_at, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    message.message_id,
                    message.group_id,
                    message.user_id,
                    message.parent_message_id,
                    message.message_text,
                    json.dumps(message.attachments) if message.attachments else None,
                    message.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupMessage(
                    message_id=row[0],
                    group_id=row[1],
                    user_id=row[2],
                    parent_message_id=row[3],
                    message_text=row[4],
                    attachments=row[5],
                    edited=row[6] or False,
                    edited_at=row[7],
                    deleted=row[8] or False,
                    deleted_at=row[9],
                    created_at=row[10]
                )

    @staticmethod
    def update_message(message: GroupMessage) -> GroupMessage:
        """Update group message."""
        query = """
            UPDATE community.group_messages
            SET message_text = %s, edited = %s, edited_at = %s, deleted = %s, deleted_at = %s
            WHERE message_id = %s
            RETURNING message_id, group_id, user_id, parent_message_id, message_text,
                      attachments, edited, edited_at, deleted, deleted_at, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    message.message_text,
                    message.edited,
                    message.edited_at,
                    message.deleted,
                    message.deleted_at,
                    message.message_id
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupMessage(
                    message_id=row[0],
                    group_id=row[1],
                    user_id=row[2],
                    parent_message_id=row[3],
                    message_text=row[4],
                    attachments=row[5],
                    edited=row[6] or False,
                    edited_at=row[7],
                    deleted=row[8] or False,
                    deleted_at=row[9],
                    created_at=row[10]
                )

    # ============================================================================
    # GROUP DISCUSSIONS
    # ============================================================================

    @staticmethod
    def find_discussions_by_group(group_id: str) -> List[GroupDiscussion]:
        """Find discussions for a group."""
        query = """
            SELECT discussion_id, group_id, created_by, title, description,
                   pinned, locked, view_count, reply_count, last_activity_at, created_at
            FROM community.group_discussions
            WHERE group_id = %s
            ORDER BY pinned DESC, last_activity_at DESC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (group_id,))
                rows = cur.fetchall()

                return [
                    GroupDiscussion(
                        discussion_id=row[0],
                        group_id=row[1],
                        created_by=row[2],
                        title=row[3],
                        description=row[4],
                        pinned=row[5] or False,
                        locked=row[6] or False,
                        view_count=row[7] or 0,
                        reply_count=row[8] or 0,
                        last_activity_at=row[9],
                        created_at=row[10]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_discussion(discussion: GroupDiscussion) -> GroupDiscussion:
        """Create new discussion."""
        query = """
            INSERT INTO community.group_discussions
            (discussion_id, group_id, created_by, title, description, last_activity_at, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING discussion_id, group_id, created_by, title, description,
                      pinned, locked, view_count, reply_count, last_activity_at, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    discussion.discussion_id,
                    discussion.group_id,
                    discussion.created_by,
                    discussion.title,
                    discussion.description,
                    discussion.last_activity_at or datetime.utcnow(),
                    discussion.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupDiscussion(
                    discussion_id=row[0],
                    group_id=row[1],
                    created_by=row[2],
                    title=row[3],
                    description=row[4],
                    pinned=row[5] or False,
                    locked=row[6] or False,
                    view_count=row[7] or 0,
                    reply_count=row[8] or 0,
                    last_activity_at=row[9],
                    created_at=row[10]
                )

    @staticmethod
    def update_discussion(discussion: GroupDiscussion) -> GroupDiscussion:
        """Update discussion."""
        query = """
            UPDATE community.group_discussions
            SET pinned = %s, locked = %s, view_count = %s, reply_count = %s, last_activity_at = %s
            WHERE discussion_id = %s
            RETURNING discussion_id, group_id, created_by, title, description,
                      pinned, locked, view_count, reply_count, last_activity_at, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    discussion.pinned,
                    discussion.locked,
                    discussion.view_count,
                    discussion.reply_count,
                    discussion.last_activity_at,
                    discussion.discussion_id
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupDiscussion(
                    discussion_id=row[0],
                    group_id=row[1],
                    created_by=row[2],
                    title=row[3],
                    description=row[4],
                    pinned=row[5] or False,
                    locked=row[6] or False,
                    view_count=row[7] or 0,
                    reply_count=row[8] or 0,
                    last_activity_at=row[9],
                    created_at=row[10]
                )

    # ============================================================================
    # GROUP POSTS
    # ============================================================================

    @staticmethod
    def find_posts_by_discussion(discussion_id: str) -> List[GroupPost]:
        """Find posts in a discussion."""
        query = """
            SELECT post_id, discussion_id, user_id, content, attachments,
                   likes_count, edited, edited_at, created_at
            FROM community.group_posts
            WHERE discussion_id = %s
            ORDER BY created_at ASC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (discussion_id,))
                rows = cur.fetchall()

                return [
                    GroupPost(
                        post_id=row[0],
                        discussion_id=row[1],
                        user_id=row[2],
                        content=row[3],
                        attachments=row[4],
                        likes_count=row[5] or 0,
                        edited=row[6] or False,
                        edited_at=row[7],
                        created_at=row[8]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_post(post: GroupPost) -> GroupPost:
        """Create new post."""
        query = """
            INSERT INTO community.group_posts
            (post_id, discussion_id, user_id, content, attachments, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING post_id, discussion_id, user_id, content, attachments,
                      likes_count, edited, edited_at, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    post.post_id,
                    post.discussion_id,
                    post.user_id,
                    post.content,
                    json.dumps(post.attachments) if post.attachments else None,
                    post.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupPost(
                    post_id=row[0],
                    discussion_id=row[1],
                    user_id=row[2],
                    content=row[3],
                    attachments=row[4],
                    likes_count=row[5] or 0,
                    edited=row[6] or False,
                    edited_at=row[7],
                    created_at=row[8]
                )

    @staticmethod
    def update_post(post: GroupPost) -> GroupPost:
        """Update post."""
        query = """
            UPDATE community.group_posts
            SET content = %s, likes_count = %s, edited = %s, edited_at = %s
            WHERE post_id = %s
            RETURNING post_id, discussion_id, user_id, content, attachments,
                      likes_count, edited, edited_at, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    post.content,
                    post.likes_count,
                    post.edited,
                    post.edited_at,
                    post.post_id
                ))

                row = cur.fetchone()
                conn.commit()

                return GroupPost(
                    post_id=row[0],
                    discussion_id=row[1],
                    user_id=row[2],
                    content=row[3],
                    attachments=row[4],
                    likes_count=row[5] or 0,
                    edited=row[6] or False,
                    edited_at=row[7],
                    created_at=row[8]
                )
