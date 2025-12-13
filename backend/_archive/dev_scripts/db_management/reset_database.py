#!/usr/bin/env python3
"""
LernsystemX Database Reset Script

Drops and recreates the database for a fresh start.
Run this before using the Setup Wizard.

Usage:
    python reset_database.py
"""

import os
import sys
import psycopg
from pathlib import Path
from getpass import getpass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def reset_database():
    """Drop and recreate the database - interaktiv mit Login-Eingabe"""

    print()
    print("=" * 80)
    print("  LernsystemX - Database Reset Tool")
    print("=" * 80)
    print()
    print("  Dieses Tool droppt die komplette Datenbank und erstellt sie neu.")
    print("  ACHTUNG: Alle vorhandenen Daten werden gelöscht!")
    print()
    print("=" * 80)
    print()

    # Interactive credential input
    print("Bitte gib deine PostgreSQL Zugangsdaten ein:")
    print()

    db_host = input("  PostgreSQL Host (z.B. 10.0.10.10): ").strip()
    if not db_host:
        print("\n❌ Host darf nicht leer sein!")
        return False

    db_port_input = input("  PostgreSQL Port [5432]: ").strip()
    db_port = int(db_port_input) if db_port_input else 5432

    db_user = input("  PostgreSQL User (z.B. postgres): ").strip()
    if not db_user:
        print("\n❌ User darf nicht leer sein!")
        return False

    db_password = getpass("  PostgreSQL Passwort: ")

    db_name = input("  Datenbank Name (z.B. lernsystemx_dev): ").strip()
    if not db_name:
        print("\n❌ Datenbank Name darf nicht leer sein!")
        return False

    print()
    print("-" * 80)
    print("  Zusammenfassung:")
    print("-" * 80)
    print(f"  Host:       {db_host}:{db_port}")
    print(f"  User:       {db_user}")
    print(f"  Datenbank:  {db_name}")
    print("-" * 80)
    print()

    # Confirm action
    confirm = input("  Möchtest du fortfahren? (ja/nein): ").strip().lower()
    if confirm not in ['ja', 'j', 'yes', 'y']:
        print("\n  ❌ Abgebrochen.")
        print()
        return False

    print()
    print("  → Verbinde zu PostgreSQL...")

    try:
        # Connect to default postgres database
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname='postgres',
            autocommit=True
        )

        cursor = conn.cursor()

        # Terminate existing connections to the database
        print(f"  → Trenne aktive Verbindungen zu '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
        """)

        # Drop database if exists
        print(f"  → Lösche Datenbank '{db_name}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")

        # Create fresh database
        print(f"  → Erstelle neue Datenbank '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")

        cursor.close()
        conn.close()

        # Connect to new database to enable extensions
        print(f"  → Aktiviere PostgreSQL Extensions...")
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
            autocommit=True
        )

        cursor = conn.cursor()

        # Enable uuid-ossp extension
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        print("     ✓ uuid-ossp aktiviert")

        # Enable pgcrypto extension
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        print("     ✓ pgcrypto aktiviert")

        cursor.close()
        conn.close()

        print()
        print("=" * 80)
        print("  ✅ ERFOLGREICH! Datenbank wurde zurückgesetzt.")
        print("=" * 80)
        print()
        print("  Nächste Schritte:")
        print()
        print("  1. Gehe zum Setup Wizard: http://10.0.20.111:5173/setup")
        print("  2. Gib die gleichen Zugangsdaten ein:")
        print(f"     Host: {db_host}")
        print(f"     Port: {db_port}")
        print(f"     User: {db_user}")
        print(f"     Datenbank: {db_name}")
        print("  3. Klicke auf 'Datenbank initialisieren'")
        print("  4. Jetzt sollten ALLE 40 Migrations ausgeführt werden!")
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
        print(f"  Fehler: {str(e)}")
        print()
        print("  Mögliche Lösungen:")
        print("   1. Prüfe ob PostgreSQL läuft")
        print("   2. Prüfe die Zugangsdaten (User/Passwort)")
        print("   3. Prüfe ob PostgreSQL auf Port {db_port} erreichbar ist")
        print("   4. Prüfe die Firewall-Einstellungen")
        print()
        print("=" * 80)
        print()
        return False

    except psycopg.errors.InsufficientPrivilege as e:
        print()
        print("=" * 80)
        print("  ❌ KEINE BERECHTIGUNG!")
        print("=" * 80)
        print()
        print(f"  Der User '{db_user}' hat keine Rechte um Datenbanken zu löschen/erstellen.")
        print()
        print("  Lösung:")
        print("   Verwende einen Superuser (z.B. 'postgres')")
        print()
        print("=" * 80)
        print()
        return False

    except Exception as e:
        print()
        print("=" * 80)
        print("  ❌ FEHLER!")
        print("=" * 80)
        print()
        print(f"  Unerwarteter Fehler: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 80)
        print()
        return False


if __name__ == '__main__':
    success = reset_database()
    sys.exit(0 if success else 1)
