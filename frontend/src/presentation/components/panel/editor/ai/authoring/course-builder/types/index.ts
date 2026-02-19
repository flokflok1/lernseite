/**
 * KursBuilder Types - Barrel Export
 *
 * Central export for all KursBuilder TypeScript types.
 * Provides a single import point for type-safe development.
 *
 * @example
 * ```typescript
 * import type {
 *   Session,
 *   ChatMessage,
 *   Course,
 *   Chapter
 * } from '@/presentation/components/panel/editor/ai/authoring/course-builder/types'
 * ```
 *
 * @module course-builder/types
 */

// Session & Chat
export type {
  Session,
  ChatMessage,
  SessionStats
} from './session.types.ts'

// Course Structure
export type {
  Course,
  Chapter,
  Lesson,
  LearningMethodInstance,
  DraftStructure,
  DraftStats
} from './course.types.ts'

// File Management
export type {
  CourseFile,
  FileUploadProgress,
  FileSelectionState
} from './file.types.ts'

// Actions & Workflows
export type {
  QuickAction,
  ContextAction,
  PendingAction,
  SelectedContext,
  WorkflowState
} from './action.types.ts'

// Theory & Explanations
export type {
  Theory,
  Explanation,
  ExplanationStep,
  TheoryGenerationRequest,
  ExplanationGenerationRequest
} from './theory.types.ts'

// Learning Methods
export type {
  LearningMethodType,
  LMSuggestion,
  LMConfiguration,
  LMSuggestionRequest,
  LMCreationRequest
} from './lm.types.ts'
