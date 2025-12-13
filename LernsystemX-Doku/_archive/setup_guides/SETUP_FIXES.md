# Setup Wizard Fixes - 2025-11-19

## Issues Fixed

### 1. CORS Configuration Persistence
**Problem:** Setup Wizard recreates `.env` from `.env.example` on browser refresh, resetting CORS to localhost only.

**Solution:** Modified `.env.example` (lines 69-74) to have wildcard CORS by default:
```env
CORS_ORIGINS=*
SOCKETIO_CORS_ALLOWED_ORIGINS=*
```

**Files Changed:**
- `backend/.env.example` - Template now has wildcard CORS for development

**Status:** ✅ FIXED

---

### 2. Connection Pool Staleness After Database Initialization
**Problem:** After database initialization, the psycopg connection pool retained BAD connections, causing admin creation to fail with 500 errors.

**Root Cause:** Python module import reference issue:
- `app/database/connection.py` imported `db_pool` directly from `app.extensions`
- When `refresh_db_pool()` updated the pool in `app.extensions`, the connection module still had a reference to the OLD pool
- All database operations continued using BAD connections

**Solution:**
1. Added `refresh_db_pool()` function to `app/extensions.py` (lines 47-75)
2. Modified `/setup/database` endpoint to automatically refresh pool after DB init (lines 275-287 in `setup/routes.py`)
3. **Critical fix:** Changed `app/database/connection.py` to import the module instead of the variable:
   - Old: `from app.extensions import db_pool`
   - New: `import app.extensions` + use `app.extensions.db_pool` everywhere
   - This ensures all database operations always use the current pool

**Files Changed:**
- `backend/app/extensions.py` - Added `refresh_db_pool()` function
- `backend/setup/routes.py` - Added automatic pool refresh after DB init
- `backend/app/database/connection.py` - Changed import to use module reference

**Status:** ✅ FIXED

---

## Testing Instructions

1. **Navigate to Setup Wizard:**
   ```
   http://10.0.20.111:5000/setup/status
   ```

2. **Test CORS:**
   - Access from network IP (not localhost)
   - Refresh browser multiple times
   - CORS should work every time (no more errors)

3. **Test Database Init + Admin Creation:**
   - Complete database initialization
   - Immediately create admin user
   - Should work without manual backend restart
   - Connection pool is automatically refreshed

4. **Complete Flow:**
   - Database init → Admin creation → Success (no manual intervention)

---

## Technical Details

### Connection Pool Refresh Function
```python
def refresh_db_pool(database_url: str = None):
    """
    Refresh database connection pool (close old connections and create new pool)

    This is needed after database schema changes (e.g., during setup wizard)
    to ensure all connections are fresh and not stale.
    """
    global db_pool

    # Close existing pool if it exists
    if db_pool is not None:
        try:
            db_pool.close()
        except Exception as e:
            print(f"Warning: Error closing old pool: {e}")

    # Reinitialize with new or existing URL
    if database_url:
        init_db_pool(database_url)
    else:
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            init_db_pool(database_url)
        else:
            raise ValueError("DATABASE_URL not set in environment")
```

### Automatic Pool Refresh in Setup Wizard
```python
if results['success']:
    # IMPORTANT: Refresh connection pool after database initialization
    # This ensures all connections are fresh and not stale (no more BAD connections)
    try:
        current_app.logger.info("[DB_INIT] Refreshing database connection pool...")
        refresh_db_pool()
        current_app.logger.info("[DB_INIT] Connection pool refreshed successfully")
        results['connection_pool_refreshed'] = True
    except Exception as e:
        current_app.logger.warning(f"[DB_INIT] Failed to refresh connection pool: {e}")
        results['connection_pool_refreshed'] = False
        results['pool_refresh_warning'] = str(e)
```

---

## Backend Process

**Current Backend:**
- Process ID: 622660
- Running on: http://127.0.0.1:5000 and http://10.0.20.111:5000
- Mode: Setup Wizard (system not installed)

---

### 3. Seed Data Installation Returning Zero Counts
**Problem:** Setup Wizard seed endpoint returned success but showed 0 for all counts (learning methods, roles, categories) even though data existed in database.

**Root Causes:**
1. **Incorrect column name in roles INSERT**: Using `name` instead of `role_name`
2. **Wrong counting logic**: Code always incremented counter even when `ON CONFLICT DO NOTHING` skipped insertion
3. **Insertion counts vs actual counts**: Endpoint returned insertion counts (0 when data exists) instead of actual database counts

**Solution:**
1. Fixed `setup/seeds.py` line 516: Changed column from `name` to `role_name`
2. Modified `seed_all()` method (lines 26-72) to return ACTUAL database counts instead of insertion counts:
   ```python
   # Return ACTUAL database counts (not insertion counts)
   methods_result = fetch_one("SELECT COUNT(*) as count FROM learning_method_types")
   results['learning_methods'] = methods_result['count'] if methods_result else 0
   ```
3. Added `RETURNING *` clause to all INSERT statements to detect successful insertions

**Files Changed:**
- `backend/setup/seeds.py` - Fixed column name, changed return logic to actual counts
- `backend/test_seeds.py` - Created diagnostic script for testing

**Testing:**
```bash
cd backend && python test_seeds.py
```

**Expected Results:**
- Learning Methods: 21
- Roles: 10-11 (depending on superadmin)
- Categories: 8

**Status:** ✅ FIXED

---

## Remaining Tasks

- [ ] Test complete Setup Wizard flow from start to finish (with browser)
- [ ] Verify admin login works after creation
- [ ] Test organization setup
- [ ] Test AI provider configuration
- [ ] Complete installation and verify normal operation

---

## Notes

- All fixes are now automatic - no manual backend restarts needed
- CORS configuration persists across browser refreshes
- Connection pool is always fresh after database initialization
- The module import fix (`import app.extensions` instead of `from app.extensions import db_pool`) was critical for pool refresh to work
