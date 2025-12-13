#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LernsystemX Database Auto-Reset Script

Liest Credentials aus db_credentials.txt und resettet die Datenbank automatisch.
"""

import os
import sys
import psycopg
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def load_credentials():
    """Load credentials from db_credentials.txt"""
    creds_file = Path(__file__).parent / 'db_credentials.txt'

    if not creds_file.exists():
        print("❌ Fehler: db_credentials.txt nicht gefunden!")
        print()
        print("Erstelle die Datei mit folgendem Inhalt:")
        print()
        print("HOST=10.0.10.10")
        print("PORT=5432")
        print("USER=postgres")
        print("PASSWORD=dein_passwort")
        print("DATABASE=lernsystemx_dev")
        print()
        return None

    creds = {}
    with open(creds_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    creds[key.strip()] = value.strip()

    required = ['HOST', 'PORT', 'USER', 'PASSWORD', 'DATABASE']
    missing = [k for k in required if k not in creds]

    if missing:
        print(f"❌ Fehler: Fehlende Werte in db_credentials.txt: {', '.join(missing)}")
        return None

    return creds

def reset_database():
    """Drop and recreate the database"""

    print()
    print("=" * 80)
    print("  LernsystemX - Database Auto-Reset")
    print("=" * 80)
    print()

    # Load credentials
    print("  → Lade Zugangsdaten aus db_credentials.txt...")
    creds = load_credentials()

    if not creds:
        return False

    db_host = creds['HOST']
    db_port = int(creds['PORT'])
    db_user = creds['USER']
    db_password = creds['PASSWORD']
    db_name = creds['DATABASE']

    print(f"     ✓ Host: {db_host}:{db_port}")
    print(f"     ✓ User: {db_user}")
    print(f"     ✓ Database: {db_name}")
    print()

    try:
        # Connect to default postgres database
        print("  → Verbinde zu PostgreSQL...")
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname='postgres',
            autocommit=True
        )
        print("     ✓ Verbunden")

        cursor = conn.cursor()

        # Terminate existing connections
        print(f"  → Trenne aktive Verbindungen zu '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
        """)
        print("     ✓ Verbindungen getrennt")

        # Drop database
        print(f"  → Lösche Datenbank '{db_name}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
        print("     ✓ Datenbank gelöscht")

        cursor.close()
        conn.close()

        print()
        print("  HINWEIS: Datenbank wurde GELÖSCHT aber nicht neu erstellt.")
        print("  Der Setup Wizard wird die Datenbank automatisch erstellen.")

        print()
        print("=" * 80)
        print("  ✅ ERFOLGREICH! Datenbank wurde zurückgesetzt.")
        print("=" * 80)
        print()
        print("  Nächster Schritt:")
        print("  → Gehe zum Setup Wizard und klicke 'Datenbank initialisieren'")
        print("  → Jetzt sollten ALLE 40 Migrations ausgeführt werden!")
        print()
        print("=" * 80)
        print()

        return True

    except psycopg.OperationalError as e:
        print()
        print("=" * 80)
        print("  ❌ VERBINDUNGSFEHLER!")
        print("=" * 80)
        print()
        print(f"  {str(e)}")
        print()
        print("  Prüfe die Zugangsdaten in db_credentials.txt")
        print()
        return False

    except Exception as e:
        print()
        print("=" * 80)
        print("  ❌ FEHLER!")
        print("=" * 80)
        print()
        print(f"  {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        print()
        return False

if __name__ == '__main__':
    success = reset_database()
    sys.exit(0 if success else 1)
