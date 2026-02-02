/**
 * Admin Organisation Management API
 */

import http from '@/infrastructure/api/http'
import type {
  AdminOrganisation,
  OrganisationsFilterParams,
  PaginatedResponse
} from './types'

export const adminGetOrganisations = async (
  params: OrganisationsFilterParams = {}
): Promise<PaginatedResponse<AdminOrganisation>> => {
  const response = await http.get<{
    success: boolean
    organisations: AdminOrganisation[]
    total: number
    page: number
    limit: number
    total_pages: number
  }>('/admin/organisations', { params })

  return {
    items: response.data.organisations,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit,
    total_pages: response.data.total_pages
  }
}

export const adminGetOrganisationDetail = async (
  orgId: number
): Promise<AdminOrganisation> => {
  const response = await http.get<{
    success: boolean
    organisation: AdminOrganisation
  }>(`/admin/organisations/${orgId}`)

  return response.data.organisation
}

export const adminUpdateOrganisationPlan = async (
  orgId: number,
  planId: string
): Promise<void> => {
  await http.patch(`/admin/organisations/${orgId}/plan`, {
    plan_id: planId
  })
}

export const adminAddOrganisationTokens = async (
  orgId: number,
  amount: number,
  reason?: string
): Promise<void> => {
  await http.post(`/admin/organisations/${orgId}/tokens`, {
    amount,
    reason
  })
}
