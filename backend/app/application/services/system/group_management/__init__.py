"""
Group Management Service Module

Provides business logic for RBAC 3.0 group-based authorization.

Classes:
    - GroupManagementService: High-level group operations with validation and audit logging
"""

from app.application.services.system.group_management.service import GroupManagementService

__all__ = ['GroupManagementService']
