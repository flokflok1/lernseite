"""
User domain enumerations
"""

from enum import Enum


class UserRole(str, Enum):
    """Valid user roles"""
    FREE = 'free'
    PREMIUM = 'premium'
    CREATOR = 'creator'
    TEACHER = 'teacher'
    SCHOOL = 'school'
    COMPANY = 'company'
    SUPPORT = 'support'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class UserStatus(str, Enum):
    """Valid user statuses"""
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    BANNED = 'banned'
    DELETED = 'deleted'
