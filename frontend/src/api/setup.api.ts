/**
 * LernsystemX - Setup API Service
 *
 * API endpoints for the Setup Wizard
 */

import axios from 'axios'

// Create separate axios instance for setup (no auth required)
const setupHttp = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for setup operations
})

// Response Interfaces
export interface SetupStatusResponse {
  installed: boolean
  version: string | null
  requires_setup: boolean
  install_info: InstallInfo | null
}

export interface InstallInfo {
  version: string
  installed_at: string
  admin_email: string
  organisation_name: string
}

export interface SystemCheckResult {
  name: string
  status: 'ok' | 'error' | 'warning'
  message: string
  details?: string
}

export interface SystemCheckResponse {
  success: boolean
  can_proceed: boolean
  checks: SystemCheckResult[]
}

export interface DatabaseInitResponse {
  success: boolean
  database_created: boolean
  tables_created: number
  indexes_created: number
  errors?: string[]
}

export interface AdminCreateRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  enable_2fa?: boolean
}

export interface AdminCreateResponse {
  success: boolean
  user_id: string
  email: string
  recovery_codes?: string[]
  totp_secret?: string
  qr_code?: string
  message: string
}

export interface OrganisationCreateRequest {
  name: string
  org_type: 'system' | 'school' | 'company' | 'academy' | 'creator_org' | 'community'
  domain?: string
  language?: string
  region?: string
}

export interface OrganisationCreateResponse {
  success: boolean
  organisation_id: number
  name: string
  message: string
}

export interface AIConfigRequest {
  openai_api_key?: string
  anthropic_api_key?: string
  deepl_api_key?: string
}

export interface AIConfigResponse {
  success: boolean
  configured_providers: string[]
  message: string
}

export interface SeedDataRequest {
  seed_methods?: boolean
  seed_categories?: boolean
  seed_roles?: boolean
}

export interface SeedDataResponse {
  success: boolean
  learning_methods?: number
  categories?: number
  roles?: number
  message?: string
}

export interface SeedStatusResponse {
  success: boolean
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  progress: number
  message: string
}

export interface VerificationResponse {
  success: boolean
  checks: Array<{
    name: string
    status: 'ok' | 'error'
    message: string
  }>
  ready_for_use: boolean
}

export interface CompleteInstallationResponse {
  success: boolean
  message: string
  redirect_url: string
}

export interface EnvironmentInfoResponse {
  success: boolean
  env_file_exists: boolean
  env_file_path: string
  is_valid: boolean
  issues: string[]
  templates_available: {
    development: boolean
    production: boolean
  }
}

export interface EnvironmentConfigRequest {
  environment: 'development' | 'production'
  overwrite?: boolean
  custom_values?: Record<string, string>
}

export interface EnvironmentConfigResponse {
  success: boolean
  message: string
  environment: string
  error?: string
}

/**
 * Get setup/installation status
 */
export const getSetupStatus = async (): Promise<SetupStatusResponse> => {
  const response = await setupHttp.get<SetupStatusResponse>('/setup/status')
  return response.data
}

/**
 * Get environment configuration info
 */
export const getEnvironmentInfo = async (): Promise<EnvironmentInfoResponse> => {
  const response = await setupHttp.get<EnvironmentInfoResponse>('/setup/environment')
  return response.data
}

/**
 * Configure environment (create .env file)
 */
export const configureEnvironment = async (data: EnvironmentConfigRequest): Promise<EnvironmentConfigResponse> => {
  const response = await setupHttp.post<EnvironmentConfigResponse>('/setup/environment', data)
  return response.data
}

/**
 * Run system checks (Python, PostgreSQL, Redis, Ports)
 */
export const runSystemCheck = async (): Promise<SystemCheckResponse> => {
  const response = await setupHttp.post<SystemCheckResponse>('/setup/check', {})
  return response.data
}

/**
 * Initialize database schema
 */
export const initDatabase = async (): Promise<DatabaseInitResponse> => {
  const response = await setupHttp.post<DatabaseInitResponse>('/setup/database', {})
  return response.data
}

/**
 * Create admin user
 */
export const createAdmin = async (data: AdminCreateRequest): Promise<AdminCreateResponse> => {
  const response = await setupHttp.post<AdminCreateResponse>('/setup/admin', data)
  return response.data
}

/**
 * Create organisation
 */
export const createOrganisation = async (data: OrganisationCreateRequest): Promise<OrganisationCreateResponse> => {
  // Map org_type to type for backend compatibility
  const requestData = {
    name: data.name,
    type: data.org_type,
    domain: data.domain,
    language: data.language,
    region: data.region
  }
  const response = await setupHttp.post<OrganisationCreateResponse>('/setup/organisation', requestData)
  return response.data
}

/**
 * Configure AI API keys
 */
export const configureAI = async (data: AIConfigRequest): Promise<AIConfigResponse> => {
  const response = await setupHttp.post<AIConfigResponse>('/setup/ki-config', data)
  return response.data
}

/**
 * Seed initial data (learning methods, categories, roles)
 */
export const seedData = async (data?: SeedDataRequest): Promise<SeedDataResponse> => {
  const response = await setupHttp.post<SeedDataResponse>('/setup/seed', data || {}, {
    headers: { 'Content-Type': 'application/json' }
  })
  return response.data
}

/**
 * Get seed status (for polling)
 */
export const getSeedStatus = async (): Promise<SeedStatusResponse> => {
  const response = await setupHttp.get<SeedStatusResponse>('/setup/seed/status')
  return response.data
}

/**
 * Verify installation
 */
export const verifyInstallation = async (): Promise<VerificationResponse> => {
  const response = await setupHttp.get<VerificationResponse>('/setup/verify')
  return response.data
}

/**
 * Complete installation
 */
export const completeInstallation = async (): Promise<CompleteInstallationResponse> => {
  const response = await setupHttp.post<CompleteInstallationResponse>('/setup/complete', {})
  return response.data
}

/**
 * Get system information (optional)
 */
export const getSystemInfo = async (): Promise<any> => {
  const response = await setupHttp.get('/setup/system-info')
  return response.data
}
