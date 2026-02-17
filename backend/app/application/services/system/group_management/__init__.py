"""
Group Management Service Module

Provides business logic for RBAC 3.0 group-based authorization.

Split across two files for Quality Gate G01 compliance (max 500 lines):
- service.py: Validation, Group CRUD, permissions, query methods
- service_part2.py: Membership management, organization initialization (B2B SaaS setup)

Classes:
    - GroupManagementService: High-level group operations with validation and audit logging
"""

from app.application.services.system.group_management.service import GroupManagementService

__all__ = ['GroupManagementService']
