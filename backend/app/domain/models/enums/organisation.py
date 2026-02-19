"""
Organisation domain enumerations
"""

from enum import Enum


class OrganisationType(str, Enum):
    """
    Organisation type enumeration

    Based on 25_Organisation-System.md:
    - school: Educational institutions (K-12, universities)
    - company: Corporate training and enterprise
    - teacher_team: Small teacher collaboration groups
    - creator_team: Content creator teams
    """
    SCHOOL = 'school'
    COMPANY = 'company'
    TEACHER_TEAM = 'teacher_team'
    CREATOR_TEAM = 'creator_team'


class OrgRole(str, Enum):
    """
    Organisation user role enumeration

    Roles within an organisation (from 01_Rollenmodell.md):
    - org_admin: Full organisation administration
    - teacher: Teacher/instructor role (schools)
    - trainer: Corporate trainer role (companies)
    - student: Student role (schools)
    - employee: Employee role (companies)
    """
    ORG_ADMIN = 'org_admin'
    TEACHER = 'teacher'
    TRAINER = 'trainer'
    STUDENT = 'student'
    EMPLOYEE = 'employee'


class BillingModel(str, Enum):
    """
    Organisation billing model enumeration

    From 25_Organisation-System.md and 06_Premium-Modell.md:
    - per_user: Charge per active user
    - flat: Flat monthly/annual fee
    - hybrid: Combination of base fee + per user
    """
    PER_USER = 'per_user'
    FLAT = 'flat'
    HYBRID = 'hybrid'


class OrgStatus(str, Enum):
    """
    Organisation status enumeration

    - active: Organisation is active and operational
    - suspended: Temporarily suspended (payment issues, violations)
    - deleted: Soft-deleted, pending permanent deletion
    """
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    DELETED = 'deleted'
