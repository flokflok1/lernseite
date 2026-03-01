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

from flask import Blueprint, request, jsonify
import os

# Create setup blueprint
setup_bp = Blueprint(
    'setup',
    __name__,
    url_prefix='/setup'
)

# Exempt setup blueprint from rate limiting
# Setup endpoints are frequently polled (/status) and should not be rate-limited
try:
    from app.core.bootstrap.extensions import limiter
    limiter.exempt(setup_bp)
except ImportError:
    # Limiter not available during early initialization
    pass

# Setup security - lock setup wizard after installation
@setup_bp.before_request
def check_setup_access():
    """
    Security check for setup wizard after installation.

    Rules:
    - System NOT installed → Allow all
    - System IS installed:
      - Read-only endpoints (/status, /verify*) → Allow
      - Write endpoints (POST/PUT/DELETE) → Require X-Setup-Admin-Key
    """
    from app.setup.diagnostics.install import InstallationChecker

    # Check if system is installed
    is_installed = InstallationChecker.is_installed()

    # If NOT installed, allow everything
    if not is_installed:
        return None

    # System IS installed - check access rules

    # Read-only endpoints are always allowed
    READ_ONLY_PATHS = ['/setup/status', '/setup/verify', '/setup/verify/report']
    if request.path in READ_ONLY_PATHS:
        return None

    # GET requests are read-only, allow them
    if request.method == 'GET':
        return None

    # Write operations (POST/PUT/DELETE) after installation
    # Require SETUP_ADMIN_KEY for security
    SETUP_ADMIN_KEY = os.getenv('SETUP_ADMIN_KEY')

    if not SETUP_ADMIN_KEY:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SETUP_LOCKED',
                'message': 'Setup wizard is locked after installation. '
                           'Contact system administrator for emergency access.',
                'hint': 'Set SETUP_ADMIN_KEY environment variable to enable admin access.'
            }
        }), 403

    # Check admin key
    admin_key = request.headers.get('X-Setup-Admin-Key')
    if admin_key != SETUP_ADMIN_KEY:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_ADMIN_KEY',
                'message': 'Invalid setup admin key. Setup wizard is locked after installation.',
                'hint': 'Provide valid X-Setup-Admin-Key header.'
            }
        }), 403

    # Admin key valid - allow access
    return None

# Import routes after blueprint creation to avoid circular imports
# Routes are organized by semantic purpose across 6 modules:
# - routes/status.py: Status & health checks (/status, /verify, /health, etc.)
# - routes/database.py: Database configuration & initialization
# - routes/setup.py: Admin user & environment setup (/environment, /check, /admin)
# - routes/config.py: Organization & AI configuration (/organisation, /ki-config)
# - routes/verification.py: Data seeding, verification, diagnostics, auto-fix
# - routes/groups.py: Authorization groups & hierarchy management (/groups) [NEW]
from app.setup.routes import status  # Fixed: was routes_status (2026-02-12)
from app.setup.routes import database
from app.setup.routes import setup
from app.setup.routes import config
from app.setup.routes import verification
from app.setup.routes import groups

# Import setup modules for external use (Fixed paths 2026-02-12)
from app.setup.diagnostics.checks.system_check import SystemCheck
from app.setup.initialization.database import DatabaseInitializer
from app.setup.diagnostics.install import InstallationChecker
from app.setup.initialization.admin import AdminSetup
from app.setup.initialization.groups import GroupSetup
from app.setup.initialization.organisations import OrganisationSetup
from app.setup.seeds.seeds import SeedData
from app.setup.initialization.ai_part2 import KISetup
from app.setup.diagnostics.verification.verify import VerificationChecks as SetupVerification  # Fixed class name (2026-02-12)

__all__ = [
    'setup_bp',
    'SystemCheck',
    'DatabaseInitializer',
    'InstallationChecker',
    'AdminSetup',
    'GroupSetup',
    'OrganisationSetup',
    'SeedData',
    'KISetup',
    'SetupVerification'
]
