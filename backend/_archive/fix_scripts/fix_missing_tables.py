#!/usr/bin/env python
"""
Fix missing tables and data in database
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'lernsystemx_dev'),
    'user': os.getenv('DB_USER', 'lernsystem'),
    'password': os.getenv('DB_PASSWORD', '')
}

def create_missing_tables():
    """Create missing tables"""
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Create system_config table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            config_id SERIAL PRIMARY KEY,
            key VARCHAR(255) UNIQUE NOT NULL,
            value TEXT,
            encrypted BOOLEAN DEFAULT FALSE,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    print("[OK] Created system_config table")

    # Create ai_api_keys table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_api_keys (
            key_id SERIAL PRIMARY KEY,
            provider VARCHAR(50) UNIQUE NOT NULL,
            encrypted_key TEXT NOT NULL,
            salt VARCHAR(255) NOT NULL,
            metadata JSONB,
            active BOOLEAN DEFAULT TRUE,
            last_validated TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    print("[OK] Created ai_api_keys table")

    conn.commit()
    cur.close()
    conn.close()

def create_upload_directories():
    """Create missing upload directories"""
    dirs = [
        'uploads/courses',
        'uploads/profiles',
        'cache',
        'temp'
    ]

    for dir_path in dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"[OK] Created directory: {dir_path}")

if __name__ == '__main__':
    print("Fixing missing database tables and directories...")
    create_missing_tables()
    create_upload_directories()
    print("\n[SUCCESS] All fixes applied successfully!")
