/**
 * Admin User Management API
 */

import http from '@/infrastructure/api/http'
import type {
  AdminUser,
  UsersFilterParams,
  PaginatedResponse,
  AuditLog,
  AuditLogsFilterParams,
  BanUserRequest
} from '../types'

export const adminGetUsers = async (
  params: UsersFilterParams = {}
): Promise<PaginatedResponse<AdminUser>> => {
  const response = await http.get<{
    success: boolean
    items: AdminUser[]
    total: number
    page: number
    per_page: number
    total_pages: number
  }>('/users', { params })

  return {
    items: response.data.items,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.per_page,
    total_pages: response.data.total_pages
  }
}

export const adminGetUserDetail = async (userId: string): Promise<AdminUser> => {
  const response = await http.get<{
    success: boolean
    user: AdminUser
  }>(`/users/${userId}`)

  return response.data.user
}

export const adminUpdateUserRole = async (
  userId: string,
  role: string
): Promise<void> => {
  await http.patch(`/users/${userId}/role`, { role })
}

export const adminToggleUserActive = async (
  userId: string,
  isActive: boolean
): Promise<void> => {
  await http.patch(`/users/${userId}/status`, {
    is_active: isActive
  })
}

export const adminDeleteUser = async (userId: string): Promise<void> => {
  await http.delete(`/users/${userId}`)
}

export const adminBanUser = async (
  userId: string,
  data: BanUserRequest
): Promise<void> => {
  await http.post(`/users/${userId}/ban`, data)
}

export const adminUnbanUser = async (
  userId: string,
  reason: string
): Promise<void> => {
  await http.post(`/users/${userId}/unban`, { reason })
}

export const adminCreateUser = async (userData: {
  email: string
  password: string
  first_name: string
  last_name: string
  role: string
}): Promise<AdminUser> => {
  const response = await http.post<{
    success: boolean
    user: AdminUser
  }>('/users', userData)

  return response.data.user
}

export const adminGrantTokens = async (
  userId: string,
  amount: number,
  reason: string
): Promise<number> => {
  const response = await http.post<{
    success: boolean
    new_balance: number
  }>(`/users/${userId}/tokens/grant`, {
    amount,
    reason
  })

  return response.data.new_balance
}

export const adminVerifyCreator = async (
  userId: string,
  verified: boolean,
  reason: string
): Promise<void> => {
  await http.post(`/users/${userId}/verify-creator`, {
    verified,
    reason
  })
}

export const adminGetAuditLogs = async (
  params: AuditLogsFilterParams = {}
): Promise<PaginatedResponse<AuditLog>> => {
  const response = await http.get<{
    success: boolean
    logs: AuditLog[]
    total: number
    page: number
    limit: number
    total_pages: number
  }>('/admin/audit-logs', { params })

  return {
    items: response.data.logs,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit,
    total_pages: response.data.total_pages
  }
}
