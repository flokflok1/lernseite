/**
 * LernsystemX - Organisation Admin Store (Pinia)
 *
 * Manages:
 * - Organisation details & settings
 * - Organisation members
 * - Organisation courses
 * - Organisation analytics
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as orgAdminApi from '@/api/orgAdmin.api'
import type {
  OrgDetail,
  OrgMember,
  OrgCourse,
  OrgAnalyticsOverview,
  OrgInviteRequest,
  OrgCourseAssignmentRequest,
  OrgSettings,
  TimeSeriesPoint,
  OrgAnalyticsCourse,
  OrgAnalyticsModule
} from '@/api/orgAdmin.api'

export const useOrgAdminStore = defineStore('orgAdmin', () => {
  // ============================================================================
  // State
  // ============================================================================

  // Organisation
  const organisation = ref<OrgDetail | null>(null)

  // Members
  const members = ref<OrgMember[]>([])
  const membersTotal = ref(0)
  const membersPage = ref(1)
  const membersLimit = ref(20)

  // Courses
  const orgCourses = ref<OrgCourse[]>([])
  const orgCoursesTotal = ref(0)
  const orgCoursesPage = ref(1)
  const orgCoursesLimit = ref(20)

  // Analytics
  const orgStats = ref<OrgAnalyticsOverview | null>(null)

  // Advanced Analytics
  const orgAnalytics = ref<{
    timeframe: 7 | 30 | 90
    eventsTimeSeries: TimeSeriesPoint[]
    activeMembersTimeSeries: TimeSeriesPoint[]
    topCourses: OrgAnalyticsCourse[]
    topModules: OrgAnalyticsModule[]
  } | null>(null)
  const orgAnalyticsLoading = ref(false)
  const orgAnalyticsError = ref<string | null>(null)

  // Loading & Error States
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ============================================================================
  // Getters
  // ============================================================================

  const hasOrg = computed(() => !!organisation.value)

  const orgName = computed(() => organisation.value?.name || '')

  const orgType = computed(() => organisation.value?.type || '')

  const memberCount = computed(() => organisation.value?.total_users || 0)

  const activeMembersCount = computed(() => organisation.value?.active_users || 0)

  const orgCourseCount = computed(() => orgCourses.value.length)

  const tokenAvailable = computed(() => organisation.value?.token_available || 0)

  const tokenUsed = computed(() => organisation.value?.token_used || 0)

  const tokenPool = computed(() => organisation.value?.token_pool || 0)

  const tokenUsagePercentage = computed(() => {
    if (!organisation.value || organisation.value.token_pool === 0) return 0
    return (organisation.value.token_used / organisation.value.token_pool) * 100
  })

  const orgCompletionRate = computed(() => {
    return orgStats.value?.avg_completion_rate || 0
  })

  const hasOrgAnalytics = computed(() => !!orgAnalytics.value)

  const orgAnalyticsTimeframe = computed(() => orgAnalytics.value?.timeframe || 7)

  // ============================================================================
  // Actions - Organisation
  // ============================================================================

  /**
   * Load organisation dashboard
   */
  const loadOrgDashboard = async (orgId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const [orgData, analyticsData] = await Promise.all([
        orgAdminApi.getOrganisationDetail(orgId),
        orgAdminApi.getOrganisationAnalytics(orgId).catch(() => null)
      ])

      organisation.value = orgData
      orgStats.value = analyticsData
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden des Dashboards'
      console.error('Failed to load org dashboard:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update organisation settings
   */
  const updateOrgSettings = async (
    orgId: number,
    settings: Partial<OrgSettings>
  ): Promise<void> => {
    try {
      await orgAdminApi.updateOrganisationSettings(orgId, settings)

      // Update local state
      if (organisation.value) {
        organisation.value = {
          ...organisation.value,
          ...settings
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Aktualisieren der Einstellungen'
      console.error('Failed to update org settings:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Members
  // ============================================================================

  /**
   * Load organisation members
   */
  const loadOrgMembers = async (
    orgId: number,
    params?: {
      page?: number
      limit?: number
      search?: string
      role?: string
      status?: 'active' | 'inactive'
    }
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await orgAdminApi.getOrganisationMembers(orgId, params)

      members.value = response.members
      membersTotal.value = response.total
      membersPage.value = response.page
      membersLimit.value = response.limit
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Mitglieder'
      console.error('Failed to load org members:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Invite member to organisation
   */
  const inviteMember = async (
    orgId: number,
    request: OrgInviteRequest
  ): Promise<void> => {
    try {
      await orgAdminApi.inviteUserToOrganisation(orgId, request)

      // Reload members
      await loadOrgMembers(orgId)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Einladen des Mitglieds'
      console.error('Failed to invite member:', err)
      throw err
    }
  }

  /**
   * Remove member from organisation
   */
  const removeMember = async (orgId: number, userId: number): Promise<void> => {
    try {
      await orgAdminApi.removeUserFromOrganisation(orgId, userId)

      // Remove from local state
      members.value = members.value.filter(m => m.user_id !== userId)
      membersTotal.value -= 1

      // Update org stats
      if (organisation.value) {
        organisation.value.total_users -= 1
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Entfernen des Mitglieds'
      console.error('Failed to remove member:', err)
      throw err
    }
  }

  /**
   * Update member's organisation role
   */
  const updateMemberRole = async (
    orgId: number,
    userId: number,
    role: string
  ): Promise<void> => {
    try {
      await orgAdminApi.updateOrganisationUserRole(orgId, userId, role)

      // Update local state
      const member = members.value.find(m => m.user_id === userId)
      if (member) {
        member.org_role = role
        member.role = role
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Ändern der Rolle'
      console.error('Failed to update member role:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Courses
  // ============================================================================

  /**
   * Load organisation courses
   */
  const loadOrgCourses = async (
    orgId: number,
    params?: {
      page?: number
      limit?: number
      search?: string
    }
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await orgAdminApi.getOrganisationCourses(orgId, params)

      orgCourses.value = response.courses
      orgCoursesTotal.value = response.total
      orgCoursesPage.value = response.page
      orgCoursesLimit.value = response.limit
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kurse'
      console.error('Failed to load org courses:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Assign course to members
   */
  const assignCourseToMembers = async (
    orgId: number,
    request: OrgCourseAssignmentRequest
  ): Promise<void> => {
    try {
      await orgAdminApi.assignCourseToMembers(orgId, request)

      // Update local course data
      const course = orgCourses.value.find(c => c.course_id === request.course_id)
      if (course) {
        course.assigned_users += request.user_ids.length
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Zuweisen des Kurses'
      console.error('Failed to assign course:', err)
      throw err
    }
  }

  /**
   * Unassign course from members
   */
  const unassignCourseFromMembers = async (
    orgId: number,
    courseId: number,
    userIds: number[]
  ): Promise<void> => {
    try {
      await orgAdminApi.unassignCourseFromMembers(orgId, courseId, userIds)

      // Update local course data
      const course = orgCourses.value.find(c => c.course_id === courseId)
      if (course) {
        course.assigned_users -= userIds.length
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Entfernen der Kurszuweisung'
      console.error('Failed to unassign course:', err)
      throw err
    }
  }

  // ============================================================================
  // Actions - Analytics
  // ============================================================================

  /**
   * Load organisation analytics (basic overview)
   */
  const loadOrgAnalytics = async (orgId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const analytics = await orgAdminApi.getOrganisationAnalytics(orgId)
      orgStats.value = analytics
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Analytics'
      console.error('Failed to load org analytics:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Load advanced organisation analytics (time series & top lists)
   */
  const loadOrgAdvancedAnalytics = async (
    orgId: number,
    timeframe: 7 | 30 | 90 = 7
  ): Promise<void> => {
    orgAnalyticsLoading.value = true
    orgAnalyticsError.value = null

    try {
      // Fetch all analytics data in parallel
      const [eventsTimeSeries, activeMembersTimeSeries, topCourses, topModules] =
        await Promise.all([
          orgAdminApi.orgGetEventsTimeSeries(orgId, { days: timeframe }),
          orgAdminApi.orgGetActiveMembersTimeSeries(orgId, { days: timeframe }),
          orgAdminApi.orgGetTopCourses(orgId, { days: timeframe, limit: 10 }),
          orgAdminApi.orgGetTopModules(orgId, { days: timeframe, limit: 10 })
        ])

      orgAnalytics.value = {
        timeframe,
        eventsTimeSeries,
        activeMembersTimeSeries,
        topCourses,
        topModules
      }
    } catch (err: any) {
      orgAnalyticsError.value =
        err.response?.data?.message || 'Fehler beim Laden der erweiterten Analytics-Daten'
      console.error('Failed to load org advanced analytics:', err)
      throw err
    } finally {
      orgAnalyticsLoading.value = false
    }
  }

  /**
   * Change organisation analytics timeframe (and reload data)
   */
  const changeOrgAnalyticsTimeframe = async (
    orgId: number,
    timeframe: 7 | 30 | 90
  ): Promise<void> => {
    await loadOrgAdvancedAnalytics(orgId, timeframe)
  }

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State - Organisation
    organisation,

    // State - Members
    members,
    membersTotal,
    membersPage,
    membersLimit,

    // State - Courses
    orgCourses,
    orgCoursesTotal,
    orgCoursesPage,
    orgCoursesLimit,

    // State - Analytics
    orgStats,

    // State - Advanced Analytics
    orgAnalytics,
    orgAnalyticsLoading,
    orgAnalyticsError,

    // State - UI
    loading,
    error,

    // Getters
    hasOrg,
    orgName,
    orgType,
    memberCount,
    activeMembersCount,
    orgCourseCount,
    tokenAvailable,
    tokenUsed,
    tokenPool,
    tokenUsagePercentage,
    orgCompletionRate,
    hasOrgAnalytics,
    orgAnalyticsTimeframe,

    // Actions - Organisation
    loadOrgDashboard,
    updateOrgSettings,

    // Actions - Members
    loadOrgMembers,
    inviteMember,
    removeMember,
    updateMemberRole,

    // Actions - Courses
    loadOrgCourses,
    assignCourseToMembers,
    unassignCourseFromMembers,

    // Actions - Analytics
    loadOrgAnalytics,
    loadOrgAdvancedAnalytics,
    changeOrgAnalyticsTimeframe
  }
})
