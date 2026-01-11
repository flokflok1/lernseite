"""
DSGVO/GDPR Compliance Module

General Data Protection Regulation (EU) 2016/679 compliance.

Key Principles:
- Lawfulness, fairness, transparency (Art. 5)
- Purpose limitation (Art. 5)
- Data minimization (Art. 5)
- Accuracy (Art. 5)
- Storage limitation (Art. 5)
- Integrity and confidentiality (Art. 5)
- Accountability (Art. 5)

Rights:
- Right to access (Art. 15)
- Right to rectification (Art. 16)
- Right to erasure ("Right to be forgotten") (Art. 17)
- Right to data portability (Art. 20)
- Right to object (Art. 21)
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class DSGVORight(Enum):
    """DSGVO Data Subject Rights."""
    ACCESS = "Art. 15"  # Right to access
    RECTIFICATION = "Art. 16"  # Right to rectification
    ERASURE = "Art. 17"  # Right to be forgotten
    RESTRICTION = "Art. 18"  # Right to restriction
    PORTABILITY = "Art. 20"  # Right to data portability
    OBJECT = "Art. 21"  # Right to object


class DSGVOCompliance:
    """
    DSGVO/GDPR compliance checker and helper.

    Validates system compliance with EU GDPR requirements.
    """

    # Data retention periods (in days)
    DEFAULT_RETENTION_PERIOD = 730  # 2 years
    LOG_RETENTION_PERIOD = 90  # 3 months
    BACKUP_RETENTION_PERIOD = 365  # 1 year

    @staticmethod
    def check_lawfulness(config: Dict) -> Dict[str, bool]:
        """
        Check lawfulness, fairness, transparency (Art. 5(1)a).

        Requirements:
        - Legal basis for processing documented
        - Privacy policy available
        - Consent mechanism implemented
        - Transparent data processing

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'legal_basis_documented': config.get('legal_basis_documented', False),
            'privacy_policy_available': config.get('privacy_policy_url') is not None,
            'consent_mechanism': config.get('consent_mechanism_enabled', False),
            'data_processing_transparency': config.get('processing_activities_documented', False),
        }
        return checks

    @staticmethod
    def check_data_minimization(config: Dict) -> Dict[str, bool]:
        """
        Check data minimization (Art. 5(1)c).

        Requirements:
        - Only necessary data collected
        - Optional fields marked
        - Data deletion after purpose fulfilled

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'minimal_data_collection': config.get('data_minimization_policy', False),
            'optional_fields_marked': config.get('optional_fields_identified', False),
            'automated_deletion': config.get('automated_data_deletion', False),
        }
        return checks

    @staticmethod
    def check_storage_limitation(config: Dict) -> Dict[str, bool]:
        """
        Check storage limitation (Art. 5(1)e).

        Requirements:
        - Retention periods defined
        - Automated deletion after retention period
        - Regular data review

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'retention_periods_defined': config.get('retention_policy_defined', False),
            'automated_deletion_enabled': config.get('automated_deletion_enabled', False),
            'regular_data_review': config.get('data_review_schedule', False),
        }
        return checks

    @staticmethod
    def check_data_subject_rights(config: Dict) -> Dict[str, bool]:
        """
        Check data subject rights implementation.

        Requirements:
        - Right to access (Art. 15)
        - Right to rectification (Art. 16)
        - Right to erasure (Art. 17)
        - Right to data portability (Art. 20)

        Args:
            config: System configuration

        Returns:
            Compliance status per right
        """
        checks = {
            'right_to_access': config.get('data_export_enabled', False),
            'right_to_rectification': config.get('profile_editing_enabled', False),
            'right_to_erasure': config.get('account_deletion_enabled', False),
            'right_to_portability': config.get('data_portability_format') == 'json',
        }
        return checks

    @staticmethod
    def check_security_measures(config: Dict) -> Dict[str, bool]:
        """
        Check security measures (Art. 32).

        Requirements:
        - Encryption at rest
        - Encryption in transit
        - Access control
        - Regular security testing

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'encryption_at_rest': config.get('encryption_at_rest', False),
            'encryption_in_transit': config.get('tls_enabled', False),
            'access_control': config.get('rbac_enabled', False),
            'security_testing': config.get('security_testing_schedule', False),
            'pseudonymization': config.get('pseudonymization_enabled', False),
        }
        return checks

    @staticmethod
    def check_breach_notification(config: Dict) -> Dict[str, bool]:
        """
        Check breach notification procedures (Art. 33, 34).

        Requirements:
        - Breach detection mechanisms
        - Notification procedures documented
        - 72-hour notification capability

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'breach_detection': config.get('breach_detection_enabled', False),
            'notification_procedures': config.get('breach_notification_procedures', False),
            'notification_contacts': config.get('dpo_contact') is not None,
        }
        return checks

    @staticmethod
    def is_data_expired(created_at: datetime, retention_days: int = DEFAULT_RETENTION_PERIOD) -> bool:
        """
        Check if data has exceeded retention period.

        Args:
            created_at: Data creation timestamp
            retention_days: Retention period in days

        Returns:
            True if data should be deleted
        """
        retention_period = timedelta(days=retention_days)
        return datetime.utcnow() - created_at > retention_period

    @staticmethod
    def generate_compliance_report(config: Dict) -> Dict[str, any]:
        """
        Generate full DSGVO compliance report.

        Args:
            config: System configuration

        Returns:
            Complete compliance report with scores
        """
        results = {
            'lawfulness': DSGVOCompliance.check_lawfulness(config),
            'data_minimization': DSGVOCompliance.check_data_minimization(config),
            'storage_limitation': DSGVOCompliance.check_storage_limitation(config),
            'data_subject_rights': DSGVOCompliance.check_data_subject_rights(config),
            'security_measures': DSGVOCompliance.check_security_measures(config),
            'breach_notification': DSGVOCompliance.check_breach_notification(config),
        }

        # Calculate compliance score
        total_checks = sum(len(checks) for checks in results.values())
        passed_checks = sum(
            sum(1 for passed in checks.values() if passed)
            for checks in results.values()
        )
        compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        return {
            'compliance_score': round(compliance_score, 2),
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'results': results,
            'compliant': compliance_score >= 90.0,  # 90% threshold for GDPR
            'dpo_required': True,  # Always required for educational platforms
        }
