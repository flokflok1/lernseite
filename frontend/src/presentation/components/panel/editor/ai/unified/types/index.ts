/**
 * Unified AI Editor — Type Barrel Export
 */

// Plan types
export type {
  ContentPlan,
  PlanPhase,
  PlanStep,
  PlanScope,
  PlanStatus,
  PlanStepStatus,
  CreatePlanRequest,
  CreatePlanFromFileRequest,
  UpdatePlanRequest,
  WizardPhase,
  CourseMeta,
  ChapterDraft,
  PlanChatMessage,
  PlanChatResponse,
  CreatePhasedPlanRequest,
  PlanChatRequest,
} from './plan.types'

// Skill types
export type {
  SkillConfig,
  SkillParameter,
  SkillParameterOption,
  SkillCategory,
  SkillContextLevel,
  ExecuteSkillRequest,
  BatchExecuteRequest,
  SkillCatalogResponse,
} from './skill.types'

// Prompt types
export type {
  PromptTemplate,
  PromptVariable,
  PromptPreset,
} from './prompt.types'
export { PROMPT_PRESETS } from './prompt.types'

// Generation types
export type {
  GenerationResult,
  GenerationVariant,
  GenerationHistoryEntry,
  GenerationStatus,
  BatchProgress,
} from './generation.types'

// Chat types (split-view)
export type {
  MessageRole,
  ChatMessage,
  ChatOperation,
  ChatConfirmation,
  ChatSession,
  FileContext,
} from './chat.types'

// Structure types (split-view)
export type {
  DraftStructure,
  DraftChapter,
  DraftLesson,
  ContentIndicator,
  SelectedContext,
} from './structure.types'

// Workflow types (split-view)
export type {
  WorkflowPhase,
  GenerateProgress,
  GenerateResult,
} from './workflow.types'
