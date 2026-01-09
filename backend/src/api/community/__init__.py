"""
Community Domain (DDD + Journey-Based Architecture)

Community groups, discussions, and collaboration system with DDD layers.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- domain/ - Domain entities (6 entities for 6 tables)
- application/ - Business logic services
- infrastructure/ - Database repositories
- journeys/ - Journey-based API routes (future)

6 Community Tables:
1. groups - Study groups and teams (5 types)
2. group_members - Membership with roles (4 roles)
3. group_resources - Shared resources (6 types)
4. group_messages - Messages with threading
5. group_discussions - Discussion threads
6. group_posts - Posts in threads

Usage:
    from src.api.community import CommunityService, Group, GroupMember

Exports:
- Group - Domain entity for group
- GroupMember - Domain entity for member
- GroupResource - Domain entity for resource
- GroupMessage - Domain entity for message
- GroupDiscussion - Domain entity for discussion
- GroupPost - Domain entity for post
- CommunityService - Business logic
- CommunityRepository - Database access
"""

from src.api.community.core.domain.entities.group import Group
from src.api.community.core.domain.entities.group_member import GroupMember
from src.api.community.core.domain.entities.group_resource import GroupResource
from src.api.community.core.domain.entities.group_message import GroupMessage
from src.api.community.core.domain.entities.group_discussion import GroupDiscussion
from src.api.community.core.domain.entities.group_post import GroupPost
from src.api.community.core.application.services.community_service import CommunityService
from src.api.community.core.infrastructure.repositories.community_repository import CommunityRepository

__all__ = [
    # Domain Entities
    'Group',
    'GroupMember',
    'GroupResource',
    'GroupMessage',
    'GroupDiscussion',
    'GroupPost',

    # Application
    'CommunityService',

    # Infrastructure
    'CommunityRepository',
]
