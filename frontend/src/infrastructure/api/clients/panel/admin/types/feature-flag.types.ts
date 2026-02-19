/**
 * Admin API - Feature Flag & Rollout Types
 *
 * Types for feature flag management and gradual rollout planning.
 */

export interface FeatureFlag {
  feature_id: string
  feature_name: string
  feature_code: string
  description?: string | null
  category: string
  is_enabled: boolean
  rollout_percentage: number
  tier_required?: string | null
  max_daily_quota?: number | null
  max_monthly_quota?: number | null
  disabled_reason?: string | null
  created_by?: string | null
  updated_by?: string | null
  created_at: string
  updated_at?: string | null
}

export interface FeatureFlagCreateRequest {
  feature_name: string
  feature_code: string
  description?: string
  category: string
  is_enabled?: boolean
  tier_required?: string
  max_daily_quota?: number
  max_monthly_quota?: number
}

export interface FeatureFlagUpdateRequest {
  feature_name?: string
  description?: string
  category?: string
  is_enabled?: boolean
  tier_required?: string
  max_daily_quota?: number
  max_monthly_quota?: number
}

export interface FeatureFlagFilters {
  limit?: number
  offset?: number
  enabled?: boolean
  category?: string
}

export interface RolloutPhase {
  phase: number
  percentage: number
  description: string
  started_at?: string
  completed_at?: string
}

export interface RolloutPlan {
  plan_id: string
  feature_name: string
  feature_id: string
  description?: string | null
  status: 'planned' | 'active' | 'paused' | 'completed' | 'rolled_back'
  current_percentage: number
  target_percentage: number
  phases: RolloutPhase[]
  paused_reason?: string | null
  started_at?: string | null
  estimated_end_date?: string | null
  completed_at?: string | null
  rolled_back_at?: string | null
  rolled_back_reason?: string | null
  created_by?: string | null
  updated_by?: string | null
  created_at: string
  updated_at?: string | null
}
