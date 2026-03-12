/**
 * Daily Recall API Client
 */
import http from '@/infrastructure/api/http'
import type { ReviewItem } from '@/infrastructure/api/clients/panel/user/learning/reviews.api'

export interface DailyRecallResponse {
  items: ReviewItem[]
  count: number
}

export async function fetchDailyRecall(limit = 10): Promise<DailyRecallResponse> {
  const { data } = await http.get('/system-features/gamification/daily-recall/questions', {
    params: { limit },
  })
  return data.data
}
