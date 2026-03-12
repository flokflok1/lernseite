/**
 * Adaptive Difficulty API Client
 */
import http from '@/infrastructure/api/http'

export interface DifficultyRecommendation {
  recommended_difficulty: 'easy' | 'medium' | 'hard'
  avg_mastery: number
  total_items: number
  mastered_count: number
}

export interface MethodDifficulty {
  difficulty_level: 'easy' | 'medium' | 'hard'
  mastery_score: number
  confidence: number
  total_reviews: number
}

export async function fetchCourseRecommendation(
  courseId: string,
): Promise<DifficultyRecommendation> {
  const { data } = await http.get(
    '/system-features/gamification/adaptive-difficulty/recommendation',
    { params: { course_id: courseId } },
  )
  return data.data
}

export async function adjustDifficulty(
  methodId: string,
): Promise<MethodDifficulty> {
  const { data } = await http.post(
    '/system-features/gamification/adaptive-difficulty/adjust',
    { method_id: methodId },
  )
  return data.data
}
