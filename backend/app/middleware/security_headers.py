"""
LernsystemX - Security Headers Middleware

Based on Dok 31 (Security Architecture) and Phase 20 requirements.

Implements security headers to protect against common web vulnerabilities:
- X-Frame-Options: Prevent clickjacking
- X-Content-Type-Options: Prevent MIME-sniffing
- X-XSS-Protection: Enable XSS filtering (legacy browsers)
- Strict-Transport-Security (HSTS): Force HTTPS
- Content-Security-Policy (CSP): Prevent XSS and data injection
- Referrer-Policy: Control referrer information
- Permissions-Policy: Control browser features

ISO 27001:2013 compliant - Application Security Controls
OWASP Top 10 compliant - Security Misconfiguration (A05:2021)
"""

from flask import Flask, request
from typing import Optional


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all HTTP responses.

    Headers added:
    - X-Frame-Options: DENY
    - X-Content-Type-Options: nosniff
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains
    - Content-Security-Policy: default-src 'self'
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: geolocation=(), microphone=(), camera=()
    """

    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize middleware.

        Args:
            app: Flask application instance (optional)
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize middleware with Flask app.

        Args:
            app: Flask application instance
        """
        self.app = app

        # Register after_request handler
        app.after_request(self.add_security_headers)

        app.logger.info('Security headers middleware initialized')

    def add_security_headers(self, response):
        """
        Add security headers to response.

        Args:
            response: Flask response object

        Returns:
            Response with security headers added
        """
        if not self.app.config.get('SECURITY_HEADERS_ENABLED', True):
            return response

        # X-Frame-Options: Prevent clickjacking
        # DENY: Page cannot be displayed in a frame/iframe
        response.headers['X-Frame-Options'] = 'DENY'

        # X-Content-Type-Options: Prevent MIME-sniffing
        # Browsers must respect the Content-Type header
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # X-XSS-Protection: Enable XSS filtering (legacy browsers)
        # Modern browsers use CSP instead, but this provides defense-in-depth
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Strict-Transport-Security (HSTS): Force HTTPS
        # Only add if request was via HTTPS (or in production)
        if request.is_secure or self.app.config.get('LSX_ENV') == 'production':
            max_age = self.app.config.get('HSTS_MAX_AGE', 31536000)  # 1 year default
            response.headers['Strict-Transport-Security'] = (
                f'max-age={max_age}; includeSubDomains; preload'
            )

        # Content-Security-Policy (CSP): Prevent XSS and data injection
        # This is a strict policy - adjust based on your frontend needs
        csp_policy = self._get_csp_policy()
        if csp_policy:
            response.headers['Content-Security-Policy'] = csp_policy

        # Referrer-Policy: Control referrer information
        # strict-origin-when-cross-origin: Send full URL for same-origin, origin only for cross-origin
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions-Policy: Control browser features
        # Disable potentially dangerous features by default
        response.headers['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), payment=(), usb=()'
        )

        # Remove server header to avoid information disclosure
        response.headers.pop('Server', None)

        return response

    def _get_csp_policy(self) -> str:
        """
        Generate Content-Security-Policy header value.

        Returns:
            CSP policy string
        """
        # Get frontend URL from config
        frontend_url = self.app.config.get('FRONTEND_URL', 'https://localhost:3000')

        # Build CSP policy
        # Adjust these directives based on your frontend requirements
        csp_directives = [
            "default-src 'self'",  # Default: only same origin
            f"connect-src 'self' {frontend_url}",  # API calls
            "img-src 'self' data: https:",  # Images: self + data URIs + HTTPS
            "style-src 'self' 'unsafe-inline'",  # Styles: allow inline (needed for many CSS frameworks)
            "script-src 'self'",  # Scripts: only same origin
            "font-src 'self' data:",  # Fonts: self + data URIs
            "frame-ancestors 'none'",  # Equivalent to X-Frame-Options: DENY
            "base-uri 'self'",  # Restrict <base> tag
            "form-action 'self'",  # Form submissions only to same origin
            "upgrade-insecure-requests",  # Upgrade HTTP to HTTPS
        ]

        return '; '.join(csp_directives)


# ==========================================
# SETUP FUNCTION
# ==========================================

def setup_security_headers(app: Flask):
    """
    Setup security headers middleware for the application.

    This function is called from the app factory if SECURITY_HEADERS_ENABLED=True.

    Args:
        app: Flask application instance
    """
    if not app.config.get('SECURITY_HEADERS_ENABLED', True):
        app.logger.warning('Security headers are DISABLED - not recommended for production')
        return

    # Initialize middleware
    security_headers = SecurityHeadersMiddleware(app)

    app.logger.info('Security headers configured:')
    app.logger.info('  - X-Frame-Options: DENY')
    app.logger.info('  - X-Content-Type-Options: nosniff')
    app.logger.info('  - X-XSS-Protection: 1; mode=block')
    app.logger.info(f"  - HSTS max-age: {app.config.get('HSTS_MAX_AGE', 31536000)} seconds")
    app.logger.info('  - Content-Security-Policy: enabled')
    app.logger.info('  - Referrer-Policy: strict-origin-when-cross-origin')
    app.logger.info('  - Permissions-Policy: restrictive')


# ==========================================
# EXPORTS
# ==========================================

__all__ = [
    'SecurityHeadersMiddleware',
    'setup_security_headers',
]
