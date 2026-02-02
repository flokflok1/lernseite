#!/usr/bin/env python3
"""
Migration Script: Import locale JSON files to database.

This script reads all locale JSON files from the frontend and imports them
into the translations schema in the database.

Usage:
    python scripts/migrate_locale_to_db.py

Schema:
    - translations.i18n_namespaces (namespace_code, name, description)
    - translations.i18n_keys (namespace_code, key_path, default_value)
    - translations.i18n_translations (key_id, language_code, translated_value)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import uuid

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg
from psycopg.rows import dict_row

# Configuration
FRONTEND_LOCALES_PATH = Path(__file__).parent.parent.parent / "frontend" / "src" / "infrastructure" / "i18n" / "locales"
LANGUAGES = ["de", "en", "pl"]
DEFAULT_LANGUAGE = "de"

# Database connection (using service file)
DB_SERVICE = "devdb"


def get_connection() -> psycopg.Connection:
    """Get database connection using service file."""
    return psycopg.connect(f"service={DB_SERVICE}")


def flatten_json(data: Dict, parent_key: str = "", sep: str = ".") -> Dict[str, str]:
    """
    Flatten nested JSON into dot-notation keys.

    Example:
        {"admin": {"title": "Admin"}} -> {"admin.title": "Admin"}
    """
    items = {}
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, sep))
        else:
            items[new_key] = str(value) if value is not None else ""
    return items


def get_namespace_from_path(file_path: Path, lang: str) -> str:
    """
    Extract namespace from file path.

    Example:
        /locales/de/admin/users.json -> admin.users
        /locales/de/common/index.json -> common
    """
    # Get relative path from language folder
    parts = file_path.relative_to(FRONTEND_LOCALES_PATH / lang).parts

    # Remove .json extension from last part
    parts = list(parts)
    parts[-1] = parts[-1].replace(".json", "")

    # If last part is 'index', remove it (e.g., common/index.json -> common)
    if parts[-1] == "index":
        parts = parts[:-1]

    return ".".join(parts) if parts else "root"


def load_locale_files() -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Load all locale files and return structured data.

    Returns:
        {
            "namespace": {
                "language_code": {
                    "key.path": "translated value"
                }
            }
        }
    """
    all_translations: Dict[str, Dict[str, Dict[str, str]]] = {}

    for lang in LANGUAGES:
        lang_path = FRONTEND_LOCALES_PATH / lang
        if not lang_path.exists():
            print(f"Warning: Language folder not found: {lang_path}")
            continue

        # Find all JSON files
        for json_file in lang_path.rglob("*.json"):
            namespace = get_namespace_from_path(json_file, lang)

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Flatten the JSON
                flat_data = flatten_json(data)

                # Initialize namespace if not exists
                if namespace not in all_translations:
                    all_translations[namespace] = {}

                # Store translations for this language
                all_translations[namespace][lang] = flat_data

                print(f"  Loaded: {lang}/{namespace} ({len(flat_data)} keys)")

            except json.JSONDecodeError as e:
                print(f"  Error parsing {json_file}: {e}")
            except Exception as e:
                print(f"  Error loading {json_file}: {e}")

    return all_translations


def ensure_namespace_exists(cursor, namespace_code: str) -> None:
    """Create namespace if it doesn't exist."""
    # Create human-readable name from namespace code
    name = namespace_code.replace(".", " > ").title()

    cursor.execute("""
        INSERT INTO translations.i18n_namespaces (namespace_code, name, description, is_active)
        VALUES (%s, %s, %s, TRUE)
        ON CONFLICT (namespace_code) DO NOTHING
    """, (namespace_code, name, f"Auto-imported from locale files"))


def get_or_create_key(cursor, namespace_code: str, key_path: str, default_value: str) -> str:
    """Get existing key_id or create new key. Returns key_id."""
    # Try to get existing key
    cursor.execute("""
        SELECT key_id FROM translations.i18n_keys
        WHERE namespace_code = %s AND key_path = %s
    """, (namespace_code, key_path))

    result = cursor.fetchone()
    if result:
        return result[0]

    # Create new key
    key_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO translations.i18n_keys (key_id, namespace_code, key_path, default_value, is_active)
        VALUES (%s, %s, %s, %s, TRUE)
    """, (key_id, namespace_code, key_path, default_value))

    return key_id


def insert_translation(cursor, key_id: str, language_code: str, translated_value: str) -> bool:
    """Insert or update translation. Returns True if inserted/updated."""
    cursor.execute("""
        INSERT INTO translations.i18n_translations
            (key_id, language_code, translated_value, translation_source, is_verified, is_active)
        VALUES (%s, %s, %s, 'imported', TRUE, TRUE)
        ON CONFLICT (key_id, language_code)
        DO UPDATE SET
            translated_value = EXCLUDED.translated_value,
            translation_source = 'imported',
            updated_at = NOW()
        WHERE translations.i18n_translations.translated_value != EXCLUDED.translated_value
    """, (key_id, language_code, translated_value))

    return cursor.rowcount > 0


def migrate_translations(all_translations: Dict[str, Dict[str, Dict[str, str]]]) -> Tuple[int, int, int]:
    """
    Migrate all translations to database.

    Returns:
        (namespaces_created, keys_created, translations_created)
    """
    namespaces_created = 0
    keys_created = 0
    translations_inserted = 0

    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Process each namespace
            for namespace_code, lang_translations in all_translations.items():
                print(f"\nProcessing namespace: {namespace_code}")

                # Ensure namespace exists
                ensure_namespace_exists(cursor, namespace_code)
                namespaces_created += 1

                # Collect all unique keys from all languages
                all_keys = set()
                for lang_data in lang_translations.values():
                    all_keys.update(lang_data.keys())

                # Process each key
                for key_path in all_keys:
                    # Get default value (prefer German, then English)
                    default_value = (
                        lang_translations.get(DEFAULT_LANGUAGE, {}).get(key_path) or
                        lang_translations.get("en", {}).get(key_path) or
                        ""
                    )

                    # Get or create key
                    key_id = get_or_create_key(cursor, namespace_code, key_path, default_value)
                    keys_created += 1

                    # Insert translations for each language
                    for lang_code, translations in lang_translations.items():
                        if key_path in translations:
                            translated_value = translations[key_path]
                            if insert_translation(cursor, key_id, lang_code, translated_value):
                                translations_inserted += 1

            # Commit all changes
            conn.commit()

    return namespaces_created, keys_created, translations_inserted


def update_language_stats() -> None:
    """Update language statistics (total_keys, translated_keys, completion_percent)."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Get total keys count
            cursor.execute("SELECT COUNT(*) FROM translations.i18n_keys WHERE is_active = TRUE")
            total_keys = cursor.fetchone()[0]

            # Update each language
            cursor.execute("""
                UPDATE translations.supported_languages sl
                SET
                    total_keys = %s,
                    translated_keys = COALESCE((
                        SELECT COUNT(DISTINCT t.key_id)
                        FROM translations.i18n_translations t
                        WHERE t.language_code = sl.language_code AND t.is_active = TRUE
                    ), 0),
                    completion_percent = CASE
                        WHEN %s > 0 THEN ROUND(
                            COALESCE((
                                SELECT COUNT(DISTINCT t.key_id)::numeric
                                FROM translations.i18n_translations t
                                WHERE t.language_code = sl.language_code AND t.is_active = TRUE
                            ), 0) / %s * 100, 2
                        )
                        ELSE 0
                    END,
                    last_sync_at = NOW()
            """, (total_keys, total_keys, total_keys))

            conn.commit()

            print(f"\nUpdated language statistics (total_keys: {total_keys})")


def main():
    """Main migration function."""
    print("=" * 60)
    print("Locale JSON to Database Migration")
    print("=" * 60)

    # Check if locales path exists
    if not FRONTEND_LOCALES_PATH.exists():
        print(f"Error: Locales path not found: {FRONTEND_LOCALES_PATH}")
        sys.exit(1)

    print(f"\nSource: {FRONTEND_LOCALES_PATH}")
    print(f"Languages: {', '.join(LANGUAGES)}")
    print(f"Default language: {DEFAULT_LANGUAGE}")

    # Load all locale files
    print("\n--- Loading locale files ---")
    all_translations = load_locale_files()

    if not all_translations:
        print("No translations found!")
        sys.exit(1)

    print(f"\nLoaded {len(all_translations)} namespaces")

    # Migrate to database
    print("\n--- Migrating to database ---")
    namespaces, keys, translations = migrate_translations(all_translations)

    # Update language statistics
    print("\n--- Updating language statistics ---")
    update_language_stats()

    # Summary
    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print(f"Namespaces processed: {namespaces}")
    print(f"Keys processed: {keys}")
    print(f"Translations inserted/updated: {translations}")


if __name__ == "__main__":
    main()
