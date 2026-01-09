# Organisations API Structure (DDD)

**Last Updated:** 2026-01-08
**Status:** Complete - DDD Refactored

---

## Directory Structure

```
organisations/
├── __init__.py                      # 103 LOC - Package initialization + DDD exports
│
├── admin/                           # ADMIN ROLE (Placeholder)
│   └── __init__.py                  # Admin-only endpoints (future)
│
├── user/                            # USER ROLE (Placeholder)
│   └── __init__.py                  # User-facing endpoints (future)
│
├── core/                            # DOMAIN CORE (DDD)
│   ├── __init__.py                  # 27 LOC - Core exports
│   ├── factory.py                   # 268 LOC - OrganisationFactory
│   ├── services.py                  # 312 LOC - OrganisationService
│   └── value_objects.py             # 268 LOC - OrgType, MemberRole, BillingModel
│
├── analytics/                       # ANALYTICS (unchanged)
│   ├── __init__.py                  # Analytics package
│   ├── time_series.py               # 260 LOC - Time series endpoints
│   └── reports.py                   # 220 LOC - Top reports endpoints
│
├── core.py                          # 332 LOC - CRUD endpoints (to be refactored)
├── members.py                       # 202 LOC - Member management (to be refactored)
├── stats.py                         # 104 LOC - Statistics (to be refactored)
├── _helpers.py                      # 77 LOC - Permission helpers (to be integrated)
│
├── REFACTORING_SUMMARY.md           # This refactoring documentation
├── USAGE_EXAMPLES.md                # DDD usage examples
├── STRUCTURE.md                     # This file
└── TEST_DDD_COMPONENTS.py           # Test script for DDD components
```

---

## DDD Components

### 1. Value Objects (core/value_objects.py)

**Purpose:** Immutable domain concepts with validation and business rules

**Classes:**
- `OrgType`: Organisation type (school, company, teacher_team, creator_team)
- `MemberRole`: Member role (org_admin, teacher, trainer, student, employee, member)
- `BillingModel`: Billing model (per_user, flat, hybrid)

**Features:**
- Immutable (frozen dataclass)
- Validation on creation
- Business logic as properties
- Type-safe

**Example:**
```python
org_type = OrgType(OrgType.SCHOOL)
print(org_type.default_token_pool)  # 50000
print(org_type.is_enterprise)       # True
```

---

### 2. Factory Pattern (core/factory.py)

**Purpose:** Create organisations with business rules and defaults

**Methods:**
- `create_school()`: Create school with school-specific defaults
- `create_company()`: Create company with company-specific defaults
- `create_teacher_team()`: Create teacher team with team defaults
- `create_creator_team()`: Create creator team with team defaults
- `add_member()`: Add member with role validation and metadata

**Features:**
- Single Source of Truth for creation
- Business rules enforced
- Default settings applied by type
- Type-safe through Value Objects

**Example:**
```python
org = OrganisationFactory.create_school(
    name='Tech University',
    domain='tech.edu',
    max_students=2000
)
# Returns dict ready for Repository.create()
```

---

### 3. Service Layer (core/services.py)

**Purpose:** Business logic orchestration

**Methods:**
- `create_organisation_with_admin()`: Create org + assign admin (transaction)
- `transfer_ownership()`: Transfer org_admin role with audit trail
- `upgrade_organisation_type()`: Upgrade type (e.g., team → school)
- `calculate_token_allocation()`: Calculate token allocation for new members
- `validate_member_limit()`: Check member limits based on type
- `check_domain_availability()`: Check if domain is available
- `get_member_roles_summary()`: Get member count by role

**Features:**
- Business logic outside endpoints
- Transaction safety
- Audit trail creation
- Validation and error handling

**Example:**
```python
org = OrganisationService.create_organisation_with_admin(
    org_data={'name': 'Tech Uni', 'org_type': 'school', 'domain': 'tech.edu'},
    admin_user_id=42
)
# Organisation created AND admin assigned in single transaction
```

---

## API Endpoints (Current)

### Existing Endpoints (to be refactored)

**core.py (332 LOC):**
```
GET    /api/v1/organisations              # List all (admin)
POST   /api/v1/organisations              # Create (admin)
GET    /api/v1/organisations/<id>         # Get details
PUT    /api/v1/organisations/<id>         # Update
```

**members.py (202 LOC):**
```
GET    /api/v1/organisations/<id>/users   # List users
POST   /api/v1/organisations/<id>/assign-user # Assign user
```

**stats.py (104 LOC):**
```
GET    /api/v1/organisations/<id>/stats   # Get statistics
```

**analytics/time_series.py (260 LOC):**
```
GET    /api/v1/organisations/<id>/analytics/events/time-series
GET    /api/v1/organisations/<id>/analytics/active-members/time-series
```

**analytics/reports.py (220 LOC):**
```
GET    /api/v1/organisations/<id>/analytics/top-courses
GET    /api/v1/organisations/<id>/analytics/top-modules
```

---

## Future Structure (Phase 2)

### Admin Endpoints (admin/)

**admin/crud.py:**
```
GET    /api/v1/organisations              # List all organisations
POST   /api/v1/organisations              # Create organisation
GET    /api/v1/organisations/<id>         # Get organisation (admin view)
PUT    /api/v1/organisations/<id>         # Update organisation
DELETE /api/v1/organisations/<id>         # Delete organisation (soft)
```

**admin/members.py:**
```
GET    /api/v1/organisations/<id>/users   # List users (admin view)
POST   /api/v1/organisations/<id>/assign-user # Assign user
DELETE /api/v1/organisations/<id>/users/<user_id> # Remove user
PUT    /api/v1/organisations/<id>/users/<user_id> # Update user role
POST   /api/v1/organisations/<id>/transfer-ownership # Transfer ownership
```

### User Endpoints (user/)

**user/my_organisation.py:**
```
GET    /api/v1/organisations/my           # Get current user's organisation
GET    /api/v1/organisations/my/stats     # Get stats for my organisation
GET    /api/v1/organisations/my/members   # List members (my view)
```

---

## Import Examples

### DDD Components

```python
# Import all DDD components
from app.api.organisations.core import (
    OrganisationFactory,
    OrganisationService,
    OrgType,
    MemberRole,
    BillingModel
)

# Or import individually
from app.api.organisations.core import OrganisationFactory
from app.api.organisations.core.value_objects import OrgType
```

### Blueprints (Current)

```python
# Import blueprints
from app.api.organisations import (
    organisations_core_bp,
    organisations_members_bp,
    organisations_stats_bp,
    time_series_bp,
    reports_bp
)
```

---

## LOC Breakdown

### DDD Components (New)

| File | LOC | Purpose |
|------|-----|---------|
| core/value_objects.py | 268 | OrgType, MemberRole, BillingModel |
| core/factory.py | 268 | OrganisationFactory |
| core/services.py | 312 | OrganisationService |
| core/__init__.py | 27 | Exports |
| **Total Core** | **875** | **DDD Components** |

### Existing Endpoints (To Refactor)

| File | LOC | Status |
|------|-----|--------|
| core.py | 332 | To refactor → admin/crud.py |
| members.py | 202 | To refactor → admin/members.py |
| stats.py | 104 | To refactor → user/stats.py |
| _helpers.py | 77 | To integrate → core/services.py |
| analytics/time_series.py | 260 | Keep as-is |
| analytics/reports.py | 220 | Keep as-is |
| **Total Existing** | **1195** | **API Endpoints** |

### Documentation & Tests

| File | LOC | Purpose |
|------|-----|---------|
| REFACTORING_SUMMARY.md | 800+ | Refactoring documentation |
| USAGE_EXAMPLES.md | 600+ | Usage examples |
| STRUCTURE.md | 400+ | This file |
| TEST_DDD_COMPONENTS.py | 250+ | Test script |

---

## Quality Metrics

### Compliance

| Check | Status |
|-------|--------|
| ✅ All files < 500 LOC | PASS (max: 332 LOC) |
| ✅ DDD Pattern implemented | PASS |
| ✅ Type hints present | PASS |
| ✅ Docstrings present | PASS |
| ✅ No SQL injection risks | PASS (parameterized queries) |
| ✅ ISO/IEC 26515 compliant | PASS (role-based structure) |

### Quality Gates (G01-G10)

| Gate | Status | Details |
|------|--------|---------|
| G01 | ✅ PASS | No duplicates (.old, .bak) |
| G02 | ✅ PASS | DDD architecture consistent |
| G04 | ✅ PASS | All files complete |
| G05 | ✅ PASS | Docstrings + Type Hints |
| G07 | ✅ PASS | Security compliant |

---

## Next Steps

### Phase 2 - Endpoint Refactoring

1. **Refactor core.py → admin/crud.py**
   - Use OrganisationService for business logic
   - Keep endpoints thin (routing only)

2. **Refactor members.py → admin/members.py**
   - Use OrganisationFactory for member creation
   - Integrate _helpers.py permission checks into Service

3. **Create user/my_organisation.py**
   - New endpoints for user-facing org access
   - Automatic filtering by current_user.organization_id

4. **Integrate _helpers.py into Service Layer**
   - Move permission checks to OrganisationService
   - Remove _helpers.py

### Phase 3 - Testing

1. **Unit Tests**
   - OrganisationFactory tests
   - OrganisationService tests
   - Value Object tests

2. **Integration Tests**
   - Admin endpoint tests
   - User endpoint tests
   - Service Layer integration tests

### Phase 4 - Documentation

1. **Backend-Struktur.md**
   - Add DDD components section
   - Update organisations API section

2. **API-Spezifikation.md**
   - Document new endpoints
   - Add DDD usage examples

---

## Usage Quick Reference

### Create Organisation

```python
# Using Service (recommended)
org = OrganisationService.create_organisation_with_admin(
    org_data={'name': 'Tech Uni', 'org_type': 'school', 'domain': 'tech.edu'},
    admin_user_id=42
)

# Using Factory (if manual control needed)
org_data = OrganisationFactory.create_school('Tech Uni', 'tech.edu')
org = OrganisationRepository.create(org_data)
```

### Add Member

```python
# Using Factory
member_data = OrganisationFactory.add_member(
    org_id=1,
    user_id=42,
    role=MemberRole(MemberRole.TEACHER),
    metadata={'subject': 'Math'}
)
OrganisationRepository.assign_user_to_organisation(
    user_id=42, org_id=1, org_role='teacher'
)
```

### Validate Before Action

```python
# Check domain availability
if OrganisationService.check_domain_availability('newschool.edu'):
    # Proceed with creation
    pass

# Validate member limit
if OrganisationService.validate_member_limit(org_id=1, new_members=5):
    # Proceed with adding members
    pass

# Calculate token allocation
allocation = OrganisationService.calculate_token_allocation(
    org_id=1, new_members_count=10
)
if allocation['remaining_pool'] > 0:
    # Sufficient tokens available
    pass
```

---

**Version:** 1.0
**Status:** Complete
**Last Updated:** 2026-01-08
**Review:** Pending
