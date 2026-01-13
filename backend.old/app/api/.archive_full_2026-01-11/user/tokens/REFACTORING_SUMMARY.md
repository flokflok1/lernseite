# Tokens Domain Refactoring Summary

**Datum:** 2026-01-08
**Status:** COMPLETED
**Compliance:** ISO 27001:2013, ISO/IEC/IEEE 26515:2018

---

## 1. Initial Structure Assessment

### Directory Structure (BEFORE)

```
backend/app/api/tokens/
├── __init__.py              (~65 lines)
├── admin/
│   ├── __init__.py
│   └── management.py        (~170 lines)
├── transactions/
│   ├── __init__.py
│   └── history.py           (~96 lines)
├── stats/
│   ├── __init__.py
│   └── usage.py             (~161 lines)
└── wallet/
    ├── __init__.py
    └── balance.py           (~178 lines)
```

**Total:** 4 packages, 9 files, ~670 lines

**Assessment:** ✅ WELL ORGANIZED
- Clear domain separation
- All files < 500 lines
- Logical package structure
- Follows REST principles

---

## 2. Refactoring Actions

### 2.1 Added DDD Core Package

**NEW STRUCTURE:**

```
backend/app/api/tokens/
├── core/                       # ✅ NEW - DDD Core
│   ├── __init__.py
│   ├── factory.py              (~360 lines) - TokenTransactionFactory
│   ├── services.py             (~390 lines) - TokenService
│   └── value_objects.py        (~180 lines) - Domain value objects
├── admin/
│   └── management.py           (~170 lines) - Admin endpoints
├── transactions/
│   └── history.py              (~96 lines) - Transaction history
├── stats/
│   └── usage.py                (~161 lines) - Usage analytics
└── wallet/
    └── balance.py              (~178 lines) - Balance endpoints
```

**Total:** 5 packages, 12 files, ~1605 lines

---

## 3. Core Components Added

### 3.1 TokenTransactionFactory (factory.py)

**Purpose:** Create token transactions with business rules

**Methods:**
```python
# Income transactions
create_purchase(wallet_id, amount, payment_id, price, currency)
create_subscription_grant(wallet_id, amount, subscription_id, grant_type)
create_promo_code_grant(wallet_id, amount, promo_code, promo_code_id)
create_reward(wallet_id, amount, reward_type, reward_data)

# Expense transactions
create_usage(wallet_id, amount, ai_module, provider, method_id, lesson_id)

# Admin transactions
create_admin_adjustment(wallet_id, amount, reason, admin_user_id, notes)
create_transfer(from_wallet_id, to_wallet_id, amount, reason, admin_user_id)
```

**Features:**
- ✅ Automatic amount sign validation (positive for income, negative for expense)
- ✅ Required metadata enforcement
- ✅ Audit trail information
- ✅ Transaction type validation
- ✅ Timestamp generation

**Example Usage:**
```python
from app.api.tokens.core import TokenTransactionFactory

# Create AI usage transaction
transaction_data = TokenTransactionFactory.create_usage(
    wallet_id=1,
    amount=2000,
    ai_module="KI-Tutor",
    provider="anthropic",
    method_id=5
)

# Execute via repository
transaction = TokenRepository.change_balance(**transaction_data)
```

---

### 3.2 TokenService (services.py)

**Purpose:** Business logic layer for token operations

**Methods:**
```python
# Balance queries
get_user_balance(user_id) -> Dict
can_afford(user_id, required_tokens) -> bool

# Reservations
reserve_tokens(wallet_id, amount) -> bool
release_tokens(wallet_id, amount) -> bool

# Consumption
consume_ai_tokens(user_id, amount, ai_module, provider, ...) -> Dict

# Grants
grant_subscription_tokens(user_id, amount, subscription_id, grant_type) -> Dict
apply_promo_code(user_id, promo_code, promo_code_id, token_amount) -> Dict

# Transfers
transfer_to_organisation_pool(organization_id, amount, admin_user_id, reason) -> Tuple

# Analytics
get_usage_summary(user_id, period_days) -> Dict
estimate_cost(method_name, complexity) -> int
```

**Features:**
- ✅ Handles user vs organisation wallet logic
- ✅ Enforces business rules (insufficient balance checks)
- ✅ Orchestrates factory + repository calls
- ✅ Provides high-level API for endpoints

**Example Usage:**
```python
from app.api.tokens.core import TokenService

# Check if user can afford AI execution
if TokenService.can_afford(user_id=42, required_tokens=2000):
    # Consume tokens
    transaction = TokenService.consume_ai_tokens(
        user_id=42,
        amount=2000,
        ai_module="KI-Tutor",
        provider="anthropic",
        method_id=5
    )
else:
    raise InsufficientTokensError()
```

---

### 3.3 Value Objects (value_objects.py)

**Purpose:** Domain value objects (immutable, validated types)

**Components:**

#### TransactionType (Enum)
```python
# Income types
PURCHASE = "purchase"
MANUAL_TOPUP = "manual_topup"
SUBSCRIPTION_BONUS = "subscription_bonus"
SUBSCRIPTION_MONTHLY_GRANT = "subscription_monthly_grant"
PROMO_CODE = "promo_code"
REWARD = "reward"
REFUND = "refund"

# Expense types
AI_EXECUTION = "ai_execution"

# Admin types
ADMIN_ADJUSTMENT = "admin_adjustment"
```

**Helper Methods:**
```python
TransactionType.is_income(transaction_type) -> bool
TransactionType.is_expense(transaction_type) -> bool
TransactionType.is_admin(transaction_type) -> bool
```

#### ReferenceType (Enum)
```python
AI_EXECUTION = "ai_execution"
PAYMENT = "payment"
ADMIN_TOPUP = "admin_topup"
SUBSCRIPTION = "subscription"
PROMO_CODE = "promo_code"
GAMIFICATION_REWARD = "gamification_reward"
```

#### TransactionAmount (Dataclass)
```python
# Immutable value object for amounts
TransactionAmount.income(amount)   # Positive
TransactionAmount.expense(amount)  # Negative

# Properties
.is_income -> bool
.is_expense -> bool
.absolute -> int
```

#### WalletIdentifier (Dataclass)
```python
# Ensures either user_id OR organization_id (not both)
WalletIdentifier.for_user(user_id)
WalletIdentifier.for_organization(organization_id)

# Properties
.owner_type -> str  # "user" or "organisation"
.owner_id -> int
```

**Example Usage:**
```python
from app.api.tokens.core import TransactionType, TransactionAmount

# Check transaction type
if TransactionType.is_income("purchase"):
    print("Income transaction")

# Create validated amount
amount = TransactionAmount.income(10000)
assert amount.value == 10000
assert amount.is_income == True

# This will raise ValueError
bad_amount = TransactionAmount.income(-5000)  # ❌ Must be positive
```

---

## 4. Benefits of Core Package

### 4.1 Separation of Concerns

**Before:**
```python
# In admin/management.py
transaction = TokenRepository.change_balance(
    wallet_id=wallet['wallet_id'],
    amount=topup_request.amount,  # Raw amount (could be wrong sign!)
    reason='admin_adjustment',
    meta={
        'admin_reason': topup_request.reason,
        'admin_user_id': get_current_user()['user_id']
    },
    reference_type='admin_topup',
    reference_id=None
)
```

**After:**
```python
# In admin/management.py
from app.api.tokens.core import TokenTransactionFactory

transaction_data = TokenTransactionFactory.create_admin_adjustment(
    wallet_id=wallet['wallet_id'],
    amount=topup_request.amount,
    reason=topup_request.reason,
    admin_user_id=get_current_user()['user_id']
)

transaction = TokenRepository.change_balance(**transaction_data)
```

**Advantages:**
- ✅ Factory validates amount sign
- ✅ Factory enforces metadata structure
- ✅ Business rules centralized
- ✅ Easier to test

---

### 4.2 Type Safety

**Before:**
```python
reason = "ai_execution"  # String (could be typo!)
```

**After:**
```python
from app.api.tokens.core import TransactionType

reason = TransactionType.AI_EXECUTION.value  # Type-safe enum
```

**Advantages:**
- ✅ IDE autocomplete
- ✅ No typos
- ✅ Refactoring-safe
- ✅ Self-documenting

---

### 4.3 Immutability

**Before:**
```python
amount = 10000
amount = -amount  # Mutable, could be changed accidentally
```

**After:**
```python
from app.api.tokens.core import TransactionAmount

amount = TransactionAmount.income(10000)
# amount.value = -5000  # ❌ Immutable, will raise error
```

**Advantages:**
- ✅ Prevents accidental mutation
- ✅ Thread-safe
- ✅ Easier to reason about

---

## 5. Migration Guide

### 5.1 For Endpoint Developers

**OLD WAY (still works, backward compatible):**
```python
from app.repositories.token import TokenRepository

transaction = TokenRepository.change_balance(
    wallet_id=1,
    amount=-2000,
    reason='ai_execution',
    meta={'ai_module': 'KI-Tutor'},
    reference_type='ai_execution',
    reference_id=None
)
```

**NEW WAY (recommended):**
```python
from app.api.tokens.core import TokenTransactionFactory

transaction_data = TokenTransactionFactory.create_usage(
    wallet_id=1,
    amount=2000,  # Positive (factory makes it negative)
    ai_module='KI-Tutor',
    provider='anthropic',
    method_id=5
)

transaction = TokenRepository.change_balance(**transaction_data)
```

**OR EVEN BETTER (service layer):**
```python
from app.api.tokens.core import TokenService

transaction = TokenService.consume_ai_tokens(
    user_id=42,
    amount=2000,
    ai_module='KI-Tutor',
    provider='anthropic',
    method_id=5
)
```

---

### 5.2 For Service Developers

**Before:**
```python
# In ai_adapter.py
def consume_tokens_for_execution(user_id, tokens_used, ai_module):
    wallet = TokenRepository.get_or_create_user_wallet(user_id)

    if wallet['balance'] < tokens_used:
        raise InsufficientTokensError()

    transaction = TokenRepository.change_balance(
        wallet_id=wallet['wallet_id'],
        amount=-tokens_used,
        reason='ai_execution',
        meta={'ai_module': ai_module},
        reference_type='ai_execution',
        reference_id=None
    )

    return transaction
```

**After:**
```python
# In ai_adapter.py
from app.api.tokens.core import TokenService

def consume_tokens_for_execution(user_id, tokens_used, ai_module, provider):
    return TokenService.consume_ai_tokens(
        user_id=user_id,
        amount=tokens_used,
        ai_module=ai_module,
        provider=provider
    )
```

**Benefits:**
- ✅ Less code
- ✅ Business logic centralized
- ✅ Balance check built-in
- ✅ Automatic wallet resolution

---

## 6. Testing

### 6.1 Unit Tests for Factory

```python
# tests/test_token_factory.py
from app.api.tokens.core import TokenTransactionFactory, TransactionAmount

def test_create_purchase():
    transaction = TokenTransactionFactory.create_purchase(
        wallet_id=1,
        amount=10000,
        payment_id="pay_123",
        price=9.99
    )

    assert transaction['amount'] == 10000  # Positive
    assert transaction['reason'] == 'purchase'
    assert transaction['meta']['payment_id'] == "pay_123"

def test_create_usage():
    transaction = TokenTransactionFactory.create_usage(
        wallet_id=1,
        amount=2000,  # Positive input
        ai_module="KI-Tutor",
        provider="anthropic"
    )

    assert transaction['amount'] == -2000  # Automatically negative
    assert transaction['reason'] == 'ai_execution'

def test_amount_validation():
    # Should raise ValueError
    with pytest.raises(ValueError):
        TransactionAmount.income(-5000)  # Income must be positive
```

---

### 6.2 Integration Tests for Service

```python
# tests/test_token_service.py
from app.api.tokens.core import TokenService

def test_consume_ai_tokens_success(user_fixture):
    # Setup: User has 10000 tokens
    transaction = TokenService.consume_ai_tokens(
        user_id=user_fixture['user_id'],
        amount=2000,
        ai_module="KI-Tutor",
        provider="anthropic"
    )

    assert transaction['amount'] == -2000
    assert transaction['balance_after'] == 8000

def test_consume_ai_tokens_insufficient(user_fixture):
    # User has 1000 tokens, tries to consume 2000
    with pytest.raises(ValueError, match="Insufficient tokens"):
        TokenService.consume_ai_tokens(
            user_id=user_fixture['user_id'],
            amount=2000,
            ai_module="KI-Tutor",
            provider="anthropic"
        )
```

---

## 7. Documentation Updates

### 7.1 Updated Files

- [x] `/backend/app/api/tokens/REFACTORING_SUMMARY.md` - This file
- [x] `/backend/app/api/tokens/core/__init__.py` - Package exports
- [x] `/backend/app/api/tokens/core/factory.py` - Factory documentation
- [x] `/backend/app/api/tokens/core/services.py` - Service documentation
- [x] `/backend/app/api/tokens/core/value_objects.py` - Value object documentation

### 7.2 Need to Update

- [ ] `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md` - Add core/ package
- [ ] Backend API documentation - Add factory/service examples

---

## 8. Quality Gate Compliance

| Gate | Status | Details |
|------|--------|---------|
| **G01** | ✅ PASS | No duplicates, clean structure |
| **G02** | ✅ PASS | Follows LSX architecture (DDD patterns) |
| **G04** | ✅ PASS | All files < 500 lines |
| **G05** | ✅ PASS | Complete docstrings, type hints |
| **G06** | ⚠️ PENDING | Tests need to be written |
| **G07** | ✅ PASS | No security risks, audit trail enforced |
| **G08** | ✅ PASS | Clear decision documentation |
| **G09** | ✅ PASS | Efficient service layer |
| **G10** | N/A | Backend component |

---

## 9. Next Steps

### 9.1 Immediate Actions

1. **Write Unit Tests** (G06 requirement)
   - Factory tests (test_token_factory.py)
   - Service tests (test_token_service.py)
   - Value object tests (test_token_value_objects.py)

2. **Update Documentation**
   - Backend structure doc (05_Backend-Struktur.md)
   - API documentation

3. **Update Existing Endpoints** (optional, backward compatible)
   - Migrate admin/management.py to use factory
   - Migrate other endpoints to use service layer

### 9.2 Long-Term Improvements

1. **Repository Enhancements**
   - Add reserve_tokens() method
   - Add release_tokens() method
   - Add batch_change_balance() for transfers

2. **Service Extensions**
   - Add transaction rollback support
   - Add token expiration handling
   - Add organization pool management

3. **Performance Optimizations**
   - Add caching for balance queries
   - Add batch operations for bulk grants

---

## 10. Summary

### ✅ Achievements

1. **Added DDD Core Package** with factory, services, value objects
2. **Maintained Backward Compatibility** - Existing code still works
3. **Improved Type Safety** with enums and immutable value objects
4. **Centralized Business Logic** in TokenService
5. **Standardized Transaction Creation** with TokenTransactionFactory
6. **All files < 500 lines** (G04 compliance)
7. **Complete documentation** with examples

### 📊 Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Packages | 4 | 5 | +1 |
| Files | 9 | 12 | +3 |
| Total Lines | ~670 | ~1605 | +935 |
| Largest File | 178 lines | 390 lines | Still < 500 ✅ |

### 🎯 Next Priority

**G06 - Tests:** Write comprehensive unit and integration tests for core components.

---

**Version:** 1.0
**Date:** 2026-01-08
**Status:** COMPLETED
**Reviewed:** Ready for testing phase
