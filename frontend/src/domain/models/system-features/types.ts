/**
 * System Features Domain Types
 *
 * Type-safe interfaces for the 25 System Features stored in
 * `support_systems.system_features`. These types mirror the DB schema
 * from migration 038_system_features.sql (Source of Truth).
 *
 * System Features are infrastructure-level capabilities (NOT Content-Lernmethoden).
 * They are organized into 10 categories and can be enabled per course/chapter.
 */

// ---------------------------------------------------------------------------
// Feature Codes (1:1 with DB `feature_code` UNIQUE column)
// ---------------------------------------------------------------------------

export type SystemFeatureCode =
  // interactive_tools (1)
  | 'whiteboard_engine'
  // it_environments (4)
  | 'it_sandbox'
  | 'code_sandbox'
  | 'network_simulation'
  | 'terminal_access'
  // audio (1)
  | 'speech_to_text'
  // exam_systems (3)
  | 'ihk_exam_system'
  | 'practical_exam_engine'
  | 'chapter_completion_system'
  // tutor (3)
  | 'comprehension_checker'
  | 'npc_tutor'
  | 'socratic_dialog'
  // gamification (3)
  | 'adaptive_difficulty'
  | 'daily_recall'
  | 'xp_quest_system'
  // collaboration (7)
  | 'peer_instruction'
  | 'team_case'
  | 'peer_review'
  | 'learning_journal'
  | 'project_portfolio'
  | 'project_based_learning'
  | 'inverted_classroom'
  // meta_features (1)
  | 'timer_wrapper'
  // visualization (1)
  | 'mindmap_generator'
  // learning_paths (1)
  | 'learning_path_generator'

// ---------------------------------------------------------------------------
// Categories (1:1 with DB `category` column — 10 distinct values)
// ---------------------------------------------------------------------------

export type SystemFeatureCategory =
  | 'audio'
  | 'collaboration'
  | 'exam_systems'
  | 'gamification'
  | 'interactive_tools'
  | 'it_environments'
  | 'learning_paths'
  | 'meta_features'
  | 'tutor'
  | 'visualization'

// ---------------------------------------------------------------------------
// Core Entity (mirrors `support_systems.system_features` table)
// ---------------------------------------------------------------------------

export interface SystemFeature {
  featureId: number
  featureCode: SystemFeatureCode
  featureName: string
  description: string
  category: SystemFeatureCategory
  requiresInfrastructure: boolean
  requiresExternalService: boolean
  active: boolean
  config: Record<string, unknown>
  icon: string | null
  formerLmId: number | null
  createdAt: string
  updatedAt: string
}

// ---------------------------------------------------------------------------
// Course-Level Feature Mapping (mirrors `support_systems.course_system_features`)
// ---------------------------------------------------------------------------

export interface CourseFeatureMapping {
  mappingId: string
  courseId: string
  featureId: number
  enabled: boolean
  configOverride: Record<string, unknown>
  enabledAt: string
}

// ---------------------------------------------------------------------------
// Chapter-Level Feature Mapping (mirrors `support_systems.chapter_system_features`)
// ---------------------------------------------------------------------------

export interface ChapterFeatureMapping {
  mappingId: string
  chapterId: string
  featureId: number
  enabled: boolean
  configOverride: Record<string, unknown>
  enabledAt: string
}

// ---------------------------------------------------------------------------
// UI Helper Types
// ---------------------------------------------------------------------------

/** Feature availability and enablement status for rendering in UI */
export interface FeatureStatus {
  available: boolean
  enabled: boolean
  configOverride?: Record<string, unknown>
}

/** Grouped features by category for admin panels and listing views */
export interface FeaturesByCategory {
  category: SystemFeatureCategory
  features: SystemFeature[]
}
