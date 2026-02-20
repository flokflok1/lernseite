"""
B2B Contact Form API - Route Handlers (Part 2)

Contains the API endpoint for contact form submission and the health check.
Split from contact.py to comply with 500-line file limit (Quality Gate G01).

Author: LernSystemX Backend Team
Created: 2026-01-22
"""

from flask import request, jsonify
from datetime import datetime
import psycopg
import logging

from app.infrastructure.error_handling.exceptions import ValidationError, APIException

from .contact import (
    bp,
    BusinessContactSchema,
    save_contact_request,
    send_admin_notification,
    send_customer_confirmation,
    check_duplicate_recent_submission,
)
from app.infrastructure.persistence.repositories.core.base import BaseRepository

# Logger
logger = logging.getLogger(__name__)


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
        industry (str, optional): "Schule", "Universitat", "Unternehmen", etc.
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
                    "message": "Sie haben bereits kurzlich eine Anfrage gesendet."
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
# Health Check
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
        BaseRepository.ping_table('b2b_contact_requests')

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
