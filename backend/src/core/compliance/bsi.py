"""
BSI (Bundesamt für Sicherheit in der Informationstechnik) Compliance Module

German IT security standards and guidelines.

Key Standards:
- BSI IT-Grundschutz (IT Baseline Protection)
- BSI C5 (Cloud Computing Compliance Controls Catalogue)
- Technical Guidelines (TR)
"""

from typing import Dict, List
from enum import Enum


class BSIModule(Enum):
    """BSI IT-Grundschutz Module Categories."""
    ISMS = "ISMS"  # Information Security Management
    ORP = "ORP"  # Organization and Personnel
    CON = "CON"  # Concepts and Procedures
    OPS = "OPS"  # Operations
    DER = "DER"  # Detection and Response
    APP = "APP"  # Applications
    SYS = "SYS"  # IT Systems
    IND = "IND"  # Industrial IT
    NET = "NET"  # Networks and Communication
    INF = "INF"  # Infrastructure


class BSICompliance:
    """
    BSI IT-Grundschutz compliance checker.

    Validates system against German BSI security standards.
    """

    @staticmethod
    def check_isms(config: Dict) -> Dict[str, bool]:
        """
        Check ISMS (Information Security Management System).

        Requirements:
        - Security policy documented
        - Risk assessment performed
        - Security organization defined
        - Security awareness training

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'security_policy': config.get('security_policy_documented', False),
            'risk_assessment': config.get('risk_assessment_performed', False),
            'security_organization': config.get('security_roles_defined', False),
            'security_training': config.get('security_training_program', False),
        }
        return checks

    @staticmethod
    def check_operations(config: Dict) -> Dict[str, bool]:
        """
        Check OPS (Operations) module.

        Requirements:
        - Change management
        - Backup and recovery
        - Logging and monitoring
        - Patch management

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'change_management': config.get('change_management_process', False),
            'backup_enabled': config.get('backup_enabled', False),
            'logging_enabled': config.get('centralized_logging', False),
            'monitoring_enabled': config.get('monitoring_enabled', False),
            'patch_management': config.get('patch_management_process', False),
        }
        return checks

    @staticmethod
    def check_detection_response(config: Dict) -> Dict[str, bool]:
        """
        Check DER (Detection and Response) module.

        Requirements:
        - Incident detection
        - Incident response plan
        - Security event logging
        - Forensic capabilities

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'incident_detection': config.get('ids_enabled', False),
            'incident_response_plan': config.get('incident_response_plan', False),
            'security_event_logging': config.get('security_logging', False),
            'forensic_capabilities': config.get('forensic_logging', False),
        }
        return checks

    @staticmethod
    def check_applications(config: Dict) -> Dict[str, bool]:
        """
        Check APP (Applications) module.

        Requirements:
        - Secure development lifecycle
        - Input validation
        - Error handling
        - Secure session management

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'secure_development': config.get('sdlc_implemented', False),
            'input_validation': config.get('input_validation_enabled', False),
            'error_handling': config.get('secure_error_handling', False),
            'session_management': config.get('secure_session_mgmt', False),
            'authentication': config.get('strong_authentication', False),
        }
        return checks

    @staticmethod
    def check_networks(config: Dict) -> Dict[str, bool]:
        """
        Check NET (Networks) module.

        Requirements:
        - Network segmentation
        - Firewall protection
        - VPN for remote access
        - TLS/SSL encryption

        Args:
            config: System configuration

        Returns:
            Compliance status
        """
        checks = {
            'network_segmentation': config.get('network_segments_defined', False),
            'firewall_enabled': config.get('firewall_enabled', False),
            'vpn_available': config.get('vpn_for_remote_access', False),
            'tls_encryption': config.get('tls_version', '').startswith('1.3'),
        }
        return checks

    @staticmethod
    def generate_compliance_report(config: Dict) -> Dict[str, any]:
        """
        Generate full BSI IT-Grundschutz compliance report.

        Args:
            config: System configuration

        Returns:
            Complete compliance report with scores
        """
        results = {
            'isms': BSICompliance.check_isms(config),
            'operations': BSICompliance.check_operations(config),
            'detection_response': BSICompliance.check_detection_response(config),
            'applications': BSICompliance.check_applications(config),
            'networks': BSICompliance.check_networks(config),
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
            'compliant': compliance_score >= 85.0,  # 85% threshold for BSI
            'grundschutz_level': BSICompliance._get_grundschutz_level(compliance_score),
        }

    @staticmethod
    def _get_grundschutz_level(score: float) -> str:
        """
        Get IT-Grundschutz protection level based on score.

        Args:
            score: Compliance score (0-100)

        Returns:
            Protection level (Basis, Standard, Hoch)
        """
        if score >= 95:
            return "Hoch"  # High protection level
        elif score >= 85:
            return "Standard"  # Standard protection level
        elif score >= 70:
            return "Basis"  # Basic protection level
        else:
            return "Unzureichend"  # Insufficient
