/**
 * Type definitions for AI Settings page.
 *
 * Shared across the parent page, child components, and composables.
 */

export interface AIProvider {
  provider_id: number
  name: string
  display_name: string
  provider_type: string
  base_url: string | null
  api_version: string | null
  active: boolean
  priority: number
  rate_limit_per_minute: number
  config: Record<string, unknown> | null
  last_validated: string | null
  has_api_key: boolean
}

export interface TestResult {
  success: boolean
  message: string
  response_time?: number
}

export interface AIModel {
  model_id?: number
  name: string
  input_price: number
  output_price: number
}

export interface ProviderModels {
  display_name: string
  models: AIModel[]
}

