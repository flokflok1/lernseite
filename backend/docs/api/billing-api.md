# LernsystemX Billing API Documentation

**Version:** 1.0.0
**Standard:** ISO/IEC/IEEE 26515:2018 - API Documentation
**Compliance:** ISO 27001:2013 - Billing and Payment Security
**Last Updated:** 2025-11-16

## Overview

The Billing API manages subscription plans, token wallets, and payment operations for LernsystemX. It provides comprehensive subscription management, token-based billing for AI features, and analytics for both users and administrators.

### Key Features

- **Subscription Management:** 6 subscription plans (Free, Premium, Creator, Teacher, School, Company)
- **Token-Based Billing:** Pay-per-use AI consumption with wallet system
- **Multi-Tenancy:** User and organisation wallet support
- **Transaction Safety:** ACID-compliant token transactions
- **Monthly Token Grants:** Automatic monthly token allocation
- **Analytics:** MRR, ARR, usage statistics, and reporting

### Base URL

```
http://localhost:5000/api/v1
```

---

## Authentication

- **Public Endpoints:** GET /subscriptions/plans
- **Authenticated Endpoints:** All other endpoints require JWT token
- **Admin Endpoints:** Stats and manual top-up endpoints require admin role

### Headers

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## Subscription Plans

### 1. Free Plan
```json
{
  "tier": "free",
  "monthly_price_eur": 0.00,
  "included_tokens": 0,
  "features": {
    "learning_methods": 11,
    "ai_access": false,
    "course_creation": false
  }
}
```

### 2. Premium Plan
```json
{
  "tier": "premium",
  "monthly_price_eur": 14.99,
  "yearly_price_eur": 129.99,
  "included_tokens": 10000,
  "features": {
    "learning_methods": 21,
    "ai_access": true,
    "course_creation": true,
    "community_publishing": true,
    "liveroom": "basic"
  }
}
```

### 3. Creator Plan
```json
{
  "tier": "pro",
  "monthly_price_eur": 29.99,
  "yearly_price_eur": 299.99,
  "included_tokens": 20000,
  "features": {
    "learning_methods": 21,
    "ai_access": true,
    "marketplace": true,
    "revenue_share": 75,
    "global_publishing": true
  }
}
```

### 4. Teacher Plan
```json
{
  "tier": "pro",
  "monthly_price_eur": 39.99,
  "yearly_price_eur": 399.99,
  "included_tokens": 30000,
  "features": {
    "learning_methods": 21,
    "ai_access": true,
    "class_management": true,
    "liveroom": "pro",
    "exam_management": true
  }
}
```

### 5. School Plan (Enterprise)
```json
{
  "tier": "enterprise",
  "monthly_price_eur": null,
  "included_tokens": null,
  "features": {
    "organisation_management": true,
    "sso": true,
    "custom_domain": true,
    "priority_support": true
  }
}
```

### 6. Company Plan (Enterprise)
```json
{
  "tier": "enterprise",
  "monthly_price_eur": null,
  "included_tokens": null,
  "features": {
    "organisation_management": true,
    "scorm_support": true,
    "compliance_reporting": true
  }
}
```

---

## Subscription Endpoints

### 1. List Subscription Plans

Get all available subscription plans.

**Endpoint:** `GET /subscriptions/plans`

**Authentication:** None (public)

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| active_only | boolean | No | true | Only return active plans |

**Example Request:**
```http
GET /api/v1/subscriptions/plans?active_only=true
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "plans": [
    {
      "plan_id": 1,
      "name": "free",
      "tier": "free",
      "monthly_price_eur": 0.00,
      "yearly_price_eur": 0.00,
      "included_tokens": 0,
      "features": {
        "learning_methods": 11,
        "ai_access": false
      },
      "active": true,
      "created_at": "2025-01-01T00:00:00"
    },
    {
      "plan_id": 2,
      "name": "premium",
      "tier": "premium",
      "monthly_price_eur": 14.99,
      "yearly_price_eur": 129.99,
      "included_tokens": 10000,
      "features": {
        "learning_methods": 21,
        "ai_access": true,
        "course_creation": true
      },
      "active": true
    }
  ],
  "total": 6
}
```

---

### 2. Get My Subscription

Get current user's subscription details.

**Endpoint:** `GET /subscriptions/me`

**Authentication:** Required (JWT)

**Example Request:**
```http
GET /api/v1/subscriptions/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "plan": "premium",
  "tier": "premium",
  "features": {
    "ai_access": true,
    "learning_methods": 21,
    "course_creation": true
  },
  "source": "user",
  "subscription": {
    "subscription_id": 123,
    "plan_name": "premium",
    "status": "active",
    "billing_cycle": "monthly",
    "started_at": "2025-01-01T00:00:00",
    "expires_at": "2025-02-01T00:00:00",
    "auto_renew": true
  }
}
```

**Response (200 OK - Free Plan):**
```json
{
  "success": true,
  "plan": "free",
  "tier": "free",
  "features": {
    "ai_access": false,
    "learning_methods": 11
  },
  "source": "default",
  "subscription": null,
  "message": "No active subscription. You are on the free plan."
}
```

---

### 3. Change Subscription

Change to a different subscription plan.

**Endpoint:** `POST /subscriptions/change`

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "new_plan_id": 3,
  "reason": "Upgrade to Creator plan",
  "prorate": true
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| new_plan_id | integer | Yes | ID of new subscription plan |
| reason | string | No | Reason for plan change |
| prorate | boolean | No | Prorate the plan change (default: true) |

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Subscription changed to creator plan",
  "subscription": {
    "subscription_id": 123,
    "plan_name": "creator",
    "tier": "pro",
    "status": "active",
    "billing_cycle": "monthly",
    "started_at": "2025-01-01T00:00:00",
    "expires_at": "2025-02-01T00:00:00"
  }
}
```

**Error Response (403 Forbidden - Organisation Subscription):**
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Your subscription is managed by your organisation. Contact your organisation admin to change plans."
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Same plan",
  "message": "You are already on this plan"
}
```

---

### 4. Cancel Subscription

Cancel current subscription.

**Endpoint:** `POST /subscriptions/cancel`

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "reason": "Too expensive",
  "immediate": false,
  "feedback": "Would reconsider if price was lower"
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| reason | string | No | Cancellation reason |
| immediate | boolean | No | Cancel immediately vs. end of period (default: false) |
| feedback | string | No | User feedback (max 1000 chars) |

**Example Response (200 OK - End of Period):**
```json
{
  "success": true,
  "message": "Your subscription will be cancelled at the end of the billing period (2025-02-01T00:00:00). You can continue using premium features until then.",
  "cancelled_at": "2025-01-15T10:30:00",
  "expires_at": "2025-02-01T00:00:00"
}
```

**Example Response (200 OK - Immediate):**
```json
{
  "success": true,
  "message": "Your subscription has been cancelled immediately. You no longer have access to premium features.",
  "cancelled_at": "2025-01-15T10:30:00",
  "expires_at": "2025-01-15T10:30:00"
}
```

---

### 5. Reactivate Subscription

Reactivate a cancelled subscription.

**Endpoint:** `POST /subscriptions/reactivate`

**Authentication:** Required (JWT)

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Your subscription has been reactivated successfully",
  "subscription": {
    "status": "active",
    "auto_renew": true,
    "expires_at": "2025-02-01T00:00:00"
  }
}
```

**Error Response (400 Bad Request - Expired):**
```json
{
  "success": false,
  "error": "Expired",
  "message": "Subscription has expired and cannot be reactivated. Please create a new subscription."
}
```

---

### 6. Get Subscription Statistics (Admin)

Get subscription statistics including MRR and ARR.

**Endpoint:** `GET /subscriptions/stats`

**Authentication:** Required (JWT + Admin role)

**Example Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "total_subscribers": 1523,
    "active_subscribers": 1342,
    "trial_subscribers": 54,
    "cancelled_subscribers": 127,
    "expired_subscribers": 0,
    "by_plan": {
      "free": 500,
      "premium": 800,
      "creator": 42
    },
    "by_status": {
      "active": 1342,
      "trial": 54,
      "cancelled": 127,
      "expired": 0
    },
    "mrr": 18950.58,
    "arr": 227406.96
  }
}
```

---

## Token Endpoints

### 1. Get My Token Balance

Get current user's token wallet balance.

**Endpoint:** `GET /tokens/me`

**Authentication:** Required (JWT)

**Example Response (200 OK):**
```json
{
  "success": true,
  "wallet": {
    "wallet_id": 1,
    "balance": 8500,
    "reserved": 1500,
    "total_purchased": 20000,
    "total_granted": 10000,
    "total_consumed": 21500,
    "monthly_grant_amount": 10000,
    "last_grant_date": "2025-01-01",
    "created_at": "2025-01-01T00:00:00"
  },
  "balance": {
    "wallet_id": 1,
    "balance": 8500,
    "reserved": 1500,
    "available": 7000,
    "source": "user",
    "monthly_grant": 10000
  }
}
```

---

### 2. Get Token Transactions

Get token transaction history.

**Endpoint:** `GET /tokens/transactions`

**Authentication:** Required (JWT)

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 50 | Max transactions (max: 100) |
| offset | integer | No | 0 | Pagination offset |

**Example Request:**
```http
GET /api/v1/tokens/transactions?limit=20&offset=0
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "transactions": [
    {
      "transaction_id": 12345,
      "amount": -2000,
      "balance_after": 8500,
      "reason": "ai_execution",
      "description": "KI-Tutor execution",
      "ai_module": "KI-Tutor",
      "created_at": "2025-01-15T10:30:00"
    },
    {
      "transaction_id": 12344,
      "amount": 10000,
      "balance_after": 10500,
      "reason": "subscription_monthly_grant",
      "description": "Monthly subscription token grant",
      "created_at": "2025-01-01T00:00:00"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

---

### 3. Get Token Usage Statistics

Get token usage analytics.

**Endpoint:** `GET /tokens/usage`

**Authentication:** Required (JWT)

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| period_days | integer | No | 30 | Statistics period in days |

**Example Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "user_id": 42,
    "current_balance": 8500,
    "total_tokens_used": 15000,
    "total_tokens_bought": 20000,
    "total_tokens_granted": 10000,
    "by_reason": {
      "ai_execution": 15000
    },
    "by_method": {
      "KI-Tutor": 8000,
      "KI-Glossar": 7000
    },
    "period_start": "2024-12-16T00:00:00",
    "period_end": "2025-01-15T00:00:00"
  },
  "period_days": 30
}
```

---

### 4. Estimate AI Cost

Estimate token cost for an AI method.

**Endpoint:** `POST /tokens/estimate`

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "method_name": "KI-Tutor",
  "complexity": "medium"
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| method_name | string | Yes | Learning method name |
| complexity | string | No | Complexity (simple, medium, complex) |

**Example Response (200 OK):**
```json
{
  "success": true,
  "estimate": {
    "method_name": "KI-Tutor",
    "complexity": "medium",
    "estimated_tokens": 500,
    "can_afford": true,
    "current_balance": 8500
  }
}
```

---

### 5. Get Organisation Tokens (Org Admin)

Get organisation token balance.

**Endpoint:** `GET /tokens/organisation/:id`

**Authentication:** Required (JWT + Org Admin)

**Example Response (200 OK):**
```json
{
  "success": true,
  "wallet": {
    "wallet_id": 10,
    "balance": 150000,
    "reserved": 5000,
    "total_purchased": 0,
    "total_granted": 200000,
    "total_consumed": 45000,
    "monthly_grant_amount": 50000
  },
  "stats": {
    "organisation_id": 5,
    "current_balance": 150000,
    "total_tokens_used": 45000,
    "by_reason": {
      "ai_execution": 45000
    }
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Only organisation admins can view organisation token balance"
}
```

---

### 6. Manual Token Top-Up (Admin)

Manually add or deduct tokens from user/organisation wallets.

**Endpoint:** `POST /tokens/manual-topup`

**Authentication:** Required (JWT + Admin role)

**Request Body:**
```json
{
  "user_id": 42,
  "amount": 5000,
  "reason": "Support compensation for service outage"
}
```

**Alternative for Organisation:**
```json
{
  "organisation_id": 10,
  "amount": 50000,
  "reason": "Enterprise plan initial grant"
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | integer | Conditional | User ID (required if no organisation_id) |
| organisation_id | integer | Conditional | Organisation ID (required if no user_id) |
| amount | integer | Yes | Token amount (positive = grant, negative = deduct) |
| reason | string | Yes | Reason for manual adjustment |

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Successfully added 5000 tokens",
  "transaction": {
    "transaction_id": 67890,
    "amount": 5000,
    "balance_after": 13500,
    "reason": "admin_adjustment",
    "created_at": "2025-01-15T11:00:00"
  },
  "new_balance": 13500,
  "target_type": "user",
  "target_id": 42
}
```

**Error Response (400 Bad Request - Insufficient Balance):**
```json
{
  "success": false,
  "error": "Invalid request",
  "message": "Insufficient balance: 8500 tokens, need 10000 tokens"
}
```

---

### 7. Get Global Token Statistics (Admin)

Get global token usage statistics.

**Endpoint:** `GET /tokens/stats`

**Authentication:** Required (JWT + Admin role)

**Example Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "total_wallets": 1523,
    "total_balance": 15234567,
    "total_purchased": 25000000,
    "total_granted": 10000000,
    "total_consumed": 19765433
  }
}
```

---

## Profile Integration

### 1. Get Profile Subscription

Get subscription info in user profile.

**Endpoint:** `GET /profile/subscription`

**Authentication:** Required (JWT)

**Example Response (200 OK):**
```json
{
  "success": true,
  "subscription": {
    "plan": "premium",
    "tier": "premium",
    "features": {
      "ai_access": true,
      "learning_methods": 21
    },
    "source": "user",
    "status": "active",
    "expires_at": "2025-02-01T00:00:00",
    "auto_renew": true,
    "billing_cycle": "monthly",
    "started_at": "2025-01-01T00:00:00"
  }
}
```

---

### 2. Get Profile Tokens

Get token balance in user profile.

**Endpoint:** `GET /profile/tokens`

**Authentication:** Required (JWT)

**Example Response (200 OK):**
```json
{
  "success": true,
  "tokens": {
    "balance": 8500,
    "reserved": 1500,
    "available": 7000,
    "total_purchased": 20000,
    "total_granted": 10000,
    "total_consumed": 21500,
    "monthly_grant": 10000,
    "last_grant_date": "2025-01-01T00:00:00",
    "source": "user"
  }
}
```

---

## AI Method Integration

When executing AI methods via `/learning-methods/:id/execute`, the billing system automatically:

1. **Pre-execution Check:**
   - Verifies user has active subscription with AI access
   - Estimates token cost based on method and complexity
   - Checks if user has sufficient token balance
   - Returns HTTP 402 (Payment Required) if insufficient tokens
   - Returns HTTP 403 (Forbidden) if no AI access in plan

2. **Post-execution Charging:**
   - Charges actual tokens used from wallet
   - Logs usage to ai_usage_logs table
   - Returns billing info in execution response

**Example AI Execution Response with Billing:**
```json
{
  "success": true,
  "execution": {
    "execution_id": 12345,
    "response": "...",
    "tokens_used": 2000,
    "provider": "openai",
    "model": "gpt-4",
    "billing": {
      "tokens_charged": 2000,
      "new_balance": 8500,
      "transaction_id": 67890
    }
  }
}
```

**Error Response (402 Payment Required):**
```json
{
  "success": false,
  "error": "Access denied",
  "reason": "Insufficient tokens. Available: 500, Required: 2000",
  "estimated_cost": 2000,
  "shortage": 1500,
  "upgrade_url": "/api/v1/subscriptions/plans"
}
```

**Error Response (403 Forbidden - No AI Access):**
```json
{
  "success": false,
  "error": "Access denied",
  "reason": "AI access not included in your plan. Upgrade to Premium or higher.",
  "required_tier": "premium",
  "user_tier": "free",
  "upgrade_url": "/api/v1/subscriptions/plans"
}
```

---

## Token Packages

Available token purchase packages:

| Package | Tokens | Price (EUR) | Discount |
|---------|--------|-------------|----------|
| Small | 5,000 | €5.99 | 0% |
| Medium | 10,000 | €9.99 | 16% |
| Large | 25,000 | €19.99 | 33% |
| XL | 50,000 | €34.99 | 42% |
| XXL | 100,000 | €59.99 | 50% |

---

## AI Method Token Costs

Estimated token costs by method (medium complexity):

| Method | Base Tokens | Simple | Medium | Complex |
|--------|-------------|--------|--------|---------|
| KI-Tutor | 500 | 250 | 500 | 1000 |
| KI-Glossar | 300 | 150 | 300 | 600 |
| Braindump | 800 | 400 | 800 | 1600 |
| KI-Quiz | 1000 | 500 | 1000 | 2000 |
| Deep Praxis | 2000 | 1000 | 2000 | 4000 |
| Deep Scenario | 2500 | 1250 | 2500 | 5000 |
| Whiteboard-KI | 600 | 300 | 600 | 1200 |
| PDF-Analyse | 400/page | 200 | 400 | 800 |
| Übersetzung | 300 | 150 | 300 | 600 |
| MindMap | 1000 | 500 | 1000 | 2000 |

---

## Error Codes

### HTTP Status Codes

- **200 OK** - Successful request
- **201 Created** - Resource created successfully
- **400 Bad Request** - Validation error or invalid request
- **401 Unauthorized** - Missing or invalid JWT token
- **402 Payment Required** - Insufficient tokens
- **403 Forbidden** - No AI access or insufficient permissions
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

### Error Response Format

```json
{
  "success": false,
  "error": "Error type",
  "message": "Human-readable error message",
  "details": "Additional error details"
}
```

---

## Security & Compliance

### ISO 27001:2013 Compliance

- **Access Control:** JWT-based authentication with role-based access
- **Data Protection:** Secure token transactions with ACID compliance
- **Audit Logging:** All transactions logged with timestamps
- **Payment Security:** No credit card data stored (Stripe integration)

### Transaction Safety

All token balance changes use database transactions:

```sql
BEGIN;
  -- Lock wallet
  SELECT * FROM token_wallets WHERE wallet_id = ? FOR UPDATE;
  -- Check balance
  -- Update balance
  -- Log transaction
COMMIT;
```

### Data Privacy

- User wallet data isolated per user/organisation
- No cross-wallet visibility
- Admin access logged and audited

---

## Rate Limiting

- **Public endpoints:** 100 requests/minute
- **Authenticated endpoints:** 500 requests/minute
- **Admin endpoints:** 1000 requests/minute

---

## Changelog

### Version 1.0.0 (2025-01-15)
- Initial release
- Subscription management endpoints
- Token wallet endpoints
- Profile integration
- AI method billing integration
- Admin statistics and manual top-up

---

## Support

For API support or questions:
- **Email:** api-support@lernsystemx.de
- **Documentation:** https://docs.lernsystemx.de
- **Status Page:** https://status.lernsystemx.de

---

**Document End**
