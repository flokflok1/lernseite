/**
 * Admin Courses API (Barrel Export)
 *
 * Re-exports course management functions from legacy admin API
 * during DDD migration. These will be refactored into content domain.
 */

// Re-export all admin course functions from legacy API
export * from '../../admin/courses.api'
