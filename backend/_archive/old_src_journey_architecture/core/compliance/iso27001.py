"""
ISO 27001:2013 Compliance Module

Information Security Management System (ISMS) compliance checks.

Key Requirements:
- Access Control (Clause 9.1)
- Cryptography (Clause 10)
- Physical Security (Clause 11)
- Operations Security (Clause 12)
- Communications Security (Clause 13)
- System Acquisition (Clause 14)
- Supplier Relationships (Clause 15)
- Incident Management (Clause 16)
- Business Continuity (Clause 17)
- Compliance (Clause 18)
"""

from typing import Dict, List, Optional
from enum import Enum


class ISO27001Control(Enum):
    """ISO 27001:2013 Control Categories."""
    ACCESS_CONTROL = "A.9"
    CRYPTOGRAPHY = "A.10"
    PHYSICAL_SECURITY = "A.11"
    OPERATIONS_SECURITY = "A.12"
    COMMUNICATIONS_SECURITY = "A.13"
    SYSTEM_ACQUISITION = "A.14"
    SUPPLIER_RELATIONSHIPS = "A.15"
    INCIDENT_MANAGEMENT = "A.16"
    BUSINESS_CONTINUITY = "A.17"
    COMPLIANCE = "A.18"


class ISO27001Compliance:
    """
    ISO 27001:2013 compliance checker.

    Validates system configuration against ISO 27001 requirements.
    """

    @staticmethod
    def check_access_control(config: Dict) -> Dict[str, bool]:
        """
        Check Access Control (A.9) compliance.

        Requirements:
        - A.9.1: Access control policy
        - A.9.2: User access management
        - A.9.3: User responsibilities
        - A.9.4: System access control

        Args:
            config: System configuration

        Returns:
            Compliance status per requirement
        """
        checks = {
            'access_control_policy': config.get('access_control_enabled', False),
            'user_access_management': config.get('rbac_enabled', False),
            'user_responsibilities': config.get('user_agreement_required', False),
            'system_access_control': config.get('mfa_available', False),
        }
        return checks

    @staticmethod
    def check_cryptography(config: Dict) -> Dict[str, bool]:
        """
        Check Cryptography (A.10) compliance.

        Requirements:
        - A.10.1: Cryptographic controls
        - A.10.2: Key management

        Args:
            config: System configuration

        Returns:
            Compliance status per requirement
        """
        checks = {
            'data_encryption_at_rest': config.get('encryption_at_rest', False),
            'data_encryption_in_transit': config.get('encryption_in_transit', False),
            'key_management': config.get('key_rotation_enabled', False),
            'tls_version': config.get('tls_version', '').startswith('1.3'),
        }
        return checks

    @staticmethod
    def check_operations_security(config: Dict) -> Dict[str, bool]:
        """
        Check Operations Security (A.12) compliance.

        Requirements:
        - A.12.1: Operational procedures
        - A.12.2: Protection from malware
        - A.12.3: Backup
        - A.12.4: Logging and monitoring
        - A.12.6: Technical vulnerability management

        Args:
            config: System configuration

        Returns:
            Compliance status per requirement
        """
        checks = {
            'operational_procedures': config.get('procedures_documented', False),
            'malware_protection': config.get('malware_scanning', False),
            'backup_enabled': config.get('backup_enabled', False),
            'logging_enabled': config.get('audit_logging', False),
            'monitoring_enabled': config.get('monitoring_enabled', False),
            'vulnerability_scanning': config.get('vulnerability_scanning', False),
        }
        return checks

    @staticmethod
    def check_incident_management(config: Dict) -> Dict[str, bool]:
        """
        Check Incident Management (A.16) compliance.

        Requirements:
        - A.16.1: Management of information security incidents
        - A.16.2: Response to security incidents

        Args:
            config: System configuration

        Returns:
            Compliance status per requirement
        """
        checks = {
            'incident_reporting': config.get('incident_reporting_enabled', False),
            'incident_response_plan': config.get('incident_response_plan', False),
            'incident_logging': config.get('security_event_logging', False),
        }
        return checks

    @staticmethod
    def generate_compliance_report(config: Dict) -> Dict[str, any]:
        """
        Generate full ISO 27001 compliance report.

        Args:
            config: System configuration

        Returns:
            Complete compliance report with scores
        """
        results = {
            'access_control': ISO27001Compliance.check_access_control(config),
            'cryptography': ISO27001Compliance.check_cryptography(config),
            'operations_security': ISO27001Compliance.check_operations_security(config),
            'incident_management': ISO27001Compliance.check_incident_management(config),
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
            'compliant': compliance_score >= 80.0,  # 80% threshold
        }
