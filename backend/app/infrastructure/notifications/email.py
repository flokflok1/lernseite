"""
Email Service Utility

Handles email sending with template rendering support.
Supports multiple email providers: SMTP, SendGrid, AWS SES.

Usage:
    from app.infrastructure.notifications.email import send_email

    send_email(
        to_email='customer@example.com',
        subject='Welcome',
        template='welcome.html',
        context={'name': 'John'}
    )
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from flask import current_app, render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending emails with template support.

    Supports:
    - SMTP (Gmail, custom server)
    - SendGrid (TODO: Implement when API key available)
    - AWS SES (TODO: Implement when credentials available)
    """

    def __init__(self, app=None):
        """Initialize email service."""
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with Flask app."""
        self.app = app

        # Email configuration
        self.smtp_server = app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = app.config.get('SMTP_PORT', 587)
        self.smtp_username = app.config.get('SMTP_USERNAME')
        self.smtp_password = app.config.get('SMTP_PASSWORD')
        self.smtp_use_tls = app.config.get('SMTP_USE_TLS', True)

        # Sender info
        self.sender_email = app.config.get('SENDER_EMAIL', 'noreply@lernsystemx.com')
        self.sender_name = app.config.get('SENDER_NAME', 'LernSystemX')

        # Provider selection
        self.email_provider = app.config.get('EMAIL_PROVIDER', 'smtp').lower()

        logger.info(f"Email service initialized with provider: {self.email_provider}")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email with HTML and optional plain text body.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            text_body: Plain text email body (optional, auto-generated if not provided)
            from_email: Sender email (default: config SENDER_EMAIL)
            from_name: Sender name (default: config SENDER_NAME)
            cc: List of CC recipients
            bcc: List of BCC recipients
            reply_to: Reply-to email address

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Use defaults if not provided
            from_email = from_email or self.sender_email
            from_name = from_name or self.sender_name

            # Auto-generate text body if not provided
            if text_body is None:
                text_body = self._html_to_text(html_body)

            # Send via configured provider
            if self.email_provider == 'smtp':
                return self._send_via_smtp(
                    to_email=to_email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                    from_email=from_email,
                    from_name=from_name,
                    cc=cc,
                    bcc=bcc,
                    reply_to=reply_to
                )
            elif self.email_provider == 'sendgrid':
                # TODO: Implement SendGrid when API key is available
                logger.warning("SendGrid not implemented yet, falling back to SMTP")
                return self._send_via_smtp(
                    to_email=to_email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                    from_email=from_email,
                    from_name=from_name,
                    cc=cc,
                    bcc=bcc,
                    reply_to=reply_to
                )
            elif self.email_provider == 'ses':
                # TODO: Implement AWS SES when credentials available
                logger.warning("AWS SES not implemented yet, falling back to SMTP")
                return self._send_via_smtp(
                    to_email=to_email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                    from_email=from_email,
                    from_name=from_name,
                    cc=cc,
                    bcc=bcc,
                    reply_to=reply_to
                )
            else:
                logger.error(f"Unknown email provider: {self.email_provider}")
                return False

        except Exception as e:
            logger.exception(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_template_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        **kwargs
    ) -> bool:
        """
        Send email using Jinja2 template.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            template_name: Template filename (e.g., 'emails/welcome.html')
            context: Dictionary of variables for template rendering
            **kwargs: Additional arguments passed to send_email()

        Returns:
            True if email sent successfully, False otherwise

        Example:
            send_template_email(
                to_email='user@example.com',
                subject='Welcome to LernSystemX',
                template_name='emails/welcome.html',
                context={'name': 'John Doe', 'company': 'Acme Inc'}
            )
        """
        try:
            # Render HTML template
            html_body = render_template(template_name, **context)

            # Try to render plain text version
            text_template = template_name.replace('.html', '.txt')
            text_body = None

            try:
                text_body = render_template(text_template, **context)
            except Exception:
                # Text template doesn't exist, will be auto-generated
                logger.debug(f"No text template found for {template_name}, will auto-generate")

            # Send email
            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                **kwargs
            )

        except Exception as e:
            logger.exception(f"Failed to send template email: {str(e)}")
            return False

    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
        from_email: str,
        from_name: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP server.

        Supports Gmail, custom SMTP servers with TLS/SSL.
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((from_name, from_email))
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)

            if reply_to:
                msg['Reply-To'] = reply_to

            # Attach plain text and HTML parts
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')

            msg.attach(part1)
            msg.attach(part2)

            # Build recipient list
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # Connect to SMTP server
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

            # Login if credentials provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            # Send email
            server.sendmail(from_email, recipients, msg.as_string())
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"Failed to send email via SMTP: {str(e)}")
            return False

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text (simple implementation).

        For production, consider using libraries like:
        - html2text
        - BeautifulSoup
        - markdownify
        """
        import re

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)

        # Replace common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text


# Global email service instance
email_service = EmailService()


# Convenience function
def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    **kwargs
) -> bool:
    """
    Convenience function for sending template emails.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        template_name: Template filename (e.g., 'emails/b2b/admin_notification.html')
        context: Dictionary of variables for template rendering
        **kwargs: Additional arguments (cc, bcc, reply_to, etc.)

    Returns:
        True if email sent successfully, False otherwise

    Example:
        send_email(
            to_email='admin@lernsystemx.com',
            subject='New B2B Contact Request',
            template_name='emails/b2b/admin_notification.html',
            context={
                'company_name': 'Acme Inc',
                'contact_person': 'John Doe',
                'email': 'john@acme.com',
                ...
            }
        )
    """
    return email_service.send_template_email(
        to_email=to_email,
        subject=subject,
        template_name=template_name,
        context=context,
        **kwargs
    )


def init_email_service(app):
    """
    Initialize email service with Flask app.

    Call this from app factory (app/__init__.py):
        from app.infrastructure.notifications.email import init_email_service
        init_email_service(app)
    """
    email_service.init_app(app)
    return email_service
