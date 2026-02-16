/**
 * User Panel - User's Personal Learning Area
 *
 * Provides access to:
 * - Dashboard with statistics and quick actions
 * - My Courses (manage personal courses)
 * - Settings (profile, subscription, notifications)
 *
 * Access Control:
 * - All authenticated users can access user panel
 * - Courses filtered by user_id
 * - Settings scoped to current user
 *
 * Architecture:
 * - Lazy-loaded components
 * - Shared CourseEditor with /course-editor/ via useAccessControl
 * - User-specific composables for state management
 */

export { default as UserPanelMain } from './UserPanelMain.vue'
export { default as UserDashboard } from './dashboard/UserDashboard.vue'
export { default as UserCourses } from './courses/UserCourses.vue'
export { default as UserSettings } from './settings/UserSettings.vue'

// Composables
export * from './composables'
