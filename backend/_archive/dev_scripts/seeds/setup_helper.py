#!/usr/bin/env python3
"""
LernsystemX Setup Helper

Interactive setup script that guides you through the complete setup process.
"""

import os
import sys
import getpass
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv, set_key
load_dotenv()

import psycopg


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🚀 LernsystemX Setup Helper")
    print("=" * 70)
    print()


def test_postgres_connection(host, port, user, password, dbname='postgres'):
    """Test PostgreSQL connection"""
    try:
        conn = psycopg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=5
        )
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


def configure_database():
    """Interactive database configuration"""
    print("Step 1: PostgreSQL Configuration")
    print("-" * 70)
    print()

    # Get current settings
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_user = os.getenv('DB_USER', 'postgres')
    db_name = os.getenv('DB_NAME', 'lernsystemx_dev')

    print(f"Current settings:")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  User: {db_user}")
    print(f"  Database: {db_name}")
    print()

    # Ask for password
    print("Please enter your PostgreSQL password for user 'postgres':")
    print("(This is the password you set during PostgreSQL installation)")
    print()

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        password = getpass.getpass(f"Password (attempt {attempt}/{max_attempts}): ")

        # Test connection
        print("Testing connection...", end=" ")
        success, error = test_postgres_connection(db_host, db_port, db_user, password)

        if success:
            print("✓ SUCCESS!")
            print()

            # Save to .env file
            env_file = Path(__file__).parent / '.env'
            set_key(env_file, 'DB_PASSWORD', password)

            # Update DATABASE_URL
            database_url = f"postgresql://{db_user}:{password}@{db_host}:{db_port}/{db_name}"
            set_key(env_file, 'DATABASE_URL', database_url)

            print(f"✓ Configuration saved to .env")
            print()
            return True, password

        else:
            print(f"✗ FAILED")
            print(f"  Error: {error}")
            print()

    print("❌ Maximum attempts exceeded. Could not connect to PostgreSQL.")
    print()
    print("Please check:")
    print("  1. PostgreSQL is running: Get-Service postgresql-x64-17")
    print("  2. Your password is correct")
    print("  3. PostgreSQL is accepting connections on port 5432")
    print()
    return False, None


def reset_database(password):
    """Reset database"""
    print()
    print("Step 2: Database Reset")
    print("-" * 70)
    print()

    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_user = os.getenv('DB_USER', 'postgres')
    db_name = os.getenv('DB_NAME', 'lernsystemx_dev')

    print("This will:")
    print(f"  1. Drop database '{db_name}' (if exists)")
    print(f"  2. Create fresh database '{db_name}'")
    print(f"  3. Enable PostgreSQL extensions")
    print()

    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Skipped.")
        return False

    print()

    try:
        # Connect to postgres database
        print("Connecting to PostgreSQL...")
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=password,
            dbname='postgres',
            autocommit=True
        )
        cursor = conn.cursor()

        # Terminate connections
        print(f"Terminating existing connections to '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
        """)

        # Drop database
        print(f"Dropping database '{db_name}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")

        # Create database
        print(f"Creating database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")

        cursor.close()
        conn.close()

        # Connect to new database for extensions
        print("Enabling PostgreSQL extensions...")
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=password,
            dbname=db_name,
            autocommit=True
        )
        cursor = conn.cursor()

        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        print("  ✓ uuid-ossp")

        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        print("  ✓ pgcrypto")

        cursor.close()
        conn.close()

        print()
        print("✓ Database reset complete!")
        return True

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Main setup flow"""
    print_banner()

    # Step 1: Configure database
    success, password = configure_database()
    if not success:
        sys.exit(1)

    # Step 2: Reset database
    success = reset_database(password)
    if not success:
        print()
        print("Database reset failed. Please fix the errors and try again.")
        sys.exit(1)

    # Done
    print()
    print("=" * 70)
    print("✓ Setup Helper Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start the backend:")
    print("     python run.py")
    print()
    print("  2. Open browser and navigate to:")
    print("     http://localhost:5000/setup/status")
    print()
    print("  3. Click 'Initialize Database' to run all 40 migrations")
    print()
    print("The Setup Wizard will guide you through the rest!")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("Setup cancelled by user.")
        sys.exit(1)
