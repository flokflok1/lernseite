# Backend Root Cleanup Analysis - C-CLEANUP v3

**Datum:** 2025-11-23
**Ziel:** Aufräumen des chaotischen Backend-Root-Verzeichnisses

## Gefundene Dateien (38 Python-Skripte)

### KATEGORIE A - Sicher archivierbar (Dev/Debug-Skripte)

#### A1: Test-Skripte (10 Dateien)
| Datei | Grund | Import-Check |
|-------|-------|--------------|
| `test_admin_creation_debug.py` | One-Off Debug-Skript | ❌ Nicht importiert |
| `test_category_create.py` | One-Off Test | ❌ Nicht importiert |
| `test_courses_query.py` | One-Off Test | ❌ Nicht importiert |
| `test_create_admin.py` | One-Off Test | ❌ Nicht importiert |
| `test_environment_setup.py` | One-Off Test | ❌ Nicht importiert |
| `test_list_query.py` | One-Off Test | ❌ Nicht importiert |
| `test_login.py` | One-Off Test | ❌ Nicht importiert |
| `test_migration.py` | One-Off Test | ❌ Nicht importiert |
| `test_seeds.py` | One-Off Test | ❌ Nicht importiert |
| `test_setup_status.py` | One-Off Test | ❌ Nicht importiert |

**Begründung:** Diese Skripte sind einmalige Debug/Test-Skripte. Sollten nach `backend/tests/` verschoben werden oder archiviert werden, wenn obsolet.

#### A2: Check-Skripte (11 Dateien)
| Datei | Grund | Import-Check | Sicherheitsrisiko |
|-------|-------|--------------|-------------------|
| `check_admin.py` | Dev-Check mit **HARDCODED CREDENTIALS** | ❌ Nicht importiert | ⚠️ **JA** (DB-Password im Code) |
| `check_audit_logs.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_audit_logs_columns.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_courses_columns.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_courses_schema.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_migrations.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_organizations_schema.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_tables.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_users_schema.py` | One-Off Check | ❌ Nicht importiert | - |
| `check_wallets.py` | One-Off Check | ❌ Nicht importiert | - |
| `delete_admin.py` | One-Off Delete-Skript | ❌ Nicht importiert | ⚠️ Destruktiv |

**Begründung:** Development-Checks, die manuell ausgeführt wurden. Ersetzt durch Setup Wizard.

**WICHTIG:** `check_admin.py` enthält **hardcoded Credentials** (Zeile 8-12) - MUSS gelöscht oder Credentials entfernt werden!

#### A3: Database Management (9 Dateien)
| Datei | Grund | Import-Check | Ersetzt durch |
|-------|-------|--------------|---------------|
| `create_database.py` | DB-Erstellung | ❌ Nicht importiert | Setup Wizard |
| `reset_database.py` | DB-Reset | ❌ Nicht importiert | Setup Wizard |
| `reset_database_auto.py` | DB-Reset (auto) | ❌ Nicht importiert | Setup Wizard |
| `reset_db_auto.py` | DB-Reset (Duplikat) | ❌ Nicht importiert | Setup Wizard |
| `reset_db_now.py` | DB-Reset (Duplikat) | ❌ Nicht importiert | Setup Wizard |
| `force_reset_db.py` | DB-Force-Reset | ❌ Nicht importiert | Setup Wizard |
| `drop_all_tables.py` | **Destruktiv** | ❌ Nicht importiert | Setup Wizard |
| `truncate_all_tables.py` | **Destruktiv** | ❌ Nicht importiert | Setup Wizard |
| `kill_db_connections.py` | DB-Connection-Kill | ❌ Nicht importiert | PgAdmin |

**Begründung:** Alle DB-Management-Aufgaben werden jetzt durch Setup Wizard erledigt. Diese Skripte sind obsolet.

**WARNUNG:** `drop_all_tables.py` und `truncate_all_tables.py` sind destruktiv - sollten archiviert werden.

#### A4: View/Seed-Skripte (3 Dateien)
| Datei | Grund | Import-Check | Ersetzt durch |
|-------|-------|--------------|---------------|
| `create_categories_view.py` | View-Erstellung | ❌ Nicht importiert | Migration 043 |
| `create_organisations_view.py` | View-Erstellung | ❌ Nicht importiert | Migration |
| `seed_missing_data.py` | One-Off Seed | ❌ Nicht importiert | Setup Wizard Seeds |

**Begründung:** Views werden durch Migrationen erstellt, Seeds durch Setup Wizard.

#### A5: Migration Helper (3 Dateien)
| Datei | Grund | Import-Check | Ersetzt durch |
|-------|-------|--------------|---------------|
| `run_migration_041.py` | One-Off Migration | ❌ Nicht importiert | `run_migration.py` |
| `run_migration_043.py` | One-Off Migration | ❌ Nicht importiert | `run_migration.py` |
| `add_creator_id_alias.py` | One-Off Fix | ❌ Nicht importiert | Migration |

**Begründung:** Spezifische Migrations-Runner sind obsolet, da `run_migration.py` generisch ist.

### KATEGORIE B - Behalten (Produktiv genutzt)

| Datei | Grund | Status |
|-------|-------|--------|
| `run.py` | **Application Entry Point** | ✅ BEHALTEN |
| `gunicorn.conf.py` | Gunicorn Production Config | ✅ BEHALTEN |
| `run_production.py` | Production Runner | ✅ BEHALTEN |
| `run_migration.py` | Generic Migration Runner | ✅ BEHALTEN |
| `setup_helper.py` | Setup Wizard Helper | ✅ BEHALTEN (falls genutzt) |

**Begründung:** Diese Dateien sind essentiell für den Betrieb oder werden aktiv genutzt.

### KATEGORIE C - Prüfen (Unklar)

| Datei | Grund | Aktion |
|-------|-------|--------|
| `setup_helper.py` | Wird von Setup Wizard genutzt? | Prüfen, ob importiert wird |

## Zusammenfassung

**Kategorie A (Archivieren):** 36 Dateien
- 10x Test-Skripte
- 11x Check-Skripte
- 9x DB-Management
- 3x View/Seed-Skripte
- 3x Migration Helper

**Kategorie B (Behalten):** 4-5 Dateien
- `run.py`, `gunicorn.conf.py`, `run_production.py`, `run_migration.py`, (`setup_helper.py`)

**Kategorie C (Prüfen):** 1 Datei
- `setup_helper.py`

## Empfohlene Archive-Struktur

```
backend/_archive/
├── dev_scripts/
│   ├── tests/           # 10 test_*.py Dateien
│   ├── checks/          # 11 check_*.py Dateien
│   ├── db_management/   # 9 DB-Management Skripte
│   ├── migrations/      # 3 One-Off Migration-Runner
│   └── seeds/           # 3 View/Seed-Skripte
```

## Sicherheitswarnung

⚠️ **KRITISCH:** `check_admin.py` enthält **hardcoded Credentials**:
```python
DB_HOST = '10.0.10.222'
DB_USER = 'lernsystem'
DB_PASSWORD = '***REMOVED***'  # ⚠️ HARDCODED PASSWORD
```

**Aktion:** Datei MUSS archiviert werden, Credentials sollten aus Git-History entfernt werden (falls committed).

## Nächste Schritte

1. ✅ setup_helper.py Import-Check
2. ⏳ Archive-Ordner erstellen
3. ⏳ 36 Dateien nach `_archive/` verschieben
4. ⏳ Systemtest (Backend starten)
5. ⏳ Final Report erstellen
