"""
Privacy Core Module

Data privacy and anonymization services.

DSGVO-compliant data anonymization techniques:
- Data masking
- Pseudonymization (Art. 4(5))
- Generalization
- Data suppression
- K-anonymity

Usage:
    from src.core.privacy import DataAnonymizer

    # Anonymize email
    anon_email = DataAnonymizer.anonymize_email('user@example.com')

    # Pseudonymize user ID
    pseudo_id = DataAnonymizer.pseudonymize('user123')

    # Anonymize entire user data
    anon_data = DataAnonymizer.anonymize_user_data(user_data, level='full')
"""

from src.core.privacy.anonymizer import DataAnonymizer

__all__ = [
    'DataAnonymizer',
]
