#!/usr/bin/env python3
"""
i18n Migration Script: Frontend JSON → Database

Loads translation files from frontend/src/locales/ into database:
1. Parses JSON structure
2. Creates i18n_namespaces
3. Creates i18n_keys
4. Stores i18n_translations
5. Validates and reports progress

Usage:
    python migrate_frontend_i18n_to_db.py [--language de|en|pl|all] [--namespace admin|common|all]
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import argparse
import logging
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.database import get_connection
from app.repositories.i18n_repository import I18nRepository
from app.core.bootstrap.extensions import init_db_pool

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class I18nMigrator:
    """Handles migration of frontend JSON translations to database."""

    FRONTEND_LOCALES_PATH = Path(__file__).parent.parent.parent / "frontend" / "src" / "locales"
    SUPPORTED_LANGUAGES = ['de', 'en', 'pl']

    def __init__(self, language_filter: str = None, namespace_filter: str = None):
        """
        Initialize migrator.

        Args:
            language_filter: Language to migrate ('de', 'en', 'pl', or 'all')
            namespace_filter: Namespace to migrate or 'all'
        """
        self.language_filter = language_filter or 'all'
        self.namespace_filter = namespace_filter or 'all'
        self.stats = {
            'languages_processed': 0,
            'namespaces_created': 0,
            'keys_created': 0,
            'translations_created': 0,
            'errors': []
        }

    def get_languages(self) -> List[str]:
        """Get languages to process."""
        if self.language_filter == 'all':
            return self.SUPPORTED_LANGUAGES
        elif self.language_filter in self.SUPPORTED_LANGUAGES:
            return [self.language_filter]
        else:
            raise ValueError(f"Unknown language: {self.language_filter}")

    def get_json_files(self, language: str) -> Dict[str, Path]:
        """
        Get JSON files for a language.

        Returns dict of {namespace: filepath}
        """
        lang_dir = self.FRONTEND_LOCALES_PATH / language

        if not lang_dir.exists():
            raise FileNotFoundError(f"Language directory not found: {lang_dir}")

        files = {}

        # Find all .json files in language directory
        for json_file in lang_dir.glob("*.json"):
            namespace = json_file.stem  # filename without .json
            files[namespace] = json_file

        # Also check subdirectories (e.g., windows/*.json)
        for subdir in lang_dir.iterdir():
            if subdir.is_dir():
                for json_file in subdir.glob("*.json"):
                    # Use directory/file structure as namespace
                    namespace = f"{subdir.name}/{json_file.stem}"
                    files[namespace] = json_file

        return files

    def flatten_json(
        self,
        obj: Any,
        prefix: str = ""
    ) -> Dict[str, str]:
        """
        Flatten nested JSON structure into key=value pairs.

        Example:
            Input:  {"admin": {"users": {"title": "Users"}}}
            Output: {"admin.users.title": "Users"}
        """
        result = {}

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    result.update(self.flatten_json(value, new_key))
                elif isinstance(value, str):
                    result[new_key] = value
                else:
                    logger.warning(f"Skipping non-string value at {new_key}: {value}")

        return result

    def load_json_file(self, filepath: Path) -> Dict[str, str]:
        """
        Load and flatten JSON file.

        Returns dict of {key_path: translation_text}
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return self.flatten_json(data)

        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {e}")
            raise

    def migrate_language(self, language: str, connection) -> Tuple[int, int, int]:
        """
        Migrate translations for a language.

        Returns: (namespaces_created, keys_created, translations_created)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Migrating language: {language}")
        logger.info(f"{'='*70}")

        repo = I18nRepository(connection)
        namespaces_created = 0
        keys_created = 0
        translations_created = 0

        try:
            # Get JSON files for this language
            json_files = self.get_json_files(language)
            logger.info(f"Found {len(json_files)} JSON files for {language}")

            # Process each JSON file
            for namespace_code, filepath in sorted(json_files.items()):
                # Check namespace filter
                if (self.namespace_filter != 'all' and
                    not namespace_code.startswith(self.namespace_filter)):
                    logger.debug(f"Skipping namespace: {namespace_code}")
                    continue

                logger.info(f"  Processing namespace: {namespace_code}")

                # Load translations from JSON
                try:
                    translations = self.load_json_file(filepath)
                except Exception as e:
                    self.stats['errors'].append(
                        f"Failed to load {namespace_code}/{language}: {e}"
                    )
                    continue

                # Create/update namespace
                namespace_name = namespace_code.replace('/', ' - ').replace('_', ' ').title()
                namespace = repo.get_or_create_namespace(namespace_code, namespace_name)

                if namespace and 'key_count' in namespace:
                    # Namespace created
                    namespaces_created += 1
                    logger.debug(f"    Namespace created: {namespace_code}")

                # Create translations
                for key_path, translation_text in translations.items():
                    try:
                        # Create/update key and translation
                        result = repo.create_translation(
                            namespace_code,
                            key_path,
                            language,
                            translation_text,
                            translated_by=None  # System migration (no user attribution)
                        )

                        translations_created += 1

                    except Exception as e:
                        logger.warning(
                            f"    Error creating translation for "
                            f"{namespace_code}/{key_path}/{language}: {e}"
                        )
                        logger.debug(f"    Traceback: {traceback.format_exc()}")
                        self.stats['errors'].append(
                            f"Translation failed: {namespace_code}/{key_path}: {e}"
                        )

                logger.info(
                    f"    ✓ Created {translations_created} translations from "
                    f"{len(translations)} keys in {filepath.name}"
                )

            logger.info(f"\nLanguage {language} migration complete:")
            logger.info(f"  - Namespaces: {namespaces_created}")
            logger.info(f"  - Keys: {keys_created}")
            logger.info(f"  - Translations: {translations_created}")

        except Exception as e:
            logger.error(f"Error migrating language {language}: {e}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            self.stats['errors'].append(f"Language {language} failed: {e}")

        return namespaces_created, keys_created, translations_created

    def run(self) -> bool:
        """
        Run migration.

        Returns: True if successful, False if errors occurred
        """
        logger.info("\n" + "="*70)
        logger.info("i18n MIGRATION: Frontend JSON → Database")
        logger.info("="*70)

        # Check frontend locales path exists
        if not self.FRONTEND_LOCALES_PATH.exists():
            logger.error(f"Frontend locales path not found: {self.FRONTEND_LOCALES_PATH}")
            return False

        try:
            # Create Flask app and initialize database pool
            app = create_app('development')

            # The create_app() factory initializes the database pool via register_extensions()
            # No additional initialization needed here

            with app.app_context():
                # Migrate each language
                languages = self.get_languages()

                for language in languages:
                    try:
                        with get_connection() as conn:
                            ns, keys, trans = self.migrate_language(language, conn)
                            self.stats['languages_processed'] += 1
                            self.stats['namespaces_created'] += ns
                            self.stats['keys_created'] += keys
                            self.stats['translations_created'] += trans

                    except Exception as e:
                        logger.error(f"Failed to migrate language {language}: {e}")
                        logger.error(f"Full traceback:\n{traceback.format_exc()}")
                        self.stats['errors'].append(f"Language {language}: {e}")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            self.stats['errors'].append(f"Fatal error: {e}")
            return False

        # Print summary
        self._print_summary()

        return len(self.stats['errors']) == 0

    def _print_summary(self):
        """Print migration summary."""
        logger.info("\n" + "="*70)
        logger.info("MIGRATION SUMMARY")
        logger.info("="*70)
        logger.info(f"Languages processed: {self.stats['languages_processed']}")
        logger.info(f"Namespaces created: {self.stats['namespaces_created']}")
        logger.info(f"Keys created: {self.stats['keys_created']}")
        logger.info(f"Translations created: {self.stats['translations_created']}")

        if self.stats['errors']:
            logger.info(f"\n⚠️  {len(self.stats['errors'])} errors occurred:")
            for error in self.stats['errors'][:10]:  # Show first 10
                logger.info(f"  - {error}")
            if len(self.stats['errors']) > 10:
                logger.info(f"  ... and {len(self.stats['errors']) - 10} more")
        else:
            logger.info("\n✅ Migration completed successfully!")

        logger.info("="*70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Migrate frontend i18n JSON files to database'
    )
    parser.add_argument(
        '--language',
        choices=['de', 'en', 'pl', 'all'],
        default='all',
        help='Language to migrate (default: all)'
    )
    parser.add_argument(
        '--namespace',
        default='all',
        help='Namespace to migrate (default: all)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run migration
    migrator = I18nMigrator(args.language, args.namespace)
    success = migrator.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
