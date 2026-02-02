"""
Setup Wizard: i18n System Integration

Handles i18n import during first-time system setup.
- Step in Setup Wizard execution flow
- Reads frontend locale JSON files (de, en, pl)
- Imports into database (i18n_keys + i18n_translations)
- Provides status and progress information
- Validates import completeness

Usage in Setup Wizard:
    from setup.i18n_setup import I18nSetup

    # Get step info
    step_info = I18nSetup.get_step_info()

    # Execute import
    success, result = await I18nSetup.execute()

ISO/IEC/IEEE 26515:2018 compliant
"""

from typing import Tuple, Dict, Any, List
from pathlib import Path
import logging

from app.services.i18n_import_service import I18nImportService
from app.repositories.i18n_import_repository import I18nImportRepository

logger = logging.getLogger(__name__)


class I18nSetup:
    """Setup Wizard step for i18n system initialization"""

    @staticmethod
    def get_step_info() -> Dict[str, Any]:
        """
        Get setup step metadata

        Returns:
            {
              'step': 'i18n_import',
              'title': 'Internationalization (i18n)',
              'description': 'Import frontend translations into database',
              'required': True,
              'order': 2,  # After database, before admin
              'dependencies': ['database'],
              'estimated_duration_seconds': 15,
              'rollback_supported': True
            }
        """
        return {
            'step': 'i18n_import',
            'title': 'Internationalization (i18n)',
            'description': 'Import frontend translations into database',
            'required': True,
            'order': 2,
            'dependencies': ['database'],
            'estimated_duration_seconds': 15,
            'rollback_supported': True
        }

    @staticmethod
    async def validate_prerequisites() -> Tuple[bool, List[str]]:
        """
        Validate that setup can proceed

        Checks:
        - Database initialized (i18n tables exist)
        - Frontend locale files exist
        - All 3 languages present (de, en, pl)
        - Locale files are readable

        Returns:
            (is_valid: bool, issues: List[str])
        """
        issues = []

        # Check database tables exist
        try:
            from app.repositories.i18n_import_repository import I18nImportRepository
            namespaces = I18nImportRepository.get_all_namespaces()
            if not namespaces:
                issues.append("No i18n namespaces found in database - run migrations first")
        except Exception as e:
            issues.append(f"Database check failed: {str(e)}")

        # Check frontend locales exist
        locales_path = I18nImportService.LOCALES_PATH
        if not locales_path.exists():
            issues.append(f"Frontend locale directory not found: {locales_path}")
        else:
            # Check each language directory
            for lang in I18nImportService.LANGUAGES:
                lang_path = locales_path / lang
                if not lang_path.exists():
                    issues.append(f"Language directory missing: {lang_path}")

        return len(issues) == 0, issues

    @staticmethod
    async def execute() -> Tuple[bool, Dict[str, Any]]:
        """
        Execute i18n import

        Workflow:
        1. Validate prerequisites
        2. Read locale files
        3. Create i18n_keys entries
        4. Create i18n_translations entries
        5. Validate completeness
        6. Return status

        Returns:
            (
              success: bool,
              result: {
                'status': 'completed' | 'partial' | 'failed',
                'title': 'i18n System',
                'message': 'Imported X keys and Y translations',
                'stats': {
                  'keys_created': 345,
                  'translations_created': 1035,
                  'languages_imported': 3,
                  'files_processed': 8,
                  'duration_seconds': 12.5
                },
                'warnings': [],
                'errors': []
              }
            )
        """
        result = {
            'status': 'pending',
            'title': 'i18n System',
            'message': '',
            'stats': {
                'keys_created': 0,
                'translations_created': 0,
                'languages_imported': 0,
                'files_processed': 0,
                'duration_seconds': 0
            },
            'warnings': [],
            'errors': []
        }

        try:
            # Step 1: Validate prerequisites
            logger.info("[i18n] Validating prerequisites...")
            is_valid, issues = await I18nSetup.validate_prerequisites()
            if not is_valid:
                logger.error(f"[i18n] Prerequisite check failed: {issues}")
                result['status'] = 'failed'
                result['errors'].extend(issues)
                result['message'] = f"Setup failed: {issues[0]}"
                return False, result

            logger.info("[i18n] ✓ Prerequisites validated")

            # Step 2: Read locale files
            logger.info("[i18n] Reading locale files...")
            try:
                locales = I18nImportService.read_all_locales()
                languages_imported = len(locales)
                logger.info(f"[i18n] ✓ Loaded {languages_imported} languages")
            except Exception as e:
                logger.error(f"[i18n] Failed to read locale files: {str(e)}")
                result['status'] = 'failed'
                result['errors'].append(str(e))
                result['message'] = f"Failed to read locale files: {str(e)}"
                return False, result

            # Step 3: Collect keys and validate
            logger.info("[i18n] Collecting unique keys...")
            all_keys = I18nImportService.collect_all_keys(locales)
            logger.info(f"[i18n] ✓ Found {len(all_keys)} unique keys")

            # Step 4: Import to database
            logger.info("[i18n] Creating database entries...")
            keys_created = 0
            translations_created = 0
            errors = []

            # Get all namespaces
            namespaces = I18nImportRepository.get_all_namespaces()
            if not namespaces:
                raise Exception("No i18n namespaces found in database")

            # Create keys and translations
            for key_path, (namespace_code, _) in all_keys.items():
                namespace_id = namespaces.get(namespace_code)
                if not namespace_id:
                    errors.append(f"Unknown namespace: {namespace_code}")
                    continue

                # Create key
                key_id = I18nImportRepository.create_key(namespace_id, key_path)
                if key_id:
                    keys_created += 1

                    # Create translations for each language
                    for language in I18nImportService.LANGUAGES:
                        try:
                            value = locales[language].get(namespace_code, {}).get(key_path)
                            if not value:
                                errors.append(
                                    f"Missing translation: {key_path} [{language}]"
                                )
                                continue

                            trans_id = I18nImportRepository.create_translation(
                                key_id,
                                language,
                                value
                            )
                            if trans_id:
                                translations_created += 1
                        except Exception as e:
                            logger.warning(
                                f"Failed to create translation for {key_path} [{language}]: {str(e)}"
                            )
                            errors.append(str(e))
                else:
                    errors.append(f"Failed to create key: {key_path}")

            logger.info(f"[i18n] ✓ Created {keys_created} keys and {translations_created} translations")

            # Step 5: Validate import
            logger.info("[i18n] Validating import completeness...")
            validation = I18nImportRepository.validate_import_complete()

            if validation['is_complete']:
                logger.info("[i18n] ✓ Import validation passed")
                result['status'] = 'completed'
                success = True
            else:
                logger.warning(f"[i18n] Validation issues: {validation['issues']}")
                result['status'] = 'partial'
                result['warnings'].extend(validation['issues'])
                # Still return True since we have at least some data
                success = True

            # Step 6: Prepare result
            result['stats']['keys_created'] = keys_created
            result['stats']['translations_created'] = translations_created
            result['stats']['languages_imported'] = languages_imported
            result['stats']['files_processed'] = sum(
                len(files) for files in
                [list((I18nImportService.LOCALES_PATH / lang).glob('*.json'))
                 for lang in I18nImportService.LANGUAGES]
            )

            if result['status'] == 'completed':
                result['message'] = (
                    f"Successfully imported {keys_created} keys and "
                    f"{translations_created} translations for {languages_imported} languages"
                )
            else:
                result['message'] = (
                    f"Partially imported {keys_created} keys and "
                    f"{translations_created} translations (see warnings)"
                )

            if errors:
                result['errors'] = errors[:10]  # Limit to first 10 errors

            return success, result

        except Exception as e:
            logger.exception("[i18n] Unexpected error during import")
            result['status'] = 'failed'
            result['message'] = f"Unexpected error: {str(e)}"
            result['errors'].append(str(e))
            return False, result

    @staticmethod
    async def rollback() -> Tuple[bool, str]:
        """
        Rollback i18n import (delete all imported data)

        WARNING: This deletes all i18n_translations and i18n_keys!
        Only use for setup rollback.

        Returns:
            (success: bool, message: str)
        """
        try:
            logger.warning("[i18n] Rolling back import - deleting all translations and keys")
            success = I18nImportRepository.delete_all_imports()
            if success:
                return True, "i18n rollback completed"
            else:
                return False, "i18n rollback failed"
        except Exception as e:
            logger.exception("[i18n] Rollback failed")
            return False, f"Rollback error: {str(e)}"

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """
        Get current i18n import status

        Returns:
            {
              'is_initialized': True | False,
              'statistics': {
                'total_keys': 345,
                'total_translations': 1035,
                'languages': 3,
                'namespaces': 8
              }
            }
        """
        try:
            stats = I18nImportRepository.get_import_statistics()
            return {
                'is_initialized': stats['total_keys'] > 0,
                'statistics': stats
            }
        except Exception as e:
            logger.error(f"Failed to get i18n status: {str(e)}")
            return {
                'is_initialized': False,
                'statistics': None,
                'error': str(e)
            }


# Export for use in Setup Wizard
__all__ = ['I18nSetup']
