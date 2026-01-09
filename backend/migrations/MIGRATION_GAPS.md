# Migration Nummerierungslücken

**Stand:** 2026-01-06
**Grund:** Cleanup von toten/duplizierten Migrations

## Dokumentierte Lücken

| Nummer | Ursprüngliche Datei | Grund der Löschung |
|--------|--------------------|--------------------|
| 041 | `041_learning_method_types.sql` | Placeholder, Inhalt in 011 integriert |
| 042 | - | Nie existiert |
| 054 | `054_lm_refactoring_and_features.sql` | Deprecated LMs, Tabellen nach 008/026 verschoben |
| 063 | `063_system_features_tables.sql` | Tote Tabellen in PUBLIC Schema |
| 071 | - | Nie existiert |

## Warum nicht renummerieren?

1. **Git-Historie:** Renummerierung würde Historie verfälschen
2. **Referenzen:** Andere Dateien könnten Nummern referenzieren
3. **Risiko:** Fehler beim Umbenennen möglich

## Regel für Zukunft

Neue Migrations bekommen die nächste freie Nummer nach der höchsten existierenden:
- Aktuell höchste: 075
- Nächste neue Migration: 076
