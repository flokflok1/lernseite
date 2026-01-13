#!/usr/bin/env python3
"""
Seed AI Providers into the database
Run this script once to add the default AI providers
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize the Flask app to setup database pool
from app import create_app
app = create_app()

# Push application context
ctx = app.app_context()
ctx.push()

from app.database.connection import execute_query, fetch_all

def seed_ai_providers():
    """Insert default AI providers if they don't exist"""

    # Check if providers already exist
    check_query = "SELECT COUNT(*) as count FROM ai_providers"
    try:
        result = fetch_all(check_query)
        if result and result[0].get('count', 0) > 0:
            print(f"AI providers already exist ({result[0]['count']} providers found)")
            return
    except Exception as e:
        print(f"Error checking providers: {e}")
        # Table might not exist, try to create it

    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ai_providers (
        provider_id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        display_name VARCHAR(255) NOT NULL,
        provider_type VARCHAR(50) NOT NULL,
        base_url VARCHAR(500),
        api_version VARCHAR(20),
        encrypted_api_key TEXT,
        encryption_salt VARCHAR(255),
        active BOOLEAN DEFAULT TRUE,
        priority INTEGER DEFAULT 0,
        rate_limit_per_minute INTEGER,
        config JSONB,
        last_validated TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    try:
        execute_query(create_table_sql)
        print("AI providers table created/verified")
    except Exception as e:
        print(f"Note: {e}")

    # Create health table if not exists
    create_health_sql = """
    CREATE TABLE IF NOT EXISTS ai_provider_health (
        health_id BIGSERIAL PRIMARY KEY,
        provider_id INTEGER REFERENCES ai_providers(provider_id) ON DELETE CASCADE,
        status VARCHAR(20) NOT NULL,
        response_time_ms INTEGER,
        error_message TEXT,
        checked_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    try:
        execute_query(create_health_sql)
        print("AI provider health table created/verified")
    except Exception as e:
        print(f"Note: {e}")

    # Insert default providers
    providers = [
        ('openai', 'OpenAI', 'openai', 'https://api.openai.com/v1', 100, 60),
        ('anthropic', 'Anthropic Claude', 'anthropic', 'https://api.anthropic.com', 90, 60),
        ('google', 'Google Gemini', 'google', 'https://generativelanguage.googleapis.com', 80, 60),
    ]

    insert_sql = """
    INSERT INTO ai_providers (name, display_name, provider_type, base_url, priority, rate_limit_per_minute, active)
    VALUES (%s, %s, %s, %s, %s, %s, false)
    ON CONFLICT (name) DO NOTHING
    """

    for provider in providers:
        try:
            execute_query(insert_sql, provider)
            print(f"Inserted provider: {provider[0]}")
        except Exception as e:
            print(f"Error inserting {provider[0]}: {e}")

    # Verify
    result = fetch_all("SELECT provider_id, name, display_name, active FROM ai_providers ORDER BY priority DESC")
    print(f"\nAI Providers in database:")
    for row in result:
        print(f"  - {row['name']} ({row['display_name']}) - Active: {row['active']}")


if __name__ == '__main__':
    print("Seeding AI Providers...")
    seed_ai_providers()
    print("\nDone!")
