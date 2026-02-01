"""
Panel Alias Middleware - Parallel URL Prefix Support

Provides URL aliasing for admin-panel routes:
- /api/v1/panel/* -> /api/v1/admin-panel/* (new, preferred)
- /api/v1/admin-panel/* -> deprecated (Sunset header added)

This allows gradual migration from the old /admin-panel/ prefix
to the shorter /panel/ prefix without breaking existing clients.

Usage:
    from app.api.middleware.panel_alias import register_panel_alias_middleware
    register_panel_alias_middleware(app)
"""

from flask import Flask, request, Response
from werkzeug.wrappers import Response as WerkzeugResponse
from datetime import datetime, timedelta
from typing import Optional


# Configuration
OLD_PREFIX = '/api/v1/admin-panel'
NEW_PREFIX = '/api/v1/panel'

# Sunset date for old prefix (6 months from now)
SUNSET_DATE = (datetime.utcnow() + timedelta(days=180)).strftime('%a, %d %b %Y %H:%M:%S GMT')


def register_panel_alias_middleware(app: Flask) -> None:
    """
    Register middleware for panel URL aliasing.

    Rewrites /api/v1/panel/* requests to /api/v1/admin-panel/*
    and adds deprecation headers to /api/v1/admin-panel/* responses.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def rewrite_panel_url():
        """
        Rewrite /api/v1/panel/* to /api/v1/admin-panel/*.

        This allows the new shorter prefix to work with existing
        admin-panel blueprints without code duplication.
        """
        if request.path.startswith(NEW_PREFIX):
            # Store original path for logging/debugging
            request.environ['ORIGINAL_PATH'] = request.path

            # Rewrite to admin-panel path
            new_path = OLD_PREFIX + request.path[len(NEW_PREFIX):]
            request.environ['PATH_INFO'] = new_path

            # Mark this as a rewritten request (no deprecation header)
            request.environ['PANEL_REWRITTEN'] = True

            app.logger.debug(f'Panel URL rewrite: {request.environ["ORIGINAL_PATH"]} -> {new_path}')

    @app.after_request
    def add_deprecation_headers(response: Response) -> Response:
        """
        Add deprecation headers to /api/v1/admin-panel/* responses.

        Headers added:
        - Deprecation: true
        - Sunset: <date>
        - Link: <new-url>; rel="successor-version"

        These headers follow RFC 8594 (Sunset Header) and
        RFC 8288 (Web Linking) standards.
        """
        # Skip if this was a rewritten request (using new prefix)
        if request.environ.get('PANEL_REWRITTEN'):
            return response

        # Only add headers for admin-panel routes
        original_path = request.environ.get('ORIGINAL_PATH', request.path)
        if original_path.startswith(OLD_PREFIX):
            # RFC 8594 - Sunset Header
            response.headers['Deprecation'] = 'true'
            response.headers['Sunset'] = SUNSET_DATE

            # RFC 8288 - Link to new endpoint
            new_url = NEW_PREFIX + original_path[len(OLD_PREFIX):]
            response.headers['Link'] = f'<{new_url}>; rel="successor-version"'

            # Custom header for API clients
            response.headers['X-API-Deprecation-Notice'] = (
                f'This endpoint prefix is deprecated. '
                f'Please migrate to {NEW_PREFIX}/* before {SUNSET_DATE}'
            )

        return response

    app.logger.info(f'Panel alias middleware registered:')
    app.logger.info(f'  - New prefix: {NEW_PREFIX}/* (preferred)')
    app.logger.info(f'  - Old prefix: {OLD_PREFIX}/* (deprecated, sunset: {SUNSET_DATE})')


def get_canonical_url(path: str) -> str:
    """
    Get the canonical (preferred) URL for a panel endpoint.

    Args:
        path: Current request path

    Returns:
        Canonical URL using the new /panel/ prefix
    """
    if path.startswith(OLD_PREFIX):
        return NEW_PREFIX + path[len(OLD_PREFIX):]
    return path


def is_deprecated_prefix(path: str) -> bool:
    """
    Check if a path uses the deprecated prefix.

    Args:
        path: Request path to check

    Returns:
        True if using deprecated /admin-panel/ prefix
    """
    return path.startswith(OLD_PREFIX)
