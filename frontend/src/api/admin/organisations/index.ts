/**
 * Admin Domain - Organisations Subdomain Barrel Export
 * ====================================================
 *
 * Clean interface for organisation administration APIs.
 * Consolidates management, courses, and analytics endpoints.
 *
 * Usage:
 * import { getOrganisationDetail, getOrganisationMembers } from '@/api/admin'
 * import type { OrgDetail, OrgMember } from '@/api/admin'
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
  // Courses Types
  OrgCourse,
  OrgCourseAssignmentRequest,
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

// ============================================================================
// Courses API Export
// ============================================================================

export {
  assignCourseToMembers,
  getOrganisationCourses,
  unassignCourseFromMembers,
} from './courses.api'

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
