# Backend Utility Scripts

Helper scripts for backend operations, testing, and maintenance.

## Available Scripts

### Database Migrations

**`run_all_migrations.py`** - Run all database migrations in order

```bash
# Run all migrations
python scripts/run_all_migrations.py

# Show help
python scripts/run_all_migrations.py --help
```

Migrations are organized by domain:
- `01_Core/` - User management, roles, authentication
- `02_Content/` - Courses, chapters, lessons
- `03_AI/` - AI models, prompts, jobs
- And more...

### Testing & Validation

**`test_features_api.py`** - Test Feature-Based Authorization API

```bash
# Run feature API tests
python scripts/test_features_api.py
```

Tests the following endpoints:
- Feature metadata endpoint (public)
- Available features endpoint (authenticated)
- Feature access check endpoint (authenticated)
- Context-filtered features endpoint (authenticated)

### Data Migration

**`migrations/i18n_migration.py`** - Migrate frontend i18n data to database

Migrates internationalization translations from frontend to database format.

**`migrations/i18n_setup.py`** - Setup i18n infrastructure

Initializes i18n support in the application.

## Usage from Backend Root

All scripts are designed to be called from the backend root directory:

```bash
cd /home/pascal/Lernsystem/backend

# Run migrations
python scripts/run_all_migrations.py

# Test features
python scripts/test_features_api.py

# Run i18n migration
python scripts/migrations/i18n_migration.py
```

## Development

When adding new scripts:
1. Place in appropriate subdirectory (e.g., `migrations/` for migration scripts)
2. Add `__init__.py` to new subdirectories
3. Update this README.md with usage instructions
4. Ensure scripts work when called from backend root
5. Use `Path(__file__).parent.parent` to reference backend root from scripts/

---

**Last Updated**: 2026-01-18
