"""
LernsystemX Setup Package

Provides a complete installation wizard for initial system setup:
- System checks (Python, PostgreSQL, Redis, dependencies)
- Database initialization (tables, indexes, constraints)
- Admin account creation (2FA, recovery codes)
- Organisation setup (LSX Academy, multi-tenancy)
- AI API configuration (encrypted, validated)
- Seed data (21 learning methods, 10 roles, 8 categories)
- Installation verification (comprehensive checks)

ISO/IEC/IEEE 26515:2018 compliant - Setup process documentation
"""

from flask import Blueprint

# Create setup blueprint
setup_bp = Blueprint(
    'setup',
    __name__,
    url_prefix='/setup'
)

# Import routes after blueprint creation to avoid circular imports
from setup import routes

# Import setup modules for external use
from setup.system_check import SystemCheck
from setup.db_init import DatabaseInitializer
from setup.install_check import InstallationChecker
from setup.admin_setup import AdminSetup
from setup.organisation_setup import OrganisationSetup
from setup.seeds import SeedData
from setup.ki_setup import KISetup
from setup.verify import SetupVerification

__all__ = [
    'setup_bp',
    'SystemCheck',
    'DatabaseInitializer',
    'InstallationChecker',
    'AdminSetup',
    'OrganisationSetup',
    'SeedData',
    'KISetup',
    'SetupVerification'
]
