/**
 * Review API Client — Spaced Repetition endpoints
 */
import http from '@/infrastructure/api/http'

export interface ReviewItem {
  schedule_id: string
  method_id: string
  lm_title: string
  chapter_title: string
  method_type: number
  mastery_score: number
  difficulty_level: 'easy' | 'medium' | 'hard'
  next_review_at: string
  current_streak: number
}

export interface ReviewStats {
  total_items: number
  due_count: number
  mastered_count: number
  avg_mastery: number
  next_review: string | null
}

export interface MasteryEntry {
  chapter_id: string
  chapter_title: string
  order_index: number
  avg_mastery: number
  min_mastery: number
  total_lms: number
  mastered_lms: number
  due_reviews: number
  next_review: string | null
}

export const initializeReviews = async (courseId: string) => {
  const { data } = await http.post('/user/learning/reviews/initialize', {
    course_id: courseId,
  })
  return data
}

export const fetchReviewQueue = async (
  courseId: string, limit = 20,
): Promise<{ items: ReviewItem[]; stats: ReviewStats }> => {
  const { data } = await http.get('/user/learning/reviews/queue', {
    params: { course_id: courseId, limit },
  })
  return data
}

export const submitReview = async (
  methodId: string, score: number, timeSeconds: number,
) => {
  const { data } = await http.post('/user/learning/reviews/submit', {
    method_id: methodId, score, time_seconds: timeSeconds,
  })
  return data.review
}

export const fetchMasteryMap = async (
  courseId: string,
): Promise<MasteryEntry[]> => {
  const { data } = await http.get('/user/learning/reviews/mastery', {
    params: { course_id: courseId },
  })
  return data.mastery
}

export const fetchReviewStats = async (
  courseId: string,
): Promise<ReviewStats> => {
  const { data } = await http.get('/user/learning/reviews/stats', {
    params: { course_id: courseId },
  })
  return data.stats
}
