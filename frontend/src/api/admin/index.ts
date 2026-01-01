/**
 * LernsystemX Admin API
 *
 * Refactored from admin.api.ts (3024 lines) into 14 focused modules:
 * - types.ts: All TypeScript interfaces (750 lines)
 * - users.api.ts: User management (110 lines)
 * - organisations.api.ts: Organisation management (55 lines)
 * - courses.api.ts: Course CRUD (105 lines)
 * - analytics.api.ts: System analytics, billing, tokens (130 lines)
 * - chapters.api.ts: Chapter & category management (100 lines)
 * - lessons.api.ts: Lesson management (55 lines)
 * - ai-jobs.api.ts: AI job management (45 lines)
 * - exams.api.ts: Exam management (70 lines)
 * - prompts.api.ts: Course prompts (95 lines)
 * - files.api.ts: Course files (100 lines)
 * - ai-models.api.ts: AI model management (95 lines)
 * - learning-methods.api.ts: Learning methods (95 lines)
 * - lm-routing.api.ts: LM model routing & slots (340 lines)
 *
 * Total: ~2145 lines (-30% reduction, better organization)
 */

// Re-export all types
export * from './types'

// Re-export all API functions
export * from './users.api'
export * from './organisations.api'
export * from './courses.api'
export * from './analytics.api'
export * from './chapters.api'
export * from './lessons.api'
export * from './ai-jobs.api'
export * from './exams.api'
export * from './prompts.api'
export * from './files.api'
export * from './ai-models.api'
export * from './learning-methods.api'
export * from './lm-routing.api'
