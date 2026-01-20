/**
 * MathToolkit API - Frontend API für das Mathe-Lern-System
 */

import http from '../http'

// Types
export interface MathCategory {
  category_id: string
  category_code: string
  name: string
  description: string
  icon: string
  color: string
  sort_order: number
}

export interface MathPattern {
  pattern_id: string
  pattern_code: string
  name: string
  description: string
  formula_template: string
  formula_latex: string
  variables: PatternVariable[]
  steps_template: PatternStep[]
  example_values: Record<string, number>
  difficulty: number
  ihk_relevant: boolean
  tags: string[]
  category_code: string
  category_name: string
  category_icon: string
}

export interface PatternVariable {
  var: string
  name: string
  unit: string
  type: 'input' | 'calculated' | 'result'
}

export interface PatternStep {
  step: number
  name: string
  formula: string
  calculator: string
  hint: string
}

export interface MathFormula {
  formula_id: string
  name: string
  description: string
  formula_text: string
  formula_latex: string
  formula_display: string
  variables: Array<{ var: string; name: string }>
  example_input: Record<string, number>
  example_output: string
  is_favorite: boolean
  usage_count: number
  category_code: string
  category_name: string
  category_icon: string
}

export interface MathSession {
  session_id: string
  user_id: string
  session_type: 'tutorial' | 'practice' | 'exam' | 'pattern_recognition' | 'free'
  scaffolding_level: number
  started_at: string
  ended_at: string | null
  tasks_completed: number
  tasks_correct: number
  hints_used: number
  pattern_code: string
  pattern_name: string
}

export interface CalculationStep {
  step_id: string
  step_number: number
  input_expression: string
  input_values: Record<string, number>
  result_value: number
  result_display: string
  calculator_keystrokes: string[]
  is_correct: boolean
  expected_value: number
  error_type: string
  hint_shown: string
  created_at: string
}

export interface UserProgress {
  progress_id: string
  current_level: number
  total_attempts: number
  correct_attempts: number
  mastery_score: number
  current_streak: number
  best_streak: number
  last_practiced_at: string
  next_review_at: string
  pattern_code: string
  pattern_name: string
  category_code: string
  category_name: string
}

export interface PatternTask {
  task_id: string
  task_type: 'identify_pattern' | 'order_steps' | 'fill_formula' | 'match_values' | 'spot_error' | 'complete_calculation'
  task_text: string
  task_data: Record<string, unknown>
  solution: Record<string, unknown>
  difficulty: number
  pattern_code: string
  pattern_name: string
}

export interface CalculatorEntry {
  expression: string
  result: number
  result_display: string
  session_id?: string
  keystrokes?: string[]
  memory_used?: boolean
  memory_value?: number
}

// API Functions
export const mathToolkitApi = {
  // Categories
  async getCategories(): Promise<MathCategory[]> {
    const response = await http.get('/math-toolkit/categories')
    return response.data.data || []
  },

  // Patterns
  async getPatterns(params?: {
    category?: string
    ihk_only?: boolean
    difficulty?: number
  }): Promise<MathPattern[]> {
    const response = await http.get('/math-toolkit/patterns', { params })
    return response.data.data || []
  },

  async getPattern(patternId: string): Promise<MathPattern | null> {
    const response = await http.get(`/math-toolkit/patterns/${patternId}`)
    return response.data.data || null
  },

  // Formulas
  async getFormulas(params?: {
    category?: string
    favorites?: boolean
  }): Promise<MathFormula[]> {
    const response = await http.get('/math-toolkit/formulas', { params })
    return response.data.data || []
  },

  async toggleFormulaFavorite(formulaId: string): Promise<boolean> {
    const response = await http.post(`/math-toolkit/formulas/${formulaId}/favorite`)
    return response.data.data?.is_favorite ?? false
  },

  async useFormula(formulaId: string): Promise<void> {
    await http.post(`/math-toolkit/formulas/${formulaId}/use`)
  },

  // Calculator
  async evaluate(expression: string): Promise<{
    success: boolean
    result: number
    display: string
    expression: string
    error?: string
  }> {
    const response = await http.post('/math-toolkit/calculator/evaluate', { expression })
    return response.data
  },

  async getCalculatorHistory(limit = 50): Promise<Array<{
    history_id: string
    expression: string
    result: number
    result_display: string
    keystrokes: string[]
    created_at: string
  }>> {
    const response = await http.get('/math-toolkit/calculator/history', {
      params: { limit }
    })
    return response.data.data || []
  },

  async saveCalculatorEntry(entry: CalculatorEntry): Promise<string> {
    const response = await http.post('/math-toolkit/calculator/save', entry)
    return response.data.data?.history_id || ''
  },

  // Sessions
  async startSession(params: {
    session_type?: string
    pattern_id?: string
    scaffolding_level?: number
    course_id?: string
    lesson_id?: string
  }): Promise<string> {
    const response = await http.post('/math-toolkit/sessions', params)
    return response.data.data?.session_id || ''
  },

  async getSession(sessionId: string): Promise<MathSession | null> {
    const response = await http.get(`/math-toolkit/sessions/${sessionId}`)
    return response.data.data || null
  },

  async endSession(sessionId: string): Promise<void> {
    await http.post(`/math-toolkit/sessions/${sessionId}/end`)
  },

  async getSessionSteps(sessionId: string): Promise<CalculationStep[]> {
    const response = await http.get(`/math-toolkit/sessions/${sessionId}/steps`)
    return response.data.data || []
  },

  async saveSessionStep(sessionId: string, step: {
    step_number: number
    input_expression: string
    input_values?: Record<string, number>
    result_value?: number
    result_display?: string
    calculator_keystrokes?: string[]
    is_correct?: boolean
    expected_value?: number
    error_type?: string
    hint_shown?: string
  }): Promise<string> {
    const response = await http.post(`/math-toolkit/sessions/${sessionId}/steps`, step)
    return response.data.data?.step_id || ''
  },

  // Progress
  async getProgress(patternId?: string): Promise<UserProgress[]> {
    const response = await http.get('/math-toolkit/progress', {
      params: patternId ? { pattern_id: patternId } : undefined
    })
    return response.data.data || []
  },

  async updateProgress(patternId: string, params: {
    is_correct: boolean
    update_level?: boolean
  }): Promise<{
    current_level: number
    total_attempts: number
    correct_attempts: number
    mastery_score: number
    current_streak: number
    best_streak: number
    level_changed: boolean
  }> {
    const response = await http.post(`/math-toolkit/progress/${patternId}`, params)
    return response.data.data
  },

  // Hints
  async getHint(params: {
    pattern_id: string
    hint_type?: string
    level?: number
    step?: number
    error?: string
  }): Promise<string | null> {
    const response = await http.get('/math-toolkit/hints', { params })
    return response.data.data?.hint || null
  },

  // Pattern Recognition Tasks
  async getTasks(params?: {
    pattern_id?: string
    type?: string
    difficulty?: number
    limit?: number
  }): Promise<PatternTask[]> {
    const response = await http.get('/math-toolkit/tasks', { params })
    return response.data.data || []
  },

  async checkTaskAnswer(taskId: string, answer: unknown): Promise<{
    success: boolean
    is_correct: boolean
    solution?: Record<string, unknown>
    feedback: string
  }> {
    const response = await http.post(`/math-toolkit/tasks/${taskId}/check`, { answer })
    return response.data
  },

  // Admin
  async createPattern(pattern: {
    pattern_code: string
    name: string
    category_code: string
    formula_template: string
    variables: PatternVariable[]
    steps_template: PatternStep[]
    description?: string
    formula_latex?: string
    example_values?: Record<string, number>
    difficulty?: number
    ihk_relevant?: boolean
    tags?: string[]
  }): Promise<string> {
    const response = await http.post('/math-toolkit/admin/patterns', pattern)
    return response.data.data?.pattern_id || ''
  },

  async createFormula(formula: {
    name: string
    formula_text: string
    category_code?: string
    description?: string
    formula_latex?: string
    formula_display?: string
    variables?: Array<{ var: string; name: string }>
    example_input?: Record<string, number>
    example_output?: string
    tags?: string[]
  }): Promise<string> {
    const response = await http.post('/math-toolkit/admin/formulas', formula)
    return response.data.data?.formula_id || ''
  }
}

export default mathToolkitApi
