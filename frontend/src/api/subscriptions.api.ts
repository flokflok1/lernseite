import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface SubscriptionPlan {
  plan_id: number
  name: string
  tier: string
  monthly_price_eur: number
  yearly_price_eur: number
  included_tokens: number
  features: {
    ai_access: boolean
    learning_methods: number
    course_creation: boolean
    live_room: boolean
    max_courses?: number
    [key: string]: any
  }
  active: boolean
}

export interface SubscriptionResponse {
  subscription_id?: number
  plan: string
  tier: string
  status: 'active' | 'trial' | 'cancelled' | 'expired' | 'none'
  billing_cycle?: 'monthly' | 'yearly'
  started_at?: string
  expires_at?: string | null
  auto_renew: boolean
  features: {
    ai_access: boolean
    learning_methods: number
    course_creation: boolean
    [key: string]: any
  }
  source: 'user' | 'organisation' | 'default'
}

// ============================================================================
// Subscription API Functions
// ============================================================================

/**
 * Get all available subscription plans (public)
 */
export const getPlans = async (activeOnly = true): Promise<SubscriptionPlan[]> => {
  const response = await http.get<{ success: boolean; plans: SubscriptionPlan[] }>('/subscriptions/plans', {
    params: { active_only: activeOnly }
  })
  return response.data.plans
}

/**
 * Get current user's subscription
 */
export const getMySubscription = async (): Promise<SubscriptionResponse> => {
  const response = await http.get<{ success: boolean; subscription: SubscriptionResponse | null } & Partial<SubscriptionResponse>>('/subscriptions/me')

  // Handle case where subscription is null (free plan)
  if (response.data.subscription) {
    return response.data.subscription
  }

  // Return default free plan structure
  return {
    plan: response.data.plan || 'free',
    tier: response.data.tier || 'free',
    status: 'none',
    auto_renew: false,
    features: response.data.features || {
      ai_access: false,
      learning_methods: 11,
      course_creation: false
    },
    source: response.data.source || 'default'
  }
}

/**
 * Change subscription plan
 */
export const changeSubscription = async (newPlanId: number, reason?: string): Promise<SubscriptionResponse> => {
  const response = await http.post<{ success: boolean; subscription: SubscriptionResponse }>('/subscriptions/change', {
    new_plan_id: newPlanId,
    reason: reason || 'User requested plan change',
    prorate: true
  })
  return response.data.subscription
}

/**
 * Cancel subscription
 */
export const cancelSubscription = async (reason?: string, immediate = false, feedback?: string): Promise<{ cancelled_at: string; expires_at: string }> => {
  const response = await http.post<{ success: boolean; cancelled_at: string; expires_at: string }>('/subscriptions/cancel', {
    reason: reason || 'User requested cancellation',
    immediate,
    feedback
  })
  return {
    cancelled_at: response.data.cancelled_at,
    expires_at: response.data.expires_at
  }
}

/**
 * Reactivate cancelled subscription
 */
export const reactivateSubscription = async (): Promise<SubscriptionResponse> => {
  // Send empty object to ensure Content-Type header is set (required by API Gateway)
  const response = await http.post<{ success: boolean; subscription: SubscriptionResponse }>('/subscriptions/reactivate', {})
  return response.data.subscription
}
