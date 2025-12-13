# Setup Wizard API Documentation

**Version:** 1.0.0
**Base URL:** `/setup`
**ISO/IEC/IEEE 26515:2018 Compliant**

## Overview

The Setup Wizard API provides endpoints for initial system installation and configuration. All endpoints return JSON responses with consistent error handling.

**Installation Flow:**
1. Check Status → 2. System Check → 3. Database Init → 4. Admin Creation → 5. Organisation Setup → 6. KI Config → 7. Seed Data → 8. Complete

---

## Endpoints

### 1. GET /setup/status
Check installation status

**Response:**
```json
{
  "installed": false,
  "version": null,
  "requires_setup": true,
  "install_info": null
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/setup/status
```

---

### 2. POST /setup/check
Run comprehensive system checks

**Checks:**
- Python 3.12+ version
- PostgreSQL connection
- Redis connection
- File permissions
- Port availability
- Dependencies

**Response:**
```json
{
  "success": true,
  "can_proceed": true,
  "checks": [
    {
      "name": "Python Version",
      "status": "ok",
      "message": "Python 3.12.0 detected",
      "details": "Required: 3.12+"
    },
    {
      "name": "PostgreSQL Connection",
      "status": "ok",
      "message": "Connected to PostgreSQL 16.0",
      "details": "Connection successful"
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/setup/check
```

---

### 3. POST /setup/database
Initialize database schema

**Creates:**
- 15 core tables (users, roles, organisations, etc.)
- 26+ performance indexes
- Constraints and foreign keys

**Response:**
```json
{
  "success": true,
  "database_created": false,
  "tables_created": 15,
  "indexes_created": 26,
  "errors": []
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/setup/database
```

**Tables Created:**
1. `users` - User accounts with 2FA support
2. `roles` - User roles with hierarchy (10 roles)
3. `organisations` - Multi-tenancy support
4. `courses` - Course management
5. `modules` - Course modules
6. `learning_methods` - 21 learning methods
7. `token_wallets` - AI token management
8. `token_transactions` - Token usage tracking
9. `subscriptions` - Stripe subscriptions
10. `system_config` - System configuration
11. `audit_logs` - Audit trail
12. `ai_api_keys` - Encrypted API keys
13. `categories` - 5-level categorization
14. `recovery_codes` - Account recovery
15. `migration_history` - Migration tracking

---

### 4. POST /setup/admin
Create superadmin user with 2FA support

**Request Body:**
```json
{
  "email": "admin@lsx.de",
  "password": "SecurePass123!",
  "first_name": "Admin",
  "last_name": "User",
  "enable_2fa": true
}
```

**Password Requirements:**
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Response (without 2FA):**
```json
{
  "success": true,
  "user_id": 1,
  "email": "admin@lsx.de",
  "first_name": "Admin",
  "last_name": "User",
  "recovery_codes": [
    "a3f9d2e1b4c7f8a2",
    "b2c8e3d1a6f9e4b7",
    "..."
  ],
  "message": "Admin user created successfully"
}
```

**Response (with 2FA):**
```json
{
  "success": true,
  "user_id": 1,
  "email": "admin@lsx.de",
  "first_name": "Admin",
  "last_name": "User",
  "recovery_codes": ["...", "..."],
  "totp_secret": "JBSWY3DPEHPK3PXP",
  "two_factor_enabled": true,
  "qr_code": "iVBORw0KGgoAAAANSUhEUgAA...",
  "message": "Admin user created successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/setup/admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@lsx.de",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "last_name": "User",
    "enable_2fa": true
  }'
```

**Important:** Save recovery codes securely! They are shown only once.

---

### 5. POST /setup/organisation
Create organisation (LSX Academy, schools, companies)

**Request Body (LSX Academy):**
```json
{
  "name": "LSX Academy",
  "type": "system",
  "domain": "lsx.de"
}
```

**Request Body (Custom Organisation):**
```json
{
  "name": "Example School",
  "type": "school",
  "domain": "school.example.com",
  "branding": {
    "primary_color": "#3b82f6",
    "secondary_color": "#1e40af",
    "logo_url": "/uploads/logo.png"
  },
  "settings": {
    "max_users": 1000,
    "allow_public_courses": false
  }
}
```

**Organisation Types:**
- `system` - LSX Academy (default system org)
- `school` - Schools with teachers and students
- `company` - Corporate training
- `creator_org` - Content creators
- `community` - Community learning

**Response:**
```json
{
  "success": true,
  "organisation_id": 1,
  "name": "LSX Academy",
  "type": "system",
  "domain": "lsx.de",
  "message": "Organisation created successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/setup/organisation \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LSX Academy",
    "type": "system",
    "domain": "lsx.de"
  }'
```

---

### 6. POST /setup/ki-config
Configure AI API keys (encrypted)

**Request Body:**
```json
{
  "provider": "openai",
  "api_key": "sk-proj-...",
  "validate": true,
  "metadata": {
    "model": "gpt-4",
    "organization": "org-..."
  }
}
```

**Supported Providers:**
- `openai` - GPT-4, GPT-3.5
- `anthropic` - Claude (Sonnet, Opus, Haiku)
- `google` - PaLM, Gemini
- `cohere` - Cohere AI
- `huggingface` - HuggingFace Inference

**Response:**
```json
{
  "success": true,
  "provider": "openai",
  "validated": true,
  "message": "openai API key configured successfully",
  "note": "API key is encrypted and stored securely"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/setup/ki-config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "api_key": "sk-proj-...",
    "validate": true
  }'
```

**Security:**
- API keys are encrypted using Fernet with PBKDF2
- 100,000 iterations for key derivation
- Salt is stored separately
- Master encryption key from `ENCRYPTION_KEY` env var

---

### 7. GET /setup/ki-config
List configured AI providers

**Response:**
```json
{
  "success": true,
  "providers": [
    {
      "provider": "openai",
      "active": true,
      "last_validated": "2025-01-16T12:00:00Z",
      "metadata": {
        "model": "gpt-4"
      }
    },
    {
      "provider": "anthropic",
      "active": true,
      "last_validated": "2025-01-16T11:30:00Z",
      "metadata": {}
    }
  ],
  "stats": {
    "total": 2,
    "active_count": 2,
    "supported_providers": ["openai", "anthropic", "google", "cohere", "huggingface"]
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/setup/ki-config
```

---

### 8. POST /setup/seed
Seed initial data (learning methods, roles, categories)

**Request Body:**
```json
{
  "skip_existing": true
}
```

**Seeds:**
- **21 Learning Methods:**
  - Basic (11): Flashcards, Quiz, Lückentext, Multiple Choice, True/False, Zuordnung, Sortierung, Mindmap, Video, Audio, PDF
  - Premium (6): KI-Tutor, KI-Glossar, Braindump, Zertifikatsprüfung, Lernpfad-KI, Live-Raum
  - Pro (4): Deep Praxis, Deep Scenario, Projekt-Simulation, Echtzeit-Debugging

- **10 User Roles:**
  - user, premium, creator, teacher, school_admin, company_admin, moderator, support, admin, superadmin

- **8 Categories:**
  - Informatik & IT, Mathematik, Naturwissenschaften, Sprachen, Business & Management, Kunst & Design, Gesundheit & Medizin, Sozialwissenschaften

**Response:**
```json
{
  "success": true,
  "learning_methods": 21,
  "roles": 10,
  "categories": 8,
  "message": "Database seeded successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/setup/seed \
  -H "Content-Type: application/json" \
  -d '{"skip_existing": true}'
```

---

### 9. GET /setup/seed/status
Get seeding status

**Response:**
```json
{
  "success": true,
  "learning_methods": 21,
  "roles": 10,
  "categories": 8,
  "expected": {
    "learning_methods": 21,
    "roles": 10,
    "categories": 8
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/setup/seed/status
```

---

### 10. POST /setup/complete
Complete installation and mark as installed

**Request Body:**
```json
{
  "admin_email": "admin@lsx.de"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Installation completed successfully",
  "install_info": {
    "version": "1.0.0",
    "installed_at": "2025-01-16T12:00:00Z",
    "database_version": "1.0.0",
    "admin_email": "admin@lsx.de"
  },
  "next_step": "Login with admin credentials at /login"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/setup/complete \
  -H "Content-Type: application/json" \
  -d '{"admin_email": "admin@lsx.de"}'
```

**Important:** After completion, the `.lsx-installed` marker file is created and setup wizard becomes inaccessible.

---

### 11. GET /setup/verify
Verify installation (12 comprehensive checks)

**Checks:**
1. Database Connection
2. Database Tables (15 required)
3. Database Indexes (26+)
4. Learning Methods (21 seeded)
5. Roles (10 with critical roles)
6. Categories (8+)
7. Admin Account (superadmin exists)
8. Organisation (LSX Academy exists)
9. File Permissions (6 directories)
10. Dependencies (7 critical packages)
11. Environment Variables (3 critical)
12. Installation Marker (.lsx-installed file)

**Response:**
```json
{
  "success": true,
  "checks": [
    {
      "name": "Database Connection",
      "status": "passed",
      "message": "Database connection successful",
      "details": {
        "version": "PostgreSQL 16.0"
      }
    },
    {
      "name": "Database Tables",
      "status": "passed",
      "message": "All 15 required tables exist",
      "details": {
        "table_count": 15,
        "tables": ["users", "roles", "organisations", "..."]
      }
    }
  ],
  "errors": [],
  "warnings": [],
  "timestamp": "2025-01-16T12:00:00Z"
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/setup/verify
```

---

### 12. GET /setup/verify/report
Get formatted verification report (plain text)

**Response:**
```text
======================================================================
LernsystemX Installation Verification Report
======================================================================
Timestamp: 2025-01-16T12:00:00Z
Overall Status: PASSED

Verification Checks:
----------------------------------------------------------------------
✓ Database Connection: passed
  → Database connection successful
✓ Database Tables: passed
  → All 15 required tables exist
✓ Database Indexes: passed
  → 26 indexes found
✓ Seed Data - Learning Methods: passed
  → 21 learning methods seeded successfully
✓ Seed Data - Roles: passed
  → 10 roles configured
✓ Seed Data - Categories: passed
  → 8 categories configured
✓ Admin Account: passed
  → Superadmin account exists: admin@lsx.de
✓ Organisation Setup: passed
  → System organisation exists: LSX Academy
✓ File Permissions: passed
  → All 6 required directories exist and are writable
✓ Python Dependencies: passed
  → All critical dependencies installed
✓ Environment Variables: passed
  → All critical environment variables are set
✓ Installation Marker: passed
  → Installation marker file exists

======================================================================
Summary: 12/12 checks passed
======================================================================
```

**Example:**
```bash
curl -X GET http://localhost:5000/setup/verify/report
```

---

### 13. GET /setup/system-info
Get system information

**Response:**
```json
{
  "success": true,
  "python_version": "3.12.0 (main, Oct  2 2023, 10:00:00)",
  "platform": "Windows-10-10.0.19045-SP0",
  "database_version": "PostgreSQL 16.0 on x86_64-pc-windows-msvc",
  "table_counts": {
    "users": 1,
    "roles": 10,
    "organisations": 1,
    "courses": 0,
    "learning_methods": 21,
    "categories": 8
  },
  "environment": "development"
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/setup/system-info
```

---

### 14. GET /setup/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "LernsystemX Setup Wizard",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/setup/health
```

---

## Phase 23: Advanced System Management

### 15. POST /setup/diagnostics/run
Run comprehensive system diagnostics

**Request Body:**
```json
{
  "quick": false
}
```

**Parameters:**
- `quick` (boolean, optional): If true, runs only core checks (DB, Redis, Security). Default: false

**Response:**
```json
{
  "success": true,
  "overall_status": "warn",
  "checks": [
    {
      "name": "Database Connection",
      "status": "ok",
      "message": "Database connection successful",
      "details": {
        "version": "PostgreSQL 16.0",
        "has_migration_table": true,
        "pool_size": 10
      },
      "auto_fix_available": false,
      "auto_fix_description": null
    },
    {
      "name": "Redis Connection",
      "status": "ok",
      "message": "Redis connection successful",
      "details": {
        "version": "7.0.11",
        "used_memory_human": "1.5M",
        "connected_clients": 3
      },
      "auto_fix_available": false,
      "auto_fix_description": null
    },
    {
      "name": "AI API Keys",
      "status": "warn",
      "message": "Only 1/3 AI providers configured",
      "details": {
        "openai": true,
        "anthropic": false,
        "google": false
      },
      "auto_fix_available": false,
      "auto_fix_description": "Consider configuring backup AI providers"
    },
    {
      "name": "Security Configuration",
      "status": "ok",
      "message": "All security checks passed",
      "details": {
        "secret_key_set": true,
        "jwt_secret_set": true,
        "rate_limiting_enabled": true,
        "rbac_enabled": true,
        "https_only": true,
        "csrf_enabled": true
      },
      "auto_fix_available": false,
      "auto_fix_description": null
    }
  ],
  "timestamp": "2025-01-16T12:00:00Z",
  "summary": {
    "total_checks": 9,
    "passed": 6,
    "warnings": 2,
    "failed": 1
  }
}
```

**Diagnostic Checks (Full Mode):**
1. **Database Connection** - PostgreSQL connectivity and migration table
2. **Redis Connection** - Cache connectivity and status
3. **Security Configuration** - Secret keys, JWT, RBAC, HTTPS, CSRF
4. **AI API Keys** - OpenAI, Anthropic, Google configuration
5. **Email Configuration** - SMTP settings validation
6. **Backup Configuration** - Backup directory and permissions
7. **Monitoring Configuration** - Prometheus and metrics
8. **Storage Configuration** - Upload directory validation
9. **Celery Configuration** - Background task broker

**Quick Mode (core checks only):**
- Database Connection
- Redis Connection
- Security Configuration

**Status Values:**
- `ok` - Check passed
- `warn` - Non-critical issue detected
- `fail` - Critical issue detected

**Example:**
```bash
# Full diagnostics
curl -X POST http://localhost:5000/setup/diagnostics/run \
  -H "Content-Type: application/json" \
  -d '{"quick": false}'

# Quick diagnostics (core checks only)
curl -X POST http://localhost:5000/setup/diagnostics/run \
  -H "Content-Type: application/json" \
  -d '{"quick": true}'
```

**Error Response (403 - After Installation without Admin Auth):**
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "This endpoint requires admin authentication after installation"
}
```

---

### 16. GET /setup/status/full
Get comprehensive system status

**Response:**
```json
{
  "success": true,
  "installed": true,
  "installation_completed_at": "2025-01-16T12:00:00Z",
  "installed_by": "admin@lsx.de",
  "environment": "production",
  "system_version": "1.6.0",
  "api_version": 1,
  "api_versions_supported": [1],
  "db_schema_version": "V003",
  "last_migration": "20250115_003_add_ai_conversation_tracking",
  "last_migration_at": "2025-01-16T11:30:00Z",
  "has_pending_migrations": false,
  "pending_migrations_count": 0,
  "overall_health": "ok",
  "health_summary": {
    "passed": 3,
    "warnings": 0,
    "failed": 0
  },
  "components": {
    "database": "ok",
    "redis": "ok",
    "security": "ok"
  },
  "timestamp": "2025-01-16T12:05:00Z"
}
```

**Fields:**
- `installed` - Installation status flag
- `installation_completed_at` - ISO timestamp of installation completion
- `installed_by` - Email of admin who completed installation
- `environment` - Current environment (development/production)
- `system_version` - LernsystemX version (from versioning system)
- `api_version` - Current API version
- `api_versions_supported` - Array of supported API versions
- `db_schema_version` - Database schema version (from last migration)
- `last_migration` - Name of last applied migration
- `last_migration_at` - ISO timestamp of last migration
- `has_pending_migrations` - Boolean indicating pending migrations
- `pending_migrations_count` - Number of pending migrations
- `overall_health` - System health (ok/warn/fail)
- `health_summary` - Diagnostic check counts
- `components` - Individual component status map

**Example:**
```bash
curl -X GET http://localhost:5000/setup/status/full
```

**Error Response (403 - After Installation without Admin Auth):**
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "This endpoint requires admin authentication after installation"
}
```

---

### 17. GET /setup/status/summary
Get lightweight status summary (for quick checks)

**Response:**
```json
{
  "success": true,
  "installed": true,
  "system_version": "1.6.0",
  "environment": "production",
  "has_pending_migrations": false,
  "timestamp": "2025-01-16T12:05:00Z"
}
```

**Use Case:** Quick polling for system status without heavy diagnostics.

**Example:**
```bash
curl -X GET http://localhost:5000/setup/status/summary
```

---

### 18. GET /setup/migrations
List all database migrations with status

**Response:**
```json
{
  "success": true,
  "migrations": [
    {
      "migration_id": "20250115_001_add_course_versioning",
      "name": "Add Course Versioning",
      "version": "V001",
      "description": "Adds version control for courses and modules",
      "applied": true,
      "applied_at": "2025-01-16T10:00:00Z",
      "execution_time_ms": 234,
      "checksum": "a3f9d2e1b4c7f8a2d5e9b3c6f1a4d7e0",
      "has_rollback": true
    },
    {
      "migration_id": "20250115_002_add_learning_analytics",
      "name": "Add Learning Analytics",
      "version": "V002",
      "description": "Creates tables for learning analytics and progress tracking",
      "applied": true,
      "applied_at": "2025-01-16T10:30:00Z",
      "execution_time_ms": 187,
      "checksum": "b2c8e3d1a6f9e4b7c3d9a5f2e8b1c4d7",
      "has_rollback": true
    },
    {
      "migration_id": "20250115_003_add_ai_conversation_tracking",
      "name": "Add Ai Conversation Tracking",
      "version": "V003",
      "description": "Adds conversation history tracking for AI tutors",
      "applied": true,
      "applied_at": "2025-01-16T11:30:00Z",
      "execution_time_ms": 156,
      "checksum": "c1d7e4a9b2f5c8d3e6a9f1b4d7e2a5c8",
      "has_rollback": true
    },
    {
      "migration_id": "20250115_004_add_notification_preferences",
      "name": "Add Notification Preferences",
      "version": "V004",
      "description": "User notification preferences and channels",
      "applied": false,
      "applied_at": null,
      "execution_time_ms": null,
      "checksum": "d3e8a1c5f9b2d6e4a7c9f3b1d5e8a2c6",
      "has_rollback": true
    }
  ],
  "summary": {
    "total": 4,
    "applied": 3,
    "pending": 1
  }
}
```

**Migration Naming Pattern:**
`{timestamp}_{sequence}_{description}_{direction}.sql`

Example: `20250115_001_add_course_versioning_up.sql`

**Fields:**
- `migration_id` - Unique migration identifier
- `name` - Human-readable migration name
- `version` - Database schema version (V001, V002, etc.)
- `description` - Migration description from SQL header
- `applied` - Boolean indicating if migration has been applied
- `applied_at` - ISO timestamp of application
- `execution_time_ms` - Execution time in milliseconds
- `checksum` - SHA-256 checksum of migration file
- `has_rollback` - Boolean indicating if down migration exists

**Example:**
```bash
curl -X GET http://localhost:5000/setup/migrations
```

**Error Response (403 - After Installation without Admin Auth):**
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "Admin access required for migration management"
}
```

---

### 19. POST /setup/migrations/run
Execute pending or specific database migration

**Request Body (Run All Pending):**
```json
{
  "run_all": true
}
```

**Request Body (Run Specific Migration):**
```json
{
  "migration_id": "20250115_004_add_notification_preferences"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Successfully executed 1 migration(s)",
  "executed": [
    {
      "migration_id": "20250115_004_add_notification_preferences",
      "execution_time_ms": 142
    }
  ]
}
```

**Response (No Pending):**
```json
{
  "success": true,
  "message": "No pending migrations",
  "executed": []
}
```

**Response (Failure):**
```json
{
  "success": false,
  "message": "Migration failed: 20250115_004_add_notification_preferences",
  "error": "ERROR: column 'user_id' already exists",
  "executed": [],
  "failed_migration": "20250115_004_add_notification_preferences"
}
```

**Migration Execution:**
- Migrations are executed in chronological order (by migration_id)
- Execution stops on first failure
- Each migration is tracked in `migration_history` table
- Execution time is recorded for performance monitoring

**Example:**
```bash
# Run all pending migrations
curl -X POST http://localhost:5000/setup/migrations/run \
  -H "Content-Type: application/json" \
  -d '{"run_all": true}'

# Run specific migration
curl -X POST http://localhost:5000/setup/migrations/run \
  -H "Content-Type: application/json" \
  -d '{"migration_id": "20250115_004_add_notification_preferences"}'
```

**Error Response (403 - After Installation without Admin Auth):**
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "Admin access required for migration execution"
}
```

**Error Response (400 - Already Applied):**
```json
{
  "success": false,
  "error": "Migration already applied: 20250115_004_add_notification_preferences",
  "applied_at": "2025-01-16T12:00:00Z"
}
```

---

### 20. POST /setup/auto-fix
Run auto-fix for common system issues

**Request Body:**
```json
{
  "fixes": [
    "missing_directories",
    "pending_migrations",
    "rerun_seeds"
  ]
}
```

**Available Fixes:**
1. **missing_directories** - Create missing upload/backup directories
2. **pending_migrations** - Execute all pending migrations
3. **rerun_seeds** - Re-run seed data (idempotent)

**Response:**
```json
{
  "success": true,
  "fixes_applied": [
    {
      "fix": "missing_directories",
      "success": true,
      "message": "Created missing directories",
      "details": {
        "created": [
          "C:\\Lernsystem\\backend\\uploads",
          "C:\\backups\\lsx"
        ]
      }
    },
    {
      "fix": "pending_migrations",
      "success": true,
      "message": "Successfully executed 2 migration(s)",
      "details": {
        "executed": [
          "20250115_004_add_notification_preferences",
          "20250115_005_add_badge_system"
        ],
        "execution_time_total_ms": 298
      }
    },
    {
      "fix": "rerun_seeds",
      "success": true,
      "message": "Seed data re-run completed",
      "details": {
        "learning_methods": 21,
        "roles": 10,
        "categories": 8
      }
    }
  ]
}
```

**Response (Partial Failure):**
```json
{
  "success": false,
  "fixes_applied": [
    {
      "fix": "missing_directories",
      "success": true,
      "message": "Created missing directories",
      "details": {...}
    },
    {
      "fix": "pending_migrations",
      "success": false,
      "message": "Migration failed",
      "error": "ERROR: syntax error at or near 'CREATE'",
      "details": {
        "failed_migration": "20250115_005_add_badge_system"
      }
    }
  ]
}
```

**Auto-Fix Safety:**
- All fixes are idempotent (safe to run multiple times)
- Directory creation only creates if missing
- Migrations execute in order and stop on first failure
- Seeds use `INSERT ... ON CONFLICT DO NOTHING` pattern

**Example:**
```bash
# Run all fixes
curl -X POST http://localhost:5000/setup/auto-fix \
  -H "Content-Type: application/json" \
  -d '{
    "fixes": ["missing_directories", "pending_migrations", "rerun_seeds"]
  }'

# Run specific fix
curl -X POST http://localhost:5000/setup/auto-fix \
  -H "Content-Type: application/json" \
  -d '{"fixes": ["pending_migrations"]}'
```

**Error Response (403 - After Installation without Admin Auth):**
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "Admin access required for auto-fix operations"
}
```

**Error Response (400 - Invalid Fix):**
```json
{
  "success": false,
  "error": "Invalid fix requested",
  "details": "Unknown fix: invalid_fix_name",
  "available_fixes": ["missing_directories", "pending_migrations", "rerun_seeds"]
}
```

---

## Error Handling

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "success": false,
  "error": "Missing required fields",
  "missing": ["email", "password"]
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Database initialization failed",
  "details": "Connection refused to database"
}
```

**403 Forbidden (if already installed):**
```json
{
  "success": false,
  "error": "System already installed",
  "message": "Admin creation can only run during setup"
}
```

---

## Complete Installation Example

**Full installation flow using curl:**

```bash
# 1. Check status
curl -X GET http://localhost:5000/setup/status

# 2. Run system checks
curl -X POST http://localhost:5000/setup/check

# 3. Initialize database
curl -X POST http://localhost:5000/setup/database

# 4. Create admin user
curl -X POST http://localhost:5000/setup/admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@lsx.de",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "last_name": "User",
    "enable_2fa": true
  }'

# 5. Create LSX Academy organisation
curl -X POST http://localhost:5000/setup/organisation \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LSX Academy",
    "type": "system",
    "domain": "lsx.de"
  }'

# 6. Configure OpenAI API
curl -X POST http://localhost:5000/setup/ki-config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "api_key": "sk-proj-...",
    "validate": true
  }'

# 7. Seed initial data
curl -X POST http://localhost:5000/setup/seed \
  -H "Content-Type: application/json" \
  -d '{"skip_existing": true}'

# 8. Verify installation
curl -X GET http://localhost:5000/setup/verify

# 9. Complete setup
curl -X POST http://localhost:5000/setup/complete \
  -H "Content-Type: application/json" \
  -d '{"admin_email": "admin@lsx.de"}'
```

---

## Security Notes

1. **Password Policy:** 12+ chars, uppercase, lowercase, digit, special char
2. **API Keys:** Encrypted with Fernet + PBKDF2 (100k iterations)
3. **2FA:** Optional TOTP with QR code generation
4. **Recovery Codes:** 10 codes, bcrypt hashed
5. **Audit Logging:** All admin actions logged
6. **Installation Lock:** Setup wizard disabled after completion

---

## ISO Compliance

- **ISO/IEC/IEEE 26515:2018:** API documentation standards
- **ISO 27001:2013:** Information security (encryption, audit logs)
- **ISO 9001:2015:** Quality management (validation, verification)

---

**LernsystemX Setup Wizard v1.0.0**
**© 2025 LSX Academy**
