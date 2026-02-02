/**
 * Admin Content Management
 *
 * Admin interface for managing courses:
 * - Academy courses (Owner + Team only)
 * - Community courses (User-submitted, requires approval)
 * - Private courses (User's own, not visible)
 * - Learning methods management
 *
 * Access Control:
 * - Owner: Full access to all course types
 * - Admin: Academy + Community review only
 * - Creator/User: Can only view/manage own courses
 *
 * Architecture:
 * - Lazy-loaded components
 * - Shared CourseEditor via useAccessControl
 * - Admin-specific composables for state management
 */

export { default as AdminContentManagementMain } from './AdminContentManagementMain.vue'
export { default as AdminDashboard } from './dashboard/AdminDashboard.vue'
export { default as AdminCourses } from './courses/AdminCourses.vue'
export { default as CommunityReviewQueue } from './community-review/CommunityReviewQueue.vue'
export { default as AcademyCourses } from './academy/AcademyCourses.vue'
export { default as LMConfiguration } from './learning-methods-management/LMConfiguration.vue'

// Composables
export * from './composables'
