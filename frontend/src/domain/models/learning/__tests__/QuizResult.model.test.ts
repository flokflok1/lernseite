import { describe, it, expect } from 'vitest'
import { QuizResultModel } from '../QuizResult.model'

describe('QuizResultModel', () => {
  const createResult = (overrides = {}) =>
    QuizResultModel.fromAPI({
      quiz_id: 1,
      passed: true,
      score: 8,
      total_points: 10,
      percentage: 80,
      questions: [
        { question_id: 1, is_correct: true, points_earned: 2, max_points: 2, user_answer: 'A', correct_answer: 'A', explanation: '' },
        { question_id: 2, is_correct: true, points_earned: 2, max_points: 2, user_answer: 'B', correct_answer: 'B', explanation: '' },
        { question_id: 3, is_correct: false, points_earned: 0, max_points: 2, user_answer: 'C', correct_answer: 'D', explanation: '' },
        { question_id: 4, is_correct: true, points_earned: 2, max_points: 2, user_answer: 'A', correct_answer: 'A', explanation: '' },
        { question_id: 5, is_correct: true, points_earned: 2, max_points: 2, user_answer: 'B', correct_answer: 'B', explanation: '' }
      ],
      completed_at: '2026-02-15T10:00:00Z',
      ...overrides
    } as any)

  describe('fromAPI', () => {
    it('creates QuizResultModel from API data', () => {
      const result = createResult()
      expect(result.quizId).toBe(1)
      expect(result.passed).toBe(true)
      expect(result.score).toBe(8)
      expect(result.totalPoints).toBe(10)
      expect(result.percentage).toBe(80)
      expect(result.completedAt).toBeInstanceOf(Date)
    })

    it('handles empty questions array', () => {
      const result = createResult({ questions: undefined })
      expect(result.totalQuestions).toBe(0)
      expect(result.correctCount).toBe(0)
    })
  })

  describe('computed stats', () => {
    it('correctCount returns number of correct answers', () => {
      expect(createResult().correctCount).toBe(4)
    })

    it('totalQuestions returns total number of questions', () => {
      expect(createResult().totalQuestions).toBe(5)
    })

    it('incorrectCount returns total - correct', () => {
      expect(createResult().incorrectCount).toBe(1)
    })
  })

  describe('grading', () => {
    it('grade A for >= 90%', () => {
      expect(createResult({ percentage: 95 }).grade).toBe('A')
    })

    it('grade B for >= 80%', () => {
      expect(createResult({ percentage: 85 }).grade).toBe('B')
    })

    it('grade C for >= 70%', () => {
      expect(createResult({ percentage: 75 }).grade).toBe('C')
    })

    it('grade D for >= 60%', () => {
      expect(createResult({ percentage: 65 }).grade).toBe('D')
    })

    it('grade F for < 60%', () => {
      expect(createResult({ percentage: 50 }).grade).toBe('F')
    })

    it('isPerfect for 100%', () => {
      expect(createResult({ percentage: 100 }).isPerfect).toBe(true)
    })

    it('not isPerfect for < 100%', () => {
      expect(createResult({ percentage: 99 }).isPerfect).toBe(false)
    })
  })

  describe('display helpers', () => {
    it('getResultColor green for passed', () => {
      expect(createResult({ passed: true }).getResultColor()).toBe('text-green-600')
    })

    it('getResultColor red for failed', () => {
      expect(createResult({ passed: false }).getResultColor()).toBe('text-red-600')
    })

    it('getGradeColor green for A', () => {
      expect(createResult({ percentage: 95 }).getGradeColor()).toBe('text-green-600')
    })

    it('getGradeColor blue for B', () => {
      expect(createResult({ percentage: 85 }).getGradeColor()).toBe('text-blue-600')
    })

    it('getGradeColor yellow for C', () => {
      expect(createResult({ percentage: 75 }).getGradeColor()).toBe('text-yellow-600')
    })

    it('getGradeColor orange for D', () => {
      expect(createResult({ percentage: 65 }).getGradeColor()).toBe('text-orange-600')
    })

    it('getGradeColor red for F', () => {
      expect(createResult({ percentage: 50 }).getGradeColor()).toBe('text-red-600')
    })
  })

  describe('toJSON', () => {
    it('serializes relevant fields', () => {
      const json = createResult().toJSON()
      expect(json.quizId).toBe(1)
      expect(json.passed).toBe(true)
      expect(json.grade).toBe('B')
      expect(json.correctCount).toBe(4)
      expect(json.totalQuestions).toBe(5)
    })
  })
})
