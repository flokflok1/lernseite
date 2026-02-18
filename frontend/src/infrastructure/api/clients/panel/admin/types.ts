/**
 * LernsystemX Admin API - Type Definitions
 *
 * REFACTORED: Split into domain-specific files in ./types/ subdirectory.
 * This file re-exports everything for backward compatibility.
 *
 * Domain files:
 * - types/core.types.ts: AdminUser, AdminOrganisation, AdminCourse, etc.
 * - types/filter.types.ts: PaginatedResponse, ApiResponse, filter params
 * - types/user-management.types.ts: BanUserRequest, AuditLog, etc.
 * - types/course.types.ts: Chapters, Categories, Lessons, Prompts, Files, Exams
 * - types/analytics.types.ts: UserStatsData, CourseStatsData, TimeSeriesPoint
 * - types/ai.types.ts: AIJob, AIModel, AIModelPricing, AIProvider
 * - types/learning-method.types.ts: LM types, routing, capability slots
 * - types/feature-flag.types.ts: FeatureFlag, RolloutPlan
 */

export * from './types/index'
