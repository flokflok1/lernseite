/**
 * Admin Exam Clusters API — AI-powered cluster suggestion & management.
 */

import http from '@/infrastructure/api/http'

export interface ClusterLabel {
  de: string
  en: string
}

export interface ClusterSuggestion {
  cluster_key: string
  label: ClusterLabel
  topics: string[]
  reasoning: string
  point_share_pct: number
  question_count: number
}

export interface ClusterReviews {
  student_perspective: string
  instructor_perspective: string
  examiner_perspective: string
}

export interface ClusterSuggestionResult {
  status: 'success' | 'no_data' | 'parse_error'
  clusters: ClusterSuggestion[]
  reviews: ClusterReviews
  warnings: string[]
  overall_assessment: string
  exam_type_key: string
  region: string
  analysis_context: {
    question_count: number
    topic_count: number
    total_points: number
  }
}

export interface ExistingCluster {
  cluster_key: string
  label: ClusterLabel
  topics: string[]
  sort_order: number
}

// POST /admin/exam-courses/clusters/suggest
export const suggestClusters = async (
  examTypeKey: string,
  region: string = 'alle',
  options?: { provider?: string; model?: string },
): Promise<ClusterSuggestionResult> => {
  const { data } = await http.post('/admin/exam-courses/clusters/suggest', {
    exam_type_key: examTypeKey,
    region,
    provider: options?.provider,
    model: options?.model,
  })
  return data
}

// POST /admin/exam-courses/clusters/apply
export const applyClusters = async (
  examTypeKey: string,
  clusters: ClusterSuggestion[],
): Promise<{ saved: number; exam_type_key: string }> => {
  const { data } = await http.post('/admin/exam-courses/clusters/apply', {
    exam_type_key: examTypeKey,
    clusters,
  })
  return data
}

// GET /admin/exam-courses/clusters?exam_type_key=...
export const getClusters = async (
  examTypeKey: string,
): Promise<ExistingCluster[]> => {
  const { data } = await http.get('/admin/exam-courses/clusters', {
    params: { exam_type_key: examTypeKey },
  })
  return data.clusters || []
}
