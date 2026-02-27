/**
 * LernsystemX Admin API
 *
 * Domain-organized API clients for admin panel operations.
 */

// Shared types
export * from './types'

// AI domain (models, pricing, jobs, prompts)
export * from './ai/jobs.api'
export * from './ai/models.api'
export * from './ai/pricing.api'
export * from './ai/prompts.api'

// Courses domain (courses, chapters, lessons, files)
export * from './courses/courses.api'
export * from './courses/chapters.api'
export * from './courses/lessons.api'
export * from './courses/files.api'

// i18n domain (languages, sync)
export * from './i18n/languages.api'
export * from './i18n/sync.api'
export * from './i18n/sync.types'

// Users domain (users, roles, groups)
export * from './users/users.api'
export * from './users/roles.api'
export * from './users/groups.api'
export * from './users/groups.types'
export { default as groupsApi } from './users/groups.api'

// System domain (settings, feature flags, system features)
export * from './system/settings.api'
export * from './system/feature-flags.api'
export * from './system/system-features.api'

// Content domain (learning methods, plugins, routing)
export * from './content/learning-methods.api'
export * from './content/lm-plugins.api'
export * from './content/lm-routing.api'

// Analytics
export * from './analytics/analytics.api'

// Exams
export * from './exams/exams.api'

// Organisations
export * from './organisations/organisations.api'
export * from './organisations/index'
