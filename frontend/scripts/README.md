# Frontend Scripts

Utility and development scripts for the LernSystemX frontend application.

## Directory Structure

### `scripts/i18n/` - Internationalization (i18n) Scripts

Scripts for managing and validating internationalization/translation files.

**Scripts:**
- **`final-restructure.py`** - Final i18n restructuring automation
- **`restructure-all.py`** - Comprehensive i18n restructuring
- **`split-admin.py`** - Split admin translations into separate files
- **`validate-i18n.py`** - Validate i18n consistency across language files

**Purpose:** Manage translations across supported languages (de, en, pl) and ensure consistency.

**Usage:**
```bash
# Validate i18n files
python scripts/i18n/validate-i18n.py

# Restructure translations
python scripts/i18n/restructure-all.py

# Split admin translations
python scripts/i18n/split-admin.py
```

**Status:** See `RESTRUCTURE_COMPLETE.md` for migration status.

### `scripts/setup/` - Setup and Verification Scripts

Scripts for verifying and configuring the development environment.

**Scripts:**
- **`check-setup.js`** - Verify frontend development setup

**Purpose:** Check that all required dependencies and configurations are correct.

**Usage:**
```bash
npm run check
# or
node scripts/setup/check-setup.js
```

## Running Scripts

All scripts are designed to be called from the **frontend root directory**:

```bash
cd /home/pascal/Lernsystem/frontend

# i18n scripts
python scripts/i18n/validate-i18n.py
python scripts/i18n/restructure-all.py

# Setup verification
npm run check
```

## Adding New Scripts

When adding new scripts:

1. Place in appropriate subdirectory (`i18n/`, `setup/`, etc.)
2. Add `__init__.py` for Python subdirectories
3. Update this README.md with usage instructions
4. Ensure scripts work when called from frontend root
5. Use `Path(__file__).parent.parent` for Python scripts to reference frontend root

## Last Updated

2026-01-18
