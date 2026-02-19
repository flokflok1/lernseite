/**
 * System Features API — Request/Response Types
 *
 * Type-safe interfaces for the systemFeatures API client.
 * Grouped by category (1:1 with client structure).
 *
 * Note: Most backend endpoints are stubs (501). These types define
 * the expected contract for when features are implemented.
 */

// ---------------------------------------------------------------------------
// Interactive Tools
// ---------------------------------------------------------------------------

export interface WhiteboardDrawingData {
  type: 'freehand' | 'line' | 'rectangle' | 'circle' | 'text'
  points?: number[][]
  color?: string
  strokeWidth?: number
  text?: string
}

export interface WhiteboardRecognizeData {
  drawingIds: string[]
  recognitionType: 'shape' | 'text' | 'math'
}

export interface SandboxResources {
  cpu?: number
  memory?: number
  disk?: number
}

// ---------------------------------------------------------------------------
// Exam & Assessment
// ---------------------------------------------------------------------------

export interface IHKSimulateRequest {
  examType: string
  profession: string
  duration?: number
  questionCount?: number
}

export interface PracticalExamCreateRequest {
  title: string
  description?: string
  courseId?: string
  tasks: PracticalExamTask[]
}

export interface PracticalExamTask {
  title: string
  description: string
  maxPoints: number
  timeLimit?: number
}

export interface ComprehensionCheckRequest {
  lessonId: string
  chapterId?: string
  checkType?: 'quick' | 'detailed'
}

export interface ExamSimulationStartRequest {
  examType: string
  courseId?: string
  timeLimit?: number
}

// ---------------------------------------------------------------------------
// Math Toolkit
// ---------------------------------------------------------------------------

export interface MathPatternCreateRequest {
  name: string
  category: string
  pattern: string
  difficulty: number
  solution?: string
}

export interface MathFormulaCreateRequest {
  name: string
  latex: string
  category: string
  description?: string
}

// ---------------------------------------------------------------------------
// Gamification
// ---------------------------------------------------------------------------

export interface AdaptiveDifficultyAdjustRequest {
  userId?: string
  courseId?: string
  currentDifficulty: number
  performance: number
}

// ---------------------------------------------------------------------------
// Tutor & Coaching
// ---------------------------------------------------------------------------

export interface SocraticDialogStartRequest {
  topic: string
  lessonId?: string
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
}

// ---------------------------------------------------------------------------
// Collaboration
// ---------------------------------------------------------------------------

export interface PeerInstructionSessionRequest {
  courseId: string
  chapterId?: string
  questionCount?: number
}

export interface TeamCaseCreateRequest {
  title: string
  description: string
  courseId?: string
  teamSize?: number
}

export interface PeerReviewSubmitRequest {
  submissionId: string
  feedback: string
  rating?: number
  criteria?: Record<string, number>
}

export interface LearningJournalEntryRequest {
  title: string
  content: string
  courseId?: string
  lessonId?: string
  tags?: string[]
}

export interface ProjectPortfolioCreateRequest {
  title: string
  description?: string
  courseId?: string
  visibility?: 'private' | 'public' | 'course'
}

export interface ProjectBasedCreateRequest {
  title: string
  description: string
  courseId?: string
  milestones?: ProjectMilestone[]
}

export interface ProjectMilestone {
  title: string
  deadline?: string
  description?: string
}

export interface InvertedClassroomSessionRequest {
  courseId: string
  chapterId?: string
  preMaterials?: string[]
  sessionDate?: string
}

// ---------------------------------------------------------------------------
// IT Environments
// ---------------------------------------------------------------------------

export interface CodeSandboxCreateRequest {
  language: string
  template?: string
  resources?: SandboxResources
}

export interface NetworkSimulationStartRequest {
  topology: string
  nodes?: number
  scenario?: string
}

export interface TerminalSessionCreateRequest {
  os?: string
  image?: string
  timeout?: number
}

// ---------------------------------------------------------------------------
// Meta Features
// ---------------------------------------------------------------------------

export interface TimerStartRequest {
  duration: number
  type?: 'countdown' | 'stopwatch' | 'pomodoro'
  label?: string
}

// ---------------------------------------------------------------------------
// Visualization
// ---------------------------------------------------------------------------

export interface MindmapGenerateRequest {
  topic: string
  lessonId?: string
  depth?: number
  style?: 'radial' | 'tree' | 'org'
}

// ---------------------------------------------------------------------------
// Learning Paths
// ---------------------------------------------------------------------------

export interface LearningPathGenerateRequest {
  courseId?: string
  userId?: string
  goals?: string[]
  skillLevel?: 'beginner' | 'intermediate' | 'advanced'
}
