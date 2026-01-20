/**
 * Admin Domain - Organisations Types & Interfaces
 * ================================================
 *
 * Consolidated type definitions for all organisation-related APIs:
 * - Organisation management
 * - Member management
 * - Course assignment
 * - Analytics and reporting
 */

// Re-export all types from individual API modules for convenience
export type {
  // Management Types
  OrgDetail,
  OrgMember,
  OrgSettings,
  OrgInviteRequest,
  // Courses Types
  OrgCourse,
  OrgCourseAssignmentRequest,
  // Analytics Types
  OrgAnalyticsOverview,
  TimeSeriesPoint,
  OrgAnalyticsCourse,
  OrgAnalyticsChapter,
  OrgAnalyticsModule, // Backward compatibility alias
} from './management.api'

// Note: OrgCourse is defined in courses.api.ts but re-exported from management.api.ts
// for convenience. All types are available from '@/infrastructure/api/clients/admin/organisations'
