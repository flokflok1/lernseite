/**
 * Admin Domain - Organisations Subdomain Barrel Export
 * ====================================================
 *
 * Clean interface for organisation administration APIs.
 * Consolidates management, courses, and analytics endpoints.
 *
 * Usage:
 * import { getOrganisationDetail, getOrganisationMembers } from '@/application/services/api/panel-admin'
 * import type { OrgDetail, OrgMember } from '@/application/services/api/panel-admin'
 */

// ============================================================================
// Types Export
// ============================================================================

export type {
  // Management Types
  OrgDetail,
  OrgInviteRequest,
  OrgMember,
  OrgSettings,
  // Analytics Types
  OrgAnalyticsChapter,
  OrgAnalyticsCourse,
  OrgAnalyticsModule,
  OrgAnalyticsOverview,
  TimeSeriesPoint,
} from './types'

// ============================================================================
// Management API Export
// ============================================================================

export {
  getOrganisationDetail,
  inviteUserToOrganisation,
  removeUserFromOrganisation,
  updateOrganisationSettings,
  updateOrganisationUserRole,
  getOrganisationMembers,
} from './management.api'

// NOTE: Organisation course assignment APIs are not yet implemented
// These will be moved to the content domain when implemented

// ============================================================================
// Analytics API Export
// ============================================================================

export {
  getOrganisationAnalytics,
  getOrganisationMemberProgress,
  getOrganisationTokenUsage,
  orgGetActiveMembersTimeSeries,
  orgGetEventsTimeSeries,
  orgGetTopCourses,
  orgGetTopModules,
} from './analytics.api'
