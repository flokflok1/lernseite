/**
 * Admin API - User Management Types
 *
 * Types for user administration operations:
 * banning, token grants, creator verification, and audit logs.
 */

export interface BanUserRequest {
  reason: string
  duration_days?: number
  permanent: boolean
  notify_user: boolean
}

export interface UnbanUserRequest {
  reason: string
}

export interface GrantTokensRequest {
  amount: number
  reason: string
}

export interface VerifyCreatorRequest {
  verified: boolean
  reason: string
}

export interface AuditLog {
  log_id: number
  user_id?: number | null
  user_email?: string | null
  user_role?: string | null
  action: string
  event_category?: string | null
  resource_type?: string | null
  resource_id?: number | null
  description?: string | null
  ip_address?: string | null
  user_agent?: string | null
  session_id?: string | null
  success: boolean
  error_message?: string | null
  created_at: string
  meta?: Record<string, unknown>
}

export interface AuditLogsFilterParams {
  page?: number
  limit?: number
  user_id?: number
  action?: string
  event_category?: string
  from?: string
  to?: string
  success?: boolean
}
