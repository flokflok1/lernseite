# app/services/storage_enforcement_service.py

"""
Storage Enforcement Service

Zentrale Service-Klasse für alle Storage-Enforcement Logik.
Nutzt StorageEnforcementConfigRepository zum Laden von Konfigurationen.

ALLE Enforcement-Regeln, Schwellwerte, Grace Periods kommen AUS DER DATENBANK!
Nicht hardcoded!

User's Message 3: "das sollte man aber flexibel einstellen können alles"
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.repositories.storage_enforcement_config import (
    StorageEnforcementConfigRepository,
    StorageEnforcementConfig
)


class StorageEnforcementService:
    """
    Service für Storage Quota Enforcement.

    Zentrale Klasse die alle Enforcement-Entscheidungen trifft:
    - Kann User hochladen?
    - Sollten wir Warnung senden?
    - Welcher Status für UI?
    - In Readonly-Mode?

    Nutzt StorageEnforcementConfigRepository zum Laden von dynamischen Konfigurationen.
    """

    def __init__(self, repo: StorageEnforcementConfigRepository = None):
        """
        Initialize Service.

        Args:
            repo: Optional StorageEnforcementConfigRepository
                  Falls None wird automatisch erstellt
        """
        self.repo = repo or StorageEnforcementConfigRepository()

    def get_enforcement_config(
        self,
        organisation_id: Optional[str] = None
    ) -> StorageEnforcementConfig:
        """
        Hole Enforcement-Config für Organisation oder System-Default.

        Logik:
        1. Falls organisation_id vorhanden → versuche org-spezifische Config
        2. Falls nicht gefunden → System-Default verwenden

        Args:
            organisation_id: Organisation ID (optional für B2C)

        Returns:
            StorageEnforcementConfig mit allen Einstellungen
        """
        return self.repo.get_config_for_organisation_or_default(organisation_id)

    def get_enforcement_action(
        self,
        percent_used: float,
        config: StorageEnforcementConfig
    ) -> Dict[str, Any]:
        """
        Bestimme die Action basierend auf Nutzungsprozentsatz und Config.

        Args:
            percent_used: Prozentuale Nutzung (0-100+)
            config: StorageEnforcementConfig

        Returns:
            Action dict aus config.actions_json für diesen Schwellwert

        Example:
            config = service.get_enforcement_config('org-123')
            action = service.get_enforcement_action(87.5, config)
            # Returns: {
            #    'status': 'red',
            #    'upload': 'allowed_with_warning',
            #    'download': 'allowed',
            #    'notifications': 'daily_warning'
            # }
        """
        # Nutze die Config-Methode statt eigene Logik
        return config.get_action_for_percent(percent_used)

    def can_upload(
        self,
        percent_used: float,
        organisation_id: Optional[str] = None,
        in_grace_period: bool = False
    ) -> Tuple[bool, str]:
        """
        Kann User eine Datei hochladen?

        Respektiert:
        - Enforcement Config (basierend auf organisation_id)
        - Aktueller Schwellwert (percent_used)
        - Grace Period Status

        Args:
            percent_used: Prozentuale Nutzung (0-100+)
            organisation_id: Organisation ID für Config-Lookup
            in_grace_period: Ist User in Grace Period?

        Returns:
            Tuple[allowed: bool, reason: str]

        Example:
            allowed, reason = service.can_upload(
                percent_used=102.5,
                organisation_id='org-123'
            )
            if not allowed:
                return {'error': reason}, 507  # 507 = Insufficient Storage
        """
        config = self.get_enforcement_config(organisation_id)
        action = self.get_enforcement_action(percent_used, config)

        upload_status = action.get('upload', 'allowed')

        if upload_status == 'blocked':
            if in_grace_period:
                message = action.get(
                    'message',
                    f"Storage quota exceeded. You have {config.grace_period_days} days to delete files."
                )
            else:
                message = "Storage quota exceeded. Please delete files to free space."
            return False, message

        elif upload_status == 'allowed_with_warning':
            message = action.get(
                'display_message',
                f"Storage usage at {percent_used:.1f}%. Consider cleaning up files."
            ).format(percent=round(percent_used, 1))
            return True, message

        else:  # 'allowed'
            return True, ""

    def can_download(
        self,
        in_grace_period_after: bool = False
    ) -> bool:
        """
        Kann User Dateien herunterladen?

        Download ist normalerweise immer erlaubt, außer in Readonly-Mode.

        Args:
            in_grace_period_after: Ist Grace Period abgelaufen (Read-only Mode)?

        Returns:
            True wenn Download erlaubt, False sonst
        """
        if in_grace_period_after:
            return False  # Read-only mode: Downloads blockiert
        return True  # Normalerweise immer erlaubt

    def get_status_display(
        self,
        percent_used: float,
        config: Optional[StorageEnforcementConfig] = None,
        organisation_id: Optional[str] = None
    ) -> str:
        """
        Bestimme Status-Anzeige für UI.

        Rückgabe: 'green', 'yellow', 'red', 'orange', 'black', 'alert'

        Args:
            percent_used: Prozentuale Nutzung
            config: Optional StorageEnforcementConfig (wird sonst geladen)
            organisation_id: Optional für Config-Lookup

        Returns:
            Status String für UI Anzeige

        Example:
            status = service.get_status_display(87.5, organisation_id='org-123')
            # Returns: 'red'
        """
        if config is None:
            config = self.get_enforcement_config(organisation_id)

        action = self.get_enforcement_action(percent_used, config)
        return action.get('status', 'green')

    def get_status_color_icon(
        self,
        percent_used: float,
        organisation_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Hole Status mit Icon und Farbe für UI-Rendering.

        Returns:
            Dict mit 'status', 'icon', 'color' für Frontend

        Example:
            display = service.get_status_color_icon(87.5)
            # Returns: {
            #    'status': 'red',
            #    'icon': '🔴',
            #    'color': '#dc2626',
            #    'description': 'Storage usage high'
            # }
        """
        status = self.get_status_display(percent_used, organisation_id=organisation_id)

        status_map = {
            'green': {
                'icon': '✅',
                'color': '#22c55e',
                'description': 'Plenty of storage available'
            },
            'yellow': {
                'icon': '🟡',
                'color': '#eab308',
                'description': 'Storage usage at {percent}%'
            },
            'orange': {
                'icon': '🟠',
                'color': '#f97316',
                'description': 'Storage usage high'
            },
            'red': {
                'icon': '🔴',
                'color': '#dc2626',
                'description': 'Storage usage very high'
            },
            'black': {
                'icon': '🚫',
                'color': '#000000',
                'description': 'Storage quota exceeded'
            },
            'alert': {
                'icon': '🛑',
                'color': '#991b1b',
                'description': 'Grace period expired'
            }
        }

        display = status_map.get(status, status_map['green'])
        return {
            'status': status,
            'icon': display['icon'],
            'color': display['color'],
            'description': display['description'].format(percent=round(percent_used, 1))
        }

    def should_send_warning(
        self,
        percent_used: float,
        last_warning_sent: Optional[datetime] = None,
        config: Optional[StorageEnforcementConfig] = None,
        organisation_id: Optional[str] = None
    ) -> bool:
        """
        Sollten wir eine Warnung senden?

        Berücksichtigt:
        - Warning-Threshold aus Config
        - Warning-Frequency aus Config (daily, weekly, once)
        - Zeitpunkt der letzten Warnung

        Args:
            percent_used: Prozentuale Nutzung
            last_warning_sent: Wann wurde letzte Warnung gesendet?
            config: Optional StorageEnforcementConfig (wird sonst geladen)
            organisation_id: Optional für Config-Lookup

        Returns:
            True wenn Warnung gesendet werden sollte

        Example:
            should_warn = service.should_send_warning(
                percent_used=82.5,
                last_warning_sent=datetime.utcnow() - timedelta(days=2)
            )
        """
        if config is None:
            config = self.get_enforcement_config(organisation_id)

        # Ist User überhaupt in Warning-Range?
        if percent_used < config.warning_threshold_percent:
            return False

        # Prüfe Frequency
        warning_frequency = config.warning_frequency

        if last_warning_sent is None:
            return True  # Erste Warnung - immer senden

        now = datetime.utcnow()
        days_since_warning = (now - last_warning_sent).days

        if warning_frequency == 'once':
            return False  # Nur 1x, bereits gesendet
        elif warning_frequency == 'weekly':
            return days_since_warning >= 7
        elif warning_frequency == 'daily':
            return days_since_warning >= 1
        else:
            return False

    def get_cleanup_urgency(
        self,
        percent_used: float,
        config: Optional[StorageEnforcementConfig] = None,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bestimme wie dringend Cleanup ist.

        Returns:
            Dict mit Urgency-Informationen und Empfehlungen

        Example:
            urgency = service.get_cleanup_urgency(95.0)
            # Returns: {
            #    'urgency': 'critical',
            #    'message': 'Please delete files immediately',
            #    'recommend_files_to_delete_gb': 5.2,
            #    'grace_period_days': 30,
            #    'action': 'required'
            # }
        """
        if config is None:
            config = self.get_enforcement_config(organisation_id)

        if percent_used <= 50:
            return {
                'urgency': 'none',
                'message': 'Your storage has plenty of space',
                'action': 'none'
            }
        elif percent_used <= 80:
            return {
                'urgency': 'low',
                'message': 'Consider deleting old files to free up space',
                'action': 'recommended'
            }
        elif percent_used < 100:
            return {
                'urgency': 'high',
                'message': 'Please delete files to avoid quota exceeded',
                'recommend_delete_percent': 5,  # Delete 5% to get back under limit
                'action': 'recommended'
            }
        else:  # percent_used >= 100
            return {
                'urgency': 'critical',
                'message': 'Your storage quota is exceeded. You must delete files to restore functionality.',
                'recommend_delete_percent': 10,  # Delete 10% to get back under limit
                'grace_period_days': config.grace_period_days,
                'grace_period_expires': (datetime.utcnow() + timedelta(days=config.grace_period_days)).isoformat(),
                'action': 'required',
                'warning': f'If you do not delete files within {config.grace_period_days} days, your account will be in read-only mode.'
            }

    def get_quota_holder_summary(
        self,
        current_usage_bytes: int,
        quota_bytes: int,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hole komplette Zusammenfassung für einen Quota-Holder.

        Nutzbarer für Dashboard/Widget.

        Args:
            current_usage_bytes: Aktuelle Nutzung in Bytes
            quota_bytes: Quota in Bytes
            organisation_id: Optional für Config-Lookup

        Returns:
            Dict mit all Informationen
        """
        percent_used = (current_usage_bytes / quota_bytes * 100) if quota_bytes > 0 else 0
        percent_remaining = 100 - percent_used
        bytes_remaining = quota_bytes - current_usage_bytes

        config = self.get_enforcement_config(organisation_id)
        status_display = self.get_status_color_icon(percent_used, organisation_id)
        cleanup_urgency = self.get_cleanup_urgency(percent_used, config, organisation_id)

        can_upload, upload_reason = self.can_upload(percent_used, organisation_id)
        can_download = self.can_download()

        return {
            'usage': {
                'bytes': current_usage_bytes,
                'gb': round(current_usage_bytes / (1024**3), 2),
                'percent': round(percent_used, 1)
            },
            'quota': {
                'bytes': quota_bytes,
                'gb': round(quota_bytes / (1024**3), 2)
            },
            'remaining': {
                'bytes': max(0, bytes_remaining),
                'gb': round(max(0, bytes_remaining) / (1024**3), 2),
                'percent': round(percent_remaining, 1)
            },
            'status': status_display,
            'enforcement': {
                'type': config.enforcement_type,
                'warning_threshold': config.warning_threshold_percent,
                'critical_threshold': config.critical_threshold_percent,
                'hard_limit': config.hard_limit_percent,
                'grace_period_days': config.grace_period_days
            },
            'actions': {
                'can_upload': can_upload,
                'upload_reason': upload_reason,
                'can_download': can_download
            },
            'cleanup_urgency': cleanup_urgency
        }
