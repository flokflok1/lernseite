# Emergency Rollback Scripts

⚠️ **CRITICAL: Diese Scripts gehören NICHT zu den normalen Migrations!**

Diese befinden sich hier für Notfälle:
- Datenbankschema ist beschädigt
- Migration ist fehlgeschlagen
- Vollständiger Systemneustart nötig

## Scripts:
- **999_rollback_group_system.sql** - Entfernt RBAC 3.0 Group System komplett

## Verwendung:
```bash
# NUR im absoluten Notfall!
psql service=devdb < 999_rollback_group_system.sql
```

## Danach:
1. Root cause des Fehlers analysieren
2. Datenbank neu initialisieren
3. Alle Migrations neu anwenden
