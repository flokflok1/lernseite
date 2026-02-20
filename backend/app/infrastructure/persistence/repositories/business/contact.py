"""
Business Contact Repository

Database operations for B2B contact form submissions:
- Save contact requests
- Duplicate/spam detection

Uses psycopg3 - no ORM.
"""

from typing import Dict, Any
from psycopg.rows import dict_row

from app.infrastructure.persistence.database.connection import get_db_connection


class BusinessContactRepository:
    """Repository for B2B contact request database operations."""

    @classmethod
    def save_contact_request(cls, data: Dict[str, Any]) -> str:
        """
        Save a B2B contact request to the database.

        Args:
            data: Dict with company_name, contact_person, email, phone,
                  company_size, industry, message, source, referrer

        Returns:
            Request ID (UUID string)
        """
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "INSERT INTO b2b_contact_requests "
                    "(company_name, contact_person, email, phone, "
                    "company_size, industry, message, source, referrer, status) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'new') "
                    "RETURNING id",
                    (
                        data['company_name'],
                        data['contact_person'],
                        data['email'],
                        data['phone'],
                        data.get('company_size'),
                        data.get('industry'),
                        data['message'],
                        data.get('source', 'website'),
                        data.get('referrer'),
                    )
                )
                result = cur.fetchone()
                conn.commit()
                return result['id']

    @classmethod
    def check_duplicate_recent(cls, email: str, hours: int = 24) -> bool:
        """
        Check if email has submitted a request recently (spam protection).

        Args:
            email: Email address to check
            hours: Lookback window in hours (default 24)

        Returns:
            True if duplicate found within timeframe
        """
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT COUNT(*) as cnt FROM b2b_contact_requests "
                    "WHERE email = %s AND created_at > NOW() - make_interval(hours => %s)",
                    (email, hours)
                )
                result = cur.fetchone()
                return result['cnt'] > 0 if result else False
