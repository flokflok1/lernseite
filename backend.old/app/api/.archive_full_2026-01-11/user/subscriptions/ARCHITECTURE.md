# Subscriptions Domain - Architecture Overview

**Date:** 2026-01-08
**Status:** REFERENCE
**Domain:** subscriptions/

---

## 1. Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (Flask Blueprints)                │
├─────────────────────────────────────────────────────────────────┤
│  admin/              user/               plans/                  │
│  ├─ management.py    ├─ subscriptions.py ├─ catalog.py          │
│  │   (stats, expiring)│   (/me)          │   (list plans)       │
│  │                    └─ billing.py                              │
│                          (change, cancel, reactivate)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER (DDD Core)                       │
├─────────────────────────────────────────────────────────────────┤
│  core/factory.py          core/value_objects.py                  │
│  ├─ SubscriptionFactory   ├─ PlanType (enum)                    │
│  │  ├─ create()           ├─ BillingCycle (enum)                │
│  │  ├─ create_trial()     ├─ SubscriptionStatus (enum)          │
│  │  ├─ upgrade()          ├─ check_tier_access()                │
│  │  ├─ downgrade()        └─ get_tier_for_plan()                │
│  │  ├─ cancel()                                                  │
│  │  └─ reactivate()                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER (Business Logic)                │
├─────────────────────────────────────────────────────────────────┤
│  services/billing_service.py                                     │
│  ├─ ensure_user_can_use_ai()                                     │
│  ├─ charge_ai_usage()                                            │
│  ├─ get_effective_plan_for_user()                                │
│  ├─ allocate_monthly_tokens_for_subscription()                   │
│  └─ check_feature_access()                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  REPOSITORY LAYER (Data Access)                  │
├─────────────────────────────────────────────────────────────────┤
│  repositories/subscription/                                      │
│  ├─ crud.py                (PlanRepository)                      │
│  ├─ user_subscriptions.py (UserSubscriptionRepository)          │
│  ├─ organisation_subscriptions.py (OrganisationSubscriptionRepo)│
│  ├─ lifecycle.py           (SubscriptionLifecycleRepository)    │
│  └─ analytics.py           (SubscriptionAnalyticsRepository)    │
│                                                                   │
│  Unified: SubscriptionRepository (multiple inheritance)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (PostgreSQL)                   │
├─────────────────────────────────────────────────────────────────┤
│  Tables:                                                          │
│  ├─ subscriptions         (user/org subscriptions)               │
│  ├─ subscription_plans     (plan definitions)                    │
│  ├─ token_wallets          (user/org token balances)             │
│  └─ token_transactions     (token usage history)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Examples

### 2.1 Create Subscription

```
User Request (POST /api/v1/subscriptions/create)
    ↓
API Layer: user/subscriptions.py
    ↓
Domain Layer: SubscriptionFactory.create_subscription()
    ├─ Validate business rules
    ├─ Check for existing subscription
    ├─ Calculate dates and pricing
    └─ Build subscription data
    ↓
Repository Layer: SubscriptionRepository.create()
    ↓
Database: INSERT INTO subscriptions
    ↓
Response: Subscription created
```

### 2.2 Upgrade Subscription

```
User Request (POST /api/v1/subscriptions/change)
    ↓
API Layer: user/billing.py
    ↓
Domain Layer: SubscriptionFactory.upgrade()
    ├─ Get current subscription
    ├─ Verify tier hierarchy
    ├─ Calculate proration (TODO)
    └─ Build update data
    ↓
Repository Layer: SubscriptionRepository.update()
    ↓
Database: UPDATE subscriptions SET plan_id = ...
    ↓
Response: Subscription upgraded
```

### 2.3 Check AI Access

```
AI Request (any AI method)
    ↓
Service Layer: BillingService.ensure_user_can_use_ai()
    ├─ Get user subscription (user → org → free)
    ├─ Check plan features (ai_access)
    ├─ Check subscription status (active/trial)
    └─ Check token balance
    ↓
Repository Layer: SubscriptionRepository.get_subscription_for_user()
    ↓
Database: SELECT * FROM subscriptions WHERE user_id = ...
    ↓
Response: {allowed: true, wallet: {...}, subscription: {...}}
```

---

## 3. Domain Model

### 3.1 Subscription Lifecycle

```
┌─────────┐
│  Free   │ (No subscription record)
└─────────┘
     ↓ create_subscription()
┌─────────┐
│  Trial  │ (7 days free)
└─────────┘
     ↓ trial ends
┌─────────┐
│ Active  │ (Paid, auto-renew)
└─────────┘
     ↓ cancel()
┌───────────┐
│ Cancelled │ (Access until period end)
└───────────┘
     ↓ reactivate() OR period ends
┌─────────┐       ┌──────────┐
│ Active  │       │ Expired  │
└─────────┘       └──────────┘

Special states:
┌──────────┐  Payment failed
│ Past Due │  (Grace period)
└──────────┘
┌───────────┐  Admin action
│ Suspended │  (Manual block)
└───────────┘
```

### 3.2 Plan Hierarchy

```
                    ┌─────────────────┐
                    │  SUBSCRIPTION   │
                    │     PLANS       │
                    └─────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌───────────────┐  ┌────────────────┐  ┌──────────────┐
│  Individual   │  │  Professional  │  │ Organisation │
│  (Free/Premium)│  │ (Creator/Teacher)│ │ (School/Company)│
└───────────────┘  └────────────────┘  └──────────────┘
  │                  │                   │
  ├─ Free           ├─ Creator          ├─ School
  │  • 0 tokens     │  • 20K tokens     │  • Custom tokens
  │  • 11 methods   │  • Marketplace    │  • Unlimited users
  │  • No AI        │  • 21 methods     │  • SSO
  │                 │                   │
  └─ Premium        └─ Teacher          └─ Company
     • 10K tokens      • 30K tokens        • Compliance
     • 21 methods      • LiveRoom Pro      • SCORM
     • AI access       • Class mgmt        • Custom branding
```

---

## 4. Tier Hierarchy

```
Level 3: ENTERPRISE  ┌──────────┬──────────┐
                     │  School  │ Company  │
                     └──────────┴──────────┘
                            │
Level 2: PRO         ┌──────────┬──────────┐
                     │ Creator  │ Teacher  │
                     └──────────┴──────────┘
                            │
Level 1: PREMIUM     ┌──────────┐
                     │ Premium  │
                     └──────────┘
                            │
Level 0: FREE        ┌──────────┐
                     │   Free   │
                     └──────────┘

Access Control:
• Higher level = access to all lower level features
• check_tier_access('premium', 'free') → True ✓
• check_tier_access('free', 'premium') → False ✗
```

---

## 5. Factory Methods

### 5.1 Create Subscription

```python
SubscriptionFactory.create_subscription(
    user_id='user_123',
    plan_id=2,
    billing_cycle=BillingCycle.MONTHLY,
    promo_code='SAVE20',
    meta={'source': 'web_signup'}
)

Returns: dict {
    'subscription_id': uuid,
    'user_id': 'user_123',
    'plan_id': 2,
    'status': 'trial',
    'billing_cycle': 'monthly',
    'current_period_start': datetime,
    'current_period_end': datetime,
    'trial_ends_at': datetime (7 days),
    'auto_renew': True,
    ...
}
```

### 5.2 Upgrade

```python
SubscriptionFactory.upgrade(
    subscription_id='sub_123',
    new_plan_id=3,
    reason='Need marketplace access',
    prorate=True
)

Returns: dict {
    'plan_id': 3,
    'price': 29.99,
    'updated_at': datetime,
    'meta': {
        'upgrade_reason': 'Need marketplace access',
        'previous_plan': 'premium',
        'upgraded_at': datetime,
        'proration_credit': 0.00  # TODO
    }
}
```

### 5.3 Cancel

```python
SubscriptionFactory.cancel(
    subscription_id='sub_123',
    reason='Too expensive',
    immediate=False,
    feedback='Would reconsider if cheaper'
)

Returns: dict {
    'status': 'cancelled',
    'cancelled_at': datetime,
    'cancel_at_period_end': True,
    'auto_renew': False,
    'cancellation_reason': 'Too expensive',
    'meta': {
        'cancellation_feedback': 'Would reconsider if cheaper',
        'cancelled_at': datetime,
        'cancellation_type': 'at_period_end'
    }
}
```

---

## 6. Value Objects

### 6.1 PlanType

```python
from app.api.subscriptions.core import PlanType

plan = PlanType.PREMIUM

# Properties
plan.tier                      # "premium"
plan.is_organisation_plan      # False
plan.default_included_tokens   # 10000

# Enum values
PlanType.FREE       # "free"
PlanType.PREMIUM    # "premium"
PlanType.CREATOR    # "creator"
PlanType.TEACHER    # "teacher"
PlanType.SCHOOL     # "school"
PlanType.COMPANY    # "company"
```

### 6.2 BillingCycle

```python
from app.api.subscriptions.core import BillingCycle

cycle = BillingCycle.YEARLY

# Properties
cycle.months  # 12

# Methods
cycle.calculate_price(
    monthly_price=14.99,
    yearly_price=129.99
)  # Returns 129.99

# Enum values
BillingCycle.MONTHLY  # "monthly"
BillingCycle.YEARLY   # "yearly"
```

### 6.3 SubscriptionStatus

```python
from app.api.subscriptions.core import SubscriptionStatus

status = SubscriptionStatus.ACTIVE

# Properties
status.has_access      # True
status.is_renewable    # True

# Enum values
SubscriptionStatus.ACTIVE      # "active"
SubscriptionStatus.TRIAL       # "trial"
SubscriptionStatus.CANCELLED   # "cancelled"
SubscriptionStatus.PAST_DUE    # "past_due"
SubscriptionStatus.EXPIRED     # "expired"
SubscriptionStatus.SUSPENDED   # "suspended"
```

---

## 7. Integration Examples

### 7.1 Create User Subscription (API → Factory → Repository)

```python
# API Layer (user/subscriptions.py)
from flask import Blueprint, request, jsonify
from app.api.subscriptions.core import SubscriptionFactory, BillingCycle
from app.repositories.subscription import SubscriptionRepository

@subscriptions_bp.route('/create', methods=['POST'])
@token_required
def create_user_subscription():
    user = get_current_user()
    data = request.get_json()

    # Domain Layer (Factory)
    sub_data = SubscriptionFactory.create_subscription(
        user_id=user['user_id'],
        plan_id=data['plan_id'],
        billing_cycle=BillingCycle(data['billing_cycle']),
        promo_code=data.get('promo_code')
    )

    # Repository Layer
    subscription = SubscriptionRepository.create(sub_data)

    return jsonify({'success': True, 'subscription': subscription}), 201
```

### 7.2 Upgrade with Factory (Before vs After)

```python
# BEFORE (direct repository)
updated = SubscriptionRepository.change_subscription(
    subscription_id=sub['subscription_id'],
    new_plan_id=new_plan_id,
    reason=reason
)

# AFTER (using Factory)
from app.api.subscriptions.core import SubscriptionFactory

# Factory handles validation and business rules
upgrade_data = SubscriptionFactory.upgrade(
    subscription_id=sub['subscription_id'],
    new_plan_id=new_plan_id,
    reason=reason,
    prorate=True
)

# Repository just persists the data
updated = SubscriptionRepository.update(
    sub['subscription_id'],
    upgrade_data
)
```

---

## 8. Error Handling

### 8.1 Factory Validation Errors

```python
try:
    sub_data = SubscriptionFactory.create_subscription(
        user_id='user_123',
        plan_id=999  # Invalid plan
    )
except ValueError as e:
    # Business rule violation
    print(f"Factory error: {e}")
    # "Plan with ID 999 not found"
```

### 8.2 Common Error Scenarios

| Error | Cause | Factory Response |
|-------|-------|------------------|
| Duplicate subscription | User already has active sub | `ValueError` |
| Invalid plan | Plan not found or inactive | `ValueError` |
| Invalid upgrade | Trying to downgrade via upgrade() | `ValueError` |
| Expired subscription | Trying to reactivate expired | `ValueError` |
| Missing owner | Neither user_id nor org_id | `ValueError` |

---

## 9. Testing Checklist

### 9.1 Factory Tests

- [ ] create_subscription() - success
- [ ] create_subscription() - duplicate error
- [ ] create_subscription() - invalid plan error
- [ ] create_trial() - success
- [ ] upgrade() - success
- [ ] upgrade() - invalid tier error
- [ ] downgrade() - success
- [ ] downgrade() - invalid tier error
- [ ] cancel() - immediate
- [ ] cancel() - at period end
- [ ] reactivate() - success
- [ ] reactivate() - expired error

### 9.2 Value Objects Tests

- [ ] PlanType.tier property
- [ ] PlanType.is_organisation_plan
- [ ] PlanType.default_included_tokens
- [ ] BillingCycle.months
- [ ] BillingCycle.calculate_price()
- [ ] SubscriptionStatus.has_access
- [ ] SubscriptionStatus.is_renewable
- [ ] check_tier_access() - higher to lower (True)
- [ ] check_tier_access() - lower to higher (False)

---

## 10. API Documentation

### 10.1 Endpoints Summary

| Endpoint | Method | Auth | Role | Description |
|----------|--------|------|------|-------------|
| `/subscriptions/plans` | GET | - | Public | List all plans |
| `/subscriptions/me` | GET | Required | User | Get my subscription |
| `/subscriptions/change` | POST | Required | User | Change plan |
| `/subscriptions/cancel` | POST | Required | User | Cancel subscription |
| `/subscriptions/reactivate` | POST | Required | User | Reactivate |
| `/subscriptions/stats` | GET | Required | Admin | Get stats |
| `/subscriptions/expiring` | GET | Required | Admin | Expiring subs |

**Total:** 7 endpoints (6 implemented, 1 future: /create)

---

## 11. Deployment Notes

### 11.1 Migration Steps

1. ✅ Deploy core/ directory (factory, value_objects)
2. ⏳ Add tests for Factory and Value Objects
3. ⏳ Refactor existing endpoints to use Factory
4. ⏳ Implement proration calculation
5. ⏳ Implement promo code system
6. ⏳ Add email notifications
7. ⏳ Integrate Stripe API

### 11.2 Monitoring

**Key Metrics:**
- Subscription creation rate (per hour)
- Upgrade/downgrade ratio
- Cancellation rate (churn)
- Reactivation success rate
- Trial → Paid conversion rate

**Alerts:**
- Failed payment processing
- Unusual churn spike
- Proration calculation errors
- Factory validation failures

---

**Version:** 1.0
**Date:** 2026-01-08
**Status:** REFERENCE ARCHITECTURE
**Compliance:** ISO/IEC/IEEE 26515:2018 (DDD), ISO 27001:2013 (Security)
