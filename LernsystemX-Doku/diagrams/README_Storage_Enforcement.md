# Storage Enforcement System - PlantUML Diagram Guide

Diese Dokumentation erläutert das **dynamisch konfigurierbare Storage-Enforcement-System** durch visuelle PlantUML-Diagramme.

## 📋 Übersicht der Diagramme

### 1. **storage-enforcement-architecture.puml**
**Zweck:** Überblick über die gesamte Systemarchitektur

**Zeigt:**
- API Layer (File Upload, Storage Status, Download Endpoints)
- Service Layer (StorageEnforcementService mit allen Kernmethoden)
- Data Access Layer (Repository & Seed)
- Database Layer (storage_enforcement_configs Tabelle)
- Datenfluss zwischen den Ebenen

**Verwenden wenn:** Sie die Komponenten und deren Beziehungen verstehen möchten

```
API Endpoints
    ↓
StorageEnforcementService (Zentrale Geschäftslogik)
    ↓
StorageEnforcementConfigRepository (Datenbankzugriff)
    ↓
Datenbank (storage_enforcement_configs)
```

---

### 2. **storage-enforcement-sequence.puml**
**Zweck:** Detaillierter Ablauf eines File-Upload-Requests

**Zeigt:**
- Wie ein User eine Datei hochlädt
- Wie die Erlaubnis geprüft wird
- Wie die Konfiguration aus der Datenbank geladen wird
- Konfigurationsauflösungs-Logik (Org-Konfiguration → System-Default)
- Rückgabe der Entscheidung zum Endpoint

**Verwenden wenn:** Sie verstehen möchten, wie ein konkreter Request durch das System fließt

```
User Upload Request
    ↓
Endpoint extrahiert organisation_id
    ↓
Service: can_upload(percent_used=78.5, organisation_id)
    ↓
Repository: get_config_for_organisation_or_default()
    ↓
[Try Org-Spezifisch] → [Fallback System-Default] → [Fallback Internal]
    ↓
Service: Prüfe actions_json für den Prozentbereich
    ↓
Rückgabe: (True/False, reason)
```

---

### 3. **storage-enforcement-config-resolution.puml**
**Zweck:** Visuelle Decision-Tree für die Konfigurationsauflösung

**Zeigt:**
- Schritt-für-Schritt Entscheidungsfindung
- Prioritäten: Org-Konfiguration > System-Default > Internal Defaults
- Typische Szenarien (B2B, B2C, Neue Orgs)
- Failsafe-Mechanismen

**Verwenden wenn:** Sie die Konfigurationsauflösungs-Logik verstehen möchten

```
Anfrage mit organisation_id?
    ├─ JA: Suche org-spezifische Config
    │      └─ Gefunden? → USE
    │      └─ Nicht gefunden? → Continue
    │
    ├─ NEIN: Skip zu System-Default
    │
    → Suche System-Default
       └─ Gefunden? → USE
       └─ Nicht gefunden? → USE Internal Defaults
```

---

### 4. **storage-enforcement-datamodel.puml**
**Zweck:** Datenbankschema und Domain-Modelle

**Zeigt:**
- Tabellenstruktur (storage_enforcement_configs)
- Alle Spalten und deren Bedeutung
- JSON-Struktur (actions_json)
- Domain Model (StorageEnforcementConfig Dataclass)
- Beziehungen zwischen Tabellen

**Verwenden wenn:** Sie die Datenstruktur und Speicherung verstehen möchten

```
storage_enforcement_configs Tabelle
├─ Standard-Spalten: id, organisation_id, created_at, updated_at
├─ Enforcement-Parameter: enforcement_type, warning_threshold, grace_period
├─ Benachrichtigungen: warning_frequency, send_email_warnings
└─ Flexibilität: actions_json (JSONB)

actions_json Structure:
├─ "0_to_50": { status, upload, download, notifications }
├─ "50_to_80": { ... }
├─ "80_to_100": { ... }
├─ "100_plus": { ... }
└─ "grace_period_expired": { ... }
```

---

### 5. **storage-enforcement-b2c-vs-b2b.puml**
**Zweck:** Vergleich der B2C (Hard) und B2B (Soft) Enforcement-Modelle

**Zeigt:**
- B2C Hard Enforcement (Strikte Quotas für Einzelnutzer)
  - Warning: 75%, Critical: 90%, Hard Limit: 100%
  - Grace Period: 7 Tage
  - Häufige Warnungen: täglich

- B2B Soft Enforcement (Flexible Quotas für Organisationen)
  - Warning: 85%, Critical: 95%, Hard Limit: 110%
  - Grace Period: 30 Tage
  - Weniger häufige Warnungen: wöchentlich

**Verwenden wenn:** Sie die Unterschiede zwischen B2C und B2B verstehen möchten

```
B2C (Individual):
0% → 75% [Green] → 90% [Yellow] → 100% [Red + 7d Grace] → ReadOnly

B2B (Organisation):
0% → 85% [Green] → 95% [Yellow] → 110% [Orange] → [30d Grace] → ReadOnly
```

---

## 🔄 Architektur-Fluss

```
┌──────────────────────────────────────────────────────────┐
│                    USER REQUEST                          │
│         (File Upload mit organisation_id)               │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│            FILE UPLOAD ENDPOINT                          │
│   • Token-Validierung                                    │
│   • organisation_id Extraktion                           │
│   • Service.can_upload() Aufruf                          │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│       STORAGE ENFORCEMENT SERVICE                        │
│   • get_enforcement_config(organisation_id)              │
│   • get_enforcement_action(percent_used, config)         │
│   • Entscheidungs-Logik                                  │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│    CONFIGURATION REPOSITORY                              │
│   • Try: find_by_organisation(org_id)                    │
│   • Fallback: find_system_default()                      │
│   • Fallback: Internal Defaults                          │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              DATABASE                                    │
│   storage_enforcement_configs Table                      │
│   └─ actions_json { "0_to_50": {...}, ... }              │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│        DECISION RETURNED TO ENDPOINT                     │
│   (allowed: bool, reason: str)                           │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│            RESPONSE TO USER                              │
│   200 OK (Upload erlaubt)                                │
│   507 Insufficient Storage (Upload blockiert)            │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases

### UC1: Neuer User lädt Datei hoch (B2C)
1. **Diagram:** storage-enforcement-sequence.puml
2. **Details:** Datei hochladen → Service prüft config → System-Default verwendet → Upload erlaubt/blockiert
3. **Konfiguration:** B2C Hard Enforcement (aus Seed-Template)

### UC2: Orgadmin möchte Storage-Richtlinien ändern (B2B)
1. **Diagram:** storage-enforcement-datamodel.puml + storage-enforcement-b2c-vs-b2b.puml
2. **Aktion:**
   - Admin öffnet Admin-Panel
   - Modifiziert organisation-spezifische Config in Datenbank
   - Z.B. grace_period_days: 30 → 45
   - Alle User dieser Org sehen sofort neue Richtlinien
3. **Vorteil:** Keine Code-Änderung notwendig, 100% flexibel

### UC3: User nähert sich Storage-Limit
1. **Diagram:** storage-enforcement-b2c-vs-b2b.puml
2. **Szenario B2C (75% threshold):**
   - Bei 75%: Warnung starten (täglich)
   - Bei 90%: Warnung intensivieren
   - Bei 100%: Upload blockiert, 7 Tage Grace-Period

3. **Szenario B2B (85% threshold):**
   - Bei 85%: Warnung starten (wöchentlich)
   - Bei 110%: Upload blockiert, 30 Tage Grace-Period

### UC4: Grace Period abgelaufen (Read-Only Mode)
1. **Diagram:** storage-enforcement-b2c-vs-b2b.puml
2. **Resultat:**
   - Upload: blockiert
   - Download: readonly (nur bei B2B)
   - Neue Courses/Lessons: blockiert
   - User muss Storage bereinigen oder Admin kontaktieren

---

## 💾 Konfigurationsbeispiele

### B2C Hard Enforcement (Standard für Einzelnutzer)
```python
{
    "enforcement_type": "hard",
    "warning_threshold_percent": 75,
    "critical_threshold_percent": 90,
    "hard_limit_percent": 100,
    "grace_period_days": 7,
    "warning_frequency": "daily",
    "actions_json": {
        "0_to_50": { "status": "green", "upload": "allowed", ... },
        "50_to_80": { "status": "yellow", "upload": "allowed", ... },
        "80_to_100": { "status": "red", "upload": "allowed_with_warning", ... },
        "100_plus": { "status": "black", "upload": "blocked", ... },
        "grace_period_expired": { "status": "alert", "upload": "blocked", ... }
    }
}
```

### B2B Soft Enforcement (Für Organisationen)
```python
{
    "enforcement_type": "soft",
    "warning_threshold_percent": 85,
    "critical_threshold_percent": 95,
    "hard_limit_percent": 110,  # ← Erlaubt 10% Overflow!
    "grace_period_days": 30,    # ← Längere Grace-Period
    "warning_frequency": "weekly",  # ← Weniger aggressiv
    "actions_json": {
        "0_to_50": { "status": "green", "upload": "allowed", ... },
        "50_to_85": { "status": "yellow", "upload": "allowed", ... },
        "85_to_100": { "status": "orange", "upload": "allowed", ... },
        "100_plus": { "status": "red", "upload": "allowed_with_warning", ... },
        "grace_period_expired": { "status": "black", "upload": "blocked", ... }
    }
}
```

### Custom Enforcement (Beliebig konfigurierbar)
```python
{
    "enforcement_type": "custom",
    "warning_threshold_percent": 80,
    "critical_threshold_percent": 92,
    "hard_limit_percent": 105,
    "grace_period_days": 14,
    "warning_frequency": "twice_daily",  # ← Custom frequency!
    "actions_json": {
        "0_to_80": { ... },
        "80_to_92": { ... },
        "92_to_100": { ... },
        "100_to_105": { ... },
        "105_plus": { ... },
        "grace_period_expired": { ... }
    }
}
```

---

## 📊 Für Entwickler: Integration in Code

### 1. Repository-Zugriff
```python
from app.repositories.storage_enforcement_config import StorageEnforcementConfigRepository

with get_db_connection() as conn:
    repo = StorageEnforcementConfigRepository(conn)

    # Auflösung mit Fallback-Logik
    config = repo.get_config_for_organisation_or_default('org-123')

    # Einzelne Lookups
    org_config = repo.find_by_organisation('org-123')
    system_default = repo.find_system_default()
```

### 2. Service-Nutzung
```python
from app.services.storage_enforcement_service import StorageEnforcementService

service = StorageEnforcementService()

# Alle Informationen für Upload-Entscheidung
can_upload, reason = service.can_upload(
    percent_used=78.5,
    organisation_id='org-123'
)

# UI-Status anzeigen
status = service.get_status_display(percent_used=78.5, organisation_id='org-123')
# Returns: 'yellow'

status_display = service.get_status_color_icon(percent_used=78.5)
# Returns: { 'status': 'yellow', 'icon': '🟡', 'color': '#eab308', ... }

# Cleanup-Empfehlungen
urgency = service.get_cleanup_urgency(percent_used=95.0)
# Returns: { 'urgency': 'critical', 'message': '...', 'action': 'required' }
```

### 3. Seed-Initalisierung
```python
from app.repositories.storage_enforcement_config_seed import StorageEnforcementConfigSeed

# System-Standard initialisieren
with get_db_connection() as conn:
    repo = StorageEnforcementConfigRepository(conn)
    result = StorageEnforcementConfigSeed.seed_default_configs(repo)
    # Creates: System-Default mit B2C Hard Enforcement

# Organisation-spezifisch konfigurieren
org_result = StorageEnforcementConfigSeed.seed_organisation_config(
    repo,
    organisation_id='gymnasium-munich',
    enforcement_type='soft'  # B2B: weich
)
```

---

## ✅ Flexibilität Checklist

Das System ist **100% flexibel konfigurierbar**. Folgende Felder sind IN DER DATENBANK konfigurierbar:

- ✅ `enforcement_type` - hard/soft/none
- ✅ `warning_threshold_percent` - 0-100
- ✅ `critical_threshold_percent` - 0-100
- ✅ `hard_limit_percent` - 0-200+
- ✅ `grace_period_days` - Beliebige Anzahl Tage
- ✅ `warning_frequency` - daily/weekly/once/beliebig
- ✅ `send_email_warnings` - true/false
- ✅ `send_ui_notifications` - true/false
- ✅ `auto_cleanup_soft_deleted_days` - Beliebige Anzahl
- ✅ `actions_json` - Komplett custom pro Threshold-Range

**Keine Konfiguration ist hardcoded!** Alles lädt aus der Datenbank.

---

**Datum:** 2026-01-22
**Status:** Dokumentation Complete
**Diagramme:** 5 PlantUML-Dateien für verschiedene Aspekte
