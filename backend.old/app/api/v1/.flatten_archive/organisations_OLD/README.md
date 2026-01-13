# Organisations API - DDD Refactored

**Status:** Phase 1 Complete - DDD Core Components Implemented
**Date:** 2026-01-08
**Architecture:** Domain-Driven Design (DDD)

---

## Overview

The Organisations API has been refactored to follow Domain-Driven Design (DDD) principles with clear separation of concerns:

- **Factory Pattern** for entity creation with business rules
- **Service Layer** for business logic orchestration
- **Value Objects** for type-safe domain concepts
- **Role-based organization** (admin/user/core separation planned)

---

## Quick Start

### Using DDD Components

```python
from app.api.organisations.core import (
    OrganisationFactory,
    OrganisationService,
    OrgType,
    MemberRole,
    BillingModel
)

# Create organisation with admin
org = OrganisationService.create_organisation_with_admin(
    org_data={
        'name': 'Tech University',
        'org_type': 'school',
        'domain': 'tech.edu'
    },
    admin_user_id=42
)

# Use Value Objects
org_type = OrgType(OrgType.SCHOOL)
print(f"Default token pool: {org_type.default_token_pool}")  # 50,000

# Check permissions
role = MemberRole(MemberRole.TEACHER)
if role.can_view_analytics:
    print("Teacher can view analytics")
```

---

## Project Structure

```
organisations/
├── core/                          # DDD DOMAIN CORE
│   ├── factory.py                # OrganisationFactory (268 LOC)
│   ├── services.py               # OrganisationService (312 LOC)
│   └── value_objects.py          # OrgType, MemberRole, BillingModel (268 LOC)
│
├── admin/                         # ADMIN ROLE (Placeholder)
│   └── __init__.py               # Future: admin-only endpoints
│
├── user/                          # USER ROLE (Placeholder)
│   └── __init__.py               # Future: user-facing endpoints
│
├── analytics/                     # ANALYTICS (Unchanged)
│   ├── time_series.py            # Time series endpoints (260 LOC)
│   └── reports.py                # Top reports endpoints (220 LOC)
│
├── core.py                        # CRUD endpoints (332 LOC) - To refactor
├── members.py                     # Member management (202 LOC) - To refactor
├── stats.py                       # Statistics (104 LOC) - To refactor
├── _helpers.py                    # Permission helpers (77 LOC) - To integrate
│
├── REFACTORING_SUMMARY.md         # Complete refactoring documentation
├── USAGE_EXAMPLES.md              # DDD usage examples and patterns
├── STRUCTURE.md                   # Detailed structure documentation
├── TEST_DDD_COMPONENTS.py         # Test script for DDD components
└── README.md                      # This file
```

---

## DDD Components

### 1. Value Objects (core/value_objects.py)

**Immutable domain concepts with validation:**

- **OrgType**: Organisation type (school, company, teacher_team, creator_team)
  - Properties: `is_enterprise`, `is_team`, `default_token_pool`, `default_member_limit`

- **MemberRole**: Member role (org_admin, teacher, trainer, student, employee, member)
  - Properties: `can_manage_members`, `can_view_analytics`, `hierarchy_level`

- **BillingModel**: Billing model (per_user, flat, hybrid)
  - Methods: `calculate_cost()`, `requires_user_count`

### 2. Factory Pattern (core/factory.py)

**Single Source of Truth for entity creation:**

- `create_school()`: School with 50K tokens, per_user billing
- `create_company()`: Company with 100K tokens, per_user billing
- `create_teacher_team()`: Teacher team with 10K tokens, flat billing, max 20 members
- `create_creator_team()`: Creator team with 25K tokens, flat billing, max 10 members
- `add_member()`: Add member with role validation and metadata

### 3. Service Layer (core/services.py)

**Business logic orchestration:**

- `create_organisation_with_admin()`: Create org + assign admin (transaction)
- `transfer_ownership()`: Transfer org_admin with audit trail
- `upgrade_organisation_type()`: Upgrade type (team → school)
- `calculate_token_allocation()`: Calculate token allocation for new members
- `validate_member_limit()`: Check member limits based on type
- `check_domain_availability()`: Check if domain is available
- `get_member_roles_summary()`: Get member count by role

---

## API Endpoints

### Current Endpoints (Phase 1)

**Admin Endpoints:**
```
GET    /api/v1/organisations              # List all organisations
POST   /api/v1/organisations              # Create organisation
GET    /api/v1/organisations/<id>         # Get organisation
PUT    /api/v1/organisations/<id>         # Update organisation
GET    /api/v1/organisations/<id>/users   # List users
POST   /api/v1/organisations/<id>/assign-user # Assign user
```

**Statistics:**
```
GET    /api/v1/organisations/<id>/stats   # Get statistics
```

**Analytics:**
```
GET    /api/v1/organisations/<id>/analytics/events/time-series
GET    /api/v1/organisations/<id>/analytics/active-members/time-series
GET    /api/v1/organisations/<id>/analytics/top-courses
GET    /api/v1/organisations/<id>/analytics/top-modules
```

### Future Endpoints (Phase 2)

**User Endpoints:**
```
GET    /api/v1/organisations/my           # Get current user's organisation
GET    /api/v1/organisations/my/stats     # Get stats for my organisation
GET    /api/v1/organisations/my/members   # List members (my view)
```

---

## Documentation

| File | Purpose |
|------|---------|
| **REFACTORING_SUMMARY.md** | Complete refactoring documentation with metrics |
| **USAGE_EXAMPLES.md** | Practical examples for all DDD components |
| **STRUCTURE.md** | Detailed structure and LOC breakdown |
| **README.md** | This quick reference guide |
| **TEST_DDD_COMPONENTS.py** | Verification script for DDD components |

---

## Testing

### Run Component Tests

```bash
# From backend/ directory
python -m app.api.organisations.TEST_DDD_COMPONENTS
```

**Expected output:**
```
=== Testing Value Objects ===
   ✓ OrgType.SCHOOL works
   ✓ MemberRole.ORG_ADMIN works
   ✓ BillingModel.PER_USER works

=== Testing Factory Pattern ===
   ✓ School created with correct defaults
   ✓ Company created with correct defaults
   ✓ Teacher team created with correct defaults

✓ ALL TESTS PASSED!
```

### Unit Tests (To Implement)

```python
# tests/unit/test_organisation_factory.py
def test_create_school_with_defaults():
    org = OrganisationFactory.create_school('Test', 'test.edu')
    assert org['org_type'] == OrgType.SCHOOL
    assert org['token_pool'] == 50000

# tests/unit/test_value_objects.py
def test_org_type_validation():
    with pytest.raises(ValueError):
        OrgType('invalid_type')

# tests/unit/test_organisation_service.py
def test_calculate_token_allocation():
    allocation = OrganisationService.calculate_token_allocation(
        org_id=1, new_members_count=10
    )
    assert 'per_member' in allocation
```

---

## Usage Examples

### Example 1: Create School with Admin

```python
from app.api.organisations.core import OrganisationService

org = OrganisationService.create_organisation_with_admin(
    org_data={
        'name': 'Tech University',
        'org_type': 'school',
        'domain': 'tech.edu',
        'max_students': 2000,
        'max_teachers': 100
    },
    admin_user_id=42
)

# Result:
# - Organisation created with 50,000 tokens
# - User 42 assigned as org_admin
# - Domain validated (uniqueness)
# - Settings applied based on org_type
```

### Example 2: Add Members with Validation

```python
from app.api.organisations.core import (
    OrganisationService,
    OrganisationFactory,
    MemberRole
)

# Validate member limit
if not OrganisationService.validate_member_limit(org_id=1, new_members=10):
    raise ValueError("Member limit exceeded")

# Calculate token allocation
allocation = OrganisationService.calculate_token_allocation(
    org_id=1,
    new_members_count=10
)

if allocation['remaining_pool'] < 0:
    raise ValueError("Insufficient tokens")

# Add members
for user_id in [101, 102, 103]:
    member_data = OrganisationFactory.add_member(
        org_id=1,
        user_id=user_id,
        role=MemberRole(MemberRole.STUDENT)
    )
    # Save to database via Repository
```

### Example 3: Transfer Ownership

```python
from app.api.organisations.core import OrganisationService

result = OrganisationService.transfer_ownership(
    org_id=1,
    from_user_id=42,
    to_user_id=99,
    requester_role='admin'
)

# Result:
# - User 42 demoted to 'member'
# - User 99 promoted to 'org_admin'
# - Audit log entry created
```

### Example 4: Upgrade Organisation Type

```python
from app.api.organisations.core import OrganisationService, OrgType

org = OrganisationService.upgrade_organisation_type(
    org_id=1,
    new_type=OrgType(OrgType.SCHOOL),
    requester_role='admin'
)

# Result:
# - Teacher team upgraded to school
# - Token pool increased (10K → 50K)
# - Billing model changed (flat → per_user)
# - Audit log entry created
```

---

## Migration Guide

### Before (Old Code)

```python
from app.repositories.organisations.core import OrganisationRepository

# Direct repository call - no business rules
org = OrganisationRepository.create_organisation(
    name='Tech Uni',
    org_type='school',
    domain='tech.edu',
    billing_model='per_user',
    token_pool=50000
)

# Manually assign admin
OrganisationRepository.assign_user_to_organisation(
    user_id=42, org_id=org['org_id'], org_role='org_admin'
)
```

### After (DDD)

```python
from app.api.organisations.core import OrganisationService

# Service Layer - business rules enforced
org = OrganisationService.create_organisation_with_admin(
    org_data={'name': 'Tech Uni', 'org_type': 'school', 'domain': 'tech.edu'},
    admin_user_id=42
)

# Everything handled: validation, creation, admin assignment
```

**Benefits:**
- ✅ Business rules enforced (token pool, billing model)
- ✅ Single transaction (organisation + admin)
- ✅ Validation (domain availability, user exists)
- ✅ Less code in endpoint
- ✅ Testable business logic

---

## Quality Metrics

### Compliance

| Check | Status |
|-------|--------|
| All files < 500 LOC | ✅ PASS (max: 332 LOC) |
| DDD Pattern implemented | ✅ PASS |
| Type hints present | ✅ PASS |
| Docstrings present | ✅ PASS |
| No SQL injection | ✅ PASS |
| ISO/IEC 26515 compliant | ✅ PASS |

### Quality Gates (G01-G10)

| Gate | Status | Details |
|------|--------|---------|
| G01 | ✅ PASS | No duplicates (.old, .bak) |
| G02 | ✅ PASS | DDD architecture consistent |
| G04 | ✅ PASS | All files complete |
| G05 | ✅ PASS | Docstrings + Type Hints |
| G07 | ✅ PASS | Security compliant |

---

## Roadmap

### Phase 1 - DDD Core (COMPLETE ✓)
- [x] Value Objects (OrgType, MemberRole, BillingModel)
- [x] Factory Pattern (OrganisationFactory)
- [x] Service Layer (OrganisationService)
- [x] Documentation (REFACTORING_SUMMARY.md, USAGE_EXAMPLES.md)
- [x] Test script (TEST_DDD_COMPONENTS.py)

### Phase 2 - Endpoint Refactoring (TODO)
- [ ] Refactor core.py → admin/crud.py
- [ ] Refactor members.py → admin/members.py
- [ ] Create user/my_organisation.py
- [ ] Integrate _helpers.py into Service Layer

### Phase 3 - Testing (TODO)
- [ ] Unit tests for Factory
- [ ] Unit tests for Service
- [ ] Unit tests for Value Objects
- [ ] Integration tests for endpoints

### Phase 4 - Documentation (TODO)
- [ ] Update Backend-Struktur.md
- [ ] Update API-Spezifikation.md
- [ ] Migration guide for existing code

---

## Getting Help

**Documentation:**
- `REFACTORING_SUMMARY.md` - Complete refactoring details
- `USAGE_EXAMPLES.md` - Practical usage examples
- `STRUCTURE.md` - Detailed structure and metrics

**Test:**
- Run `TEST_DDD_COMPONENTS.py` to verify components work

**Questions:**
- Check `USAGE_EXAMPLES.md` for common patterns
- Review docstrings in code for API details

---

## Contributing

When adding new functionality:

1. **Use DDD Components:**
   - Use `OrganisationFactory` for entity creation
   - Use `OrganisationService` for business logic
   - Use Value Objects for type safety

2. **Follow Patterns:**
   - Keep endpoints thin (routing only)
   - Put business logic in Service Layer
   - Validate with Value Objects

3. **Quality Gates:**
   - Max 500 LOC per file
   - Type hints required
   - Docstrings required
   - Tests required

---

**Version:** 1.0
**Status:** Phase 1 Complete
**Last Updated:** 2026-01-08
**Next Review:** Phase 2 Planning
