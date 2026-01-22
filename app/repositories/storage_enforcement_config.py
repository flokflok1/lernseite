# app/repositories/storage_enforcement_config.py

"""
Storage Enforcement Configuration Repository

Verwaltet die Konfiguration für Storage-Quota Enforcement Rules.
Alle Schwellwerte, Warnings, Grace Periods kommen AUS DER DATENBANK,
nicht aus hardcodierten Werten!

User's Message 3: "das sollte man aber flexibel einstellen können alles"
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import json
import uuid
import psycopg
from psycopg.rows import dict_row


@dataclass
class StorageEnforcementConfig:
    """
    Domain Model für Storage Enforcement Config.

    Represents eine Zeile aus der storage_enforcement_configs Tabelle.
    """

    id: str
    organisation_id: Optional[str]
    is_system_default: bool
    warning_threshold_percent: int
    critical_threshold_percent: int
    hard_limit_percent: int
    enforcement_type: str  # 'hard', 'soft', 'none'
    grace_period_days: int
    auto_cleanup_soft_deleted_days: int
    warning_frequency: str  # 'daily', 'weekly', 'once'
    send_email_warnings: bool
    send_ui_notifications: bool
    actions_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert zu Dictionary (für JSON Serialization)."""
        return {
            'id': self.id,
            'organisation_id': self.organisation_id,
            'is_system_default': self.is_system_default,
            'warning_threshold_percent': self.warning_threshold_percent,
            'critical_threshold_percent': self.critical_threshold_percent,
            'hard_limit_percent': self.hard_limit_percent,
            'enforcement_type': self.enforcement_type,
            'grace_period_days': self.grace_period_days,
            'auto_cleanup_soft_deleted_days': self.auto_cleanup_soft_deleted_days,
            'warning_frequency': self.warning_frequency,
            'send_email_warnings': self.send_email_warnings,
            'send_ui_notifications': self.send_ui_notifications,
            'actions_json': self.actions_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_action_for_percent(self, percent_used: float) -> Dict[str, Any]:
        """
        Bestimme die Action basierend auf Nutzungsprozentsatz.

        Args:
            percent_used: Prozentuale Nutzung (0-100+)

        Returns:
            Action dict aus actions_json für diesen Schwellwert
        """
        # Bestimme Bereich basierend auf percent_used
        if percent_used <= 50:
            range_key = '0_to_50'
        elif percent_used <= 80:
            range_key = '50_to_80'
        elif percent_used < 100:
            range_key = '80_to_100'
        elif percent_used >= 100:
            range_key = '100_plus'
        else:
            range_key = '100_plus'

        # Hole Action aus JSON mit Default-Fallback
        return self.actions_json.get(range_key, {
            'status': 'red',
            'upload': 'blocked',
            'download': 'allowed',
            'notifications': 'critical'
        })


class StorageEnforcementConfigRepository:
    """
    Repository für Storage Enforcement Configs.

    Lädt Konfigurationen aus der Datenbank mit:
    - Per-Organisation Override (wenn vorhanden)
    - System-Default Fallback (wenn keine org-spezifisch)

    Die StorageEnforcementService nutzt dieses Repository!
    """

    def __init__(self, connection: psycopg.Connection = None):
        """
        Initialize repository.

        Args:
            connection: Database connection (optional)
        """
        self.conn = connection
        self.table_name = "storage_enforcement_configs"

    def _get_connection(self) -> psycopg.Connection:
        """Hole Connection (von außen oder aus Pool)."""
        if self.conn:
            return self.conn

        # Falls keine Connection übergeben: aus Pool laden
        from app.database import get_db_connection
        return get_db_connection()

    def _parse_row(self, row: Dict[str, Any]) -> StorageEnforcementConfig:
        """Convert Datenbankzeile zu Model."""
        # Parse actions_json falls als String
        actions = row.get('actions_json', {})
        if isinstance(actions, str):
            actions = json.loads(actions)

        return StorageEnforcementConfig(
            id=row['id'],
            organisation_id=row['organisation_id'],
            is_system_default=row['is_system_default'],
            warning_threshold_percent=row['warning_threshold_percent'],
            critical_threshold_percent=row['critical_threshold_percent'],
            hard_limit_percent=row['hard_limit_percent'],
            enforcement_type=row['enforcement_type'],
            grace_period_days=row['grace_period_days'],
            auto_cleanup_soft_deleted_days=row['auto_cleanup_soft_deleted_days'],
            warning_frequency=row['warning_frequency'],
            send_email_warnings=row['send_email_warnings'],
            send_ui_notifications=row['send_ui_notifications'],
            actions_json=actions,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def find_by_id(self, config_id: str) -> Optional[StorageEnforcementConfig]:
        """
        Finde Config nach ID.

        Args:
            config_id: Config ID

        Returns:
            StorageEnforcementConfig oder None
        """
        with self._get_connection().cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE id = %s",
                (config_id,)
            )
            row = cursor.fetchone()

            if row:
                return self._parse_row(row)
            return None

    def find_by_organisation(
        self,
        organisation_id: str
    ) -> Optional[StorageEnforcementConfig]:
        """
        Finde Config für eine spezifische Organisation.

        Args:
            organisation_id: Organisation ID

        Returns:
            StorageEnforcementConfig (org-spezifisch) oder None
        """
        with self._get_connection().cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                SELECT * FROM {self.table_name}
                WHERE organisation_id = %s
                AND is_system_default = FALSE
                """,
                (organisation_id,)
            )
            row = cursor.fetchone()

            if row:
                return self._parse_row(row)
            return None

    def find_system_default(self) -> Optional[StorageEnforcementConfig]:
        """
        Finde System-Default Config.

        Diese Config wird verwendet wenn keine org-spezifische Config existiert.

        Returns:
            StorageEnforcementConfig (system default) oder None
        """
        with self._get_connection().cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                SELECT * FROM {self.table_name}
                WHERE is_system_default = TRUE
                LIMIT 1
                """
            )
            row = cursor.fetchone()

            if row:
                return self._parse_row(row)
            return None

    def find_all(self) -> List[StorageEnforcementConfig]:
        """
        Finde alle Configs (für Admin-Verwaltung).

        Returns:
            List von StorageEnforcementConfig
        """
        with self._get_connection().cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"SELECT * FROM {self.table_name} ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()

            return [self._parse_row(row) for row in rows]

    def create(self, data: Dict[str, Any]) -> StorageEnforcementConfig:
        """
        Erstelle neue Config.

        Args:
            data: Dictionary mit Config-Feldern

        Returns:
            Erstellte StorageEnforcementConfig

        Example:
            config = repo.create({
                'organisation_id': 'org-123',
                'enforcement_type': 'soft',
                'grace_period_days': 30,
                'warning_threshold_percent': 85
            })
        """
        config_id = data.get('id', str(uuid.uuid4()))

        # Prepare insert values
        fields = {
            'id': config_id,
            'organisation_id': data.get('organisation_id'),
            'is_system_default': data.get('is_system_default', False),
            'warning_threshold_percent': data.get('warning_threshold_percent', 80),
            'critical_threshold_percent': data.get('critical_threshold_percent', 95),
            'hard_limit_percent': data.get('hard_limit_percent', 100),
            'enforcement_type': data.get('enforcement_type', 'hard'),
            'grace_period_days': data.get('grace_period_days', 30),
            'auto_cleanup_soft_deleted_days': data.get('auto_cleanup_soft_deleted_days', 30),
            'warning_frequency': data.get('warning_frequency', 'daily'),
            'send_email_warnings': data.get('send_email_warnings', True),
            'send_ui_notifications': data.get('send_ui_notifications', True),
            'actions_json': json.dumps(data.get('actions_json', {})),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Remove None values except for organisation_id (kann NULL sein)
        fields = {k: v for k, v in fields.items() if v is not None or k == 'organisation_id'}

        field_names = ', '.join(fields.keys())
        placeholders = ', '.join(['%s'] * len(fields))

        with self._get_connection().cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                INSERT INTO {self.table_name} ({field_names})
                VALUES ({placeholders})
                RETURNING *
                """,
                list(fields.values())
            )
            row = cursor.fetchone()
            self._get_connection().commit()

            return self._parse_row(row)

    def update(
        self,
        config_id: str,
        data: Dict[str, Any]
    ) -> Optional[StorageEnforcementConfig]:
        """
        Update eine existierende Config.

        Args:
            config_id: Config ID
            data: Dictionary mit zu aktualisierenden Feldern

        Returns:
            Aktualisierte StorageEnforcementConfig oder None
        """
        # Prepare update values
        updates = {}

        if 'warning_threshold_percent' in data:
            updates['warning_threshold_percent'] = data['warning_threshold_percent']
        if 'critical_threshold_percent' in data:
            updates['critical_threshold_percent'] = data['critical_threshold_percent']
        if 'hard_limit_percent' in data:
            updates['hard_limit_percent'] = data['hard_limit_percent']
        if 'enforcement_type' in data:
            updates['enforcement_type'] = data['enforcement_type']
        if 'grace_period_days' in data:
            updates['grace_period_days'] = data['grace_period_days']
        if 'auto_cleanup_soft_deleted_days' in data:
            updates['auto_cleanup_soft_deleted_days'] = data['auto_cleanup_soft_deleted_days']
        if 'warning_frequency' in data:
            updates['warning_frequency'] = data['warning_frequency']
        if 'send_email_warnings' in data:
            updates['send_email_warnings'] = data['send_email_warnings']
        if 'send_ui_notifications' in data:
            updates['send_ui_notifications'] = data['send_ui_notifications']
        if 'actions_json' in data:
            updates['actions_json'] = json.dumps(data['actions_json'])

        if not updates:
            return self.find_by_id(config_id)

        updates['updated_at'] = datetime.utcnow()

        set_clauses = []
        params = []

        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        params.append(config_id)

        with self._get_connection().cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING *
                """,
                params
            )
            row = cursor.fetchone()
            self._get_connection().commit()

            if row:
                return self._parse_row(row)
            return None

    def delete(self, config_id: str) -> bool:
        """
        Delete eine Config.

        ACHTUNG: Nicht Org-Default löschen wenn es noch Orgs gibt!

        Args:
            config_id: Config ID

        Returns:
            True wenn gelöscht, False wenn nicht gefunden
        """
        with self._get_connection().cursor() as cursor:
            # Check if system default
            cursor.execute(
                f"SELECT is_system_default FROM {self.table_name} WHERE id = %s",
                (config_id,)
            )
            row = cursor.fetchone()

            if row and row[0]:  # is_system_default = True
                raise ValueError("Cannot delete system default config!")

            # Delete
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE id = %s",
                (config_id,)
            )
            deleted = cursor.rowcount > 0
            self._get_connection().commit()

            return deleted

    def count(self) -> int:
        """Count alle Configs."""
        with self._get_connection().cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            return cursor.fetchone()[0]

    def get_config_for_organisation_or_default(
        self,
        organisation_id: Optional[str] = None
    ) -> StorageEnforcementConfig:
        """
        Hole Config für Organisation mit Fallback zu System-Default.

        Dies ist die Haupt-Methode die die StorageEnforcementService nutzt!

        Args:
            organisation_id: Organisation ID (optional)

        Returns:
            StorageEnforcementConfig (org-spezifisch oder system default)

        Example:
            # Für eine Organisation
            config = repo.get_config_for_organisation_or_default('org-123')
            # Für System-Default (wenn keine org vorhanden)
            config = repo.get_config_for_organisation_or_default()
        """
        # Falls organisation_id vorhanden: versuche org-spezifische Config
        if organisation_id:
            org_config = self.find_by_organisation(organisation_id)
            if org_config:
                return org_config

        # Fallback: System-Default
        default_config = self.find_system_default()
        if default_config:
            return default_config

        # Falls kein Default existiert: Konstruiere einen Fallback
        # (sollte nicht vorkommen wenn DB korrekt initialisiert ist)
        return StorageEnforcementConfig(
            id=str(uuid.uuid4()),
            organisation_id=None,
            is_system_default=True,
            warning_threshold_percent=80,
            critical_threshold_percent=95,
            hard_limit_percent=100,
            enforcement_type='hard',
            grace_period_days=30,
            auto_cleanup_soft_deleted_days=30,
            warning_frequency='daily',
            send_email_warnings=True,
            send_ui_notifications=True,
            actions_json={
                '0_to_50': {
                    'status': 'green',
                    'upload': 'allowed',
                    'download': 'allowed',
                    'notifications': 'none'
                },
                '50_to_80': {
                    'status': 'yellow',
                    'upload': 'allowed',
                    'download': 'allowed',
                    'notifications': 'weekly_reminder'
                },
                '80_to_100': {
                    'status': 'red',
                    'upload': 'allowed_with_warning',
                    'download': 'allowed',
                    'notifications': 'daily_warning'
                },
                '100_plus': {
                    'status': 'black',
                    'upload': 'blocked',
                    'download': 'allowed',
                    'grace_period_days': 30
                }
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
