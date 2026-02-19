/**
 * Learning Methods Plugin Types
 *
 * Type definitions for the LM Plugin System.
 */

export type ApprovalStatus = 'pending_review' | 'approved' | 'rejected' | 'in_revision' | 'deprecated'
export type GroupCode = 'A' | 'B' | 'C'
export type Tier = 'basic' | 'premium' | 'pro'
export type KIUsage = 'intensive' | 'medium' | 'optional'

/**
 * JSON Schema v7 for plugin configuration validation
 */
export interface JSONSchema7 {
  type: string
  properties?: Record<string, any>
  required?: string[]
  [key: string]: any
}

/**
 * Plugin metadata from database
 */
export interface LMPluginMetadata {
  plugin_id: string
  plugin_code: string
  name: string
  description?: string
  group_code: GroupCode
  tier: Tier
  ki_usage: KIUsage
  icon: string

  config_schema: JSONSchema7
  default_config?: Record<string, any>

  approval_status: ApprovalStatus
  is_active: boolean

  file_path: string
  file_hash: string

  agent_support?: Record<string, any>
  prompt_template?: string

  submitted_by?: string
  submitted_at?: string
  reviewed_by?: string
  reviewed_at?: string
  activated_at?: string

  created_at: string
  updated_at: string
}

/**
 * Plugin approval action request
 */
export interface LMPluginApprovalAction {
  plugin_id: string
  reason?: string
}

/**
 * Scan plugins response
 */
export interface ScanPluginsResponse {
  discovered_count: number
  registered_count: number
  registered_ids: string[]
}

/**
 * API Response wrapper
 */
export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
  }
}
