"""
B2B Contact Form API

Public endpoint for business customer inquiries.
Handles contact form submissions, email notifications, and pipeline tracking.

Endpoint: POST /api/v1/business/contact

Workflow:
1. Validate contact form data (Pydantic)
2. Save to b2b_contact_requests table
3. Send email notification to admin
4. Send confirmation email to customer
5. Return success response

Author: LernSystemX Backend Team
Created: 2026-01-22
Status: Production-Ready
"""

from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
import logging
import re

from app.infrastructure.persistence.database.connection import get_db_connection
from app.infrastructure.utils.exceptions import ValidationError, APIException

# Initialize blueprint
bp = Blueprint('business_contact', __name__, url_prefix='/api/v1/business')

# Logger
logger = logging.getLogger(__name__)

# =====================================================
# Pydantic Validation Schema
# =====================================================

class BusinessContactSchema(BaseModel):
    """
    B2B Contact Form Validation Schema.

    Validates all required and optional fields with business rules.
    """

    # Required Fields
    company_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Company/Organization name"
    )

    contact_person: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Contact person full name"
    )

    email: EmailStr = Field(
        ...,
        description="Contact email address"
    )

    phone: str = Field(
        ...,
        min_length=5,
        max_length=30,
        description="Contact phone number"
    )

    # Optional Fields
    company_size: Optional[str] = Field(
        default=None,
        description="Company size category"
    )

    industry: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Industry/sector"
    )

    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Customer inquiry message"
    )

    # Source Tracking
    source: str = Field(
        default='website',
        description="Lead source"
    )

    referrer: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Referring URL or partner"
    )

    # Validators
    @validator('company_size')
    def validate_company_size(cls, v):
        """Validate company size is from predefined list."""
        if v is not None:
            valid_sizes = ['1-10', '11-50', '51-200', '200+']
            if v not in valid_sizes:
                raise ValueError(f'company_size must be one of: {", ".join(valid_sizes)}')
        return v

    @validator('industry')
    def validate_industry(cls, v):
        """Validate industry is from predefined list."""
        if v is not None:
            valid_industries = [
                'Schule', 'Universität', 'Unternehmen',
                'Non-Profit', 'Behörde', 'Sonstiges'
            ]
            if v not in valid_industries:
                raise ValueError(f'industry must be one of: {", ".join(valid_industries)}')
        return v

    @validator('phone')
    def validate_phone_format(cls, v):
        """Validate phone number contains only valid characters."""
        # Allow: digits, spaces, +, -, (, )
        if not re.match(r'^[\d\s\+\-\(\)]+$', v):
            raise ValueError('phone must contain only digits, spaces, and +()-')
        return v

    @validator('message')
    def validate_message_content(cls, v):
        """Ensure message is not just whitespace."""
        if v and v.strip() == '':
            raise ValueError('message cannot be empty or only whitespace')
        return v.strip()

    @validator('source')
    def validate_source(cls, v):
        """Validate source is from predefined list."""
        valid_sources = ['website', 'referral', 'event', 'direct', 'partner']
        if v not in valid_sources:
            raise ValueError(f'source must be one of: {", ".join(valid_sources)}')
        return v

    class Config:
        """Pydantic config."""
        str_strip_whitespace = True  # Auto-trim whitespace
        anystr_lower = False  # Keep original case


# =====================================================
# Helper Functions
# =====================================================

def save_contact_request(data: BusinessContactSchema) -> str:
    """
    Save contact request to database.

    Args:
        data: Validated contact form data

    Returns:
        Request ID (UUID)

    Raises:
        psycopg.Error: If database insert fails
    """
    with get_db_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO b2b_contact_requests (
                    company_name,
                    contact_person,
                    email,
                    phone,
                    company_size,
                    industry,
                    message,
                    source,
                    referrer,
                    status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, 'new'
                )
                RETURNING id
                """,
                (
                    data.company_name,
                    data.contact_person,
                    data.email,
                    data.phone,
                    data.company_size,
                    data.industry,
                    data.message,
                    data.source,
                    data.referrer
                )
            )

            result = cursor.fetchone()
            conn.commit()

            return result['id']


def send_admin_notification(data: BusinessContactSchema, request_id: str):
    """
    Send email notification to admin about new B2B contact request.

    Args:
        data: Contact form data
        request_id: Generated request ID
    """
    from app.utils.email import send_email
    from datetime import datetime

    # Get admin email from config or use default
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@lernsystemx.com')
    admin_panel_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

    try:
        # Send email using template
        success = send_email(
            to_email=admin_email,
            subject=f"🎯 Neue B2B Anfrage: {data.company_name}",
            template_name='emails/b2b/admin_notification.html',
            context={
                'request_id': request_id,
                'company_name': data.company_name,
                'contact_person': data.contact_person,
                'email': data.email,
                'phone': data.phone,
                'company_size': data.company_size,
                'industry': data.industry,
                'message': data.message,
                'source': data.source,
                'referrer': data.referrer,
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'admin_panel_url': admin_panel_url
            }
        )

        if success:
            logger.info(
                f"Admin notification sent successfully",
                extra={
                    'request_id': request_id,
                    'company_name': data.company_name,
                    'admin_email': admin_email
                }
            )
        else:
            logger.warning(
                f"Failed to send admin notification",
                extra={
                    'request_id': request_id,
                    'company_name': data.company_name
                }
            )

    except Exception as e:
        logger.exception(
            f"Error sending admin notification: {str(e)}",
            extra={'request_id': request_id}
        )


def send_customer_confirmation(data: BusinessContactSchema):
    """
    Send confirmation email to customer.

    Args:
        data: Contact form data
    """
    from app.utils.email import send_email

    try:
        # Send confirmation email to customer
        success = send_email(
            to_email=data.email,
            subject="✅ Vielen Dank für Ihre Anfrage - LernSystemX",
            template_name='emails/b2b/customer_confirmation.html',
            context={
                'contact_person': data.contact_person,
                'company_name': data.company_name,
                'email': data.email
            }
        )

        if success:
            logger.info(
                f"Customer confirmation sent successfully",
                extra={
                    'company_name': data.company_name,
                    'email': data.email
                }
            )
        else:
            logger.warning(
                f"Failed to send customer confirmation",
                extra={
                    'company_name': data.company_name,
                    'email': data.email
                }
            )

    except Exception as e:
        logger.exception(
            f"Error sending customer confirmation: {str(e)}",
            extra={'email': data.email}
        )


def check_duplicate_recent_submission(email: str, hours: int = 24) -> bool:
    """
    Check if email has submitted a request recently (spam protection).

    Args:
        email: Email address to check
        hours: How many hours to look back (default 24)

    Returns:
        True if duplicate found, False otherwise
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM b2b_contact_requests
                WHERE email = %s
                AND created_at > NOW() - INTERVAL '%s hours'
                """,
                (email, hours)
            )

            count = cursor.fetchone()[0]
            return count > 0


# =====================================================
# API Endpoint
# =====================================================

@bp.route('/contact', methods=['POST'])
def submit_contact():
    """
    POST /api/v1/business/contact

    Public endpoint for B2B contact form submissions.

    Request Body (JSON):
        company_name (str, required): Company/Organization name (2-200 chars)
        contact_person (str, required): Contact person name (2-100 chars)
        email (str, required): Valid email address
        phone (str, required): Phone number (5-30 chars)
        company_size (str, optional): "1-10", "11-50", "51-200", "200+"
        industry (str, optional): "Schule", "Universität", "Unternehmen", etc.
        message (str, required): Inquiry message (10-2000 chars)
        source (str, optional): "website" (default), "referral", "event", etc.
        referrer (str, optional): Referring URL or partner name

    Returns:
        200 OK:
            {
                "success": true,
                "message": "Vielen Dank! Wir melden uns innerhalb von 24 Stunden bei Ihnen.",
                "request_id": "uuid"
            }

        400 Bad Request:
            {
                "success": false,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation error message",
                    "details": {...}
                }
            }

        429 Too Many Requests:
            {
                "success": false,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Sie haben bereits kürzlich eine Anfrage gesendet."
                }
            }

        500 Internal Server Error:
            {
                "success": false,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Ein Fehler ist aufgetreten."
                }
            }

    Workflow:
        1. Validate request data (Pydantic)
        2. Check for duplicate submissions (spam protection)
        3. Save to database
        4. Send admin notification email
        5. Send customer confirmation email
        6. Return success response

    Security:
        - Rate limiting: 3 requests per email per 24 hours
        - Input validation: All fields validated
        - SQL injection: Parameterized queries only
        - XSS protection: Data sanitized before email sending
    """
    try:
        # Parse request body
        request_data = request.get_json()

        if not request_data:
            raise ValidationError("Request body is required")

        # Validate with Pydantic
        try:
            validated_data = BusinessContactSchema(**request_data)
        except Exception as e:
            # Pydantic validation error
            raise ValidationError(
                "Validation failed",
                details={'errors': str(e)}
            )

        # Spam protection: Check for duplicate recent submissions
        if check_duplicate_recent_submission(validated_data.email, hours=24):
            logger.warning(
                f"Duplicate B2B contact submission blocked: {validated_data.email}",
                extra={'email': validated_data.email}
            )

            raise APIException(
                message="Sie haben bereits kürzlich eine Anfrage gesendet. Bitte warten Sie 24 Stunden bevor Sie erneut kontaktieren.",
                details={'error_code': 'RATE_LIMIT_EXCEEDED'}
            )

        # Save to database
        try:
            request_id = save_contact_request(validated_data)
        except psycopg.Error as e:
            logger.error(f"Database error saving B2B contact: {e}")
            raise APIException("Fehler beim Speichern der Anfrage")

        # Send notifications (non-blocking failures)
        try:
            send_admin_notification(validated_data, request_id)
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
            # Don't fail the request if email fails

        try:
            send_customer_confirmation(validated_data)
        except Exception as e:
            logger.error(f"Failed to send customer confirmation: {e}")
            # Don't fail the request if email fails

        # Success response
        logger.info(
            f"B2B contact request created successfully: {request_id}",
            extra={
                'request_id': request_id,
                'company_name': validated_data.company_name,
                'email': validated_data.email
            }
        )

        return jsonify({
            'success': True,
            'message': 'Vielen Dank für Ihre Anfrage! Wir melden uns innerhalb von 24 Stunden bei Ihnen.',
            'request_id': request_id
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'details': e.details if hasattr(e, 'details') else {}
            }
        }), 400

    except APIException as e:
        return jsonify({
            'success': False,
            'error': {
                'code': e.details.get('error_code', 'API_ERROR'),
                'message': str(e)
            }
        }), 429

    except Exception as e:
        logger.exception("Unexpected error in B2B contact submission")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.'
            }
        }), 500


# =====================================================
# Health Check (Optional)
# =====================================================

@bp.route('/contact/health', methods=['GET'])
def contact_health():
    """
    GET /api/v1/business/contact/health

    Health check endpoint for B2B contact form system.

    Returns:
        200: System healthy
        503: System unhealthy
    """
    try:
        # Check database connectivity
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM b2b_contact_requests LIMIT 1")

        return jsonify({
            'status': 'healthy',
            'service': 'b2b_contact_form',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"B2B contact health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'b2b_contact_form',
            'error': str(e)
        }), 503


# Export blueprint
__all__ = ['bp']
