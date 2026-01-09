# DDD Components Usage Examples

This document shows how to use the new DDD components in the organisations domain.

---

## 1. Value Objects

### OrgType

```python
from app.api.organisations.core import OrgType

# Create organisation type
org_type = OrgType(OrgType.SCHOOL)

# Check properties
if org_type.is_enterprise:
    print(f"Token pool: {org_type.default_token_pool}")  # 50,000
    print(f"Billing: {org_type.default_billing_model}")  # per_user

# Invalid type raises ValueError
try:
    invalid = OrgType('invalid')
except ValueError as e:
    print(e)  # Invalid organisation type: invalid
```

### MemberRole

```python
from app.api.organisations.core import MemberRole

# Create member role
role = MemberRole(MemberRole.TEACHER)

# Check permissions
if role.can_view_analytics:
    print("Teacher can view analytics")

if role.can_manage_members:
    print("Teacher cannot manage members")  # Won't print

# Compare roles
admin = MemberRole(MemberRole.ORG_ADMIN)
student = MemberRole(MemberRole.STUDENT)

print(admin > student)  # True (admin has higher hierarchy level)
```

### BillingModel

```python
from app.api.organisations.core import BillingModel

# Create billing model
billing = BillingModel(BillingModel.PER_USER)

# Calculate cost
cost = billing.calculate_cost(
    base_fee=100.0,
    per_user_fee=5.0,
    user_count=50,
    free_tier_users=10
)
print(f"Monthly cost: ${cost}")  # 40 users * $5 = $200

# Hybrid model
hybrid = BillingModel(BillingModel.HYBRID)
cost_hybrid = hybrid.calculate_cost(
    base_fee=100.0,
    per_user_fee=3.0,
    user_count=50,
    free_tier_users=10
)
print(f"Hybrid cost: ${cost_hybrid}")  # $100 base + (40 * $3) = $220
```

---

## 2. Factory Pattern

### Create School

```python
from app.api.organisations.core import OrganisationFactory

# Create school with defaults
org_data = OrganisationFactory.create_school(
    name='Tech University',
    domain='tech.edu',
    max_students=2000,
    max_teachers=100
)

# org_data is ready for OrganisationRepository.create()
print(org_data['org_type'])  # 'school'
print(org_data['token_pool'])  # 50000
print(org_data['billing_model'])  # 'per_user'
```

### Create Company

```python
from app.api.organisations.core import OrganisationFactory

# Create company with department structure
org_data = OrganisationFactory.create_company(
    name='Acme Corporation',
    domain='acme.com',
    employee_limit=1000,
    department_structure={
        'IT': ['Development', 'Operations', 'Security'],
        'Sales': ['EMEA', 'Americas', 'APAC'],
        'HR': ['Recruitment', 'Training']
    }
)

print(org_data['org_type'])  # 'company'
print(org_data['token_pool'])  # 100000
```

### Create Teacher Team

```python
from app.api.organisations.core import OrganisationFactory

# Create teacher team
org_data = OrganisationFactory.create_teacher_team(
    name='Mathematics Department',
    lead_teacher_id=42,
    max_members=15,
    subject_areas=['Mathematics', 'Physics', 'Chemistry']
)

print(org_data['org_type'])  # 'teacher_team'
print(org_data['token_pool'])  # 10000
print(org_data['billing_model'])  # 'flat'
```

### Create Creator Team

```python
from app.api.organisations.core import OrganisationFactory

# Create creator team
org_data = OrganisationFactory.create_creator_team(
    name='Video Production Team',
    lead_creator_id=99,
    max_members=7,
    content_types=['video', 'interactive', 'audio']
)

print(org_data['org_type'])  # 'creator_team'
print(org_data['token_pool'])  # 25000
```

### Add Member with Factory

```python
from app.api.organisations.core import OrganisationFactory, MemberRole

# Add teacher with metadata
member_data = OrganisationFactory.add_member(
    org_id=1,
    user_id=42,
    role=MemberRole(MemberRole.TEACHER),
    metadata={
        'subject': 'Mathematics',
        'department': 'Science',
        'classes': ['10A', '10B', '11C']
    }
)

# member_data is ready for OrganisationRepository.assign_user_to_organisation()
print(member_data['org_role'])  # 'teacher'
```

---

## 3. Service Layer

### Create Organisation with Admin

```python
from app.api.organisations.core import OrganisationService

# Create school with admin in single transaction
org = OrganisationService.create_organisation_with_admin(
    org_data={
        'name': 'Tech University',
        'org_type': 'school',
        'domain': 'tech.edu',
        'max_students': 2000
    },
    admin_user_id=42
)

# Organisation created and user 42 assigned as org_admin
print(org['org_id'])
```

### Transfer Ownership

```python
from app.api.organisations.core import OrganisationService

# Transfer org_admin role to another user
result = OrganisationService.transfer_ownership(
    org_id=1,
    from_user_id=42,
    to_user_id=99,
    requester_role='admin'
)

# Old admin demoted to 'member', new admin promoted to 'org_admin'
# Audit log entry created
```

### Upgrade Organisation Type

```python
from app.api.organisations.core import OrganisationService, OrgType

# Upgrade teacher team to school
org = OrganisationService.upgrade_organisation_type(
    org_id=1,
    new_type=OrgType(OrgType.SCHOOL),
    requester_role='admin'
)

# Token pool adjusted (10,000 → 50,000)
# Billing model changed (flat → per_user)
# Audit log entry created
```

### Calculate Token Allocation

```python
from app.api.organisations.core import OrganisationService

# Calculate token allocation for new members
allocation = OrganisationService.calculate_token_allocation(
    org_id=1,
    new_members_count=10
)

print(allocation)
# {
#     'per_member': 500,
#     'total_allocated': 5000,
#     'remaining_pool': 45000,
#     'billing_model': 'per_user',
#     'current_members': 90,
#     'new_members': 10
# }
```

### Validate Member Limit

```python
from app.api.organisations.core import OrganisationService

# Check if organisation can add more members
can_add = OrganisationService.validate_member_limit(
    org_id=1,
    new_members=5
)

if can_add:
    # Proceed with adding members
    pass
else:
    # Show error: "Organisation has reached member limit"
    pass
```

### Check Domain Availability

```python
from app.api.organisations.core import OrganisationService

# Check if domain is available
if OrganisationService.check_domain_availability('newschool.edu'):
    # Create organisation with this domain
    pass
else:
    # Show error: "Domain already taken"
    pass
```

### Get Member Roles Summary

```python
from app.api.organisations.core import OrganisationService

# Get summary of member counts by role
summary = OrganisationService.get_member_roles_summary(org_id=1)

print(summary)
# {
#     'org_admin': 1,
#     'teacher': 25,
#     'student': 500
# }
```

---

## 4. Integration in API Endpoints

### Example: Create Organisation Endpoint

```python
from flask import Blueprint, request, jsonify
from app.api.organisations.core import OrganisationService
from app.middleware.auth import admin_required

organisations_bp = Blueprint('organisations', __name__)

@organisations_bp.route('/organisations', methods=['POST'])
@admin_required
def create_organisation():
    """
    Create organisation with admin using DDD Service Layer
    """
    data = request.get_json()
    current_user = get_current_user()

    try:
        # Use Service Layer instead of direct Repository calls
        org = OrganisationService.create_organisation_with_admin(
            org_data={
                'name': data['name'],
                'org_type': data['org_type'],
                'domain': data.get('domain'),
                'max_students': data.get('max_students', 1000),
                'max_teachers': data.get('max_teachers', 50)
            },
            admin_user_id=current_user['user_id']
        )

        return jsonify({
            'success': True,
            'organisation': org
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
```

### Example: Validate Before Adding Members

```python
from flask import Blueprint, request, jsonify
from app.api.organisations.core import OrganisationService, OrganisationFactory, MemberRole
from app.middleware.auth import token_required

@organisations_bp.route('/organisations/<int:org_id>/add-members', methods=['POST'])
@token_required
def add_members(org_id: int):
    """
    Add multiple members with validation using DDD components
    """
    data = request.get_json()
    members_to_add = data['members']  # List of user_ids

    # Validate member limit
    if not OrganisationService.validate_member_limit(org_id, len(members_to_add)):
        return jsonify({
            'success': False,
            'error': 'Organisation member limit exceeded'
        }), 400

    # Calculate token allocation
    allocation = OrganisationService.calculate_token_allocation(org_id, len(members_to_add))

    if allocation['remaining_pool'] < 0:
        return jsonify({
            'success': False,
            'error': 'Insufficient tokens for new members'
        }), 400

    # Add members using Factory
    added = []
    for user_id in members_to_add:
        member_data = OrganisationFactory.add_member(
            org_id=org_id,
            user_id=user_id,
            role=MemberRole(MemberRole.STUDENT)
        )
        # Save to database via Repository
        # ...
        added.append(member_data)

    return jsonify({
        'success': True,
        'added': len(added),
        'allocation': allocation
    }), 201
```

---

## 5. Testing Examples

### Unit Test: Factory

```python
import pytest
from app.api.organisations.core import OrganisationFactory, OrgType

def test_create_school_with_defaults():
    org = OrganisationFactory.create_school(
        name='Test School',
        domain='test.edu'
    )

    assert org['org_type'] == OrgType.SCHOOL
    assert org['token_pool'] == 50000
    assert org['billing_model'] == 'per_user'
    assert org['status'] == 'active'

def test_create_teacher_team_enforces_member_limit():
    org = OrganisationFactory.create_teacher_team(
        name='Test Team',
        lead_teacher_id=42,
        max_members=100  # Exceeds limit
    )

    # Factory enforces max 20 members
    settings = json.loads(org['settings'])
    assert settings['max_members'] == 20
```

### Unit Test: Value Objects

```python
import pytest
from app.api.organisations.core import OrgType, MemberRole

def test_org_type_validation():
    with pytest.raises(ValueError):
        OrgType('invalid_type')

def test_member_role_permissions():
    admin = MemberRole(MemberRole.ORG_ADMIN)
    assert admin.can_manage_members is True
    assert admin.can_view_analytics is True

    student = MemberRole(MemberRole.STUDENT)
    assert student.can_manage_members is False
    assert student.can_view_analytics is False

def test_member_role_hierarchy():
    admin = MemberRole(MemberRole.ORG_ADMIN)
    teacher = MemberRole(MemberRole.TEACHER)
    student = MemberRole(MemberRole.STUDENT)

    assert admin > teacher
    assert teacher > student
    assert admin > student
```

### Unit Test: Service

```python
import pytest
from app.api.organisations.core import OrganisationService, OrgType

def test_check_domain_availability():
    # Domain not taken
    assert OrganisationService.check_domain_availability('newdomain.edu') is True

    # Domain already exists
    assert OrganisationService.check_domain_availability('existing.edu') is False

def test_validate_member_limit_for_teams():
    # Assume org_id=1 is teacher_team with 18 members
    assert OrganisationService.validate_member_limit(1, 1) is True  # 19 total (under 20)
    assert OrganisationService.validate_member_limit(1, 2) is True  # 20 total (at limit)
    assert OrganisationService.validate_member_limit(1, 3) is False # 21 total (over limit)
```

---

## 6. Migration from Old Code

### Before (Direct Repository)

```python
from app.repositories.organisations.core import OrganisationRepository

# Old way - direct repository call, no business rules
org = OrganisationRepository.create_organisation(
    name='Tech Uni',
    org_type='school',
    domain='tech.edu',
    billing_model='per_user',
    token_pool=50000
)

# Manually assign admin
OrganisationRepository.assign_user_to_organisation(
    user_id=42,
    org_id=org['org_id'],
    org_role='org_admin'
)
```

### After (DDD Service + Factory)

```python
from app.api.organisations.core import OrganisationService

# New way - Service Layer with business rules
org = OrganisationService.create_organisation_with_admin(
    org_data={
        'name': 'Tech Uni',
        'org_type': 'school',
        'domain': 'tech.edu'
    },
    admin_user_id=42
)

# Everything handled: validation, creation, admin assignment, token pool
```

**Benefits:**
- ✅ Business rules enforced (default token pool, billing model)
- ✅ Single transaction (organisation + admin)
- ✅ Validation (domain availability, user exists)
- ✅ Less code in endpoint
- ✅ Testable business logic

---

**Version:** 1.0
**Last Updated:** 2026-01-08
**Status:** Complete
