"""
Data Anonymization Module

DSGVO-compliant data anonymization and pseudonymization.

Techniques:
- Data masking (replacing sensitive data with fake data)
- Pseudonymization (replacing identifiers with pseudonyms)
- Generalization (reducing precision of data)
- Data suppression (removing sensitive attributes)
- K-anonymity (ensuring at least k individuals share same attributes)
"""

import hashlib
import secrets
import re
from typing import Optional, Dict, Any
from datetime import datetime


class DataAnonymizer:
    """
    Data anonymization service.

    DSGVO-compliant anonymization and pseudonymization of personal data.
    """

    @staticmethod
    def anonymize_email(email: str) -> str:
        """
        Anonymize email address.

        Example: john.doe@example.com → j***@example.com

        Args:
            email: Email address

        Returns:
            Anonymized email
        """
        if not email or '@' not in email:
            return '[ANONYMIZED]'

        local, domain = email.split('@', 1)
        if len(local) <= 1:
            anonymized_local = local[0] + '***'
        else:
            anonymized_local = local[0] + '***'

        return f"{anonymized_local}@{domain}"

    @staticmethod
    def anonymize_name(name: str) -> str:
        """
        Anonymize full name.

        Example: John Doe → J. D.

        Args:
            name: Full name

        Returns:
            Anonymized name
        """
        if not name:
            return '[ANONYMIZED]'

        parts = name.split()
        anonymized_parts = [f"{part[0]}." for part in parts if part]
        return ' '.join(anonymized_parts)

    @staticmethod
    def anonymize_ip(ip: str) -> str:
        """
        Anonymize IP address (remove last octet).

        Example: 192.168.1.100 → 192.168.1.0

        Args:
            ip: IP address

        Returns:
            Anonymized IP
        """
        if not ip:
            return '[ANONYMIZED]'

        # IPv4
        if '.' in ip:
            parts = ip.split('.')
            if len(parts) == 4:
                parts[-1] = '0'
                return '.'.join(parts)

        # IPv6
        if ':' in ip:
            parts = ip.split(':')
            if len(parts) >= 4:
                parts[-2:] = ['0', '0']
                return ':'.join(parts)

        return '[ANONYMIZED]'

    @staticmethod
    def pseudonymize(value: str, salt: Optional[str] = None) -> str:
        """
        Pseudonymize value using SHA-256 hash.

        Args:
            value: Value to pseudonymize
            salt: Optional salt for hashing

        Returns:
            Pseudonymized hash (64 chars)
        """
        if not value:
            return '[PSEUDONYMIZED]'

        if salt is None:
            salt = secrets.token_hex(16)

        salted_value = f"{salt}{value}"
        return hashlib.sha256(salted_value.encode()).hexdigest()

    @staticmethod
    def generalize_age(age: int) -> str:
        """
        Generalize age into age groups.

        Args:
            age: Exact age

        Returns:
            Age group (e.g., "18-24")
        """
        if age < 18:
            return "<18"
        elif age < 25:
            return "18-24"
        elif age < 35:
            return "25-34"
        elif age < 45:
            return "35-44"
        elif age < 55:
            return "45-54"
        elif age < 65:
            return "55-64"
        else:
            return "65+"

    @staticmethod
    def generalize_date(date: datetime) -> str:
        """
        Generalize datetime to year-month only.

        Args:
            date: Datetime object

        Returns:
            Generalized date (YYYY-MM)
        """
        if not date:
            return '[ANONYMIZED]'
        return date.strftime('%Y-%m')

    @staticmethod
    def suppress_field(value: Any) -> str:
        """
        Suppress sensitive field completely.

        Args:
            value: Any value

        Returns:
            Suppressed marker
        """
        return '[SUPPRESSED]'

    @staticmethod
    def anonymize_user_data(user_data: Dict[str, Any], level: str = 'full') -> Dict[str, Any]:
        """
        Anonymize user data dictionary.

        Args:
            user_data: User data dictionary
            level: Anonymization level ('full', 'partial', 'pseudonym')

        Returns:
            Anonymized user data
        """
        anonymized = user_data.copy()

        if level == 'full':
            # Full anonymization (DSGVO Art. 17)
            if 'email' in anonymized:
                anonymized['email'] = DataAnonymizer.anonymize_email(anonymized['email'])
            if 'name' in anonymized:
                anonymized['name'] = DataAnonymizer.anonymize_name(anonymized['name'])
            if 'first_name' in anonymized:
                anonymized['first_name'] = anonymized['first_name'][0] + '***'
            if 'last_name' in anonymized:
                anonymized['last_name'] = anonymized['last_name'][0] + '***'
            if 'ip_address' in anonymized:
                anonymized['ip_address'] = DataAnonymizer.anonymize_ip(anonymized['ip_address'])
            if 'phone' in anonymized:
                anonymized['phone'] = '[ANONYMIZED]'
            if 'address' in anonymized:
                anonymized['address'] = '[ANONYMIZED]'

        elif level == 'partial':
            # Partial anonymization (analytics use)
            if 'email' in anonymized:
                anonymized['email'] = DataAnonymizer.anonymize_email(anonymized['email'])
            if 'ip_address' in anonymized:
                anonymized['ip_address'] = DataAnonymizer.anonymize_ip(anonymized['ip_address'])
            if 'age' in anonymized:
                anonymized['age_group'] = DataAnonymizer.generalize_age(anonymized['age'])
                del anonymized['age']

        elif level == 'pseudonym':
            # Pseudonymization (internal analytics)
            if 'email' in anonymized:
                anonymized['email_hash'] = DataAnonymizer.pseudonymize(anonymized['email'])
                del anonymized['email']
            if 'user_id' in anonymized:
                anonymized['user_hash'] = DataAnonymizer.pseudonymize(anonymized['user_id'])

        return anonymized

    @staticmethod
    def is_anonymized(value: str) -> bool:
        """
        Check if value is already anonymized.

        Args:
            value: Value to check

        Returns:
            True if value is anonymized
        """
        anonymized_markers = ['[ANONYMIZED]', '[PSEUDONYMIZED]', '[SUPPRESSED]', '***']
        return any(marker in str(value) for marker in anonymized_markers)
