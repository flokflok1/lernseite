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
 * } from '@/presentation/components/ai/admin/authoring/kurs-builder/types'
 * ```
 *
 * @module kurs-builder/types
 */

// Session & Chat
export type {
  Session,
  ChatMessage,
  SessionStats
} from './session.types'

// Course Structure
export type {
  Course,
  Chapter,
  Lesson,
  LearningMethodInstance,
  DraftStructure,
  DraftStats
} from './course.types'

// File Management
export type {
  CourseFile,
  FileUploadProgress,
  FileSelectionState
} from './file.types'

// Actions & Workflows
export type {
  QuickAction,
  ContextAction,
  PendingAction,
  SelectedContext,
  WorkflowState
} from './action.types'

// Theory & Explanations
export type {
  Theory,
  Explanation,
  ExplanationStep,
  TheoryGenerationRequest,
  ExplanationGenerationRequest
} from './theory.types'

// Learning Methods
export type {
  LearningMethodType,
  LMSuggestion,
  LMConfiguration,
  LMSuggestionRequest,
  LMCreationRequest
} from './lm.types'
