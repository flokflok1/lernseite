/**
 * QuizResult Domain Model
 *
 * Encapsulates quiz completion results and grading logic.
 * Extracts business rules from quiz result display components.
 *
 * Data source: QuizResult in infrastructure/api/clients/learning/types.ts
 *
 * Example:
 *   const result = QuizResultModel.fromAPI(apiData)
 *   result.grade           // 'A' | 'B' | 'C' | 'D' | 'F'
 *   result.correctCount    // number of correct answers
 *   result.formattedTime   // '2m 30s'
 */

import type { QuizResult as ApiQuizResult, QuizQuestionResult } from './types'

export class QuizResultModel {
  constructor(
    public readonly quizId: number,
    public readonly passed: boolean,
    public readonly score: number,
    public readonly totalPoints: number,
    public readonly percentage: number,
    public readonly questions: QuizQuestionResult[],
    public readonly completedAt: Date
  ) {}

  // ── Computed Stats ────────────────────────────────────────────

  get correctCount(): number {
    return this.questions.filter(q => q.is_correct).length
  }

  get totalQuestions(): number {
    return this.questions.length
  }

  get incorrectCount(): number {
    return this.totalQuestions - this.correctCount
  }

  // ── Grading ───────────────────────────────────────────────────

  get grade(): string {
    if (this.percentage >= 90) return 'A'
    if (this.percentage >= 80) return 'B'
    if (this.percentage >= 70) return 'C'
    if (this.percentage >= 60) return 'D'
    return 'F'
  }

  get isPerfect(): boolean {
    return this.percentage === 100
  }

  // ── Display Helpers ───────────────────────────────────────────

  getResultColor(): string {
    if (this.passed) return 'text-green-600'
    return 'text-red-600'
  }

  getGradeColor(): string {
    switch (this.grade) {
      case 'A': return 'text-green-600'
      case 'B': return 'text-blue-600'
      case 'C': return 'text-yellow-600'
      case 'D': return 'text-orange-600'
      default: return 'text-red-600'
    }
  }

  // ── Factory ───────────────────────────────────────────────────

  static fromAPI(data: ApiQuizResult): QuizResultModel {
    return new QuizResultModel(
      data.quiz_id,
      data.passed,
      data.score,
      data.total_points,
      data.percentage,
      data.questions || [],
      new Date(data.completed_at || Date.now())
    )
  }

  toJSON(): Record<string, unknown> {
    return {
      quizId: this.quizId,
      passed: this.passed,
      score: this.score,
      totalPoints: this.totalPoints,
      percentage: this.percentage,
      grade: this.grade,
      correctCount: this.correctCount,
      totalQuestions: this.totalQuestions,
    }
  }
}
