# Migration Nummerierungslücken

**Stand:** 2026-01-16 (Updated after comprehensive audit)
**Grund:** Cleanup von toten/duplizierten Migrations + Restructuring

---

## Dokumentierte Lücken

| Nummer | Ursprüngliche Datei | Grund der Löschung | Archiv-Ort |
|--------|--------------------|--------------------|------------|
| **038** | `038_i18n_complete.sql` | Alte i18n-Implementierung, ersetzt durch 084-088 | `11_System/.archive_2026-01-13/`<br>`.archive_2026-01-16/` |
| **042** | - | Nie existiert | - |
| **054** | `054_lm_refactoring_and_features.sql` | Deprecated LMs (12-32), Tabellen nach 008/026 verschoben | Dokumentiert (alt) |
| **063** | `063_system_features_tables.sql` | Tote Tabellen in PUBLIC Schema | Dokumentiert (alt) |
| **068** | `068_course_ai_settings.sql`<br>`068_role_feature_assignments.sql` | **Duplikate aufgelöst:**<br>→ 090 (01_Core)<br>→ 093 (03_AI) | `.archive_2026-01-16/` |
| **069** | `069_agent_global_knowledge.sql`<br>`069_permission_thresholds.sql` | **Duplikate aufgelöst:**<br>→ 091 (01_Core)<br>→ 094 (03_AI, split into part1/part2) | `.archive_2026-01-16/` |
| **071** | - | Nie existiert | - |
| **072** | `072_i18n_system.sql` | Alte i18n-Implementierung, ersetzt durch 084-088 | `11_System/.archive_2026-01-13/` |

---

## Duplikate-Auflösung (2026-01-16)

**Problem:** 10 Dateien hatten duplicate Nummern (067-081 Range)

**Lösung:** Renummerierung zu 089-098

| Alt | Neu | Datei | Kategorie | Archiv |
|-----|-----|-------|-----------|--------|
| 067 | 089 | `add_owner_admin.sql` | 01_Core | ✅ |
| 068 | 090 | `role_feature_assignments.sql` | 01_Core | ✅ |
| 069 | 091 | `permission_thresholds.sql` | 01_Core | ✅ |
| 067 | 092 | `ai_model_profiles_base.sql` | 03_AI | ✅ |
| 068 | 093 | `course_ai_settings.sql` | 03_AI | ✅ |
| 069 | 094 | `agent_global_knowledge.sql` (split) | 03_AI | ✅ |
| 076 | 095 | `feature_flags.sql` | 11_System | ✅ |
| 079 | 096 | `social_posts.sql` | 08_Social | ✅ |
| 080 | 097 | `social_follows.sql` | 08_Social | ✅ |
| 081 | 098 | `social_engagement.sql` | 08_Social | ✅ |

---

## Große Dateien-Split (2026-01-16)

**Problem:** 6 Dateien überschritten Quality Gate G01 (max 500 Zeilen)

**Lösung:** Split in part1, part2, part3 Dateien

| Nummer | Original | Zeilen | Split | Parts |
|--------|----------|--------|-------|-------|
| 048 | `ai_authoring_studio.sql` | 857 | 3 | 295 + 299 + 294 |
| 053 | `capability_slots.sql` | 505 | 2 | 252 + 253 |
| 064 | `math_toolkit.sql` | 522 | 2 | 289 + 287 |
| 076 | `multi_tenancy_extensions.sql` | 510 | 2 | 277 + 267 |
| 078 | `row_level_security.sql` | 525 | 2 | 293 + 275 |
| 094 | `agent_global_knowledge.sql` | 574 | 2 | 287 + 320 |

**Archiv:** Alle Originale in `.archive_2026-01-16/`

---

## Warum nicht renummerieren?

1. **Git-Historie:** Renummerierung würde Historie verfälschen
2. **Referenzen:** Andere Dateien könnten Nummern referenzieren
3. **Risiko:** Fehler beim Umbenennen möglich
4. **Setup Wizard:** Verarbeitet Dateien alphabetisch - Lücken sind kein Problem

**Setup Wizard Execution Order:**
```python
sorted(migration_files, key=lambda p: p.name)  # Alphabetically by filename
```

Split-Dateien (048_basename_part1.sql, 048_basename_part2.sql) sortieren automatisch korrekt.

---

## Aktuelle Nummerierung (Stand 2026-01-16)

### Belegte Nummern: 000-098 (minus 8 Lücken = 91 Dateien + 13 Parts = 104 Dateien)

**Nächste freie Nummer:** **099**

**Highest number:** 098

**Total migrations (inkl. Parts):** 104

**Parts-System:**
- Split-Dateien nutzen `_part1`, `_part2`, `_part3` Suffix
- Alphabetische Sortierung garantiert korrekte Ausführungsreihenfolge
- Foreign Keys in part2 referenzieren Tabellen aus part1 ✅

---

## Regel für Zukunft

### Neue Migration erstellen:

1. **Nummer vergeben:**
   ```bash
   # Höchste Nummer finden
   find backend/migrations -name "[0-9][0-9][0-9]_*.sql" -not -path "*/.archive*" \
     -exec basename {} \; | cut -c1-3 | sort -rn | head -1

   # Output: 098 → Nächste Nummer: 099
   ```

2. **Datei erstellen:**
   - Format: `NNN_beschreibung.sql`
   - Max 500 Zeilen (Quality Gate G01)
   - Header mit Dateinamen (Migration: NNN_beschreibung.sql)

3. **Bei >500 Zeilen:**
   - Split in `NNN_beschreibung_part1.sql`, `NNN_beschreibung_part2.sql`
   - Tabellen in part1, Dependencies in part2
   - Headers müssen Split dokumentieren

4. **Migration testen:**
   ```bash
   cd backend
   python run_migration.py
   ```

---

## Verifikation

**Alle Checks bestanden (2026-01-16):**

- ✅ Setup Wizard Order korrekt (alphabetisch)
- ✅ Schemas werden zuerst erstellt (001_core_users_roles.sql)
- ✅ Keine aktiven Duplikate
- ✅ Alle Dateien <500 Zeilen
- ✅ Foreign Key Dependencies in korrekter Reihenfolge
- ✅ Alle Lücken dokumentiert

**Siehe:** `.claude/MIGRATION_VERIFICATION_REPORT.md` für vollständigen Audit-Report

---

**Version:** 2.0
**Last Updated:** 2026-01-16
**Status:** ✅ PRODUCTION READY
