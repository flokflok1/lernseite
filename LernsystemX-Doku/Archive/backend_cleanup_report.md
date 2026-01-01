# Backend Cleanup Report - C-CLEANUP v2 (SAFE)

**Datum:** 2025-01-23
**Version:** 2.0 (Safe Cleanup)
**Ziel:** Vorsichtige Identifikation und Archivierung von totem Code

## Übersicht

Diese Cleanup-Runde identifiziert **nur offensichtlich tote Dateien** und verschiebt sie in `backend\_archive\`. Keine Hard-Deletes.

## Kategorien-Definition

- **A (Kategorie A)** = Offensichtlich tot, sicher archivierbar (One-Off Fix-Skripte)
- **B (Kategorie B)** = Wahrscheinlich tot, aber vorsichtig (kritische Stellen, z.B. Repositories)
- **C (Kategorie C)** = Kandidat für späteren Refactor (z.B. zu große Dateien, aber aktiv genutzt)

## Gefundene Kandidaten

### 1. Fix-Skripte im Root (Kategorie A)

| Datei | Größe | Datum | Import-Check | Grund | Aktion |
|-------|-------|-------|--------------|-------|--------|
| `check_and_fix_categories.py` | 1.9K | Nov 21 | ❌ Nicht importiert | One-Off Fix-Skript für Kategorien | ✅ **A** - Archive |
| `fix_courses_columns.py` | 4.5K | Nov 21 | ❌ Nicht importiert | One-Off Fix für Courses-Spalten | ✅ **A** - Archive |
| `fix_courses_view_v2.py` | 2.1K | Nov 21 | ❌ Nicht importiert | One-Off Fix für Courses-View | ✅ **A** - Archive |
| `fix_missing_tables.py` | 2.1K | Nov 19 | ❌ Nicht importiert | One-Off Fix für fehlende Tabellen | ✅ **A** - Archive |
| `fix_subscriptions_plan_id.py` | 3.8K | Nov 19 | ❌ Nicht importiert | One-Off Fix für Subscriptions | ✅ **A** - Archive |

**Begründung Kategorie A:**
- Alle 5 Dateien sind **One-Off Fix-Skripte**
- Werden **nirgendwo importiert** (Grep-Check durchgeführt)
- Keine Referenzen in `run.py`, `wsgi.py`, oder anderen Modulen
- Zweck: Einmalige Datenbankmigrationen/Fixes (bereits durchgeführt)
- Ersetzt durch: SQL-Migrationen oder direkte DB-Fixes

### 2. Scripts-Ordner (Noch nicht gescannt)

Status: **PENDING** - Wird in nächstem Scan überprüft

### 3. Backend App-Module (Noch nicht gescannt)

Status: **PENDING** - Ungenutzte Module werden separat identifiziert

## Zusammenfassung

**Kategorie A (Sicher archivierbar):**
- ✅ 5 Fix-Skripte im Backend-Root
- Aktion: Verschieben nach `backend\_archive\fix_scripts\`

**Kategorie B (Vorsichtig):**
- Noch keine identifiziert

**Kategorie C (Beobachten):**
- Noch keine identifiziert

## Nächste Schritte

1. ✅ Frontend-Scan durchführen
2. ✅ Reports schreiben (Backend + Frontend)
3. ⏳ Nur Kategorie-A Dateien nach `_archive` verschieben
4. ⏳ Systemtest (Backend/Frontend starten)
5. ⏳ Bei Problemen: Sofort Revert

## Änderungsprotokoll

| Datum | Aktion | Dateien | Status |
|-------|--------|---------|--------|
| 2025-01-23 | Scan | 5 Fix-Skripte identifiziert | ✅ Completed |
| 2025-01-23 | Archive | - | ⏳ Pending |

---

**Hinweis:** Dieser Report dient der **Dokumentation**. Archivierung erfolgt erst nach Freigabe und Systemtest.
