import http from '@/infrastructure/api/http'

export interface ChapterPreview {
  topic: string
  question_count: number
  lm_types: number[]
  point_weight: number
  parent_label?: Record<string, string> | null
  child_topics?: string[] | null
  // Curriculum fields
  curriculum_position_id?: number | null
  curriculum_position_code?: string | null
  objectives_total?: number
  objectives_with_questions?: number
  objectives_ai_only?: number
  coverage_source?: 'exam_questions' | 'ai_generated' | 'mixed' | null
  // Exam relevance
  relevance_score?: number
  exam_appearance_rate?: number
  relevance_trend?: 'rising' | 'stable' | 'declining' | null
  is_gap?: boolean
  ai_confidence?: number
}

export interface CoursePlan {
  title: string
  exam_type: string
  region: string
  curriculum_framework_id?: number | null
  sort_mode?: string
  total_questions: number
  total_points: number
  chapters: ChapterPreview[]
}

export interface GenerateResult {
  course_id: string
  chapters_count: number
  lm_count: number
  tokens_used: number
  status?: 'generating' | 'ready'
}

export interface GenerationProgress {
  total: number
  completed: number
  failed: number
  status: 'generating' | 'ready' | 'partial' | 'failed' | 'unknown'
}

export async function previewExamCourse(
  examType: string,
  region: string = 'alle',
  frameworkId?: number,
  sortMode?: string,
): Promise<CoursePlan> {
  const response = await http.post<{ success: boolean; plan: CoursePlan }>(
    '/admin/exam-courses/preview',
    {
      exam_type: examType,
      region,
      framework_id: frameworkId,
      sort_mode: sortMode,
    },
  )
  return response.data.plan
}

export async function generateExamCourse(
  examType: string,
  region: string = 'alle',
  options?: { provider?: string; model?: string },
  frameworkId?: number,
  sortMode?: string,
): Promise<GenerateResult> {
  const response = await http.post<{ success: boolean } & GenerateResult>(
    '/admin/exam-courses/generate',
    {
      exam_type: examType,
      region,
      options,
      framework_id: frameworkId,
      sort_mode: sortMode,
    },
  )
  return {
    course_id: response.data.course_id,
    chapters_count: response.data.chapters_count,
    lm_count: response.data.lm_count,
    tokens_used: response.data.tokens_used,
    status: response.data.status,
  }
}

export async function getGenerationProgress(
  courseId: string
): Promise<GenerationProgress> {
  const response = await http.get<{ success: boolean; data: GenerationProgress }>(
    `/admin/exam-courses/courses/${courseId}/generation-progress`
  )
  return response.data.data
}
