# Database Migration Strategy - LernsystemX

**Version:** 1.0
**Status:** ✅ Implemented
**Based on:** Dok 33 (Versioning-Change-Management.md) - Phase 22

---

## 1. Overview

This document defines the database migration strategy for LernsystemX, ensuring controlled, versioned, and reversible database schema changes.

### 1.1 Key Principles

| Principle | Implementation |
|-----------|----------------|
| **Version Control** | All migrations are versioned and tracked in migration history |
| **Rollback Capability** | Every migration has a corresponding rollback script |
| **Change Request Integration** | Migrations are tied to Change Requests (CRs) |
| **Zero Downtime** | Migrations support online/offline strategies |
| **Testing Required** | All migrations tested on staging before production |

---

## 2. Migration Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer                                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Create Change Request (CR)                               │
│     - Impact Level: L4/L5 (DB schema changes)                │
│     - Target Version: e.g., 1.6.0                            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Write Migration Scripts                                  │
│     - migrations/{timestamp}_{name}_up.sql                   │
│     - migrations/{timestamp}_{name}_down.sql                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Test on Development DB                                   │
│     - Run migration                                          │
│     - Verify schema                                          │
│     - Test rollback                                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  4. CR Approval (Admin + Security for L4/L5)                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Test on Staging DB                                       │
│     - Full backup                                            │
│     - Run migration                                          │
│     - Integration tests                                      │
│     - Performance tests                                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Production Deployment                                    │
│     - Maintenance window (if needed)                         │
│     - Full backup                                            │
│     - Run migration                                          │
│     - Verify success                                         │
│     - Update migration_history table                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Monitoring & Validation                                  │
│     - Check application logs                                 │
│     - Monitor performance                                    │
│     - Rollback if critical issues                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Migration File Structure

### 3.1 Directory Layout

```
backend/
├── migrations/
│   ├── 20250115_001_add_course_version_up.sql
│   ├── 20250115_001_add_course_version_down.sql
│   ├── 20250120_002_add_api_deprecation_registry_up.sql
│   ├── 20250120_002_add_api_deprecation_registry_down.sql
│   └── README.md
└── docs/
    └── architecture/
        └── database-migration-strategy.md
```

### 3.2 Migration Naming Convention

```
{timestamp}_{sequence}_{description}_{direction}.sql

Examples:
- 20250115_001_add_course_version_up.sql
- 20250115_001_add_course_version_down.sql
- 20250120_002_add_api_deprecation_registry_up.sql
```

| Component | Format | Description |
|-----------|--------|-------------|
| **timestamp** | YYYYMMDD | Date of migration creation |
| **sequence** | 001-999 | Daily sequence number |
| **description** | snake_case | Brief description (max 50 chars) |
| **direction** | up/down | Migration or rollback |

---

## 4. Migration Script Template

### 4.1 Up Migration Template

```sql
-- Migration: {description}
-- Version: {target_version}
-- CR: {cr_number}
-- Author: {author_name}
-- Date: {creation_date}

-- Description:
-- {detailed_description}

-- Dependencies:
-- {list_of_dependencies}

BEGIN;

-- ==========================================
-- Schema Changes
-- ==========================================

-- Example: Add column
ALTER TABLE courses
ADD COLUMN version VARCHAR(10) DEFAULT '1.0';

-- Example: Create table
CREATE TABLE IF NOT EXISTS api_deprecation_registry (
    deprecation_id SERIAL PRIMARY KEY,
    api_version INT NOT NULL,
    endpoint_path VARCHAR(255) NOT NULL,
    deprecation_date TIMESTAMP NOT NULL,
    sunset_date TIMESTAMP NOT NULL,
    replacement_endpoint VARCHAR(255),
    migration_guide_url TEXT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(api_version, endpoint_path)
);

-- Example: Create index
CREATE INDEX idx_courses_version ON courses(version);

-- ==========================================
-- Data Migration (if needed)
-- ==========================================

-- Example: Update existing data
UPDATE courses
SET version = '1.0'
WHERE version IS NULL;

-- ==========================================
-- Constraints
-- ==========================================

-- Example: Add constraint
ALTER TABLE courses
ADD CONSTRAINT chk_version_format
CHECK (version ~ '^\d+\.\d+$');

COMMIT;
```

### 4.2 Down Migration Template

```sql
-- Rollback: {description}
-- Version: {target_version}
-- CR: {cr_number}

BEGIN;

-- ==========================================
-- Reverse Schema Changes (in reverse order!)
-- ==========================================

-- Remove constraint
ALTER TABLE courses
DROP CONSTRAINT IF EXISTS chk_version_format;

-- Drop index
DROP INDEX IF EXISTS idx_courses_version;

-- Drop table
DROP TABLE IF EXISTS api_deprecation_registry;

-- Remove column
ALTER TABLE courses
DROP COLUMN IF EXISTS version;

COMMIT;
```

---

## 5. Migration History Table

### 5.1 Schema

```sql
CREATE TABLE IF NOT EXISTS migration_history (
    migration_id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(20) NOT NULL,
    change_request_id INTEGER REFERENCES change_requests(cr_id),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rollback_available BOOLEAN DEFAULT TRUE,
    rollback_sql TEXT,
    execution_time_ms INTEGER,
    executed_by INTEGER REFERENCES users(user_id),
    environment VARCHAR(50) DEFAULT 'production',  -- development, staging, production
    status VARCHAR(20) DEFAULT 'success',  -- success, failed, rolled_back
    error_message TEXT,
    CONSTRAINT chk_migration_status CHECK (status IN ('success', 'failed', 'rolled_back'))
);

CREATE INDEX idx_migration_version ON migration_history(version);
CREATE INDEX idx_migration_executed_at ON migration_history(executed_at);
CREATE INDEX idx_migration_status ON migration_history(status);
```

### 5.2 Sample Data

```sql
INSERT INTO migration_history (
    migration_name,
    version,
    change_request_id,
    rollback_sql,
    execution_time_ms,
    executed_by,
    environment
) VALUES (
    '20250115_001_add_course_version',
    '1.6.0',
    42,
    'ALTER TABLE courses DROP COLUMN IF EXISTS version;',
    152,
    1,
    'production'
);
```

---

## 6. Migration Execution

### 6.1 Manual Execution (Development)

```bash
# Connect to database
psql -U lernsystemx -d lernsystemx_dev

# Run migration
\i migrations/20250115_001_add_course_version_up.sql

# Verify
SELECT * FROM migration_history ORDER BY executed_at DESC LIMIT 1;

# Test rollback
\i migrations/20250115_001_add_course_version_down.sql
```

### 6.2 Automated Execution (Production)

```bash
# Using Python script (future implementation)
python scripts/run_migration.py --migration 20250115_001_add_course_version --environment production

# Output:
# [2025-01-15 10:30:00] Starting migration: 20250115_001_add_course_version
# [2025-01-15 10:30:00] Creating backup: backup_20250115_103000.sql
# [2025-01-15 10:30:02] Backup completed
# [2025-01-15 10:30:02] Executing migration...
# [2025-01-15 10:30:02] Migration successful (152ms)
# [2025-01-15 10:30:02] Recording in migration_history
# [2025-01-15 10:30:02] Done
```

---

## 7. Rollback Strategy

### 7.1 Rollback Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Detect Issue                                             │
│     - Application errors                                     │
│     - Performance degradation                                │
│     - Data integrity issues                                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Decision: Rollback or Hotfix?                            │
│     - Critical issue → Immediate rollback                    │
│     - Minor issue → Hotfix migration                         │
└────────────────────────────┬────────────────────────────────┘
                             │ (Rollback path)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Stop Application (if needed)                             │
│     - Prevent data corruption                                │
│     - Maintenance mode                                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Execute Rollback Script                                  │
│     - Run {migration}_down.sql                               │
│     - Verify schema restored                                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Update Migration History                                 │
│     - Mark as 'rolled_back'                                  │
│     - Delete record or update status                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Restart Application                                      │
│     - Verify functionality                                   │
│     - Monitor logs                                           │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Rollback Command

```bash
# Rollback last migration
python scripts/rollback_migration.py --last

# Rollback specific migration
python scripts/rollback_migration.py --migration 20250115_001_add_course_version

# Rollback to version
python scripts/rollback_migration.py --to-version 1.5.0
```

---

## 8. Version Correlation

### 8.1 System Version ↔ DB Schema Version

| System Version | DB Schema Version | Migration | Description |
|----------------|-------------------|-----------|-------------|
| 1.0.0 | 1.0 | Initial schema | Base schema from setup wizard |
| 1.5.0 | 1.5 | 20250110_001 | Added subscriptions, billing |
| 1.6.0 | 1.6 | 20250115_001 | Added course versioning |
| 2.0.0 | 2.0 | 20250301_001 | API v2 schema changes |

### 8.2 Compatibility Matrix

| API Version | DB Schema Version | Compatible System Versions |
|-------------|-------------------|----------------------------|
| v1 | 1.0 - 1.9 | 1.0.0 - 1.9.x |
| v2 | 2.0+ | 2.0.0+ |

---

## 9. Zero-Downtime Migrations

### 9.1 Online Migration Strategies

For large tables or high-traffic systems, use these patterns:

#### Pattern 1: Additive Changes Only

```sql
-- Safe: Add nullable column
ALTER TABLE courses
ADD COLUMN version VARCHAR(10);

-- Safe: Add index concurrently (PostgreSQL)
CREATE INDEX CONCURRENTLY idx_courses_version ON courses(version);
```

#### Pattern 2: Multi-Phase Migration

**Phase 1: Add new column (nullable)**
```sql
ALTER TABLE users
ADD COLUMN email_verified BOOLEAN;
```

**Phase 2: Populate data (background job)**
```python
# Run as Celery task
for user in User.query.all():
    user.email_verified = check_email_verified(user.email)
    db.session.commit()
```

**Phase 3: Make NOT NULL (next version)**
```sql
ALTER TABLE users
ALTER COLUMN email_verified SET NOT NULL;
```

#### Pattern 3: Shadow Table Approach

```sql
-- Create new table with desired schema
CREATE TABLE courses_v2 AS SELECT * FROM courses;
ALTER TABLE courses_v2 ADD COLUMN version VARCHAR(10);

-- Populate version column
UPDATE courses_v2 SET version = '1.0';

-- Rename tables atomically
BEGIN;
ALTER TABLE courses RENAME TO courses_old;
ALTER TABLE courses_v2 RENAME TO courses;
COMMIT;

-- Drop old table after verification
DROP TABLE courses_old;
```

---

## 10. Best Practices

### 10.1 DO's

✅ **Always write rollback scripts** before executing migration
✅ **Test on staging** with production-like data volume
✅ **Use transactions** (BEGIN/COMMIT) for atomicity
✅ **Create backups** before production migrations
✅ **Use idempotent operations** (IF NOT EXISTS, IF EXISTS)
✅ **Add comments** explaining the why, not just the what
✅ **Version control** all migration scripts in Git
✅ **Monitor performance** impact of migrations
✅ **Use indexes concurrently** for large tables (PostgreSQL)
✅ **Document breaking changes** in CHANGELOG.md

### 10.2 DON'Ts

❌ **Don't modify existing migrations** once deployed to production
❌ **Don't delete data** without explicit CR approval
❌ **Don't run migrations manually** in production without approval
❌ **Don't skip testing rollbacks**
❌ **Don't create migrations during change freeze** periods
❌ **Don't use DROP COLUMN** on large tables without offline window
❌ **Don't alter column types** without testing data compatibility
❌ **Don't assume default values** will work for existing data

---

## 11. Change Impact Levels

| Level | Migration Type | Approval | Downtime | Example |
|-------|----------------|----------|----------|---------|
| **L1** | N/A | N/A | N/A | Documentation only |
| **L2** | Data only | Team Lead | No | Add rows to lookup table |
| **L3** | Additive schema | Product Manager | No | Add nullable column, create index |
| **L4** | Breaking changes | Admin | Maybe | Alter column type, add NOT NULL |
| **L5** | Critical schema | Admin + Security | Yes | Drop table, restructure schema |

---

## 12. Migration Checklist

```markdown
## Pre-Migration Checklist

□ CR created and approved
□ Migration scripts written (up + down)
□ Rollback script tested on dev DB
□ Migration tested on dev DB
□ Impact assessment documented
□ Downtime requirement identified
□ Backup strategy defined
□ Staging deployment tested
□ Performance impact measured
□ Monitoring alerts configured

## Post-Migration Checklist

□ Migration executed successfully
□ Migration history updated
□ Application logs reviewed
□ Performance metrics normal
□ Rollback tested (if safe)
□ Documentation updated
□ Team notified
□ CHANGELOG.md updated
```

---

## 13. Future Enhancements

**Phase 23+ (Planned):**
- Automated migration runner with Python
- Migration dry-run mode
- Database schema versioning table
- Integration with CI/CD pipeline
- Automated rollback on failure
- Migration performance profiling
- Schema diff tool
- Migration dependency management

---

## 14. References

- **Dok 33:** Versioning-Change-Management.md
- **PostgreSQL Docs:** ALTER TABLE, CREATE INDEX CONCURRENTLY
- **ISO/IEC/IEEE 42010:2011** - Architecture Description
- **CHANGELOG.md** - System version history
- **migrations/** - Migration scripts directory

---

**Document Version:** 1.0
**Last Updated:** 2025
**Status:** ✅ Production Ready
