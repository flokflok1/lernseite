# app/repositories/storage_enforcement_config_seed.py

"""
Seed data für Storage Enforcement Configs.

Initialisiert die Datenbank mit Standard-Enforcement-Regeln.
Diese können später pro Organisation angepasst werden.

User's Message: "das sollte man aber flexibel einstellen können alles"
"""

import json
from typing import Dict, Any
from app.repositories.storage_enforcement_config import StorageEnforcementConfigRepository


class StorageEnforcementConfigSeed:
    """
    Seed-Daten für Storage Enforcement Configs.

    Initialisiert System-Default und Beispiel-Configs für B2C/B2B.
    """

    @staticmethod
    def get_default_actions_json() -> Dict[str, Any]:
        """
        Standardmäßige Enforcement Levels.

        Diese sind die "klassischen" Levels aus Section 3.8:
        0-50% = Green
        50-80% = Yellow
        80-100% = Red
        >100% = Black
        >100% nach Grace Period = Alert
        """
        return {
            "0_to_50": {
                "status": "green",
                "upload": "allowed",
                "download": "allowed",
                "notifications": "none",
                "display_message": "✅ Plenty of storage available"
            },
            "50_to_80": {
                "status": "yellow",
                "upload": "allowed",
                "download": "allowed",
                "notifications": "weekly_reminder",
                "display_message": "🟡 Storage usage at {percent}%. Consider cleaning up.",
                "encourage_cleanup": False
            },
            "80_to_100": {
                "status": "red",
                "upload": "allowed_with_warning",
                "download": "allowed",
                "notifications": "daily_warning",
                "display_message": "🔴 Storage usage at {percent}%. Please delete files to free space.",
                "encourage_cleanup": True,
                "suggest_cleanup_candidates": True
            },
            "100_plus": {
                "status": "black",
                "upload": "blocked",
                "download": "allowed",
                "new_courses": "blocked",
                "notifications": "critical",
                "grace_period_days": 30,
                "display_message": "🚫 Storage quota exceeded ({percent}%). You have {grace_period_days} days to delete files.",
                "force_cleanup": True,
                "allow_deletions_only": True
            },
            "grace_period_expired": {
                "status": "alert",
                "upload": "blocked",
                "download": "readonly",
                "new_courses": "blocked",
                "new_lessons": "blocked",
                "notifications": "critical",
                "display_message": "🛑 Grace period expired. Account in READ-ONLY mode. Contact support.",
                "action_required": True,
                "contact_support": True
            }
        }

    @staticmethod
    def get_b2c_hard_enforcement() -> Dict[str, Any]:
        """
        B2C Enforcement: HART (strict limits).

        Für Individual-Nutzer mit Subscription:
        - Strictes Enforcement bei 100%
        - Kurze Grace Period (7-14 Tage)
        - Keine Leniency
        """
        return {
            "name": "B2C Hard Enforcement",
            "enforcement_type": "hard",
            "warning_threshold_percent": 75,
            "critical_threshold_percent": 90,
            "hard_limit_percent": 100,
            "grace_period_days": 7,  # Nur 7 Tage
            "auto_cleanup_soft_deleted_days": 30,
            "warning_frequency": "daily",
            "send_email_warnings": True,
            "send_ui_notifications": True,
            "actions_json": StorageEnforcementConfigSeed.get_default_actions_json()
        }

    @staticmethod
    def get_b2b_soft_enforcement() -> Dict[str, Any]:
        """
        B2B Enforcement: WEICH (lenient limits).

        Für Organisationen/Schulen mit Administratoren:
        - Warnungen statt sofortige Blockade
        - Längere Grace Period (30 Tage)
        - Admin kann quotas erhöhen
        """
        return {
            "name": "B2B Soft Enforcement",
            "enforcement_type": "soft",
            "warning_threshold_percent": 85,  # Erst später warnen
            "critical_threshold_percent": 95,
            "hard_limit_percent": 110,  # Etwas über 100% erlaubt
            "grace_period_days": 30,  # 30 Tage zum Aufräumen
            "auto_cleanup_soft_deleted_days": 45,
            "warning_frequency": "weekly",  # Weniger aggressive Warnungen
            "send_email_warnings": True,
            "send_ui_notifications": True,
            "actions_json": {
                "0_to_50": {
                    "status": "green",
                    "upload": "allowed",
                    "download": "allowed",
                    "notifications": "none"
                },
                "50_to_85": {
                    "status": "yellow",
                    "upload": "allowed",
                    "download": "allowed",
                    "notifications": "weekly_reminder",
                    "suggest_admin_contact": False
                },
                "85_to_100": {
                    "status": "orange",
                    "upload": "allowed_with_warning",
                    "download": "allowed",
                    "notifications": "weekly_alert",
                    "suggest_admin_contact": True,
                    "display_message": "🟠 Storage at {percent}%. Contact admin to request increase."
                },
                "100_plus": {
                    "status": "red",
                    "upload": "allowed_with_warning",  # Noch erlaubt!
                    "download": "allowed",
                    "notifications": "daily_alert",
                    "grace_period_days": 30,
                    "suggest_admin_contact": True,
                    "display_message": "🔴 Storage quota exceeded. Contact admin to request increase or delete files."
                },
                "grace_period_expired": {
                    "status": "black",
                    "upload": "blocked",
                    "download": "allowed",
                    "notifications": "critical",
                    "contact_support": True,
                    "display_message": "⚫ Grace period expired. Please contact admin immediately."
                }
            }
        }

    @staticmethod
    def seed_default_configs(repo: StorageEnforcementConfigRepository) -> Dict[str, Any]:
        """
        Seed die Standardkonfigurationen in die Datenbank.

        Args:
            repo: StorageEnforcementConfigRepository

        Returns:
            Dict mit Informationen über erstellte Configs
        """
        results = {
            'created': [],
            'skipped': [],
            'errors': []
        }

        # 1. Hole oder erstelle System-Default
        default_config = repo.find_system_default()

        if not default_config:
            try:
                b2c_config = StorageEnforcementConfigSeed.get_b2c_hard_enforcement()
                created = repo.create({
                    'is_system_default': True,
                    **b2c_config
                })
                results['created'].append({
                    'type': 'system_default',
                    'id': created.id,
                    'enforcement_type': created.enforcement_type
                })
            except Exception as e:
                results['errors'].append({
                    'type': 'system_default',
                    'error': str(e)
                })
        else:
            results['skipped'].append({
                'type': 'system_default',
                'reason': 'Already exists',
                'id': default_config.id
            })

        return results

    @staticmethod
    def seed_organisation_config(
        repo: StorageEnforcementConfigRepository,
        organisation_id: str,
        enforcement_type: str = 'soft'
    ) -> Dict[str, Any]:
        """
        Erstelle oder update Enforcement Config für eine Organisation.

        Args:
            repo: StorageEnforcementConfigRepository
            organisation_id: Organisation ID
            enforcement_type: 'hard' (B2C) oder 'soft' (B2B)

        Returns:
            Erstellte/aktualisierte Config
        """
        # Prüfe ob schon vorhanden
        existing = repo.find_by_organisation(organisation_id)

        if existing:
            return {
                'status': 'skipped',
                'reason': 'Config already exists',
                'config_id': existing.id
            }

        # Lade Template basierend auf Type
        if enforcement_type == 'soft':
            config_data = StorageEnforcementConfigSeed.get_b2b_soft_enforcement()
        else:
            config_data = StorageEnforcementConfigSeed.get_b2c_hard_enforcement()

        # Erstelle
        created = repo.create({
            'organisation_id': organisation_id,
            **config_data
        })

        return {
            'status': 'created',
            'config_id': created.id,
            'organisation_id': organisation_id,
            'enforcement_type': created.enforcement_type,
            'warning_threshold_percent': created.warning_threshold_percent,
            'grace_period_days': created.grace_period_days
        }


# Usage Examples:

"""
# In einem Initialization Script oder Management Command:

from app.database import get_db_connection
from app.repositories.storage_enforcement_config import StorageEnforcementConfigRepository
from app.repositories.storage_enforcement_config_seed import StorageEnforcementConfigSeed

# Initialize default configs
with get_db_connection() as conn:
    repo = StorageEnforcementConfigRepository(conn)

    # Seed System-Default
    results = StorageEnforcementConfigSeed.seed_default_configs(repo)
    print("Seeded:", results)

    # Erstelle Config für eine Organisation
    org_result = StorageEnforcementConfigSeed.seed_organisation_config(
        repo,
        organisation_id='org-gymnasium-muenchen',
        enforcement_type='soft'  # B2B: weich
    )
    print("Created:", org_result)
"""
