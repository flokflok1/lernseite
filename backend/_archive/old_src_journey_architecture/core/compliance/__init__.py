"""
Compliance Core Module

Security and regulatory compliance systems.

Standards:
- ISO 27001:2013 (Information Security Management)
- DSGVO/GDPR (EU Data Protection)
- BSI IT-Grundschutz (German IT Security)

Usage:
    from src.core.compliance import ISO27001Compliance, DSGVOCompliance, BSICompliance

    # Generate compliance reports
    iso_report = ISO27001Compliance.generate_compliance_report(config)
    dsgvo_report = DSGVOCompliance.generate_compliance_report(config)
    bsi_report = BSICompliance.generate_compliance_report(config)
"""

from src.core.compliance.iso27001 import ISO27001Compliance, ISO27001Control
from src.core.compliance.dsgvo import DSGVOCompliance, DSGVORight
from src.core.compliance.bsi import BSICompliance, BSIModule

__all__ = [
    # ISO 27001
    'ISO27001Compliance',
    'ISO27001Control',

    # DSGVO/GDPR
    'DSGVOCompliance',
    'DSGVORight',

    # BSI
    'BSICompliance',
    'BSIModule',
]
