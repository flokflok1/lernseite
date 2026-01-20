/**
 * Admin Domain - Organisation Courses API
 * =======================================
 *
 * Course management and assignment within organisations.
 * Part of the DDD Architecture - Infrastructure Layer (API Clients).
 *
 * Handles:
 * - Course listing and discovery
 * - Course assignment to organisation members
 * - Course unassignment
 *
 * Usage:
 * import { getOrganisationCourses, assignCourseToMembers } from '@/api/admin'
 * import type { OrgCourse } from '@/api/admin'
 */

import http from '../../http'

// ============================================================================
// Organisation Course Types
// ============================================================================

/**
 * Course information in organisation context.
 * Shows assignment and progress statistics.
 */
export interface OrgCourse {
  /** Unique course identifier */
  course_id: number
  /** Course title */
  title: string
  /** Course description */
  description?: string
  /** Course category/subject */
  category?: string
  /** Difficulty level (beginner, intermediate, advanced) */
  level?: string
  /** Number of organisation members assigned to this course */
  assigned_users: number
  /** Overall completion percentage across all assigned users */
  completion_rate?: number
  /** Average progress percentage */
  avg_progress?: number
  /** When course was created */
  created_at: string
}

/**
 * Request to assign a course to organisation members.
 */
export interface OrgCourseAssignmentRequest {
  /** Course to assign */
  course_id: number
  /** User IDs to assign course to */
  user_ids: number[]
}

// ============================================================================
// Course Management API
// ============================================================================

/**
 * Get organisation courses (org admin).
 *
 * Retrieves list of courses that can be assigned within the organisation.
 * Shows assignment counts and completion statistics.
 *
 * @param orgId - Organisation identifier
 * @param params - Pagination and search parameters
 * @returns Paginated course list
 *
 * @example
 * const result = await getOrganisationCourses(123, {
 *   page: 1,
 *   limit: 20,
 *   search: 'Python'
 * })
 * console.log(`Total courses: ${result.total}`)
 * console.log(`Page courses: ${result.courses.length}`)
 */
export const getOrganisationCourses = async (
  orgId: number,
  params?: {
    page?: number
    limit?: number
    search?: string
  }
): Promise<{
  courses: OrgCourse[]
  total: number
  page: number
  limit: number
}> => {
  const response = await http.get<{
    success: boolean
    courses: OrgCourse[]
    total: number
    page: number
    limit: number
  }>(`/organisations/${orgId}/courses`, { params })

  return {
    courses: response.data.courses,
    total: response.data.total,
    page: response.data.page,
    limit: response.data.limit
  }
}

/**
 * Assign course to organisation members (org admin).
 *
 * Makes a course available/mandatory for specified organisation members.
 * Members will see course in their course list and can start it.
 *
 * @param orgId - Organisation identifier
 * @param request - Assignment request with course and user IDs
 *
 * @example
 * await assignCourseToMembers(123, {
 *   course_id: 456,
 *   user_ids: [789, 790, 791]
 * })
 * console.log('Course assigned to 3 members')
 */
export const assignCourseToMembers = async (
  orgId: number,
  request: OrgCourseAssignmentRequest
): Promise<void> => {
  await http.post(`/organisations/${orgId}/courses/assign`, request)
}

/**
 * Unassign course from members (org admin).
 *
 * Removes course assignment from specified organisation members.
 * Members will no longer see the course as assigned (but can still access it if public).
 *
 * @param orgId - Organisation identifier
 * @param courseId - Course to unassign
 * @param userIds - User IDs to unassign course from
 *
 * @example
 * await unassignCourseFromMembers(123, 456, [789, 790])
 * console.log('Course unassigned from 2 members')
 */
export const unassignCourseFromMembers = async (
  orgId: number,
  courseId: number,
  userIds: number[]
): Promise<void> => {
  await http.post(`/organisations/${orgId}/courses/${courseId}/unassign`, {
    user_ids: userIds
  })
}
