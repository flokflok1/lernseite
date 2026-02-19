/**
 * LernsystemX - Panel Organisations Sub-Store (Pinia)
 *
 * Manages admin organisation management:
 * - Organisation listing with pagination and filters
 * - Plan updates and token pool management
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as adminApi from '@/infrastructure/api/clients/panel/admin'
import type {
  AdminOrganisation,
  OrganisationsFilterParams,
  PaginatedResponse
} from '@/infrastructure/api/clients/panel/admin'

export const usePanelOrganisationsStore = defineStore('panel-organisations', () => {
  // State
  const organisations = ref<AdminOrganisation[]>([])
  const orgsTotal = ref(0)
  const orgsPage = ref(1)
  const orgsLimit = ref(20)
  const orgsTotalPages = ref(0)
  const orgFilters = ref<OrganisationsFilterParams>({})
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions

  /**
   * Load organisations with filters
   */
  const loadOrganisations = async (
    params: OrganisationsFilterParams = {}
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<AdminOrganisation> =
        await adminApi.adminGetOrganisations(params)

      organisations.value = response.items
      orgsTotal.value = response.total
      orgsPage.value = response.page
      orgsLimit.value = response.limit
      orgsTotalPages.value = response.total_pages
      orgFilters.value = params
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Organisationen'
      console.error('Failed to load organisations:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update organisation plan
   */
  const updateOrganisationPlan = async (
    orgId: number,
    planId: string
  ): Promise<void> => {
    try {
      await adminApi.adminUpdateOrganisationPlan(orgId, planId)

      const org = organisations.value.find(o => o.organisation_id === orgId)
      if (org) {
        org.plan_id = planId
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Ändern des Plans'
      console.error('Failed to update organisation plan:', err)
      throw err
    }
  }

  /**
   * Add tokens to organisation
   */
  const addOrganisationTokens = async (
    orgId: number,
    amount: number,
    reason?: string
  ): Promise<void> => {
    try {
      await adminApi.adminAddOrganisationTokens(orgId, amount, reason)

      const org = organisations.value.find(o => o.organisation_id === orgId)
      if (org) {
        org.token_pool += amount
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Hinzufügen von Tokens'
      console.error('Failed to add organisation tokens:', err)
      throw err
    }
  }

  return {
    // State
    organisations,
    orgsTotal,
    orgsPage,
    orgsLimit,
    orgsTotalPages,
    orgFilters,
    loading,
    error,

    // Actions
    loadOrganisations,
    updateOrganisationPlan,
    addOrganisationTokens
  }
})
