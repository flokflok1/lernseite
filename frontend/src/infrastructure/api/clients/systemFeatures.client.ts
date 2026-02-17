/**
 * System Features API Client
 *
 * API client for 25 System-Features organized in 10 categories.
 *
 * Base URL: /api/v1/system-features
 *
 * Categories:
 * - interactive       # Interactive Tools (3 features)
 * - exam              # Exam & Assessment (4 features + simulations)
 * - math/toolkit      # Math Toolkit (4 features)
 * - gamification      # Gamification (3 features)
 * - tutor             # Tutor & Coaching (2 features)
 * - collaboration     # Collaboration (7 features)
 * - it-environments   # IT Environments (3 features)
 * - meta              # Meta Features (1 feature)
 * - visualization     # Visualization (1 feature)
 * - learning-paths    # Learning Paths (1 feature)
 */

import type { AxiosResponse } from 'axios'
import http from '@/infrastructure/api/http'
import type {
  WhiteboardDrawingData,
  WhiteboardRecognizeData,
  SandboxResources,
  IHKSimulateRequest,
  PracticalExamCreateRequest,
  ComprehensionCheckRequest,
  ExamSimulationStartRequest,
  MathPatternCreateRequest,
  MathFormulaCreateRequest,
  AdaptiveDifficultyAdjustRequest,
  SocraticDialogStartRequest,
  PeerInstructionSessionRequest,
  TeamCaseCreateRequest,
  PeerReviewSubmitRequest,
  LearningJournalEntryRequest,
  ProjectPortfolioCreateRequest,
  ProjectBasedCreateRequest,
  InvertedClassroomSessionRequest,
  CodeSandboxCreateRequest,
  NetworkSimulationStartRequest,
  TerminalSessionCreateRequest,
  TimerStartRequest,
  MindmapGenerateRequest,
  LearningPathGenerateRequest
} from './systemFeatures.types'

const BASE_URL = '/api/v1/system-features'

// =============================================================================
// INTERACTIVE TOOLS
// =============================================================================

export const interactiveTools = {
  /**
   * Whiteboard Engine
   */
  whiteboard: {
    createCanvas: (data: { title: string; width?: number; height?: number }): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/interactive/whiteboard/canvas`, data),

    getCanvas: (canvasId: string): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}`),

    addDrawing: (canvasId: string, data: WhiteboardDrawingData): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}/draw`, data),

    recognizeDrawing: (canvasId: string, data: WhiteboardRecognizeData): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}/recognize`, data),

    deleteCanvas: (canvasId: string): Promise<AxiosResponse> =>
      http.delete(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}`)
  },

  /**
   * IT Sandbox
   */
  sandbox: {
    createEnvironment: (data: { type: string; os: string; resources?: SandboxResources }): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/interactive/it-sandbox/environment`, data),

    executeCode: (envId: string, data: { code: string; language: string; timeout?: number }): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/interactive/it-sandbox/environment/${envId}/execute`, data),

    deleteEnvironment: (envId: string): Promise<AxiosResponse> =>
      http.delete(`${BASE_URL}/interactive/it-sandbox/environment/${envId}`)
  },

  /**
   * Speech-to-Text
   */
  speech: {
    transcribe: (data: FormData): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/interactive/speech-to-text/transcribe`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      }),

    getTranscription: (transcriptionId: string): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/interactive/speech-to-text/transcription/${transcriptionId}`)
  }
}

// =============================================================================
// EXAM & ASSESSMENT
// =============================================================================

export const exam = {
  /**
   * IHK Exam System
   */
  ihk: {
    simulate: (data: IHKSimulateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/exam/ihk/simulate`, data)
  },

  /**
   * Practical Exam Engine
   */
  practical: {
    create: (data: PracticalExamCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/exam/practical/create`, data)
  },

  /**
   * Comprehension Checker
   */
  comprehension: {
    check: (data: ComprehensionCheckRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/exam/comprehension/check`, data)
  },

  /**
   * Chapter Completion System
   */
  chapterCompletion: {
    getStatus: (chapterId: string): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/exam/chapter-completion/status/${chapterId}`)
  },

  /**
   * Exam Simulations (existing)
   */
  simulations: {
    getAttempts: (): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/exam/simulations/attempts`),

    startSimulation: (data: ExamSimulationStartRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/exam/simulations/start`, data)
  }
}

// =============================================================================
// MATH TOOLKIT
// =============================================================================

export const mathToolkit = {
  /**
   * Math Practice
   */
  practice: {
    getPractice: (): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/math/toolkit/practice`)
  },

  /**
   * Math Reference Library
   */
  reference: {
    getReference: (): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/math/toolkit/reference`)
  },

  /**
   * Math Tasks
   */
  tasks: {
    getTasks: (): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/math/toolkit/tasks`)
  },

  /**
   * Admin Functions
   */
  admin: {
    createPattern: (data: MathPatternCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/math/toolkit/admin/patterns`, data),

    createFormula: (data: MathFormulaCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/math/toolkit/admin/formulas`, data)
  }
}

// =============================================================================
// GAMIFICATION
// =============================================================================

export const gamification = {
  /**
   * Adaptive Difficulty
   */
  adaptiveDifficulty: {
    adjust: (data: AdaptiveDifficultyAdjustRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/gamification/adaptive-difficulty/adjust`, data)
  },

  /**
   * XP & Quest System
   */
  xpQuest: {
    getStatus: (): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/gamification/xp-quest/status`)
  },

  /**
   * Daily Recall
   */
  dailyRecall: {
    getQuestions: (): Promise<AxiosResponse> =>
      http.get(`${BASE_URL}/gamification/daily-recall/questions`)
  }
}

// =============================================================================
// TUTOR & COACHING
// =============================================================================

export const tutor = {
  /**
   * NPC Tutor
   */
  npc: {
    chat: (data: { message: string }): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/tutor/npc/chat`, data)
  },

  /**
   * Socratic Dialog
   */
  socratic: {
    start: (data: SocraticDialogStartRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/tutor/socratic/start`, data)
  }
}

// =============================================================================
// COLLABORATION
// =============================================================================

export const collaboration = {
  /**
   * Peer Instruction
   */
  peerInstruction: {
    createSession: (data: PeerInstructionSessionRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/collaboration/peer-instruction/session`, data)
  },

  /**
   * Team Case
   */
  teamCase: {
    create: (data: TeamCaseCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/collaboration/team-case/create`, data)
  },

  /**
   * Peer Review
   */
  peerReview: {
    submit: (data: PeerReviewSubmitRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/collaboration/peer-review/submit`, data)
  },

  /**
   * Learning Journal
   */
  learningJournal: {
    createEntry: (data: LearningJournalEntryRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/collaboration/learning-journal/entry`, data)
  },

  /**
   * Project Portfolio
   */
  projectPortfolio: {
    create: (data: ProjectPortfolioCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/collaboration/project-portfolio/create`, data)
  },

  /**
   * Project-Based Learning
   */
  projectBased: {
    createProject: (data: ProjectBasedCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/collaboration/project-based/project`, data)
  },

  /**
   * Inverted Classroom
   */
  invertedClassroom: {
    createSession: (data: InvertedClassroomSessionRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/collaboration/inverted-classroom/session`, data)
  }
}

// =============================================================================
// IT ENVIRONMENTS
// =============================================================================

export const itEnvironments = {
  /**
   * Code Sandbox
   */
  codeSandbox: {
    create: (data: CodeSandboxCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/it-environments/code-sandbox/create`, data)
  },

  /**
   * Network Simulation
   */
  networkSimulation: {
    start: (data: NetworkSimulationStartRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/it-environments/network-simulation/simulate`, data)
  },

  /**
   * Terminal Access
   */
  terminalAccess: {
    createSession: (data: TerminalSessionCreateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/it-environments/terminal-access/session`, data)
  }
}

// =============================================================================
// META FEATURES
// =============================================================================

export const meta = {
  /**
   * Timer Wrapper
   */
  timer: {
    start: (data: TimerStartRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/meta/timer-wrapper/start`, data)
  }
}

// =============================================================================
// VISUALIZATION
// =============================================================================

export const visualization = {
  /**
   * Mindmap Generator
   */
  mindmap: {
    generate: (data: MindmapGenerateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/visualization/mindmap-generator/generate`, data)
  }
}

// =============================================================================
// LEARNING PATHS
// =============================================================================

export const learningPaths = {
  /**
   * Learning Path Generator
   */
  pathGenerator: {
    generate: (data: LearningPathGenerateRequest): Promise<AxiosResponse> =>
      http.post(`${BASE_URL}/learning-paths/path-generator/generate`, data)
  }
}

// =============================================================================
// DEFAULT EXPORT (All Features)
// =============================================================================

export const systemFeaturesClient = {
  interactive: interactiveTools,
  exam,
  math: mathToolkit,
  gamification,
  tutor,
  collaboration,
  itEnvironments,
  meta,
  visualization,
  learningPaths
}

export default systemFeaturesClient
