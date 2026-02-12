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
import { apiClient } from '../config/apiClient'

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
      apiClient.post(`${BASE_URL}/interactive/whiteboard/canvas`, data),

    getCanvas: (canvasId: string): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}`),

    addDrawing: (canvasId: string, data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}/draw`, data),

    recognizeDrawing: (canvasId: string, data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}/recognize`, data),

    deleteCanvas: (canvasId: string): Promise<AxiosResponse> =>
      apiClient.delete(`${BASE_URL}/interactive/whiteboard/canvas/${canvasId}`)
  },

  /**
   * IT Sandbox
   */
  sandbox: {
    createEnvironment: (data: { type: string; os: string; resources?: any }): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/interactive/it-sandbox/environment`, data),

    executeCode: (envId: string, data: { code: string; language: string; timeout?: number }): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/interactive/it-sandbox/environment/${envId}/execute`, data),

    deleteEnvironment: (envId: string): Promise<AxiosResponse> =>
      apiClient.delete(`${BASE_URL}/interactive/it-sandbox/environment/${envId}`)
  },

  /**
   * Speech-to-Text
   */
  speech: {
    transcribe: (data: FormData): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/interactive/speech-to-text/transcribe`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      }),

    getTranscription: (transcriptionId: string): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/interactive/speech-to-text/transcription/${transcriptionId}`)
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
    simulate: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/exam/ihk/simulate`, data)
  },

  /**
   * Practical Exam Engine
   */
  practical: {
    create: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/exam/practical/create`, data)
  },

  /**
   * Comprehension Checker
   */
  comprehension: {
    check: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/exam/comprehension/check`, data)
  },

  /**
   * Chapter Completion System
   */
  chapterCompletion: {
    getStatus: (chapterId: string): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/exam/chapter-completion/status/${chapterId}`)
  },

  /**
   * Exam Simulations (existing)
   */
  simulations: {
    getAttempts: (): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/exam/simulations/attempts`),

    startSimulation: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/exam/simulations/start`, data)
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
      apiClient.get(`${BASE_URL}/math/toolkit/practice`)
  },

  /**
   * Math Reference Library
   */
  reference: {
    getReference: (): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/math/toolkit/reference`)
  },

  /**
   * Math Tasks
   */
  tasks: {
    getTasks: (): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/math/toolkit/tasks`)
  },

  /**
   * Admin Functions
   */
  admin: {
    createPattern: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/math/toolkit/admin/patterns`, data),

    createFormula: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/math/toolkit/admin/formulas`, data)
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
    adjust: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/gamification/adaptive-difficulty/adjust`, data)
  },

  /**
   * XP & Quest System
   */
  xpQuest: {
    getStatus: (): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/gamification/xp-quest/status`)
  },

  /**
   * Daily Recall
   */
  dailyRecall: {
    getQuestions: (): Promise<AxiosResponse> =>
      apiClient.get(`${BASE_URL}/gamification/daily-recall/questions`)
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
      apiClient.post(`${BASE_URL}/tutor/npc/chat`, data)
  },

  /**
   * Socratic Dialog
   */
  socratic: {
    start: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/tutor/socratic/start`, data)
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
    createSession: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/collaboration/peer-instruction/session`, data)
  },

  /**
   * Team Case
   */
  teamCase: {
    create: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/collaboration/team-case/create`, data)
  },

  /**
   * Peer Review
   */
  peerReview: {
    submit: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/collaboration/peer-review/submit`, data)
  },

  /**
   * Learning Journal
   */
  learningJournal: {
    createEntry: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/collaboration/learning-journal/entry`, data)
  },

  /**
   * Project Portfolio
   */
  projectPortfolio: {
    create: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/collaboration/project-portfolio/create`, data)
  },

  /**
   * Project-Based Learning
   */
  projectBased: {
    createProject: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/collaboration/project-based/project`, data)
  },

  /**
   * Inverted Classroom
   */
  invertedClassroom: {
    createSession: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/collaboration/inverted-classroom/session`, data)
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
    create: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/it-environments/code-sandbox/create`, data)
  },

  /**
   * Network Simulation
   */
  networkSimulation: {
    start: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/it-environments/network-simulation/simulate`, data)
  },

  /**
   * Terminal Access
   */
  terminalAccess: {
    createSession: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/it-environments/terminal-access/session`, data)
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
    start: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/meta/timer-wrapper/start`, data)
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
    generate: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/visualization/mindmap-generator/generate`, data)
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
    generate: (data: any): Promise<AxiosResponse> =>
      apiClient.post(`${BASE_URL}/learning-paths/path-generator/generate`, data)
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
