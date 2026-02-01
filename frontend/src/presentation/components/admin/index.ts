/**
 * Admin Components
 *
 * Barrel export for all admin components.
 * Includes dashboard, content management, user management, etc.
 */

// Dashboard
export { AdminDashboard } from './dashboard'

// Content Management
export { default as AdminContentManagementMain } from './content-management/AdminContentManagementMain.vue'
export { default as AdminCourses } from './content-management/courses/AdminCourses.vue'
export { default as CommunityReviewQueue } from './content-management/community-review/CommunityReviewQueue.vue'
export { default as AcademyCourses } from './content-management/academy/AcademyCourses.vue'
export { default as LMConfiguration } from './content-management/learning-methods-management/LMConfiguration.vue'
export * from './content-management/composables'

// Feature Flags
export * from './feature-flags'

// Groups Management
export * from './groups'

// AI Operations
export * from './ai-operations'
