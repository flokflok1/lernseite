"""
LernsystemX API Gateway - Versioning & Change Management

Gateway-level API version detection and management.

Implements:
- URL-based version detection (/api/v1/, /api/v2/)
- Header-based version override (optional)
- Version validation and support check
- Deprecation warnings
- Version headers in responses

Based on Dok 33 (Versioning-Change-Management.md) - Phase 22
"""

from flask import Flask, request, g, jsonify
from typing import Optional, Tuple
import re
from datetime import datetime


class APIVersionManager:
    """
    Manages API version detection, validation, and headers.

    Supports:
    - URL-based version detection (/api/v{N}/)
    - Header-based version override (X-LSX-API-Version)
    - Version support validation
    - Deprecation notices
    """

    def __init__(self, app: Flask = None):
        """Initialize API version manager"""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize version management with Flask app.

        Registers before_request handler for version detection.

        Args:
            app: Flask application instance
        """
        self.app = app

        # Register version detection
        app.before_request(self.detect_api_version)

        app.logger.info('API Version Management initialized')
        app.logger.info(f"  - Current API version: v{app.config.get('API_VERSION_CURRENT', 1)}")
        app.logger.info(f"  - Supported versions: {app.config.get('API_VERSION_SUPPORTED', ['1'])}")
        app.logger.info(f"  - Detection strategy: {app.config.get('API_VERSION_DETECTION', 'url')}")

    def detect_api_version(self):
        """
        Detect API version from URL or header before each request.

        Stores detected version in g.api_version for use in request handlers.
        Validates version support and returns error if unsupported.

        Detection strategies:
        - url: Extract from /api/v{N}/ path
        - header: Read from X-LSX-API-Version header
        - both: URL primary, header as override (if allowed)

        Returns:
            Error response if version unsupported, None otherwise
        """
        # Skip version detection for non-API routes
        if not request.path.startswith('/api/'):
            return None

        # Skip for health checks and metrics
        skip_paths = ['/health', '/metrics']
        if any(request.path.startswith(path) for path in skip_paths):
            return None

        detection_strategy = self.app.config.get('API_VERSION_DETECTION', 'url')
        allow_header_override = self.app.config.get('API_VERSION_ALLOW_HEADER_OVERRIDE', False)

        version = None

        # 1. URL-based detection (primary)
        if detection_strategy in ['url', 'both']:
            version = self._extract_version_from_url(request.path)

        # 2. Header-based detection or override
        if detection_strategy == 'header' or (detection_strategy == 'both' and allow_header_override):
            header_version = self._extract_version_from_header()
            if header_version is not None:
                version = header_version

        # 3. Fallback to default version
        if version is None:
            version = self.app.config.get('API_VERSION_DEFAULT', 1)

        # Store in request context
        g.api_version = version

        # Validate version support
        if self.app.config.get('API_ENFORCE_VERSION_CHECK', True):
            validation_error = self._validate_version(version)
            if validation_error:
                return validation_error

        return None

    def _extract_version_from_url(self, path: str) -> Optional[int]:
        """
        Extract API version from URL path.

        Matches pattern: /api/v{N}/...

        Args:
            path: Request URL path

        Returns:
            Version number or None if not found
        """
        match = re.search(r'/api/v(\d+)/', path)
        if match:
            return int(match.group(1))
        return None

    def _extract_version_from_header(self) -> Optional[int]:
        """
        Extract API version from request header.

        Reads from X-LSX-API-Version header.

        Returns:
            Version number or None if not found
        """
        header_name = self.app.config.get('API_VERSION_HEADER', 'X-LSX-API-Version')
        version_str = request.headers.get(header_name)

        if version_str:
            try:
                return int(version_str)
            except ValueError:
                self.app.logger.warning(f"Invalid version in header: {version_str}")
                return None

        return None

    def _validate_version(self, version: int) -> Optional[Tuple]:
        """
        Validate if version is supported.

        Args:
            version: API version number

        Returns:
            Error response tuple (json, status_code) or None if valid
        """
        supported_versions = self.app.config.get('API_VERSION_SUPPORTED', ['1'])

        # Convert to integers for comparison
        try:
            supported_versions = [int(v.strip()) for v in supported_versions]
        except (ValueError, AttributeError):
            supported_versions = [1]

        if version not in supported_versions:
            if self.app.config.get('API_REJECT_UNSUPPORTED_VERSIONS', True):
                return jsonify({
                    'success': False,
                    'error': 'Unsupported API version',
                    'message': f'API v{version} is not supported',
                    'current_version': self.app.config.get('API_VERSION_CURRENT'),
                    'supported_versions': supported_versions,
                    'migration_guide': f"{self.app.config.get('API_DEPRECATION_NOTICE_URL')}/v{version}"
                }), 410  # 410 Gone

        return None

    def add_version_headers(self, response):
        """
        Add version and deprecation headers to response.

        Headers added:
        - X-LSX-API-Version: Current API version
        - X-LSX-System-Version: System version (SEMVER)
        - X-LSX-Deprecated: true/false (if applicable)
        - X-LSX-Deprecation-Date: When deprecation was announced
        - X-LSX-Sunset-Date: When version will be removed
        - X-LSX-Migration-Guide: URL to migration documentation

        Args:
            response: Flask response object

        Returns:
            Modified response with version headers
        """
        # Skip for non-API routes
        if not request.path.startswith('/api/'):
            return response

        # Get version from request context
        api_version = getattr(g, 'api_version', self.app.config.get('API_VERSION_DEFAULT', 1))

        # Add API version header
        version_header = self.app.config.get('API_VERSION_HEADER', 'X-LSX-API-Version')
        response.headers[version_header] = str(api_version)

        # Add system version header
        system_version_header = self.app.config.get('API_SYSTEM_VERSION_HEADER', 'X-LSX-System-Version')
        system_version = self.app.config.get('LSX_VERSION', '1.0.0')
        response.headers[system_version_header] = system_version

        # Add deprecation headers if version is deprecated
        if self.app.config.get('API_DEPRECATION_ENABLED', True):
            self._add_deprecation_headers(response, api_version)

        return response

    def _add_deprecation_headers(self, response, version: int):
        """
        Add deprecation headers if version is deprecated.

        Checks deprecation registry and adds appropriate headers.

        Args:
            response: Flask response object
            version: API version number
        """
        # Get deprecation info from configuration or database
        # For Phase 22, we use configuration-based deprecation
        # In future phases, this could be database-driven

        deprecation_info = self._get_deprecation_info(version)

        if deprecation_info and deprecation_info.get('deprecated', False):
            # Add deprecation flag
            deprecation_header = self.app.config.get('API_DEPRECATION_HEADER', 'X-LSX-Deprecated')
            response.headers[deprecation_header] = 'true'

            # Add deprecation date
            if deprecation_info.get('deprecation_date'):
                date_header = self.app.config.get('API_DEPRECATION_DATE_HEADER', 'X-LSX-Deprecation-Date')
                response.headers[date_header] = deprecation_info['deprecation_date']

            # Add sunset date
            if deprecation_info.get('sunset_date'):
                sunset_header = self.app.config.get('API_SUNSET_DATE_HEADER', 'X-LSX-Sunset-Date')
                response.headers[sunset_header] = deprecation_info['sunset_date']

            # Add migration guide URL
            migration_header = self.app.config.get('API_MIGRATION_GUIDE_HEADER', 'X-LSX-Migration-Guide')
            migration_url = f"{self.app.config.get('API_DEPRECATION_NOTICE_URL')}/v{version}-migration"
            response.headers[migration_header] = migration_url

    def _get_deprecation_info(self, version: int) -> Optional[dict]:
        """
        Get deprecation information for a version.

        In Phase 22: Configuration-based (hardcoded for now)
        In future: Database-driven via deprecation registry

        Args:
            version: API version number

        Returns:
            Deprecation info dict or None
        """
        # Placeholder: In Phase 22, only v1 is active (not deprecated)
        # When v2 is released, v1 would be marked deprecated here

        # Example structure for when v2 is released:
        # deprecation_registry = {
        #     1: {
        #         'deprecated': True,
        #         'deprecation_date': '2025-06-01',
        #         'sunset_date': '2026-06-01',
        #         'replacement_version': 2
        #     }
        # }

        # For now, no versions are deprecated
        return None

    def get_current_version_info(self) -> dict:
        """
        Get comprehensive version information for system status endpoint.

        Returns:
            Dictionary with version details
        """
        supported_versions = self.app.config.get('API_VERSION_SUPPORTED', ['1'])
        try:
            supported_versions = [int(v.strip()) for v in supported_versions]
        except (ValueError, AttributeError):
            supported_versions = [1]

        return {
            'system_version': self.app.config.get('LSX_VERSION', '1.0.0'),
            'environment': self.app.config.get('LSX_ENV', 'production'),
            'api': {
                'current_version': self.app.config.get('API_VERSION_CURRENT', 1),
                'supported_versions': supported_versions,
                'default_version': self.app.config.get('API_VERSION_DEFAULT', 1),
                'support_window_months': self.app.config.get('API_VERSION_SUPPORT_WINDOW', 12),
                'deprecation_warning_months': self.app.config.get('API_VERSION_DEPRECATION_WARNING', 6)
            },
            'detection': {
                'strategy': self.app.config.get('API_VERSION_DETECTION', 'url'),
                'allow_header_override': self.app.config.get('API_VERSION_ALLOW_HEADER_OVERRIDE', False)
            },
            'deprecation': {
                'enabled': self.app.config.get('API_DEPRECATION_ENABLED', True),
                'notice_url': self.app.config.get('API_DEPRECATION_NOTICE_URL')
            }
        }


# Global instance
_version_manager = APIVersionManager()


def setup_gateway_versioning(app: Flask):
    """
    Setup API versioning for the application.

    Args:
        app: Flask application instance
    """
    _version_manager.init_app(app)

    # Register after_request handler for version headers
    @app.after_request
    def add_version_headers_to_response(response):
        """Add version headers to all API responses"""
        return _version_manager.add_version_headers(response)


def get_api_version() -> int:
    """
    Get current API version from request context.

    Returns:
        API version number
    """
    return getattr(g, 'api_version', 1)


def get_version_info() -> dict:
    """
    Get comprehensive version information.

    Returns:
        Dictionary with version details
    """
    return _version_manager.get_current_version_info()
