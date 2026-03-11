/**
 * Exam Cockpit API Client
 *
 * User-facing API for the personal exam dashboard (Exam Cockpit).
 * Aggregates readiness, weaknesses, predictions, and recommendations.
 */

import http from '@/infrastructure/api/http'

export interface CockpitWeaknessEntry {
  position_id: number
  position_code: string
  position_title: string
  proficiency_score: number
  severity: string
  recommendation?: string
  peer_comparison?: { percentile: number; avg_accuracy: number; user_count: number } | null
}

export interface CockpitPrediction {
  position_id: number
  position_code: string
  position_title: string
  probability: number
  confidence: string
  reasoning: string
}

export interface CockpitRecommendation {
  position_code: string
  position_title: string
  action: string
  reason: string
  priority: number
  severity: string
  proficiency_score: number
}

export interface CockpitData {
  overall_readiness: number
  strengths: CockpitWeaknessEntry[]
  critical_weaknesses: CockpitWeaknessEntry[]
  predictions: CockpitPrediction[]
  recommendations: CockpitRecommendation[]
  coverage_percent: number
  gap_count: number
  total_positions: number
}

export const fetchCockpitData = async (examType: string): Promise<CockpitData> => {
  const { data } = await http.get('/user/exam-trainer/cockpit', {
    params: { exam_type: examType },
  })
  return data
}
