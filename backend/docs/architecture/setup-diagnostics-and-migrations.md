# Setup Wizard: Diagnostics & Migration Management

**Version:** 1.0.0
**Phase:** Phase 23 - Setup Wizard Erweiterungen
**Standard:** ISO/IEC/IEEE 26515:2018

---

## 1. Overview

This document describes the diagnostics and migration management extensions to the LernsystemX Setup Wizard (Phase 23), providing:

- **System Diagnostics**: Health checks across all system components
- **System Status**: Consolidated installation, runtime, and version information
- **Migration Management**: Database migration execution and tracking
- **Auto-Fix Capabilities**: Automated fixes for common system issues

These features extend the initial setup wizard with post-installation management capabilities.

---

## 2. Architecture Components

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Setup Routes                              │
│                  (/setup/*)                                  │
└────────┬────────────────────────────────────────────┬───────┘
         │                                             │
         ▼                                             ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Diagnostics    │  │  System Status   │  │    Migration     │
│     Module       │  │     Module       │  │     Manager      │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌──────────────────────────────────────────────────────────────┐
│              System Components & Resources                    │
├─────────────┬──────────────┬──────────────┬─────────────────┤
│  PostgreSQL │    Redis     │  AI Providers │  File System   │
└─────────────┴──────────────┴──────────────┴─────────────────┘
```

### 2.2 Module Structure

```
backend/
├── setup/
│   ├── diagnostics.py          # Health checks and diagnostics
│   ├── status.py                # System status aggregation
│   ├── migrations.py            # Migration management
│   ├── routes.py                # API endpoints (extended)
│   ├── install_check.py         # Installation verification
│   └── system_check.py          # Pre-installation checks
├── migrations/                   # SQL migration files
│   ├── {timestamp}_{seq}_{desc}_up.sql
│   └── {timestamp}_{seq}_{desc}_down.sql
└── docs/
    ├── api/
    │   └── setup-wizard-api.md  # API documentation
    └── architecture/
        └── setup-diagnostics-and-migrations.md  # This document
```

---

## 3. System Diagnostics

### 3.1 Purpose

System diagnostics provide comprehensive health checks across all system components, enabling:

- **Proactive Monitoring**: Detect issues before they cause failures
- **Configuration Validation**: Verify all components are properly configured
- **Auto-Fix Identification**: Suggest automated fixes where available
- **Health Reporting**: Provide actionable health status (OK/WARN/FAIL)

### 3.2 Diagnostic Checks

#### Core Checks (Quick Mode)
Always executed, even in quick mode:

1. **Database Connection**
   - PostgreSQL connectivity test
   - Version detection
   - Migration history table check
   - Connection pool status

2. **Redis Connection**
   - Cache connectivity test
   - Redis version and memory usage
   - Connected clients count

3. **Security Configuration**
   - SECRET_KEY length (≥32 chars)
   - JWT_SECRET_KEY configuration
   - Rate limiting enabled
   - RBAC enabled
   - HTTPS-only cookies
   - CSRF protection

#### Extended Checks (Full Mode)
Additional checks in full diagnostic mode:

4. **AI API Keys**
   - OpenAI key configured
   - Anthropic key configured
   - Google key configured
   - Warns if <2 providers configured

5. **Email Configuration**
   - SMTP server settings
   - Authentication credentials
   - Default sender address

6. **Backup Configuration**
   - Backup directory exists
   - Directory is writable
   - Backup schedule configured

7. **Monitoring Configuration**
   - Monitoring enabled flag
   - Metrics endpoint configured
   - Prometheus integration

8. **Storage Configuration**
   - Upload directory exists
   - Upload directory writable
   - Adequate disk space

9. **Celery Configuration**
   - Broker URL configured
   - Result backend configured
   - Broker accessibility test

### 3.3 Diagnostic Result Structure

```python
@dataclass
class DiagnosticCheckResult:
    name: str                           # Human-readable check name
    status: Literal["ok", "warn", "fail"]  # Check status
    message: str                        # Status message
    details: Optional[Dict[str, Any]]   # Additional details
    auto_fix_available: bool            # Can be auto-fixed
    auto_fix_description: Optional[str] # How to fix
```

**Status Levels:**
- `ok`: Check passed, no issues
- `warn`: Non-critical issue, system operational
- `fail`: Critical issue, system may malfunction

### 3.4 Implementation

**Location:** `backend/setup/diagnostics.py`

**Key Classes:**
- `DiagnosticCheckResult`: Single check result
- `DiagnosticsReport`: Aggregated report with statistics
- `SystemDiagnostics`: Diagnostic runner with individual check methods

**Usage Example:**
```python
from setup.diagnostics import SystemDiagnostics

# Run full diagnostics
report = SystemDiagnostics.run_all_diagnostics(quick=False)

# Run quick diagnostics (core checks only)
quick_report = SystemDiagnostics.run_all_diagnostics(quick=True)

# Convert to JSON
report_dict = SystemDiagnostics.get_report_dict(report)
```

**API Endpoint:**
```
POST /setup/diagnostics/run
Body: {"quick": false}
```

---

## 4. System Status

### 4.1 Purpose

System status provides a consolidated view of:

- **Installation State**: Is system installed, when, by whom
- **Version Information**: System version, API version, environment
- **Database Schema**: Current schema version from migrations
- **Migration State**: Pending migrations count
- **Health Summary**: Quick health indicators
- **Component Status**: Individual component health (DB, Redis, Security)

### 4.2 Status Components

#### Installation Status
From `InstallationChecker`:
- `installed`: Boolean installation flag
- `installation_completed_at`: ISO timestamp
- `installed_by`: Admin email who completed setup
- `install_version`: Version at installation time

#### Version Information
From Phase 22 versioning system:
- `system_version`: LernsystemX semantic version
- `environment`: development/staging/production
- `api_version_current`: Current API version
- `api_versions_supported`: Array of supported API versions

#### Database Schema Version
From `migration_history` table:
- `db_schema_version`: Version from last migration (V001, V002, etc.)
- `last_migration`: Migration ID of last applied migration
- `last_migration_at`: ISO timestamp of last migration

#### Migration State
From `MigrationManager`:
- `has_pending_migrations`: Boolean pending flag
- `pending_migrations_count`: Number of unapplied migrations

#### Health Summary
From quick diagnostics:
- `overall_health`: ok/warn/fail
- `health_summary`: {passed, warnings, failed} counts

#### Component Status
Individual component health map:
- `database`: ok/warn/fail
- `redis`: ok/warn/fail
- `security`: ok/warn/fail

### 4.3 Implementation

**Location:** `backend/setup/status.py`

**Key Class:**
- `SystemStatus`: Static methods for status retrieval

**Methods:**
- `get_installation_status()`: Installation info
- `get_version_information()`: Version info
- `get_database_schema_version()`: DB schema version
- `get_migration_status()`: Migration state
- `get_health_status()`: Health summary
- `get_component_status()`: Component health map
- `get_system_status()`: **Comprehensive status** (combines all above)
- `get_status_summary()`: **Lightweight summary** (quick polling)

**Usage Example:**
```python
from setup.status import SystemStatus

# Get comprehensive status
status = SystemStatus.get_system_status()

# Get lightweight summary (for polling)
summary = SystemStatus.get_status_summary()
```

**API Endpoints:**
```
GET /setup/status/full     # Comprehensive status
GET /setup/status/summary  # Lightweight summary
```

### 4.4 Status Endpoint Strategy

**Full Status (`/setup/status/full`):**
- Use for admin dashboards
- Use when detailed information needed
- Runs quick diagnostics (3 core checks)
- Queries multiple subsystems

**Summary Status (`/setup/status/summary`):**
- Use for health check polling
- Use for quick status indicators
- Minimal database queries
- Fast response time

---

## 5. Migration Management

### 5.1 Purpose

Migration management provides:

- **Migration Discovery**: Automatic detection of migration files
- **Migration Tracking**: History of applied migrations
- **Migration Execution**: Controlled migration application
- **Checksum Validation**: Detect modified migration files
- **Rollback Support**: Down migrations for reversibility

Based on Phase 22 database migration strategy.

### 5.2 Migration File Structure

**Naming Pattern:**
```
{timestamp}_{sequence}_{description}_{direction}.sql
```

**Example:**
```
20250115_001_add_course_versioning_up.sql
20250115_001_add_course_versioning_down.sql
```

**Components:**
- `timestamp`: YYYYMMDD format (20250115)
- `sequence`: 3-digit sequence (001, 002, 003)
- `description`: Snake_case description (add_course_versioning)
- `direction`: up (apply) or down (rollback)

**SQL File Header:**
```sql
-- Version: V001
-- Description: Adds version control for courses and modules
-- Author: LernsystemX Team
-- Date: 2025-01-15

-- Migration code follows...
CREATE TABLE IF NOT EXISTS course_versions (
    version_id SERIAL PRIMARY KEY,
    ...
);
```

### 5.3 Migration Discovery

**Process:**
1. Scan `backend/migrations/` directory
2. Find all `*_up.sql` files
3. Parse filename components (timestamp, sequence, description)
4. Locate corresponding `*_down.sql` file
5. Extract version and description from SQL header
6. Calculate SHA-256 checksum
7. Return list of discovered migrations

**Implementation:**
```python
from setup.migrations import MigrationManager

# Discover all migration files
migrations = MigrationManager.discover_migrations()

# Returns List[Migration]
# Each Migration has: migration_id, name, version, description,
#                     up_sql_path, down_sql_path, checksum
```

### 5.4 Migration Tracking

**Migration History Table:**
```sql
CREATE TABLE migration_history (
    migration_id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(20) NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    executed_by INTEGER,
    environment VARCHAR(50) DEFAULT 'production',
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    CONSTRAINT chk_migration_status CHECK (status IN ('success', 'failed', 'rolled_back'))
);
```

**Tracked Information:**
- Migration name (unique identifier)
- Version (V001, V002, etc.)
- Execution timestamp
- Execution time in milliseconds
- User who executed migration
- Environment (development/production)
- Status (success/failed/rolled_back)
- Error message (if failed)

### 5.5 Migration Execution

**Process:**
1. Verify migration exists and not already applied
2. Read migration SQL file
3. Execute SQL in database transaction
4. Record execution time
5. Insert record into `migration_history`
6. Commit transaction
7. Return execution result

**Run All Pending:**
```python
from setup.migrations import MigrationManager

# Run all pending migrations in order
result = MigrationManager.run_pending_migrations(user_id=1)

# Returns:
# {
#   "success": True/False,
#   "message": "...",
#   "executed": [{"migration_id": "...", "execution_time_ms": 123}, ...],
#   "failed_migration": "..." (if failed)
# }
```

**Run Specific Migration:**
```python
result = MigrationManager.run_migration(
    migration_id="20250115_001_add_course_versioning",
    user_id=1
)
```

**Execution Guarantees:**
- Migrations execute in chronological order (by migration_id)
- Execution stops on first failure
- Each migration runs in its own transaction
- No partial migrations (all-or-nothing per migration)

### 5.6 Checksum Validation

**Purpose:**
- Detect modified migration files
- Prevent silent schema drift
- Ensure reproducible migrations

**Process:**
1. Calculate SHA-256 of migration file at discovery
2. Store checksum with migration metadata
3. Compare checksums before execution (future feature)

**Implementation:**
```python
checksum = MigrationManager.calculate_file_checksum(filepath)
# Returns: "a3f9d2e1b4c7f8a2d5e9b3c6f1a4d7e0"
```

### 5.7 Migration List API

**Endpoint:** `GET /setup/migrations`

**Response Structure:**
```json
{
  "success": true,
  "migrations": [
    {
      "migration_id": "20250115_001_add_course_versioning",
      "name": "Add Course Versioning",
      "version": "V001",
      "description": "Adds version control for courses",
      "applied": true,
      "applied_at": "2025-01-16T10:00:00Z",
      "execution_time_ms": 234,
      "checksum": "a3f9d2e1b4c7f8a2...",
      "has_rollback": true
    },
    ...
  ],
  "summary": {
    "total": 4,
    "applied": 3,
    "pending": 1
  }
}
```

### 5.8 Migration Execution API

**Endpoint:** `POST /setup/migrations/run`

**Run All Pending:**
```json
{
  "run_all": true
}
```

**Run Specific Migration:**
```json
{
  "migration_id": "20250115_004_add_notification_preferences"
}
```

---

## 6. Auto-Fix Capabilities

### 6.1 Purpose

Auto-fix provides automated resolution for common system issues:

- **Missing Directories**: Create required directories
- **Pending Migrations**: Execute all pending migrations
- **Missing Seed Data**: Re-run seed data (idempotent)

### 6.2 Available Fixes

#### 1. Missing Directories

**Fix:** `missing_directories`

**What it does:**
- Checks for upload directory
- Checks for backup directory
- Creates missing directories with appropriate permissions

**Implementation:**
```python
upload_folder = current_app.config.get('UPLOAD_FOLDER')
backup_path = current_app.config.get('BACKUP_PATH')

if not os.path.exists(upload_folder):
    os.makedirs(upload_folder, exist_ok=True)

if not os.path.exists(backup_path):
    os.makedirs(backup_path, exist_ok=True)
```

**Idempotent:** Yes (safe to run multiple times)

#### 2. Pending Migrations

**Fix:** `pending_migrations`

**What it does:**
- Discovers all pending migrations
- Executes migrations in chronological order
- Stops on first failure

**Implementation:**
```python
from setup.migrations import MigrationManager

result = MigrationManager.run_pending_migrations(user_id=None)
```

**Idempotent:** Yes (already applied migrations are skipped)

#### 3. Re-run Seeds

**Fix:** `rerun_seeds`

**What it does:**
- Re-runs all seed data operations
- Uses `INSERT ... ON CONFLICT DO NOTHING` pattern
- Seeds learning methods, roles, categories

**Implementation:**
```python
from setup.seed_data import SeedData

SeedData.seed_all()
```

**Idempotent:** Yes (uses ON CONFLICT DO NOTHING)

### 6.3 Auto-Fix API

**Endpoint:** `POST /setup/auto-fix`

**Request:**
```json
{
  "fixes": [
    "missing_directories",
    "pending_migrations",
    "rerun_seeds"
  ]
}
```

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

### 6.4 Safety Considerations

**All auto-fixes are designed to be:**
- **Idempotent**: Safe to run multiple times
- **Non-destructive**: Never delete or modify existing data
- **Transactional**: Database operations are atomic
- **Logged**: All operations recorded in audit logs

**NOT Auto-Fixable:**
- Complex configuration issues
- Security misconfigurations (require manual review)
- Failed migrations with schema conflicts
- Missing API keys (require user input)

---

## 7. Security & Access Control

### 7.1 Pre-Installation Access

**Before `.lsx-installed` file exists:**
- All setup endpoints are publicly accessible
- No authentication required
- Rate limiting applies

**Rationale:** Setup wizard must be accessible for initial installation.

### 7.2 Post-Installation Access

**After `.lsx-installed` file exists:**

**Publicly Accessible:**
- `GET /setup/health` - Health check endpoint

**Admin-Only Endpoints:**
- `POST /setup/diagnostics/run` - Requires admin/superadmin role
- `GET /setup/status/full` - Requires admin/superadmin role
- `GET /setup/status/summary` - Requires admin/superadmin role
- `GET /setup/migrations` - Requires admin/superadmin role
- `POST /setup/migrations/run` - Requires admin/superadmin role
- `POST /setup/auto-fix` - Requires admin/superadmin role

**Authentication:**
- JWT token in Authorization header
- RBAC check for admin or superadmin role
- Rate limiting per user

**Error Response (403):**
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "This endpoint requires admin authentication after installation"
}
```

### 7.3 Audit Logging

**All Phase 23 operations are logged:**
- Diagnostic runs (user, timestamp, results)
- Migration executions (user, migration, result, time)
- Auto-fix operations (user, fixes applied, results)

**Log Location:** `audit_logs` table

**Log Fields:**
- `user_id`: User who performed action
- `action`: Action name (e.g., "run_diagnostics", "run_migration")
- `resource_type`: Resource type (e.g., "migration", "diagnostics")
- `resource_id`: Resource identifier (e.g., migration_id)
- `changes`: JSON with action details
- `ip_address`: Request IP address
- `timestamp`: ISO timestamp

---

## 8. Integration with Existing Systems

### 8.1 Phase 22 Versioning Integration

**System Version:**
```python
from app.gateway.versioning import get_version_info

version_info = get_version_info()
system_version = version_info['system_version']  # e.g., "1.6.0"
```

**API Version:**
```python
api_version = version_info['api']['current_version']  # e.g., 1
supported_versions = version_info['api']['supported_versions']  # [1]
```

**Environment:**
```python
environment = version_info['environment']  # development/production
```

### 8.2 Phase 20 Security Integration

**RBAC Checks:**
```python
from app.gateway.security import require_role

@require_role(['admin', 'superadmin'])
def run_diagnostics():
    # Only admins can access
    pass
```

**Rate Limiting:**
```python
from app.gateway.rate_limit import rate_limit

@rate_limit(calls=10, period=60)  # 10 calls per minute
def run_diagnostics():
    pass
```

### 8.3 Phase 19 Monitoring Integration

**Metrics Collection:**
```python
from app.monitoring import metrics

# Track diagnostic runs
metrics.diagnostic_runs.inc()

# Track migration execution time
metrics.migration_execution_time.observe(execution_time_ms)
```

**Health Check Integration:**
```python
from setup.diagnostics import SystemDiagnostics

# Used by monitoring health endpoint
report = SystemDiagnostics.run_all_diagnostics(quick=True)
overall_health = report.overall_status
```

### 8.4 Phase 18 Backup Integration

**Backup Diagnostics:**
- Check if backup directory exists
- Check if backup directory is writable
- Suggest auto-fix if directory missing

---

## 9. Database Schema

### 9.1 Migration History Table

**Created by:** First migration execution

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS migration_history (
    migration_id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(20) NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    executed_by INTEGER,
    environment VARCHAR(50) DEFAULT 'production',
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    CONSTRAINT chk_migration_status CHECK (status IN ('success', 'failed', 'rolled_back'))
);

CREATE INDEX IF NOT EXISTS idx_migration_version ON migration_history(version);
CREATE INDEX IF NOT EXISTS idx_migration_executed_at ON migration_history(executed_at);
CREATE INDEX IF NOT EXISTS idx_migration_status ON migration_history(status);
```

**Purpose:**
- Track all applied migrations
- Record execution metadata
- Enable migration status queries
- Support rollback tracking (future)

---

## 10. Error Handling

### 10.1 Diagnostic Errors

**Scenario:** Component check fails

**Handling:**
- Catch exception in individual check method
- Return `DiagnosticCheckResult` with status="fail"
- Include error details in `details` field
- Continue with remaining checks (don't abort)

**Example:**
```python
try:
    redis_client.ping()
    return DiagnosticCheckResult(status="ok", ...)
except Exception as e:
    return DiagnosticCheckResult(
        status="fail",
        message=f"Redis connection failed: {str(e)}",
        details={"error": str(e)}
    )
```

### 10.2 Migration Errors

**Scenario:** Migration execution fails

**Handling:**
- Transaction rolls back automatically
- No record inserted into `migration_history`
- Error returned to caller with details
- Subsequent migrations NOT executed

**Response:**
```json
{
  "success": false,
  "message": "Migration failed: 20250115_004_add_notification_preferences",
  "error": "ERROR: column 'user_id' already exists",
  "executed": [],
  "failed_migration": "20250115_004_add_notification_preferences"
}
```

### 10.3 Auto-Fix Errors

**Scenario:** One auto-fix fails

**Handling:**
- Continue with remaining fixes (don't abort)
- Mark overall success=false
- Include error details for failed fix
- Return success=true for completed fixes

**Response:**
```json
{
  "success": false,
  "fixes_applied": [
    {
      "fix": "missing_directories",
      "success": true,
      "message": "Created missing directories"
    },
    {
      "fix": "pending_migrations",
      "success": false,
      "message": "Migration failed",
      "error": "ERROR: syntax error"
    }
  ]
}
```

---

## 11. Performance Considerations

### 11.1 Quick vs Full Diagnostics

**Quick Mode (3 checks):**
- Database connection (~10ms)
- Redis connection (~5ms)
- Security config (~1ms)
- **Total:** ~16ms

**Full Mode (9 checks):**
- Core checks: ~16ms
- AI keys check: ~1ms
- Email config check: ~1ms
- Backup config check: ~2ms (file system)
- Monitoring config check: ~1ms
- Storage config check: ~2ms (file system)
- Celery config check: ~5ms (Redis ping)
- **Total:** ~28ms

**Recommendation:**
- Use quick mode for polling/health checks
- Use full mode for admin dashboards

### 11.2 Status Endpoints

**Full Status (`/setup/status/full`):**
- Runs quick diagnostics: ~16ms
- Queries installation check: ~5ms
- Queries version info: ~1ms
- Queries migration status: ~10ms
- **Total:** ~32ms

**Summary Status (`/setup/status/summary`):**
- Queries installation check: ~5ms
- Queries version info: ~1ms
- Queries migration count: ~3ms
- **Total:** ~9ms

**Recommendation:**
- Use summary for status polling (every 30-60s)
- Use full for dashboard refresh (every 5-10min)

### 11.3 Migration Discovery

**Process:**
- Scan filesystem for `*_up.sql` files
- Read first 10 lines of each file (version/description)
- Calculate SHA-256 checksum
- Query `migration_history` for applied status

**Performance:**
- ~2ms per migration file
- For 10 migrations: ~20ms
- For 50 migrations: ~100ms

**Caching:**
- Migration list can be cached for 1-5 minutes
- Invalidate cache on migration execution

---

## 12. Testing Strategy

### 12.1 Unit Tests

**Diagnostic Tests:**
```python
def test_database_connection_check_success():
    result = SystemDiagnostics.check_database_connection()
    assert result.status == "ok"
    assert "version" in result.details

def test_database_connection_check_failure():
    # Mock db_pool to return None
    result = SystemDiagnostics.check_database_connection()
    assert result.status == "fail"
```

**Migration Tests:**
```python
def test_discover_migrations():
    migrations = MigrationManager.discover_migrations()
    assert len(migrations) > 0
    assert migrations[0].migration_id is not None

def test_run_migration_success():
    result = MigrationManager.run_migration("test_migration", user_id=1)
    assert result["success"] == True
    assert result["execution_time_ms"] > 0
```

### 12.2 Integration Tests

**End-to-End Diagnostic Flow:**
```python
def test_diagnostics_endpoint():
    response = client.post('/setup/diagnostics/run', json={"quick": False})
    assert response.status_code == 200
    data = response.json
    assert "overall_status" in data
    assert "checks" in data
    assert len(data["checks"]) == 9
```

**End-to-End Migration Flow:**
```python
def test_migration_execution():
    # Create test migration file
    # Run migration
    response = client.post('/setup/migrations/run', json={"run_all": True})
    assert response.status_code == 200
    assert response.json["success"] == True

    # Verify migration recorded in history
    with db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM migration_history WHERE migration_name = %s", (migration_id,))
            assert cur.fetchone() is not None
```

### 12.3 Security Tests

**Authentication Required After Installation:**
```python
def test_diagnostics_requires_auth_after_install():
    # Mark system as installed
    create_install_marker()

    # Try to run diagnostics without auth
    response = client.post('/setup/diagnostics/run', json={})
    assert response.status_code == 403
    assert "Authentication required" in response.json["error"]
```

---

## 13. Future Enhancements

### 13.1 Rollback Support

**Goal:** Enable migration rollback using down files

**Implementation:**
```python
def rollback_migration(migration_id: str, user_id: int):
    # Find migration
    # Check if applied
    # Read down SQL file
    # Execute down SQL
    # Update migration_history status to 'rolled_back'
    pass
```

**API Endpoint:**
```
POST /setup/migrations/rollback
Body: {"migration_id": "20250115_004_add_notification_preferences"}
```

### 13.2 Scheduled Diagnostics

**Goal:** Automatic periodic diagnostics with alerting

**Implementation:**
- Celery periodic task (daily/weekly)
- Run full diagnostics
- Send email/Slack alert if overall_status != "ok"
- Store diagnostic history for trending

### 13.3 Migration Dry-Run

**Goal:** Preview migration changes without applying

**Implementation:**
```python
def dry_run_migration(migration_id: str):
    # Begin transaction
    # Execute migration SQL
    # Query schema changes
    # Rollback transaction
    # Return preview of changes
    pass
```

**Use Case:** Verify migration safety before applying to production

### 13.4 Advanced Auto-Fix

**Additional Fixes:**
- **Repair Indexes**: Rebuild missing or corrupted indexes
- **Fix Permissions**: Correct file/directory permissions
- **Reset Caches**: Clear Redis caches
- **Optimize Database**: Run VACUUM ANALYZE

---

## 14. Compliance & Standards

### 14.1 ISO/IEC/IEEE 26515:2018

**API Documentation:**
- All endpoints documented with request/response examples
- Error codes and responses specified
- Usage examples provided

**Architecture Documentation:**
- Component diagrams included
- Data flow described
- Integration points documented

### 14.2 ISO 27001:2013 (Security)

**Access Control:**
- RBAC enforced for post-installation endpoints
- JWT authentication required
- Rate limiting applied

**Audit Logging:**
- All privileged operations logged
- User, timestamp, and action recorded
- Tamper-evident log storage

### 14.3 ISO 9001:2015 (Quality)

**Validation:**
- Comprehensive diagnostic checks
- Migration checksum validation
- Auto-fix idempotency guarantees

**Testing:**
- Unit tests for all components
- Integration tests for API endpoints
- Security tests for access control

---

## 15. Deployment Considerations

### 15.1 Production Deployment

**Pre-Deployment Checklist:**
- [ ] All migrations tested in staging
- [ ] Backup configured and tested
- [ ] Monitoring enabled
- [ ] Security configuration verified
- [ ] Rate limits configured

**Migration Strategy:**
1. Run diagnostics to verify system health
2. Backup database
3. Run pending migrations
4. Verify migrations applied successfully
5. Run diagnostics again to confirm health

### 15.2 Monitoring Integration

**Key Metrics:**
- Diagnostic check failures
- Migration execution time
- Auto-fix success rate
- System health status

**Alerting:**
- Alert if overall_health = "fail"
- Alert if migration execution fails
- Alert if critical component (DB/Redis) fails diagnostic

### 15.3 Backup Integration

**Before Migrations:**
- Automatic database backup
- Store migration state
- Enable point-in-time recovery

**After Failed Migration:**
- Restore from backup
- Investigate failure cause
- Fix migration SQL
- Retry migration

---

## 16. Conclusion

Phase 23 Setup Wizard extensions provide comprehensive system management capabilities:

- **Diagnostics**: 9 comprehensive health checks (quick mode: 3 core checks)
- **Status**: Consolidated installation, version, schema, and health information
- **Migrations**: Database migration discovery, execution, and tracking
- **Auto-Fix**: Idempotent fixes for common system issues

**Key Benefits:**
- Proactive issue detection and resolution
- Simplified post-installation management
- Reduced manual intervention for common issues
- Enhanced system observability

**Integration:**
- Phase 22: Versioning system for version information
- Phase 20: Security (RBAC, authentication, audit logs)
- Phase 19: Monitoring (metrics, health checks, alerting)
- Phase 18: Backup (backup verification, pre-migration backups)

**Next Steps:**
- Implement frontend UI for diagnostics and migrations
- Add scheduled diagnostics with alerting
- Enhance auto-fix with additional repair capabilities
- Implement migration rollback support

---

**Document Version:** 1.0.0
**Last Updated:** 2025-01-16
**Author:** LernsystemX Development Team
**Review Status:** Approved
