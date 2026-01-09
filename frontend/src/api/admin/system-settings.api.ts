/**
 * LernsystemX Admin API - System Settings
 *
 * API client for system settings operations.
 */

import http from '../http'

// ============================================================================
// Types
// ============================================================================

export interface SystemStatus {
  environment: 'development' | 'production'
  debug_enabled: boolean
  maintenance_mode: boolean
  uptime_seconds: number
  version: string
  database_connected: boolean
  redis_connected: boolean
  timestamp: string
}

export interface SwitchModeRequest {
  mode: 'development' | 'production'
}

export interface SwitchModeResponse {
  success: boolean
  message: string
  previous_environment: string
  new_environment: string
  requires_restart: boolean
  restart_instructions: string
}

export interface MaintenanceModeRequest {
  enabled: boolean
  message?: string
}

export interface MaintenanceModeResponse {
  success: boolean
  message: string
  maintenance_enabled: boolean
  maintenance_message: string
  debug_auto_enabled: boolean
}

export interface Setting {
  setting_id: number
  key: string
  value: any
  value_type: 'string' | 'number' | 'boolean' | 'json'
  category: string
  description?: string
  editable: boolean
  encrypted: boolean
  created_at: string
  updated_at: string
}

export interface UpdateSettingRequest {
  value: string
  value_type?: 'string' | 'number' | 'boolean' | 'json'
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get current system status
 */
export async function getSystemStatus(): Promise<SystemStatus> {
  const response = await http.get<{ success: boolean; status: SystemStatus }>(
    '/admin/system/status'
  )
  return response.data.status
}

/**
 * Switch system environment mode
 */
export async function switchSystemMode(
  request: SwitchModeRequest
): Promise<SwitchModeResponse> {
  const response = await http.post<SwitchModeResponse>(
    '/admin/system/mode',
    request
  )
  return response.data
}

/**
 * Toggle maintenance mode
 */
export async function toggleMaintenanceMode(
  request: MaintenanceModeRequest
): Promise<MaintenanceModeResponse> {
  const response = await http.post<MaintenanceModeResponse>(
    '/admin/system/maintenance',
    request
  )
  return response.data
}

/**
 * Get all system settings
 */
export async function getAllSettings(category?: string): Promise<Setting[]> {
  const response = await http.get<{ success: boolean; settings: Setting[] }>(
    '/admin/system/settings',
    { params: { category } }
  )
  return response.data.settings
}

/**
 * Get single setting by key
 */
export async function getSetting(key: string): Promise<Setting> {
  const response = await http.get<{ success: boolean; setting: Setting }>(
    `/admin/system/settings/${key}`
  )
  return response.data.setting
}

/**
 * Update setting value
 */
export async function updateSetting(
  key: string,
  request: UpdateSettingRequest
): Promise<Setting> {
  const response = await http.patch<{ success: boolean; setting: Setting }>(
    `/admin/system/settings/${key}`,
    request
  )
  return response.data.setting
}
