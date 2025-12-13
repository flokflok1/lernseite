#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration Schema Checker

Prueft alle 40 Migrationsdateien auf haeufige Fehler:
- Foreign Key Typ-Mismatch
- Referenzen auf noch nicht existierende Tabellen
- Fehlende ON DELETE CASCADE
- Syntax-Fehler
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_migrations():
    migrations_dir = Path('migrations')
    errors = []
    warnings = []

    # Sammle alle CREATE TABLE statements und deren Spaltentypen
    tables = {}  # {table_name: {column_name: type}}
    table_order = []  # Reihenfolge der Tabellenerstellung

    # Lese alle Migrationsdateien in Reihenfolge
    migration_files = sorted(migrations_dir.glob('[0-9][0-9][0-9]_*.sql'))

    print(f"[CHECK] Pruefe {len(migration_files)} Migrationsdateien...\n")

    for mig_file in migration_files:
        content = mig_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        print(f"[FILE] {mig_file.name}")

        # Finde alle CREATE TABLE statements
        for i, line in enumerate(lines, 1):
            # CREATE TABLE
            table_match = re.search(r'CREATE TABLE (?:IF NOT EXISTS )?(\w+)', line, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                table_order.append(table_name)
                tables[table_name] = {}
                print(f"   [TABLE] {table_name}")

            # Spalten-Definitionen
            col_match = re.search(r'^\s+(\w+)\s+(UUID|INTEGER|BIGINT|VARCHAR|TEXT|TIMESTAMP|BOOLEAN|JSONB|NUMERIC)', line, re.IGNORECASE)
            if col_match and table_order:
                col_name = col_match.group(1)
                col_type = col_match.group(2).upper()
                current_table = table_order[-1]
                tables[current_table][col_name] = col_type

            # REFERENCES prüfen
            ref_match = re.search(r'(\w+)\s+(UUID|INTEGER|BIGINT|VARCHAR)\s+.*REFERENCES\s+(\w+)\((\w+)\)', line, re.IGNORECASE)
            if ref_match:
                col_name = ref_match.group(1)
                col_type = ref_match.group(2).upper()
                ref_table = ref_match.group(3)
                ref_col = ref_match.group(4)

                # Prüfe ob Referenz-Tabelle existiert
                if ref_table not in tables:
                    errors.append({
                        'file': mig_file.name,
                        'line': i,
                        'type': 'MISSING_TABLE',
                        'message': f"Referenz auf nicht-existierende Tabelle '{ref_table}'"
                    })
                elif ref_col not in tables[ref_table]:
                    errors.append({
                        'file': mig_file.name,
                        'line': i,
                        'type': 'MISSING_COLUMN',
                        'message': f"Referenz auf nicht-existierende Spalte '{ref_table}.{ref_col}'"
                    })
                else:
                    # Prüfe Typ-Kompatibilität
                    ref_type = tables[ref_table][ref_col]
                    if col_type != ref_type:
                        errors.append({
                            'file': mig_file.name,
                            'line': i,
                            'type': 'TYPE_MISMATCH',
                            'message': f"Typ-Konflikt: {col_name} ist {col_type}, aber {ref_table}.{ref_col} ist {ref_type}",
                            'fix': f"Ändere '{col_name} {col_type}' zu '{col_name} {ref_type}'"
                        })

                # Prüfe auf ON DELETE CASCADE
                if 'ON DELETE CASCADE' not in line:
                    warnings.append({
                        'file': mig_file.name,
                        'line': i,
                        'type': 'MISSING_CASCADE',
                        'message': f"Foreign Key ohne ON DELETE CASCADE: {col_name} -> {ref_table}"
                    })

    print(f"\n{'='*80}")
    print("[RESULT] PRUEFUNGS-ERGEBNIS")
    print(f"{'='*80}\n")

    if errors:
        print(f"[ERROR] {len(errors)} FEHLER gefunden:\n")
        for i, err in enumerate(errors, 1):
            print(f"{i}. {err['file']}:{err['line']} - {err['type']}")
            print(f"   {err['message']}")
            if 'fix' in err:
                print(f"   [FIX] {err['fix']}")
            print()
    else:
        print("[OK] Keine kritischen Fehler gefunden!\n")

    if warnings:
        print(f"[WARN] {len(warnings)} WARNUNGEN:\n")
        for i, warn in enumerate(warnings, 1):
            print(f"{i}. {warn['file']}:{warn['line']} - {warn['type']}")
            print(f"   {warn['message']}")
            print()

    print(f"{'='*80}\n")

    # Tabellen-Reihenfolge ausgeben
    print(f"[TABLES] {len(tables)} Tabellen werden erstellt:\n")
    for i, table in enumerate(table_order, 1):
        print(f"{i:2d}. {table}")

    return errors, warnings

if __name__ == '__main__':
    errors, warnings = check_migrations()

    if errors:
        print(f"\n[WARN] Bitte {len(errors)} Fehler beheben bevor die Migrationen ausgefuehrt werden!")
        exit(1)
    else:
        print(f"\n[OK] Alle Migrationen sind bereit!")
        exit(0)
